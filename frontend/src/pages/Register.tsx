import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../types';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    phone_number: '',
    role: 'broker' as UserRole,
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    setIsSubmitting(true);

    try {
      await register({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        full_name: form.full_name.trim(),
        phone_number: form.phone_number.trim(),
        role: form.role,
      });
      navigate('/dashboard', { replace: true });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Registration failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="card">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900">Register as a BimaGrid agent</h1>
          <p className="mt-2 text-sm text-slate-500">
            Create your agent account to onboard farmers, monitor parametric policies, and coordinate
            payouts across your ward or cooperative.
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
          <label className="sm:col-span-2">
            <span className="mb-1 block text-sm font-medium text-slate-700">Full name</span>
            <input
              className="input-field"
              value={form.full_name}
              onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Username</span>
            <input
              className="input-field"
              value={form.username}
              onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Email</span>
            <input
              type="email"
              className="input-field"
              value={form.email}
              onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Phone number</span>
            <input
              className="input-field"
              placeholder="+254712345678"
              value={form.phone_number}
              onChange={(event) => setForm((current) => ({ ...current, phone_number: event.target.value }))}
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Agent role</span>
            <select
              className="input-field"
              value={form.role}
              onChange={(event) =>
                setForm((current) => ({ ...current, role: event.target.value as UserRole }))
              }
            >
              <option value="broker">Broker / Field Agent</option>
              <option value="farmer">Farmer</option>
              <option value="customer">Customer</option>
            </select>
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Password</span>
            <input
              type="password"
              className="input-field"
              minLength={8}
              value={form.password}
              onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Confirm password</span>
            <input
              type="password"
              className="input-field"
              minLength={8}
              value={form.confirmPassword}
              onChange={(event) =>
                setForm((current) => ({ ...current, confirmPassword: event.target.value }))
              }
              required
            />
          </label>

          <div className="sm:col-span-2">
            <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
              {isSubmitting ? 'Creating account…' : 'Create account'}
            </button>
          </div>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already registered?{' '}
          <Link to="/login" className="font-semibold text-bima-700 hover:text-bima-800">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
