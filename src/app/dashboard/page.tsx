import { auth } from '@/auth';
import DashboardClient from './dashboard-client';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {

  const session = await auth();

  if (!session?.user) {
    redirect('/login');
  }

  const userProp = {
    name: session.user.name ?? 'Guest User',
    email: session.user.email ?? 'No Email',
    avatar: session.user.image ?? '',
  };

  return <DashboardClient user={userProp} />;
}