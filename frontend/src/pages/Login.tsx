import { FormEvent, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

type LoginMode = 'email' | 'phone';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as { from?: string } | null)?.from ?? '/dashboard';

  const [mode, setMode] = useState<LoginMode>('email');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const username = identifier.trim();
      await login({ username, password });
      navigate(redirectTo, { replace: true });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Login failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[calc(100vh-12rem)] max-w-lg items-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="card w-full">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-bima-700 text-xl font-bold text-white">
            BG
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Agent login</h1>
          <p className="mt-2 text-sm text-slate-500">
            Sign in to manage farmer onboarding, policies, and parametric payouts.
          </p>
        </div>

        <div className="mb-6 flex rounded-lg bg-slate-100 p-1">
          <button
            type="button"
            onClick={() => setMode('email')}
            className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition ${
              mode === 'email' ? 'bg-white text-bima-800 shadow-sm' : 'text-slate-600'
            }`}
          >
            Email / Username
          </button>
          <button
            type="button"
            onClick={() => setMode('phone')}
            className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition ${
              mode === 'phone' ? 'bg-white text-bima-800 shadow-sm' : 'text-slate-600'
            }`}
          >
            Phone
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">
              {mode === 'email' ? 'Email or username' : 'Phone number'}
            </span>
            <input
              type={mode === 'email' ? 'text' : 'tel'}
              className="input-field"
              placeholder={mode === 'email' ? 'agent@cooperative.ke' : '+254712345678'}
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              autoComplete={mode === 'email' ? 'username' : 'tel'}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Password</span>
            <input
              type="password"
              className="input-field"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>

          <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          New agent?{' '}
          <Link to="/register" className="font-semibold text-bima-700 hover:text-bima-800">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
