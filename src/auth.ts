import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import { authConfig } from './auth.config';
import { z } from 'zod';
import bcrypt from 'bcryptjs';
import { getUser } from './lib/data';
 
export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  providers: [
    Credentials({
      async authorize(credentials) {
        const parsedCredentials = z
          .object({ email: z.string().email(), password: z.string().min(6) })
          .safeParse(credentials);
 
        if (parsedCredentials.success) {
          const { email, password } = parsedCredentials.data;
          const user = await getUser(email);
          if (!user) {
            console.log('No user found with that email.');
            return null;
          }
          
          const passwordsMatch = await bcrypt.compare(password, user.password);
 
          if (passwordsMatch) {
            return {
              id: user.id,
              name: user.name,
              email: user.email,
            };
          }
        }
 
        console.log('Invalid credentials');
        return null;
      },
    }),
  ],
});