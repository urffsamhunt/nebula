import asyncio
import panel as pn
import param
from typing import List, Dict, Any

# --- Direct Import of Backend Logic ---
# This assumes your project structure allows these imports
from core import db
from graph.workflow import graph_app
from api.v1.schemas.analysis import AnalysisResponse

# --- Configuration ---
pn.extension(sizing_mode="stretch_width")

# --- Application State Management using Param ---
class AppState(param.Parameterized):
    # Widgets
    resume_files = param.List(default=[], doc="List of uploaded resume files.")
    job_select = param.Selector(objects={}, doc="Selector for job descriptions.")
    
    # Buttons
    add_job_btn = param.Action(lambda self: self._open_add_job_modal(), label="Add New Job")
    refresh_jobs_btn = param.Action(lambda self: self.fetch_jobs(), label="Refresh List")
    evaluate_btn = param.Action(lambda self: self._start_evaluation(), label="Analyze Resumes")
    
    # Data
    evaluations = param.Dict(default={}, doc="Stores the state of each resume analysis.")
    
    # Internal state
    _modal_content = param.List(default=[])

    def __init__(self, **params):
        super().__init__(**params)
        self.fetch_jobs()

    @param.depends('refresh_jobs_btn', watch=True)
    def fetch_jobs(self):
        """Fetches all job descriptions from the database."""
        try:
            job_data = db.get_all_job_description()
            choices = {str(job["id"]): f"{job['job_role']} at {job['company_name']}" for job in job_data}
            self.param.job_select.objects = choices
        except Exception as e:
            pn.state.notifications.error(f"Failed to fetch jobs: {e}")

    def _open_add_job_modal(self):
        """Creates and shows the 'Add Job' modal content."""
        self.new_company = pn.widgets.TextInput(name="Company Name", placeholder="e.g., Google")
        self.new_role = pn.widgets.TextInput(name="Job Role", placeholder="e.g., Software Engineer")
        self.new_desc = pn.widgets.TextAreaInput(name="Job Description", height=200)
        save_btn = pn.widgets.Button(name="Save", button_type="primary")
        save_btn.on_click(self._save_new_job)

        self._modal_content = [
            pn.Column(
                pn.pane.Markdown("### Add New Job Description"),
                self.new_company,
                self.new_role,
                self.new_desc,
                pn.Row(pn.layout.HSpacer(), save_btn)
            )
        ]
        pn.state.template.open_modal()
    
    def _save_new_job(self, event):
        """Saves the new job description to the database."""
        try:
            db.save_job_description(
                company_name=self.new_company.value,
                job_role=self.new_role.value,
                description=self.new_desc.value,
            )
            pn.state.notifications.success("Job description saved!")
            self.fetch_jobs()
            pn.state.template.close_modal()
        except Exception as e:
            pn.state.notifications.error(f"Failed to save job: {e}")

    def _start_evaluation(self):
        """Starts the async task to handle the evaluation of all files."""
        if not self.resume_files or not self.job_select:
            pn.state.notifications.warning("Please upload resumes and select a job.")
            return
        
        # Clear previous results
        self.evaluations = {}
        
        # Schedule the coroutine to run without blocking
        pn.state.schedule_coroutine(self._handle_evaluation_async())

    async def _handle_evaluation_async(self):
        """Runs analysis for all uploaded resumes concurrently."""
        job_info = db.get_job_description(int(self.job_select))
        job_description_text = job_info["description"]
        
        # Create a list of analysis tasks
        analysis_tasks = [
            self._run_analysis_for_file(file_content, file_name, job_description_text)
            for file_name, file_content in self.resume_files
        ]
        await asyncio.gather(*analysis_tasks)
    
    async def _run_analysis_for_file(self, file_content: bytes, file_name: str, job_description: str):
        """Handles the streaming analysis for a single file and updates its state."""
        file_id = f"file_{hash(file_name)}"
        
        # Determine file format from extension
        file_ext = file_name.split('.')[-1].lower()
        file_format_map = {"pdf": "pdf", "docx": "docx", "txt": "txt"}
        file_format = file_format_map.get(file_ext)
        if not file_format:
            self.evaluations[file_id] = {"name": file_name, "status": "Error", "result": {"error": "Unsupported file type"}}
            self.param.trigger('evaluations')
            return

        # Set initial state
        self.evaluations[file_id] = {"name": file_name, "status": "Analyzing", "progress": [], "result": None}
        self.param.trigger('evaluations')

        try:
            initial_state = {
                "resume_file_content": file_content,
                "file_format": file_format,
                "job_description": job_description,
                "progress": []
            }

            # Stream results directly from the LangGraph app
            async for event in graph_app.astream(initial_state):
                node_name, node_output = next(iter(event.items()))
                
                if node_name == "__end__":
                    final_state = node_output
                    final_result = AnalysisResponse(
                        relevance_score=final_state["final_score"],
                        missing_keywords=final_state["hard_analysis"]["missing_keywords"],
                        verdict=final_state["final_verdict"],
                        suggestions=final_state["final_suggestions"]
                    )
                    self.evaluations[file_id]["status"] = "Complete"
                    self.evaluations[file_id]["result"] = final_result.model_dump()
                else:
                    self.evaluations[file_id]["progress"] = node_output.get("progress", [])
                
                self.param.trigger('evaluations') # Trigger UI update

        except Exception as e:
            self.evaluations[file_id]["status"] = "Error"
            self.evaluations[file_id]["result"] = {"error": str(e)}
            self.param.trigger('evaluations')

    @param.depends('evaluations', watch=True)
    def _render_results_area(self):
        """Renders the analysis results for each file based on the reactive state."""
        if not self.evaluations:
            return pn.pane.Markdown("Upload resumes and select a job description to begin.")

        cards = []
        for data in self.evaluations.values():
            status_ui = []
            result_ui = pn.Column()
            verdict_class = ""

            if data["status"] == "Analyzing":
                status_ui.append(pn.indicators.LoadingSpinner(value=True, width=20, height=20))
                status_ui.append(pn.pane.Markdown(f"**Analyzing...** (`{data['progress'][-1] if data['progress'] else 'Starting'}`)", margin=(0, 5)))
            
            elif data["status"] == "Complete":
                res = data["result"]
                verdict = res.get('verdict', '').lower()
                status_ui.append(pn.pane.Markdown("**✅ Complete**", margin=(0, 5)))
                result_ui = pn.Column(
                    pn.layout.Divider(),
                    pn.pane.Markdown("#### Report"),
                    pn.pane.Markdown(f"**Verdict:** {res.get('verdict', 'N/A')}"),
                    pn.pane.Markdown(f"**Relevance Score:** {res.get('relevance_score', 0)}%"),
                    pn.pane.Markdown(f"**Missing Keywords:**\n\n> {', '.join(res.get('missing_keywords', [])) or 'None'}"),
                    pn.pane.Markdown(f"**Suggestions:**\n\n> {res.get('suggestions', 'N/A')}"),
                )
            
            elif data["status"] == "Error":
                status_ui.append(pn.pane.Markdown(f"**❌ Error:** {data['result']['error']}", margin=(0, 5), style={'color': 'red'}))

            cards.append(
                pn.layout.Card(
                    pn.Row(*status_ui, align='center'),
                    result_ui,
                    title=data["name"],
                    styles={'border-left': f'5px solid {"#28a745" if data["status"] == "Complete" and verdict == "high" else "#ffc107" if data["status"] == "Complete" and verdict == "medium" else "#dc3545" if data["status"] == "Complete" else "#6c757d"}'}
                )
            )
        return pn.Column(*cards, sizing_mode="stretch_width")

# --- UI Layout ---
def create_app():
    state = AppState()

    # Define widgets and link them to the state manager
    file_input = pn.widgets.FileInput(multiple=True, accept=".pdf,.docx,.txt")
    file_input.link(state, value='resume_files', bidirectional=True)
    
    sidebar = pn.Column(
        pn.pane.Markdown("#### Controls"),
        file_input,
        pn.bind(pn.widgets.Select.from_param, state.param.job_select, name="Select Job Description"),
        pn.Row(
            pn.widgets.Button.from_param(state.param.add_job_btn),
            pn.widgets.Button.from_param(state.param.refresh_jobs_btn, button_type="default"),
        ),
        pn.layout.Divider(),
        pn.widgets.Button.from_param(state.param.evaluate_btn, button_type="primary", sizing_mode="stretch_width"),
        width=350
    )

    main_area = pn.Column(
        pn.pane.Markdown("#### Analysis Results"),
        state._render_results_area,
    )

    template = pn.template.FastListTemplate(
        site="Resume Analyzer",
        title="📄",
        sidebar=[sidebar],
        main=[main_area],
        modal=state._modal_content
    )
    return template

# --- Create and Serve the App ---
create_app().servable()