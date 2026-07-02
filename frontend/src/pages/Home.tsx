import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const FEATURES = [
  {
    title: 'Zero-touch parametric payouts',
    description:
      'Satellite-verified drought, flood, and hail triggers release M-Pesa payouts within 60 seconds — no manual claims adjustment.',
    icon: '⚡',
  },
  {
    title: 'H3 spatial precision',
    description:
      'Uber H3 Resolution 9 hexagons (~0.1 km²) align coverage to individual smallholder plots across Kenya and East Africa.',
    icon: '🗺️',
  },
  {
    title: 'Multi-peril coverage',
    description:
      'Protect maize, beans, sorghum, and more against drought, flood, frost, heat stress, hail, and pest outbreaks.',
    icon: '🌾',
  },
  {
    title: 'Cryptographic audit trail',
    description:
      'Independent Rust oracle nodes sign consensus data for regulators and reinsurers to verify every payout independently.',
    icon: '🔐',
  },
  {
    title: 'Offline-first USSD access',
    description:
      'Farmers register and check policy status via *384*XXX# — agents extend reach through the web portal.',
    icon: '📱',
  },
  {
    title: 'Mitigation discounts',
    description:
      'openEO satellite analytics verify drip irrigation and other measures, reducing premiums for verified practices.',
    icon: '🛰️',
  },
];

const STATS = [
  { label: 'Payout speed', value: '< 60s' },
  { label: 'Spatial resolution', value: 'H3 Res 9' },
  { label: 'Oracle consensus', value: '3 nodes' },
  { label: 'Perils covered', value: '6+' },
];

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div>
      <section className="relative overflow-hidden bg-gradient-to-br from-bima-950 via-bima-900 to-emerald-900 text-white">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute -left-20 top-10 h-72 w-72 rounded-full bg-bima-400 blur-3xl" />
          <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-emerald-300 blur-3xl" />
        </div>

        <div className="relative mx-auto grid max-w-7xl gap-12 px-4 py-20 sm:px-6 lg:grid-cols-2 lg:items-center lg:px-8 lg:py-28">
          <div>
            <p className="mb-4 inline-flex rounded-full border border-bima-400/40 bg-bima-800/40 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-bima-100">
              East Africa · Parametric Insurance
            </p>
            <h1 className="text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
              Turn satellite data into instant liquidity for farmers
            </h1>
            <p className="mt-6 max-w-xl text-lg text-bima-100">
              BimaGrid is a decentralized parametric climate insurance protocol for smallholder
              farmers. Agents onboard communities, monitor policies, and trigger evaluations — all
              backed by oracle consensus and trustless smart contract execution.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              {isAuthenticated ? (
                <Link to="/dashboard" className="btn-primary bg-white text-bima-900 hover:bg-bima-50">
                  Open dashboard
                </Link>
              ) : (
                <>
                  <Link to="/register" className="btn-primary bg-white text-bima-900 hover:bg-bima-50">
                    Register as agent
                  </Link>
                  <Link
                    to="/login"
                    className="inline-flex items-center justify-center rounded-lg border border-white/30 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/10"
                  >
                    Agent login
                  </Link>
                </>
              )}
            </div>
          </div>

          <div className="card border-white/10 bg-white/10 text-white backdrop-blur">
            <h2 className="text-lg font-semibold">Mission</h2>
            <p className="mt-3 text-bima-50">
              Deliver climate resilience to subsistence farmers without a single human in the claims
              loop. When rainfall drops below threshold, oracles reach consensus and M-Pesa sends
              liquidity before the next planting season is lost.
            </p>
            <dl className="mt-8 grid grid-cols-2 gap-4">
              {STATS.map((stat) => (
                <div key={stat.label} className="rounded-xl bg-white/10 p-4">
                  <dt className="text-xs uppercase tracking-wide text-bima-200">{stat.label}</dt>
                  <dd className="mt-1 text-2xl font-bold">{stat.value}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold text-slate-900">Built for agents on the ground</h2>
          <p className="mt-4 text-lg text-slate-600">
            The BimaGrid Agent Portal connects field officers, brokers, and cooperatives to the
            operational data plane — onboarding farmers, tracking active policies, and monitoring
            parametric payouts in real time.
          </p>
        </div>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <article key={feature.title} className="card transition hover:border-bima-200 hover:shadow-md">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-bima-50 text-2xl">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-slate-900">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{feature.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="border-y border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="grid gap-8 lg:grid-cols-3">
            <div className="card bg-bima-50 border-bima-100">
              <p className="text-sm font-semibold uppercase tracking-wide text-bima-700">Plane 1</p>
              <h3 className="mt-2 text-xl font-bold text-slate-900">Operational Data</h3>
              <p className="mt-2 text-sm text-slate-600">
                Django + PostGIS + openEO handle identity, land registry, H3 indexing, and premium
                calculation.
              </p>
            </div>
            <div className="card bg-emerald-50 border-emerald-100">
              <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">Plane 2</p>
              <h3 className="mt-2 text-xl font-bold text-slate-900">Oracle Consensus</h3>
              <p className="mt-2 text-sm text-slate-600">
                Three independent Rust nodes ingest CHIRPS, NASA POWER, and Sentinel-2 data with
                ECDSA signing.
              </p>
            </div>
            <div className="card bg-teal-50 border-teal-100">
              <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">Plane 3</p>
              <h3 className="mt-2 text-xl font-bold text-slate-900">Execution</h3>
              <p className="mt-2 text-sm text-slate-600">
                Smart contracts verify oracle signatures, evaluate thresholds, and authorize M-Pesa
                B2C payouts automatically.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="card flex flex-col items-start justify-between gap-6 bg-gradient-to-r from-bima-700 to-emerald-700 text-white lg:flex-row lg:items-center">
          <div>
            <h2 className="text-2xl font-bold">Ready to protect your community?</h2>
            <p className="mt-2 max-w-2xl text-bima-50">
              Join the BimaGrid agent network to register farmers, issue parametric policies, and
              deliver instant drought relief when satellites detect peril.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link to="/register" className="btn-primary bg-white text-bima-900 hover:bg-bima-50">
              Create agent account
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center rounded-lg border border-white/40 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
            >
              Sign in
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
