const STATUS_STYLES: Record<string, string> = {
  active: 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20',
  paid_out: 'bg-teal-400/10 text-teal-400 border border-teal-400/20',
  draft: 'bg-slate-400/10 text-slate-300 border border-slate-400/20',
  submitted: 'bg-blue-400/10 text-blue-400 border border-blue-400/20',
  under_review: 'bg-amber-400/10 text-amber-400 border border-amber-400/20',
  verified: 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20',
  approved: 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20',
  rejected: 'bg-red-400/10 text-red-400 border border-red-400/20',
  cancelled: 'bg-red-500/10 text-red-500 border border-red-500/20',
  lapsed: 'bg-orange-400/10 text-orange-400 border border-orange-400/20',
  completed: 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20',
  pending: 'bg-amber-400/10 text-amber-400 border border-amber-400/20',
  failed: 'bg-red-400/10 text-red-400 border border-red-400/20',
};

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const normalized = status.toLowerCase().replace(/\s+/g, '_');
  const style = STATUS_STYLES[normalized] ?? 'bg-slate-400/10 text-slate-300 border border-slate-400/20';

  return (
    <span
      className={`inline-flex items-center justify-center rounded-full px-2.5 py-1 text-xs font-semibold capitalize backdrop-blur-sm ${style} ${className}`}
    >
      <span className={`mr-1.5 h-1.5 w-1.5 rounded-full animate-pulse ${style.split(' ')[1].replace('text-', 'bg-')}`} />
      {status.replace(/_/g, ' ')}
    </span>
  );
}
