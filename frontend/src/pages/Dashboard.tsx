import { useCallback, useEffect, useMemo, useState } from 'react';
import { API_BASE_URL, dashboardApi } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import RegisterFarmerModal from '../components/RegisterFarmerModal';
import StatusBadge from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';
import type { Claim, HealthResponse, Payout, Policy } from '../types';

function formatCurrency(value: string | number): string {
  const amount = typeof value === 'string' ? parseFloat(value) : value;
  if (Number.isNaN(amount)) return 'KES 0';
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(value: string): string {
  if (!value) return '—';
  return new Date(value).toLocaleDateString('en-KE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export default function Dashboard() {
  const { user } = useAuth();
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionMessage, setActionMessage] = useState('');
  const [actionError, setActionError] = useState('');
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
  const [evaluationH3, setEvaluationH3] = useState('8928308280fffff');
  const [isEvaluating, setIsEvaluating] = useState(false);

  const loadDashboard = useCallback(async () => {
    setError('');
    setIsLoading(true);

    try {
      const [policyData, claimData, payoutData, healthData] = await Promise.all([
        dashboardApi.getPolicies(),
        dashboardApi.getClaims(),
        dashboardApi.getPayouts(),
        dashboardApi.health().catch(() => null),
      ]);

      setPolicies(policyData);
      setClaims(claimData);
      setPayouts(payoutData);
      setHealth(healthData);

      if (policyData[0]?.coverage_h3) {
        setEvaluationH3(policyData[0].coverage_h3);
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load dashboard data.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const activePolicies = useMemo(
    () => policies.filter((policy) => policy.status === 'active'),
    [policies],
  );

  const totalPremium = useMemo(
    () => policies.reduce((sum, policy) => sum + parseFloat(policy.premium_amount || '0'), 0),
    [policies],
  );

  const totalPayouts = useMemo(
    () => payouts.reduce((sum, payout) => sum + parseFloat(payout.amount || '0'), 0),
    [payouts],
  );

  const farmerRecords = useMemo(() => {
    const byOnboarding = new Map<string, Policy>();
    policies.forEach((policy) => {
      if (!byOnboarding.has(policy.onboarding)) {
        byOnboarding.set(policy.onboarding, policy);
      }
    });
    return Array.from(byOnboarding.entries()).map(([onboardingId, policy]) => ({
      onboardingId,
      policy,
    }));
  }, [policies]);

  const isAdmin = user?.profile?.role === 'admin' || user?.profile?.role === 'broker';

  const handleTriggerEvaluation = async () => {
    setActionMessage('');
    setActionError('');
    setIsEvaluating(true);

    try {
      const result = await dashboardApi.triggerEvaluation({
        h3_index: evaluationH3,
        simulate_drought: true,
      });
      setActionMessage(
        `Oracle evaluation queued for H3 ${evaluationH3}. Task: ${String(result.task_id ?? 'submitted')}.`,
      );
      await loadDashboard();
    } catch (evalError) {
      setActionError(
        evalError instanceof Error ? evalError.message : 'Failed to trigger evaluation.',
      );
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleSimulateDrought = async () => {
    setActionMessage('');
    setActionError('');

    try {
      await dashboardApi.simulateDrought({
        h3_index: evaluationH3,
        rainfall_mm: 15,
        ndvi: 0.35,
      });
      setActionMessage(`Drought simulation recorded for H3 ${evaluationH3}.`);
    } catch (simError) {
      setActionError(simError instanceof Error ? simError.message : 'Simulation failed.');
    }
  };

  if (isLoading) {
    return <LoadingSpinner label="Loading dashboard…" />;
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-bima-700">Agent dashboard</p>
          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            Welcome, {user?.profile?.full_name || user?.username}
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Monitor assigned farmers, active parametric policies, and recent claims & payouts.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button type="button" onClick={() => setIsRegisterModalOpen(true)} className="btn-primary">
            Register farmer
          </button>
          <button type="button" onClick={() => void loadDashboard()} className="btn-secondary">
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {actionMessage && (
        <div className="mb-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {actionMessage}
        </div>
      )}

      {actionError && (
        <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {actionError}
        </div>
      )}

      <div className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="card">
          <p className="text-sm text-slate-500">Assigned farmers</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{farmerRecords.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-500">Active policies</p>
          <p className="mt-2 text-3xl font-bold text-emerald-700">{activePolicies.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-500">Total premium volume</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{formatCurrency(totalPremium)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-500">Recent payouts</p>
          <p className="mt-2 text-3xl font-bold text-teal-700">{formatCurrency(totalPayouts)}</p>
        </div>
      </div>

      <div className="grid gap-8 xl:grid-cols-3">
        <section className="card xl:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Farmer & policy records</h2>
            <span className="text-xs text-slate-500">{policies.length} policies</span>
          </div>

          {policies.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-200 px-4 py-10 text-center">
              <p className="text-sm text-slate-500">No policies assigned yet.</p>
              <button
                type="button"
                onClick={() => setIsRegisterModalOpen(true)}
                className="btn-primary mt-4"
              >
                Register your first farmer
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500">
                    <th className="px-3 py-2 font-medium">Policy</th>
                    <th className="px-3 py-2 font-medium">Crop</th>
                    <th className="px-3 py-2 font-medium">H3 cell</th>
                    <th className="px-3 py-2 font-medium">Premium</th>
                    <th className="px-3 py-2 font-medium">Coverage</th>
                    <th className="px-3 py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {policies.map((policy) => (
                    <tr key={policy.id} className="border-b border-slate-100">
                      <td className="px-3 py-3 font-medium text-slate-900">{policy.policy_number}</td>
                      <td className="px-3 py-3 capitalize">{policy.crop}</td>
                      <td className="px-3 py-3 font-mono text-xs text-slate-600">{policy.coverage_h3}</td>
                      <td className="px-3 py-3">{formatCurrency(policy.premium_amount)}</td>
                      <td className="px-3 py-3 text-slate-600">
                        {formatDate(policy.coverage_start)} – {formatDate(policy.coverage_end)}
                      </td>
                      <td className="px-3 py-3">
                        <StatusBadge status={policy.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-slate-900">Quick actions</h2>
            <p className="mt-1 text-sm text-slate-500">Demo tools for hackathon and field testing.</p>

            <label className="mt-4 block">
              <span className="mb-1 block text-sm font-medium text-slate-700">H3 index</span>
              <input
                className="input-field font-mono text-xs"
                value={evaluationH3}
                onChange={(event) => setEvaluationH3(event.target.value)}
              />
            </label>

            <div className="mt-4 space-y-3">
              <button
                type="button"
                onClick={() => void handleTriggerEvaluation()}
                disabled={isEvaluating || !evaluationH3}
                className="btn-primary w-full"
              >
                {isEvaluating ? 'Queuing evaluation…' : 'Trigger oracle evaluation'}
              </button>

              {isAdmin && (
                <button
                  type="button"
                  onClick={() => void handleSimulateDrought()}
                  disabled={!evaluationH3}
                  className="btn-secondary w-full"
                >
                  Simulate drought (God Mode)
                </button>
              )}

              <button
                type="button"
                onClick={() => setIsRegisterModalOpen(true)}
                className="btn-secondary w-full"
              >
                Register new farmer
              </button>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-slate-900">System status</h2>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">API base</dt>
                <dd className="font-mono text-xs text-slate-700">{API_BASE_URL}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Backend health</dt>
                <dd>
                  {health ? (
                    <StatusBadge status={health.status === 'healthy' ? 'active' : 'failed'} />
                  ) : (
                    <span className="text-slate-400">Unavailable</span>
                  )}
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Version</dt>
                <dd className="text-slate-700">{health?.version ?? '—'}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Your role</dt>
                <dd className="capitalize text-slate-700">{user?.profile?.role}</dd>
              </div>
            </dl>
          </div>
        </section>
      </div>

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        <section className="card">
          <h2 className="text-lg font-semibold text-slate-900">Recent claims</h2>
          {claims.length === 0 ? (
            <p className="mt-4 text-sm text-slate-500">No claims recorded for your portfolio.</p>
          ) : (
            <ul className="mt-4 divide-y divide-slate-100">
              {claims.slice(0, 5).map((claim) => (
                <li key={claim.id} className="flex items-start justify-between gap-4 py-3">
                  <div>
                    <p className="font-medium text-slate-900">{claim.claim_number}</p>
                    <p className="text-sm capitalize text-slate-500">{claim.loss_type}</p>
                    <p className="text-xs text-slate-400">{formatDate(claim.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-slate-900">{formatCurrency(claim.claimed_amount)}</p>
                    <StatusBadge status={claim.status} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card">
          <h2 className="text-lg font-semibold text-slate-900">Recent payouts</h2>
          {payouts.length === 0 ? (
            <p className="mt-4 text-sm text-slate-500">No M-Pesa payouts yet for your assigned policies.</p>
          ) : (
            <ul className="mt-4 divide-y divide-slate-100">
              {payouts.slice(0, 5).map((payout) => (
                <li key={payout.id} className="flex items-start justify-between gap-4 py-3">
                  <div>
                    <p className="font-medium text-slate-900">{formatCurrency(payout.amount)}</p>
                    <p className="text-sm text-slate-500">{payout.phone_number}</p>
                    <p className="font-mono text-xs text-slate-400">{payout.reference}</p>
                  </div>
                  <div className="text-right">
                    <StatusBadge status={payout.status} />
                    <p className="mt-1 text-xs text-slate-400">{formatDate(payout.created_at)}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <RegisterFarmerModal
        isOpen={isRegisterModalOpen}
        onClose={() => setIsRegisterModalOpen(false)}
        onSuccess={() => void loadDashboard()}
      />
    </div>
  );
}
