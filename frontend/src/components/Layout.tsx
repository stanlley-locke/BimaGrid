import { Outlet, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import { Toaster } from 'react-hot-toast';

export default function Layout() {
  const location = useLocation();
  const isHome = location.pathname === '/';
  const isDashboard = location.pathname === '/dashboard';

  return (
    <div className={`flex min-h-screen flex-col selection:bg-bima-yellow/50 ${isDashboard ? 'bg-[#F4F1ED]' : ''}`}>
      <Toaster 
        position="top-right" 
        toastOptions={{
          style: {
            background: '#3A5A40',
            color: '#fff',
            borderRadius: '1rem',
            border: 'none',
          }
        }} 
      />
      {!isDashboard && <Navbar />}
      <main className={`flex-1 ${!isHome && !isDashboard ? 'pt-24' : ''}`}>
        <Outlet />
      </main>
    </div>
  );
}
