Pre-requisites:
Poetry

Install Poetry

The installer script is available directly at install.python-poetry.org, and is developed in its own repository. The script can be executed directly (i.e. ‘curl python’) or downloaded and then executed from disk (e.g. in a CI environment).

Linux, macOS, Windows (WSL)

curl -sSL https://install.python-poetry.org | python3 -

Windows (Powershell)

(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -



Setup:

Set the API key in .env in /backend


cd backend
poetry install

Download NLTK data: Open a Python shell (python) and run:
Python

poetry run python
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
exit()


poetry run uvicorn main:app --reload