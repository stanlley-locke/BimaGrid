import { FormEvent, useState } from 'react';
import { dashboardApi } from '../api/client';
import type { RegisterFarmerPayload } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Tractor, Map, Phone, Leaf } from 'lucide-react';
import toast from 'react-hot-toast';

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
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const updateField = <K extends keyof RegisterFarmerPayload>(key: K, value: RegisterFarmerPayload[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    const tId = toast.loading('Registering farmer...');

    try {
      await dashboardApi.registerFarmer(form);
      toast.success(`Farmer account created for ${form.full_name}`, { id: tId });
      onSuccess();
      onClose(); // Auto-close on success
    } catch (submitError) {
      toast.error(submitError instanceof Error ? submitError.message : 'Failed to register farmer.', { id: tId });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
          onClick={onClose}
        />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="card w-full max-w-2xl max-h-[90vh] overflow-y-auto relative z-10 p-6 sm:p-8"
        >
          <div className="absolute top-0 left-0 w-full h-2 bg-bima-green" />
          
          <div className="mb-8 flex items-start justify-between gap-4 border-b border-slate-100 pb-6">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-[1rem] bg-bima-lightGreen/50 text-bima-darkGreen">
                <Tractor className="w-7 h-7" />
              </div>
              <div>
                <h2 className="text-2xl font-extrabold text-bima-darkGreen tracking-tight">Register Farmer</h2>
                <p className="mt-1 text-sm text-slate-500 font-medium">
                  Create a new farmer account and capture their farm details.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="rounded-[1rem] p-2.5 bg-slate-50 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="grid gap-6 sm:grid-cols-2">
            <label className="sm:col-span-2 block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Full Name</span>
              <input
                className="input-field"
                value={form.full_name}
                onChange={(event) => updateField('full_name', event.target.value)}
                placeholder="Jane Doe"
                required
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Username</span>
              <input
                className="input-field"
                value={form.username}
                onChange={(event) => updateField('username', event.target.value)}
                placeholder="janedoe"
                required
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Email</span>
              <input
                type="email"
                className="input-field"
                value={form.email}
                onChange={(event) => updateField('email', event.target.value)}
                placeholder="jane@example.com"
                required
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Phone Number</span>
              <div className="relative">
                <input
                  className="input-field pl-11"
                  placeholder="+254712345678"
                  value={form.phone_number}
                  onChange={(event) => updateField('phone_number', event.target.value)}
                  required
                />
                <Phone className="absolute left-4 top-4 w-4 h-4 text-bima-green" />
              </div>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">M-Pesa Number</span>
              <input
                className="input-field"
                placeholder="254712345678"
                value={form.mpesa_number}
                onChange={(event) => updateField('mpesa_number', event.target.value)}
                required
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Temporary Password</span>
              <input
                type="password"
                className="input-field"
                minLength={8}
                value={form.password}
                onChange={(event) => updateField('password', event.target.value)}
                placeholder="••••••••"
                required
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Ward Code</span>
              <input
                className="input-field"
                placeholder="1234"
                value={form.ward_code}
                onChange={(event) => updateField('ward_code', event.target.value)}
                required
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Primary Crop</span>
              <div className="relative">
                <select
                  className="input-field appearance-none pr-10"
                  value={form.crop}
                  onChange={(event) => updateField('crop', event.target.value)}
                >
                  {CROP_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value} className="bg-white text-slate-900">
                      {option.label}
                    </option>
                  ))}
                </select>
                <Leaf className="absolute right-4 top-4 w-4 h-4 text-bima-green pointer-events-none" />
              </div>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Farm Size (Acreage)</span>
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

            <label className="sm:col-span-2 block">
              <span className="mb-2 block text-sm font-semibold text-bima-darkGreen">Farm Location Code (Region)</span>
              <div className="relative">
                <input
                  className="input-field font-mono text-xs pl-11 bg-slate-50 border-slate-200"
                  value={form.h3_index}
                  onChange={(event) => updateField('h3_index', event.target.value)}
                  placeholder="e.g. 8928308280fffff"
                  required
                />
                <Map className="absolute left-4 top-4 w-4 h-4 text-bima-green" />
              </div>
            </label>

            <div className="flex gap-4 sm:col-span-2 mt-4 pt-6 border-t border-slate-100">
              <button type="button" onClick={onClose} className="btn-secondary flex-1 py-4 text-base">
                Cancel
              </button>
              <button type="submit" disabled={isSubmitting} className="btn-primary flex-1 py-4 text-base shadow-md hover:shadow-lg">
                {isSubmitting ? 'Creating...' : 'Create farmer account'}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
