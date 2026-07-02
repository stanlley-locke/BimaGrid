interface LoadingSpinnerProps {
  label?: string;
  className?: string;
}

export default function LoadingSpinner({ label = 'Loading…', className = '' }: LoadingSpinnerProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-3 py-12 ${className}`}>
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-bima-200 border-t-bima-700" />
      <p className="text-sm text-slate-500">{label}</p>
    </div>
  );
}
