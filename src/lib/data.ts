import 'server-only';
import { createClient } from '@supabase/supabase-js';
import type { User } from './definitions';
import bcrypt from 'bcryptjs';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!,
  { auth: { persistSession: false } }
);

function createServiceRoleClient() {
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!,
    {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
      },
    }
  );
}

export async function getUser(email: string): Promise<User | undefined> {
  try {
    const { data, error } = await supabase
      .from('users')
      .select('*') 
      .eq('email', email)
      .single();

    if (error && error.code !== 'PGRST116') {
      console.error('Supabase error:', error.message);
      throw new Error('Failed to fetch user.');
    }

    return data || undefined;
  } catch (error) {
    console.error('Failed to fetch user:', error);
    throw new Error('Failed to fetch user.');
  }
}

export async function createUser(name: string, email: string, password: string) {
  const supabase = createServiceRoleClient();
  
  try {
    const hashedPassword = await bcrypt.hash(password, 10);

    const { data, error } = await supabase
      .from('users')
      .insert([
        { name: name, email: email, password: hashedPassword }
      ])
      .select();

    if (error) {
      if (error.code === '23505') { 
        console.error('Email already exists.');
        throw new Error('Email already exists.');
      }
      console.error('Supabase error:', error.message);
      throw new Error('Failed to create user.');
    }

    console.log('User created:', data);
    return data;

  } catch (error) {
    console.error('Database Error: Failed to create user:', error);
    throw new Error('Failed to create user.');
  }
}