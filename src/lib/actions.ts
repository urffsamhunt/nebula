'use server';

import { signIn, signOut } from '@/auth';
import { AuthError } from 'next-auth';
import { createUser } from './data';

export async function authenticate(
  prevState: string | undefined,
  formData: FormData,
) {
  try {
    await signIn('credentials', formData);
  } catch (error) {
    if (error instanceof AuthError) {
      switch (error.type) {
        case 'CredentialsSignin':
          return 'Invalid credentials.';
        default:
          return 'Something went wrong.';
      }
    }
    throw error;
  }
}

export async function logout() {
  'use server';
  await signOut();
}

export async function signUp(prevState: string | undefined, formData: FormData) {
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  if (!name || !email || !password) {
    return 'Please fill in all fields.';
  }

  try {
    await createUser(name, email, password);
  } catch (error: any) {
    if (error.message.includes('Email already exists')) {
      return 'An account with this email already exists.';
    }
    console.error('Create user error:', error.message);
    return 'Database Error: Failed to create user.';
  }

  try {
    await signIn('credentials', { email, password });
  } catch (error) {
    if (error instanceof AuthError) {
      switch (error.type) {
        case 'CredentialsSignin':
          return 'Login failed after sign up. Please try logging in manually.';
        default:
          return 'Something went wrong during sign in.';
      }
    }
    throw error;
  }
}