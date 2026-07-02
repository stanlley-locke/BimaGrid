import { FormEvent, useState } from 'react';
import { dashboardApi } from '../api/client';
import type { RegisterFarmerPayload } from '../types';

const CROP_OPTIONS = [
  { value: 'maize', label: 'Maize' },
  { value: 'beans', label: 'Beans' },
  { value: 'sorghum', label: 'Sorghum' },
  { value: 'rice', label: 'Rice' },
  { value: 'coffee', label: 'Coffee' },
  { value: 'tea', label: 'Tea' },
  { value: 'mixed', label: 'Mixed Crops' },
];

interface RegisterFarmerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function RegisterFarmerModal({ isOpen, onClose, onSuccess }: RegisterFarmerModalProps) {
  const [form, setForm] = useState<RegisterFarmerPayload>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone_number: '',
    ward_code: '',
    crop: 'maize',
    acreage: '1.0',
    mpesa_number: '',
    h3_index: '8928308280fffff',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  if (!isOpen) return null;

  const updateField = <K extends keyof RegisterFarmerPayload>(key: K, value: RegisterFarmerPayload[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setSuccessMessage('');
    setIsSubmitting(true);

    try {
      await dashboardApi.registerFarmer(form);
      setSuccessMessage(`Farmer account created for ${form.full_name}. They can complete onboarding via USSD or login.`);
      onSuccess();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Failed to register farmer.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
      <div className="card max-h-[90vh] w-full max-w-2xl overflow-y-auto">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Register Farmer</h2>
            <p className="mt-1 text-sm text-slate-500">
              Create a farmer account and capture initial farm details for onboarding.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            {successMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
          <label className="sm:col-span-2">
            <span className="mb-1 block text-sm font-medium text-slate-700">Full name</span>
            <input
              className="input-field"
              value={form.full_name}
              onChange={(event) => updateField('full_name', event.target.value)}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Username</span>
            <input
              className="input-field"
              value={form.username}
              onChange={(event) => updateField('username', event.target.value)}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Email</span>
            <input
              type="email"
              className="input-field"
              value={form.email}
              onChange={(event) => updateField('email', event.target.value)}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Phone</span>
            <input
              className="input-field"
              placeholder="+254712345678"
              value={form.phone_number}
              onChange={(event) => updateField('phone_number', event.target.value)}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">M-Pesa number</span>
            <input
              className="input-field"
              placeholder="254712345678"
              value={form.mpesa_number}
              onChange={(event) => updateField('mpesa_number', event.target.value)}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Temporary password</span>
            <input
              type="password"
              className="input-field"
              minLength={8}
              value={form.password}
              onChange={(event) => updateField('password', event.target.value)}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Ward code</span>
            <input
              className="input-field"
              placeholder="1234"
              value={form.ward_code}
              onChange={(event) => updateField('ward_code', event.target.value)}
              required
            />
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Crop</span>
            <select
              className="input-field"
              value={form.crop}
              onChange={(event) => updateField('crop', event.target.value)}
            >
              {CROP_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span className="mb-1 block text-sm font-medium text-slate-700">Acreage</span>
            <input
              type="number"
              step="0.1"
              min="0.1"
              className="input-field"
              value={form.acreage}
              onChange={(event) => updateField('acreage', event.target.value)}
              required
            />
          </label>

          <label className="sm:col-span-2">
            <span className="mb-1 block text-sm font-medium text-slate-700">H3 coverage index</span>
            <input
              className="input-field font-mono text-xs"
              value={form.h3_index}
              onChange={(event) => updateField('h3_index', event.target.value)}
              required
            />
          </label>

          <div className="flex gap-3 sm:col-span-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="btn-primary flex-1">
              {isSubmitting ? 'Creating…' : 'Create farmer account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
