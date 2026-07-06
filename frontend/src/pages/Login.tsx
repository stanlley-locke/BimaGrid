import { FormEvent, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { LogIn, User, Briefcase, KeyRound, Mail, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';

type LoginType = 'farmer' | 'agent';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as { from?: string } | null)?.from ?? '/dashboard';

  const [loginType, setLoginType] = useState<LoginType>('farmer');
  const [identifier, setIdentifier] = useState('');
  const [agentEmail, setAgentEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!identifier || !password || (loginType === 'agent' && !agentEmail)) {
      toast.error('Please enter all required fields.');
      return;
    }

    try {
      setIsSubmitting(true);
      await login({ username: identifier, password });
      toast.success(`Successfully logged in as ${loginType}!`);
      navigate(redirectTo, { replace: true });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[90vh] flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 bg-[#F4F1ED]">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="sm:mx-auto sm:w-full sm:max-w-md"
      >
        <Link to="/" className="flex items-center gap-3 justify-center mb-6 group">
          <img src="/bimagrid_logo.png" alt="BimaGrid Logo" className="h-14 w-14 rounded-2xl object-cover shadow-sm group-hover:scale-105 transition-transform" />
          <span className="text-4xl font-extrabold tracking-tight text-[#1B2B20] font-sans">bimagrid</span>
        </Link>
        <h2 className="mt-2 text-center text-3xl font-extrabold text-[#1B2B20] tracking-tight">
          Welcome back
        </h2>
        <p className="mt-2 text-center text-[15px] font-medium text-slate-500">
          Sign in to your BimaGrid account
        </p>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        className="mt-8 sm:mx-auto sm:w-full sm:max-w-md"
      >
        <div className="bg-white py-8 px-4 shadow-xl sm:rounded-[2rem] sm:px-10 border border-slate-100">
          
          <div className="flex bg-[#F4F1ED] p-1.5 rounded-2xl mb-8">
            <button
              type="button"
              onClick={() => { setLoginType('farmer'); setIdentifier(''); setAgentEmail(''); setPassword(''); }}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold transition-all ${
                loginType === 'farmer' 
                  ? 'bg-white text-[#1B2B20] shadow-sm' 
                  : 'text-slate-500 hover:text-[#1B2B20]'
              }`}
            >
              <User className="w-4 h-4" /> Farmer
            </button>
            <button
              type="button"
              onClick={() => { setLoginType('agent'); setIdentifier(''); setAgentEmail(''); setPassword(''); }}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold transition-all ${
                loginType === 'agent' 
                  ? 'bg-white text-[#1B2B20] shadow-sm' 
                  : 'text-slate-500 hover:text-[#1B2B20]'
              }`}
            >
              <Briefcase className="w-4 h-4" /> Agent
            </button>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <AnimatePresence mode="wait">
              <motion.div
                key={loginType}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                {loginType === 'agent' && (
                  <div>
                    <label htmlFor="agentEmail" className="block text-[13px] font-bold text-slate-700 uppercase tracking-wider mb-2">
                      Agent Email
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-slate-400" />
                      </div>
                      <input
                        id="agentEmail"
                        name="agentEmail"
                        type="email"
                        required
                        value={agentEmail}
                        onChange={(e) => setAgentEmail(e.target.value)}
                        placeholder="agent@bimagrid.com"
                        className="block w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-sm font-medium focus:ring-2 focus:ring-[#659A5F] focus:border-[#659A5F] transition-all placeholder:text-slate-400"
                      />
                    </div>
                  </div>
                )}

                <div>
                  <label htmlFor="identifier" className="block text-[13px] font-bold text-slate-700 uppercase tracking-wider mb-2">
                    {loginType === 'agent' ? 'Agent ID' : 'Phone Number or Email'}
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      {loginType === 'agent' ? (
                        <Briefcase className="h-5 w-5 text-slate-400" />
                      ) : (
                        <User className="h-5 w-5 text-slate-400" />
                      )}
                    </div>
                    <input
                      id="identifier"
                      name="identifier"
                      type="text"
                      required
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      placeholder={loginType === 'agent' ? 'e.g. AGN-G26A001' : 'Enter your phone or email'}
                      className="block w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-sm font-medium focus:ring-2 focus:ring-[#659A5F] focus:border-[#659A5F] transition-all placeholder:text-slate-400"
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label htmlFor="password" className="block text-[13px] font-bold text-slate-700 uppercase tracking-wider">
                      Password
                    </label>
                    <Link to="#" className="text-[13px] font-bold text-[#659A5F] hover:text-[#1B2B20] transition-colors">
                      Forgot password?
                    </Link>
                  </div>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <KeyRound className="h-5 w-5 text-slate-400" />
                    </div>
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      className="block w-full pl-11 pr-12 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-sm font-medium focus:ring-2 focus:ring-[#659A5F] focus:border-[#659A5F] transition-all placeholder:text-slate-400"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors focus:outline-none"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 py-4 px-4 border border-transparent rounded-2xl shadow-sm text-[15px] font-bold text-white bg-[#1B2B20] hover:bg-[#2c4233] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1B2B20] transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <LogIn className="w-5 h-5" /> Sign In {loginType === 'agent' ? 'as Agent' : ''}
                  </>
                )}
              </button>
            </div>
          </form>

          {loginType === 'farmer' && (
            <div className="mt-8 text-center">
              <p className="text-sm font-medium text-slate-500">
                New to BimaGrid?{' '}
                <Link to="/register" className="font-bold text-[#659A5F] hover:text-[#1B2B20] transition-colors">
                  Create a farmer account
                </Link>
              </p>
            </div>
          )}
          {loginType === 'agent' && (
            <div className="mt-8 text-center p-4 bg-slate-50 rounded-xl">
              <p className="text-xs font-medium text-slate-500 leading-relaxed">
                Agents are registered by Administrators. You will receive your Agent ID via email when your account is approved.
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
