import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getStoredToken } from '../api/client';
import LoadingSpinner from './LoadingSpinner';
import { ForcePasswordResetModal } from './ForcePasswordResetModal';

interface ProtectedRouteProps {
  children: ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading, refreshUser } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingSpinner label="Checking session…" />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  const token = getStoredToken() || '';

  return (
    <>
      <ForcePasswordResetModal 
        isOpen={Boolean(user?.profile?.requires_password_change)} 
        token={token} 
        onSuccess={() => { refreshUser() }} 
      />
      {children}
    </>
  );
}
