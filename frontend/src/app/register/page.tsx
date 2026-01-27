'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AuthForm, { AuthFormData } from '@/components/AuthForm';
import { signUp } from '@/lib/auth-client';

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async (data: AuthFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await signUp(data.email, data.password, data.name || '');

      if (result.error) {
        if (result.error.toLowerCase().includes('already')) {
          setError('An account with this email already exists');
        } else {
          setError(result.error || 'Registration failed. Please try again.');
        }
        return;
      }

      // Registration successful - redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      console.error('Registration error:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-fuchsia-50 dark:from-indigo-950 dark:via-purple-950 dark:to-violet-950 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 bg-clip-text text-transparent">
            Create Account
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Join Todo App to manage your tasks
          </p>
        </div>

        {/* Form Card */}
        <div className="glass-strong rounded-2xl shadow-xl p-8">
          <AuthForm
            mode="register"
            onSubmit={handleRegister}
            error={error}
            isLoading={isLoading}
          />

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link
                href="/login"
                className="font-semibold text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-gray-500 dark:text-gray-500">
          By creating an account, you agree to our Terms of Service
        </p>
      </div>
    </div>
  );
}
