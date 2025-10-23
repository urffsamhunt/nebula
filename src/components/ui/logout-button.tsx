import { logout } from '@/lib/actions';
import { Button } from '@/components/ui/button';
import { PowerIcon } from '@heroicons/react/24/outline';

export default function LogoutButton() {
  return (
    <form action={logout}>
      <Button type="submit" variant="ghost" className="w-full justify-start">
        <PowerIcon className="w-6 h-6 mr-2" />
        <div className="hidden md:block">Sign Out</div>
      </Button>
    </form>
  );
}