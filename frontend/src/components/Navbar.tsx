import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function navClassName({ isActive }: { isActive: boolean }) {
  return isActive
    ? 'rounded-lg bg-bima-50 px-3 py-2 text-sm font-semibold text-bima-800'
    : 'rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900';
}

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-bima-700 text-lg font-bold text-white">
            BG
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900">BimaGrid</p>
            <p className="text-xs text-slate-500">Agent Portal</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          <NavLink to="/" end className={navClassName}>
            Home
          </NavLink>
          {isAuthenticated ? (
            <NavLink to="/dashboard" className={navClassName}>
              Dashboard
            </NavLink>
          ) : (
            <>
              <NavLink to="/login" className={navClassName}>
                Login
              </NavLink>
              <NavLink to="/register" className={navClassName}>
                Register
              </NavLink>
            </>
          )}
        </nav>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium text-slate-900">
                  {user?.profile?.full_name || user?.username}
                </p>
                <p className="text-xs capitalize text-slate-500">{user?.profile?.role}</p>
              </div>
              <button type="button" onClick={logout} className="btn-secondary">
                Sign out
              </button>
            </>
          ) : (
            <Link to="/register" className="btn-primary hidden sm:inline-flex">
              Become an agent
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
