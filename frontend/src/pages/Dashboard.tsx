import { useCallback, useEffect, useMemo, useState } from 'react';
import { dashboardApi } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import RegisterFarmerModal from '../components/RegisterFarmerModal';
import StatusBadge from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';
import type { Claim, HealthResponse, Payout, Policy } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, FileText, Banknote, RefreshCw, Zap, CloudLightning, 
  Activity, AlertCircle, ArrowUpRight, LayoutDashboard, Database,
  Settings, Server, LogOut, Search, Menu, Bell, CloudRain, Shield, BookOpen, Sliders, Leaf, Tractor, X
} from 'lucide-react';
import toast from 'react-hot-toast';

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

const tabVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 30 } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } }
};

type TabId = 'overview' | 'farmers' | 'claims' | 'weather' | 'resources' | 'system' | 'settings';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
  const [evaluationH3, setEvaluationH3] = useState('8928308280fffff');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [selectedPolicyForDetail, setSelectedPolicyForDetail] = useState<Policy | null>(null);
  const [weatherSearchH3, setWeatherSearchH3] = useState('8928308280fffff');
  const [weatherAnalysis, setWeatherAnalysis] = useState<{ rainfall: number | null; ndvi: number | null; loading: boolean; error: string | null }>({
    rainfall: null,
    ndvi: null,
    loading: false,
    error: null
  });
  const [resourceSearch, setResourceSearch] = useState('');
  const [calculatorAcreage, setCalculatorAcreage] = useState('1.0');
  const [calculatorCrop, setCalculatorCrop] = useState('maize');

  const loadDashboard = useCallback(async (showToast = false) => {
    if (!showToast) setIsLoading(true);
    
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
      
      if (showToast) {
        toast.success("Dashboard data refreshed");
      }
    } catch (loadError) {
      toast.error(loadError instanceof Error ? loadError.message : 'Failed to load dashboard data.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const handleQueryWeather = async () => {
    if (!weatherSearchH3) return;
    setWeatherAnalysis(prev => ({ ...prev, loading: true, error: null }));
    try {
      const [rainfallRes, ndviRes] = await Promise.all([
        dashboardApi.getRainfall(weatherSearchH3),
        dashboardApi.getNdvi(weatherSearchH3)
      ]);
      setWeatherAnalysis({
        rainfall: rainfallRes.value,
        ndvi: ndviRes.value,
        loading: false,
        error: null
      });
      toast.success(`Weather analysis fetched for ${weatherSearchH3}`);
    } catch (err) {
      setWeatherAnalysis({
        rainfall: null,
        ndvi: null,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to query'
      });
      toast.error('Failed to query weather metrics.');
    }
  };

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

  const filteredPolicies = useMemo(() => {
    if (!searchQuery) return policies;
    const lowerQuery = searchQuery.toLowerCase();
    return policies.filter(p => 
      p.policy_number?.toLowerCase().includes(lowerQuery) || 
      p.coverage_h3?.toLowerCase().includes(lowerQuery) ||
      p.crop?.toLowerCase().includes(lowerQuery)
    );
  }, [policies, searchQuery]);

  const isAdmin = user?.profile?.role === 'admin' || user?.profile?.role === 'broker';
  const isFarmer = user?.profile?.role === 'farmer';

  const farmerActivePoliciesCount = useMemo(
    () => policies.filter((p) => p.status === 'active').length,
    [policies]
  );

  const farmerTotalAcreage = useMemo(
    () => policies.reduce((sum, p) => sum + parseFloat(p.insured_acreage || '0'), 0),
    [policies]
  );

  const farmerTotalPremium = useMemo(
    () => policies.reduce((sum, p) => sum + parseFloat(p.premium_amount || '0'), 0),
    [policies]
  );

  const farmerTotalPayouts = useMemo(
    () => payouts.reduce((sum, p) => sum + parseFloat(p.amount || '0'), 0),
    [payouts]
  );

  const handleTriggerEvaluation = async () => {
    setIsEvaluating(true);
    const tId = toast.loading("Checking weather data...");
    try {
      await dashboardApi.triggerEvaluation({ h3_index: evaluationH3, simulate_drought: true });
      toast.success(`Check started successfully.`, { id: tId });
      await loadDashboard();
    } catch (evalError) {
      toast.error(evalError instanceof Error ? evalError.message : 'Failed to check weather.', { id: tId });
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleSimulateDrought = async () => {
    const tId = toast.loading("Simulating bad weather...");
    try {
      await dashboardApi.simulateDrought({ h3_index: evaluationH3, rainfall_mm: 15, ndvi: 0.35 });
      toast.success(`Bad weather simulation recorded for region ${evaluationH3}`, { id: tId });
    } catch (simError) {
      toast.error(simError instanceof Error ? simError.message : 'Simulation failed.', { id: tId });
    }
  };

  const NavItem = ({ id, icon: Icon, label }: { id: TabId, icon: any, label: string }) => (
    <button 
      onClick={() => setActiveTab(id)}
      title={label}
      className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center p-3' : 'gap-4 px-5 py-4'} rounded-2xl text-[13px] font-extrabold tracking-wide transition-all duration-300 ${activeTab === id ? 'bg-gradient-to-r from-[#1B2B20] to-[#2a4232] text-white shadow-[0_8px_20px_rgba(27,43,32,0.2)]' : 'text-slate-500 hover:bg-[#F4F1ED] hover:text-[#1B2B20]'}`}
    >
      <Icon className={`w-5 h-5 shrink-0 ${activeTab === id ? 'text-[#EAD35B]' : ''}`} /> 
      {!isSidebarCollapsed && <span>{label}</span>}
    </button>
  );

  if (isLoading) {
    return (
      <div className="h-screen bg-[#F8F7F5] flex items-center justify-center">
        <LoadingSpinner label="Loading dashboard…" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#F8F7F5] overflow-hidden selection:bg-bima-yellow/50">
      {/* Sidebar */}
      <aside className={`${isSidebarCollapsed ? 'w-[90px]' : 'w-[280px]'} bg-white border-r border-slate-100 flex flex-col flex-shrink-0 z-30 shadow-[4px_0_40px_rgba(0,0,0,0.02)] transition-all duration-300 ease-in-out relative`}>
        <div className={`p-8 ${isSidebarCollapsed ? 'flex justify-center px-4' : ''}`}>
          {!isSidebarCollapsed ? (
            <div className="flex items-center gap-4">
              <div className="relative">
                <img src="/bimagrid_logo.png" alt="BimaGrid Logo" className="h-12 w-12 rounded-[14px] object-cover shadow-sm" />
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-bima-yellow rounded-full border-2 border-white"></div>
              </div>
              <div>
                <p className="text-2xl font-black tracking-tight text-bima-darkGreen font-sans leading-none">bimagrid</p>
                <p className="text-[10px] font-extrabold text-bima-green uppercase tracking-widest mt-1">
                  {isFarmer ? 'Farmer Portal' : 'Agent Portal'}
                </p>
              </div>
            </div>
          ) : (
            <img src="/bimagrid_logo.png" alt="BimaGrid Logo" className="h-12 w-12 rounded-[14px] object-cover shadow-sm" />
          )}
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar px-4 pb-8 space-y-2 mt-2">
          {!isSidebarCollapsed && (
            <p className="px-5 text-[10px] font-extrabold text-slate-400 uppercase tracking-widest mb-4">Main Navigation</p>
          )}
          
          <NavItem id="overview" icon={LayoutDashboard} label="Overview" />
          {isFarmer ? (
            <NavItem id="farmers" icon={Shield} label="My Policies" />
          ) : (
            <NavItem id="farmers" icon={Users} label="Farmers & Plans" />
          )}
          <NavItem id="claims" icon={Banknote} label={isFarmer ? "My Payouts" : "Claims & Payouts"} />
          {!isFarmer && <NavItem id="weather" icon={CloudRain} label="Weather Analytics" />}
          
          <div className="my-6"></div>
          {!isSidebarCollapsed && (
            <p className="px-5 text-[10px] font-extrabold text-slate-400 uppercase tracking-widest mb-4">
              {isFarmer ? "Account" : "Management"}
            </p>
          )}
          
          {!isFarmer && <NavItem id="resources" icon={BookOpen} label="Agent Resources" />}
          {!isFarmer && <NavItem id="system" icon={Server} label="System Actions" />}
          <NavItem id="settings" icon={Sliders} label="Settings" />
        </div>

        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          {!isSidebarCollapsed && !isFarmer && (
            <button type="button" onClick={() => setIsRegisterModalOpen(true)} className="w-full flex items-center justify-center gap-2 py-4 px-4 border border-transparent rounded-2xl shadow-[0_4px_14px_rgba(101,154,95,0.3)] text-sm font-bold text-white bg-bima-green hover:bg-[#527d4c] transition-all mb-3 hover:-translate-y-0.5">
              <Shield className="w-4 h-4" /> Register Farmer
            </button>
          )}
          <button 
            type="button" 
            onClick={() => void logout()} 
            title="Sign Out"
            className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center p-4' : 'gap-3 px-5 py-4'} rounded-2xl text-[13px] font-extrabold text-red-500 hover:bg-red-50 transition-colors`}
          >
            <LogOut className="w-5 h-5 shrink-0" /> {!isSidebarCollapsed && <span>Sign Out</span>}
          </button>
        </div>
      </aside>

      {/* Main Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        
        {/* Dedicated Dashboard Navbar */}
        <header className="h-[90px] bg-white/80 backdrop-blur-md border-b border-slate-100 flex items-center justify-between px-6 sm:px-10 shrink-0 relative z-20">
           <div className="flex items-center gap-6">
             <button 
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)} 
                className="p-3 text-slate-400 hover:text-bima-darkGreen bg-white hover:bg-slate-50 rounded-2xl shadow-sm border border-slate-100 transition-all focus:outline-none focus:ring-2 focus:ring-bima-yellow"
             >
               <Menu className="w-5 h-5" />
             </button>
             <div className="hidden sm:block">
               <h2 className="text-[22px] font-black text-bima-darkGreen capitalize tracking-tight">
                  {isFarmer && activeTab === 'farmers' ? 'My Policies' : isFarmer && activeTab === 'claims' ? 'My Payouts' : activeTab.replace('-', ' ')}
               </h2>
               <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">
                 <span>Portal</span> <span className="w-1 h-1 rounded-full bg-slate-300"></span> <span className="text-bima-green">{isFarmer && activeTab === 'farmers' ? 'My Policies' : isFarmer && activeTab === 'claims' ? 'My Payouts' : activeTab.replace('-', ' ')}</span>
               </div>
             </div>
           </div>
           
           <div className="flex items-center gap-6">
              <button className="relative p-3 bg-white border border-slate-100 shadow-sm text-slate-400 hover:text-bima-darkGreen rounded-2xl transition-all group hover:-translate-y-0.5 hover:shadow-md">
                 <Bell className="w-5 h-5 group-hover:animate-wiggle" />
                 <span className="absolute top-2 right-2.5 w-2.5 h-2.5 bg-bima-yellow border-2 border-white rounded-full animate-pulse"></span>
              </button>
              
              <div className="h-10 w-px bg-slate-200"></div>
              
              <div className="flex items-center gap-4 cursor-pointer group bg-white border border-slate-100 p-2 pr-5 rounded-[20px] shadow-sm hover:shadow-md transition-all">
                 <div className="w-10 h-10 rounded-[14px] bg-gradient-to-br from-bima-lightGreen to-bima-green flex items-center justify-center font-black text-white text-lg shadow-inner">
                   {user?.profile?.full_name?.charAt(0) || user?.username?.charAt(0) || 'A'}
                 </div>
                 <div className="hidden md:block text-sm text-left">
                   <p className="font-extrabold text-bima-darkGreen group-hover:text-bima-green transition-colors leading-tight">{user?.profile?.full_name || 'Agent'}</p>
                   <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-0.5">{user?.profile?.role || 'Broker'}</p>
                 </div>
              </div>
           </div>
        </header>

        {/* Scrollable Content Area */}
        <main className="flex-1 overflow-y-auto relative z-10 scroll-smooth p-6 sm:p-10">
          <div className="absolute inset-0 opacity-[0.02] pointer-events-none -z-10" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='3' cy='3' r='1.5' fill='%231B2B20'/%3E%3C/svg%3E\")", backgroundSize: "24px 24px" }}></div>
          
          <div className="max-w-[1400px] mx-auto">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10">
              <div>
                <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-bima-darkGreen capitalize">
                  {activeTab === 'overview' ? `Welcome back, ${user?.profile?.full_name?.split(' ')[0] || (isFarmer ? 'Farmer' : 'Agent')}` : isFarmer && activeTab === 'farmers' ? 'My Policies' : isFarmer && activeTab === 'claims' ? 'My Payouts' : activeTab.replace('-', ' ')}
                </h1>
                {activeTab === 'overview' && (
                   <p className="text-[15px] font-semibold text-slate-500 mt-2 max-w-xl leading-relaxed">
                     {isFarmer ? 'Here is a summary of your active crop protection plans and payouts.' : "Here is what's happening with your registered farm protection plans today."}
                   </p>
                )}
              </div>
              <button type="button" onClick={() => void loadDashboard(true)} className="btn-secondary gap-2 text-sm px-5 py-3 bg-white hover:bg-slate-50 shadow-sm border border-slate-200 shrink-0 hover:-translate-y-0.5 transition-transform">
                <RefreshCw className="w-4 h-4 text-bima-green" /> <span className="hidden sm:inline text-bima-darkGreen">Refresh Data</span>
              </button>
            </div>

            <AnimatePresence mode="wait">
              {activeTab === 'overview' && (
                <motion.div key="overview" variants={tabVariants} initial="initial" animate="animate" exit="exit" className="space-y-10">
                  {/* Premium Stats Grid */}
                  <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
                    {isFarmer ? (
                      [
                        { label: 'Active Policies', value: farmerActivePoliciesCount, icon: Shield, color: 'text-[#EAD35B]', bg: 'bg-[#EAD35B]/20', gradient: 'from-[#EAD35B]/30' },
                        { label: 'Insured Farm Size', value: `${farmerTotalAcreage.toFixed(1)} Acres`, icon: Leaf, color: 'text-[#659A5F]', bg: 'bg-[#659A5F]/10', gradient: 'from-[#659A5F]/20' },
                        { label: 'Premium Paid', value: formatCurrency(farmerTotalPremium), icon: Banknote, color: 'text-[#1B2B20]', bg: 'bg-[#1B2B20]/5', gradient: 'from-[#1B2B20]/10' },
                        { label: 'Payouts Received', value: formatCurrency(farmerTotalPayouts), icon: Zap, color: 'text-[#5A8855]', bg: 'bg-[#5A8855]/10', gradient: 'from-[#5A8855]/20' },
                      ].map((stat) => (
                        <div key={stat.label} className="relative group overflow-hidden bg-white rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 hover:shadow-[0_8px_40px_rgb(27,43,32,0.08)] hover:-translate-y-1 transition-all duration-300">
                          <div className={`absolute -top-10 -right-10 w-40 h-40 opacity-40 bg-gradient-to-bl ${stat.gradient} to-transparent rounded-full -z-10 group-hover:scale-150 transition-transform duration-700 ease-out`}></div>
                          <div className={`w-14 h-14 rounded-[14px] ${stat.bg} flex items-center justify-center mb-6 shadow-inner`}>
                            <stat.icon className={`w-7 h-7 ${stat.color}`} />
                          </div>
                          <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest">{stat.label}</p>
                          <p className="mt-2 text-3xl font-black text-bima-darkGreen tracking-tighter">{stat.value}</p>
                        </div>
                      ))
                    ) : (
                      [
                        { label: 'Farmers Registered', value: farmerRecords.length, icon: Users, color: 'text-[#659A5F]', bg: 'bg-[#659A5F]/10', gradient: 'from-[#659A5F]/20' },
                        { label: 'Active Plans', value: activePolicies.length, icon: FileText, color: 'text-[#EAD35B]', bg: 'bg-[#EAD35B]/20', gradient: 'from-[#EAD35B]/30' },
                        { label: 'Total Payments', value: formatCurrency(totalPremium), icon: Banknote, color: 'text-[#1B2B20]', bg: 'bg-[#1B2B20]/5', gradient: 'from-[#1B2B20]/10' },
                        { label: 'Recent Payouts', value: formatCurrency(totalPayouts), icon: Zap, color: 'text-[#5A8855]', bg: 'bg-[#5A8855]/10', gradient: 'from-[#5A8855]/20' },
                      ].map((stat) => (
                        <div key={stat.label} className="relative group overflow-hidden bg-white rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 hover:shadow-[0_8px_40px_rgb(27,43,32,0.08)] hover:-translate-y-1 transition-all duration-300">
                          <div className={`absolute -top-10 -right-10 w-40 h-40 opacity-40 bg-gradient-to-bl ${stat.gradient} to-transparent rounded-full -z-10 group-hover:scale-150 transition-transform duration-700 ease-out`}></div>
                          <div className={`w-14 h-14 rounded-[14px] ${stat.bg} flex items-center justify-center mb-6 shadow-inner`}>
                            <stat.icon className={`w-7 h-7 ${stat.color}`} />
                          </div>
                          <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest">{stat.label}</p>
                          <p className="mt-2 text-3xl font-black text-bima-darkGreen tracking-tighter">{stat.value}</p>
                        </div>
                      ))
                    )}
                  </div>

                  <div className="grid lg:grid-cols-2 gap-8">
                    {isFarmer ? (
                      <>
                        {/* Farmer Advisory Widget */}
                        <div className="bg-white rounded-3xl p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 relative overflow-hidden group">
                          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-bima-lightGreen/20 to-transparent rounded-bl-full -z-10 group-hover:scale-110 transition-transform duration-700"></div>
                          <div className="flex items-center gap-4 mb-4">
                             <div className="p-3 bg-bima-green/20 rounded-2xl text-bima-green">
                               <Leaf className="w-6 h-6" />
                             </div>
                             <h3 className="text-2xl font-black text-bima-darkGreen tracking-tight">Agricultural Advisory</h3>
                          </div>
                          <p className="text-[15px] font-semibold text-slate-500 mb-6 leading-relaxed">
                            Weather systems indicate stable conditions. Satellite arrays are tracking H3 region cell: <span className="font-mono text-bima-darkGreen bg-slate-100 px-2 py-0.5 rounded font-bold">{policies[0]?.coverage_h3 || '8928308280fffff'}</span>.
                          </p>
                          <div className="bg-slate-50 border border-slate-100 rounded-2xl p-6">
                            <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Smart Recommendation</p>
                            <p className="text-sm font-bold text-bima-darkGreen leading-relaxed">
                              Keep weeding crop areas clean to maximize soil moisture retention. The regional rainfall index is within standard ranges.
                            </p>
                          </div>
                        </div>

                        {/* Smart Contract Protection Widget */}
                        <div className="bg-gradient-to-br from-[#1B2B20] to-[#0f1812] rounded-3xl p-10 shadow-[0_20px_40px_rgba(27,43,32,0.3)] text-white relative overflow-hidden group">
                          <div className="absolute inset-0 opacity-[0.05] pointer-events-none" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='3' cy='3' r='1.5' fill='%23ffffff'/%3E%3C/svg%3E\")", backgroundSize: "24px 24px" }}></div>
                          <div className="absolute -top-20 -right-20 w-64 h-64 bg-bima-green/20 blur-[50px] rounded-full group-hover:bg-bima-green/30 transition-colors duration-700"></div>
                          
                          <div className="relative z-10 flex flex-col h-full justify-between">
                            <div>
                              <h3 className="text-2xl font-black text-white mb-2 tracking-tight flex items-center gap-3">
                                <Shield className="w-6 h-6 text-bima-lightGreen" /> Blockchain Protected
                              </h3>
                              <p className="text-[15px] font-semibold text-white/60 mb-6">Automated verification & instant claims processing</p>
                              
                              <p className="text-sm font-bold text-slate-300 leading-relaxed mb-6">
                                Your policy is bound to the BimaGrid smart contract. If weather data registers severe drought, payouts are instantly triggered to your phone number: <span className="font-mono text-white underline">{user?.profile?.phone_number || 'Registered M-Pesa'}</span>.
                              </p>
                            </div>
                            
                            <div className="pt-4 border-t border-white/10 flex items-center justify-between text-xs text-white/50 font-mono">
                              <span>CONTRACT STATUS</span>
                              <span className="text-emerald-400 font-bold tracking-widest flex items-center gap-1.5">
                                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span> ACTIVE
                              </span>
                            </div>
                          </div>
                        </div>
                      </>
                    ) : (
                      <>
                        {/* Quick Action Widget */}
                        <div className="bg-white rounded-3xl p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 relative overflow-hidden group">
                          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-bima-lightGreen/20 to-transparent rounded-bl-full -z-10 group-hover:scale-110 transition-transform duration-700"></div>
                          <div className="flex items-center gap-4 mb-4">
                             <div className="p-3 bg-bima-yellow/20 rounded-2xl text-bima-yellow">
                               <CloudRain className="w-6 h-6" />
                             </div>
                             <h3 className="text-2xl font-black text-bima-darkGreen tracking-tight">Simulate Weather</h3>
                          </div>
                          <p className="text-[15px] font-semibold text-slate-500 mb-8 max-w-sm leading-relaxed">
                            Check satellite data for a specific farm region to verify policies and process immediate payouts.
                          </p>
                          <div className="flex flex-col sm:flex-row gap-4">
                            <input
                              className="w-full sm:max-w-[240px] px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl font-mono text-sm font-bold text-slate-700 focus:ring-2 focus:ring-bima-green focus:border-bima-green transition-all placeholder:text-slate-400 shadow-inner"
                              value={evaluationH3}
                              onChange={(e) => setEvaluationH3(e.target.value)}
                              placeholder="e.g. 8928308280fffff"
                            />
                            <button
                              type="button"
                              onClick={() => void handleTriggerEvaluation()}
                              disabled={isEvaluating || !evaluationH3}
                              className="btn-primary sm:flex-1 shadow-[0_4px_14px_rgba(101,154,95,0.3)] hover:shadow-[0_6px_20px_rgba(101,154,95,0.4)] hover:-translate-y-0.5 py-4 px-6"
                            >
                              {isEvaluating ? (
                                <><RefreshCw className="w-5 h-5 mr-2 animate-spin" /> Checking…</>
                              ) : (
                                <><Activity className="w-5 h-5 mr-2" /> Verify Satellite Data</>
                              )}
                            </button>
                          </div>
                        </div>

                        {/* System Health Widget */}
                        <div className="bg-gradient-to-br from-[#1B2B20] to-[#0f1812] rounded-3xl p-10 shadow-[0_20px_40px_rgba(27,43,32,0.3)] text-white relative overflow-hidden group">
                          <div className="absolute inset-0 opacity-[0.05] pointer-events-none" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='3' cy='3' r='1.5' fill='%23ffffff'/%3E%3C/svg%3E\")", backgroundSize: "24px 24px" }}></div>
                          <div className="absolute -top-20 -right-20 w-64 h-64 bg-bima-green/20 blur-[50px] rounded-full group-hover:bg-bima-green/30 transition-colors duration-700"></div>
                          
                          <div className="flex flex-wrap justify-between items-start gap-4 mb-10 relative z-10">
                            <div>
                              <h3 className="text-2xl font-black text-white mb-2 tracking-tight flex items-center gap-3">
                                <Server className="w-6 h-6 text-bima-lightGreen" /> System Health
                              </h3>
                              <p className="text-[15px] font-semibold text-white/60">Live backend connectivity and API status</p>
                            </div>
                            {health ? (
                              <div className="px-4 py-2 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-black tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(16,185,129,0.15)]">
                                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_rgba(16,185,129,1)]"></span>
                                ONLINE
                              </div>
                            ) : (
                              <div className="px-4 py-2 rounded-xl bg-red-500/20 border border-red-500/30 text-red-400 text-xs font-black tracking-widest flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full bg-red-400"></span>
                                OFFLINE
                              </div>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-5 relative z-10">
                            <div className="bg-white/5 rounded-[20px] p-6 border border-white/10 backdrop-blur-md hover:bg-white/10 transition-colors">
                              <p className="text-[11px] font-black uppercase tracking-widest text-white/50 mb-2">Platform Version</p>
                              <p className="text-2xl font-mono font-bold text-white">{health?.version ?? '—'}</p>
                            </div>
                            <div className="bg-white/5 rounded-[20px] p-6 border border-white/10 backdrop-blur-md hover:bg-white/10 transition-colors">
                              <p className="text-[11px] font-black uppercase tracking-widest text-white/50 mb-2">Active Protocols</p>
                              <p className="text-2xl font-mono font-bold text-bima-yellow">4 Modules</p>
                            </div>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </motion.div>
              )}

              {activeTab === 'farmers' && (
                <motion.div key="farmers" variants={tabVariants} initial="initial" animate="animate" exit="exit">
                  <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 overflow-hidden">
                    <div className="p-8 border-b border-slate-100 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                      <div>
                        <h2 className="text-2xl font-black text-bima-darkGreen tracking-tight">
                          {isFarmer ? 'My Crop Insurance Policies' : 'Farmer & Plan Records'}
                        </h2>
                        <p className="text-[15px] font-semibold text-slate-500 mt-2 max-w-md leading-relaxed">
                          {isFarmer ? 'A comprehensive history of your crop protection plans and active coverage.' : 'Complete directory of all farmers registered under your active agent account.'}
                        </p>
                      </div>
                      
                      <div className="flex flex-col sm:flex-row items-center gap-4 shrink-0">
                        <div className="relative w-full sm:w-80">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <Search className="h-5 w-5 text-slate-400" />
                          </div>
                          <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search by Plan ID, Crop..."
                            className="block w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-sm font-bold focus:ring-2 focus:ring-bima-green focus:border-bima-green transition-all placeholder:text-slate-400 shadow-inner"
                          />
                        </div>
                        <div className="flex items-center gap-3 w-full sm:w-auto">
                          <span className="px-5 py-3.5 rounded-2xl bg-bima-lightGreen/20 text-bima-darkGreen font-black text-sm border border-bima-lightGreen/50 shrink-0">
                            {policies.length} Plans
                          </span>
                          {!isFarmer && (
                            <button onClick={() => setIsRegisterModalOpen(true)} className="btn-primary py-3.5 px-6 text-sm shadow-[0_4px_14px_rgba(101,154,95,0.3)] hover:-translate-y-0.5 whitespace-nowrap">
                              <Users className="w-4 h-4 mr-2" /> New Farmer
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
 
                    {filteredPolicies.length === 0 ? (
                      <div className="p-20 flex flex-col items-center justify-center text-center bg-slate-50/30">
                        <div className="h-24 w-24 rounded-[2rem] bg-white flex items-center justify-center mb-8 border border-slate-100 shadow-sm">
                          <Database className="h-10 w-10 text-slate-300" />
                        </div>
                        <h3 className="text-xl font-black text-slate-700 tracking-tight">
                          {searchQuery ? 'No matching records found' : 'No records found'}
                        </h3>
                        <p className="text-[15px] font-semibold text-slate-500 mt-3 max-w-md leading-relaxed">
                          {searchQuery 
                            ? `We couldn't find any plans matching "${searchQuery}". Try adjusting your search term.` 
                            : (isFarmer ? "You don't have any crop insurance policies registered at the moment. Please contact an agent to get started." : "You haven't registered any farmers or farm plans yet. Click the button above to get started.")}
                        </p>
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="min-w-full text-left text-sm whitespace-nowrap">
                          <thead>
                            <tr className="bg-slate-50 border-b border-slate-100">
                              <th className="px-8 py-5 text-[11px] font-black text-slate-400 uppercase tracking-widest">Plan ID</th>
                              {!isFarmer && <th className="px-8 py-5 text-[11px] font-black text-slate-400 uppercase tracking-widest">Farmer</th>}
                              <th className="px-8 py-5 text-[11px] font-black text-slate-400 uppercase tracking-widest">Crop Protection</th>
                              <th className="px-8 py-5 text-[11px] font-black text-slate-400 uppercase tracking-widest">Region Code</th>
                              <th className="px-8 py-5 text-[11px] font-black text-slate-400 uppercase tracking-widest">Premium</th>
                              <th className="px-8 py-5 text-[11px] font-black text-slate-400 uppercase tracking-widest">Coverage Window</th>
                              <th className="px-8 py-5 text-[11px] font-black text-slate-400 uppercase tracking-widest">Status</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {filteredPolicies.map((policy) => (
                              <tr key={policy.id} onClick={() => setSelectedPolicyForDetail(policy)} className="hover:bg-slate-50 cursor-pointer transition-colors group">
                                <td className="px-8 py-6 font-black text-bima-darkGreen text-[15px]">{policy.policy_number}</td>
                                {!isFarmer && (
                                  <td className="px-8 py-6 font-bold text-slate-800 text-[14px]">
                                    {policy.farmer_name || 'Jane Doe'}
                                  </td>
                                )}
                                <td className="px-8 py-6 capitalize text-slate-600 font-bold flex items-center gap-3">
                                  <span className="w-2.5 h-2.5 rounded-full bg-bima-green shadow-[0_0_10px_rgba(101,154,95,0.4)]"></span>
                                  {policy.crop}
                                </td>
                                <td className="px-8 py-6 font-mono text-[11px] font-black text-slate-500">
                                  <span className="bg-white px-3 py-1.5 rounded-lg border border-slate-200 group-hover:border-slate-300 transition-colors">{policy.coverage_h3}</span>
                                </td>
                                <td className="px-8 py-6 font-black text-bima-darkGreen text-lg">{formatCurrency(policy.premium_amount)}</td>
                                <td className="px-8 py-6 text-slate-500 font-semibold text-xs">
                                  {formatDate(policy.coverage_start)} <span className="mx-2 text-slate-300">to</span> {formatDate(policy.coverage_end)}
                                </td>
                                <td className="px-8 py-6">
                                  <StatusBadge status={policy.status} />
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              {activeTab === 'claims' && (
                <motion.div key="claims" variants={tabVariants} initial="initial" animate="animate" exit="exit" className="grid lg:grid-cols-2 gap-8">
                  {/* Recent Claims */}
                  <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 overflow-hidden flex flex-col relative group">
                    <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-bima-yellow/10 to-transparent rounded-bl-full -z-10 group-hover:scale-110 transition-transform duration-700"></div>
                    <div className="p-8 border-b border-slate-100 flex items-center justify-between">
                      <h2 className="text-2xl font-black text-bima-darkGreen flex items-center gap-3 tracking-tight">
                        <div className="p-2.5 bg-bima-yellow/20 rounded-xl text-bima-yellow">
                           <AlertCircle className="w-5 h-5" />
                        </div>
                        Loss Claims
                      </h2>
                      <span className="text-xs font-black text-slate-400 uppercase tracking-widest">{claims.length} Records</span>
                    </div>
                    {claims.length === 0 ? (
                      <div className="p-20 flex-1 flex flex-col items-center justify-center text-center">
                        <div className="h-20 w-20 rounded-[2rem] bg-slate-50 flex items-center justify-center mb-6 border border-slate-100">
                          <FileText className="h-8 w-8 text-slate-300" />
                        </div>
                        <p className="text-[15px] font-bold text-slate-500">No claims recorded yet.</p>
                      </div>
                    ) : (
                      <ul className="divide-y divide-slate-100 bg-white/50 backdrop-blur-md">
                        {claims.map((claim) => (
                          <li key={claim.id} className="flex items-center justify-between gap-4 p-8 hover:bg-slate-50 transition-colors">
                            <div>
                              <p className="font-black text-bima-darkGreen text-xl tracking-tight">{claim.claim_number}</p>
                              <p className="text-[13px] font-bold capitalize text-slate-500 mt-2 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-bima-yellow"></span>
                                {claim.loss_type}
                              </p>
                              <p className="text-[11px] font-black text-slate-400 mt-2 tracking-widest uppercase">{formatDate(claim.created_at)}</p>
                            </div>
                            <div className="text-right flex flex-col items-end">
                              <p className="font-black text-bima-darkGreen text-2xl mb-3 tracking-tighter">{formatCurrency(claim.claimed_amount)}</p>
                              <StatusBadge status={claim.status} />
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  {/* Recent Payouts */}
                  <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 overflow-hidden flex flex-col relative group">
                    <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-[#659A5F]/10 to-transparent rounded-bl-full -z-10 group-hover:scale-110 transition-transform duration-700"></div>
                    <div className="p-8 border-b border-slate-100 flex items-center justify-between">
                      <h2 className="text-2xl font-black text-bima-darkGreen flex items-center gap-3 tracking-tight">
                        <div className="p-2.5 bg-[#659A5F]/20 rounded-xl text-[#659A5F]">
                           <ArrowUpRight className="w-5 h-5" />
                        </div>
                        M-Pesa Payouts
                      </h2>
                      <span className="text-xs font-black text-slate-400 uppercase tracking-widest">{payouts.length} Transfers</span>
                    </div>
                    {payouts.length === 0 ? (
                      <div className="p-20 flex-1 flex flex-col items-center justify-center text-center">
                        <div className="h-20 w-20 rounded-[2rem] bg-slate-50 flex items-center justify-center mb-6 border border-slate-100">
                          <Banknote className="h-8 w-8 text-slate-300" />
                        </div>
                        <p className="text-[15px] font-bold text-slate-500">No payouts dispatched yet.</p>
                      </div>
                    ) : (
                      <ul className="divide-y divide-slate-100 bg-white/50 backdrop-blur-md">
                        {payouts.map((payout) => (
                          <li key={payout.id} className="flex items-center justify-between gap-4 p-8 hover:bg-slate-50 transition-colors">
                            <div>
                              <p className="font-black text-bima-darkGreen text-3xl tracking-tighter">{formatCurrency(payout.amount)}</p>
                              <p className="text-[15px] font-bold text-slate-500 mt-2">{payout.phone_number}</p>
                              <div className="inline-block px-3 py-1.5 bg-slate-100 rounded-lg mt-3 border border-slate-200">
                                <p className="font-mono text-[10px] font-black text-slate-500 uppercase">REF: {payout.reference}</p>
                              </div>
                            </div>
                            <div className="text-right flex flex-col items-end">
                              <StatusBadge status={payout.status} />
                              <p className="mt-4 text-[11px] font-black text-slate-400 tracking-widest uppercase">{formatDate(payout.created_at)}</p>
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </motion.div>
              )}

              {activeTab === 'system' && (
                <motion.div key="system" variants={tabVariants} initial="initial" animate="animate" exit="exit" className="max-w-4xl">
                  <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 overflow-hidden relative">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-bima-lightGreen/10 to-transparent rounded-bl-full -z-10"></div>
                    <div className="p-8 md:p-10">
                      <h2 className="text-2xl font-black text-bima-darkGreen flex items-center gap-3 mb-10 tracking-tight">
                        <div className="p-3 bg-bima-lightGreen/20 rounded-xl text-bima-green">
                          <Settings className="w-6 h-6" />
                        </div>
                        Administrator Tools
                      </h2>

                      <div className="space-y-6">
                        <div className="p-8 rounded-[24px] border border-slate-200 bg-slate-50 flex flex-col sm:flex-row items-start gap-6 hover:shadow-md transition-shadow">
                          <div className="p-4 bg-white rounded-2xl shadow-sm border border-slate-100 shrink-0">
                            <Activity className="w-7 h-7 text-bima-green" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-black text-bima-darkGreen text-xl tracking-tight">Manual Weather Evaluation</h3>
                            <p className="text-[15px] text-slate-500 font-medium mt-2 mb-6 max-w-lg leading-relaxed">Force trigger an immediate satellite data check for a specific H3 Region Code index.</p>
                            <div className="flex flex-col sm:flex-row gap-4">
                              <input
                                className="input-field font-mono text-sm max-w-[280px] bg-white border-slate-200 shadow-inner px-5 py-4 rounded-2xl"
                                value={evaluationH3}
                                onChange={(e) => setEvaluationH3(e.target.value)}
                                placeholder="Region Code"
                              />
                              <button
                                type="button"
                                onClick={() => void handleTriggerEvaluation()}
                                disabled={isEvaluating || !evaluationH3}
                                className="btn-primary text-sm px-8 py-4 shadow-[0_4px_14px_rgba(101,154,95,0.3)] hover:-translate-y-0.5"
                              >
                                Execute Check
                              </button>
                            </div>
                          </div>
                        </div>

                        {isAdmin && (
                          <div className="p-8 rounded-[24px] border border-bima-yellow/40 bg-gradient-to-br from-bima-yellow/10 to-bima-yellow/5 flex flex-col sm:flex-row items-start gap-6 hover:shadow-md transition-shadow">
                            <div className="p-4 bg-white rounded-2xl shadow-sm border border-bima-yellow/20 shrink-0">
                              <CloudLightning className="w-7 h-7 text-bima-yellow" />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-black text-bima-darkGreen text-xl tracking-tight">Simulate Weather Event</h3>
                              <p className="text-[15px] text-slate-600 font-medium mt-2 mb-6 max-w-lg leading-relaxed">Force a severe drought simulation in a region to test the automated mobile money payouts system end-to-end.</p>
                              <button
                                type="button"
                                onClick={() => void handleSimulateDrought()}
                                disabled={!evaluationH3}
                                className="btn-outline border-bima-yellow text-bima-darkGreen hover:bg-bima-yellow hover:text-bima-darkGreen text-[15px] font-bold px-8 py-4 bg-white shadow-sm hover:shadow-md transition-all hover:-translate-y-0.5"
                              >
                                Simulate Drought for {evaluationH3 || 'Region'}
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              {activeTab === 'weather' && (
                <motion.div key="weather" variants={tabVariants} initial="initial" animate="animate" exit="exit" className="space-y-8">
                  <div className="bg-white rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100">
                    <h3 className="text-xl font-extrabold text-bima-darkGreen mb-2 flex items-center gap-2">
                      <CloudRain className="w-5 h-5 text-bima-green" /> Regional Spatial Grid Analysis
                    </h3>
                    <p className="text-sm text-slate-500 font-medium mb-6">
                      Query real-time meteorological indexes and NDVI baseline metrics for any H3 grid cell.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-4 max-w-xl">
                      <input
                        className="input-field font-mono text-sm py-3 px-5 rounded-2xl flex-1 border-slate-200"
                        value={weatherSearchH3}
                        onChange={(e) => setWeatherSearchH3(e.target.value)}
                        placeholder="Enter H3 Grid Index (e.g. 8928308280fffff)"
                      />
                      <button
                        type="button"
                        onClick={() => void handleQueryWeather()}
                        disabled={weatherAnalysis.loading}
                        className="btn-primary py-3 px-6 text-sm flex items-center justify-center gap-2"
                      >
                        {weatherAnalysis.loading ? (
                          <><RefreshCw className="w-4 h-4 animate-spin" /> Querying...</>
                        ) : (
                          <><Search className="w-4 h-4" /> Analyze Grid</>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Weather Metrics display */}
                  <div className="grid md:grid-cols-3 gap-6">
                    {/* Card 1: NDVI */}
                    <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm flex flex-col justify-between">
                      <div>
                        <div className="w-10 h-10 rounded-[10px] bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
                          <Leaf className="w-5 h-5" />
                        </div>
                        <p className="text-xs font-black text-slate-400 uppercase tracking-widest">NDVI Metric</p>
                        <p className="text-2xl font-black text-slate-800 mt-2 font-mono">
                          {weatherAnalysis.ndvi !== null ? weatherAnalysis.ndvi.toFixed(2) : '—'}
                        </p>
                      </div>
                      <div className="mt-6 border-t border-slate-50 pt-4 text-xs font-bold">
                        {weatherAnalysis.ndvi !== null ? (
                          weatherAnalysis.ndvi >= 0.5 ? (
                            <span className="text-emerald-500">🟢 Healthy Crop Vegetation</span>
                          ) : weatherAnalysis.ndvi >= 0.35 ? (
                            <span className="text-yellow-500">🟡 Moderate Dry Stress</span>
                          ) : (
                            <span className="text-red-500">🔴 Severe Drought / Crop Damage</span>
                          )
                        ) : (
                          <span className="text-slate-400">Perform analysis query</span>
                        )}
                      </div>
                    </div>

                    {/* Card 2: Rainfall */}
                    <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm flex flex-col justify-between">
                      <div>
                        <div className="w-10 h-10 rounded-[10px] bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
                          <CloudRain className="w-5 h-5" />
                        </div>
                        <p className="text-xs font-black text-slate-400 uppercase tracking-widest">Precipitation</p>
                        <p className="text-2xl font-black text-slate-800 mt-2 font-mono">
                          {weatherAnalysis.rainfall !== null ? `${weatherAnalysis.rainfall.toFixed(1)} mm` : '—'}
                        </p>
                      </div>
                      <div className="mt-6 border-t border-slate-50 pt-4 text-xs font-bold">
                        {weatherAnalysis.rainfall !== null ? (
                          weatherAnalysis.rainfall > 10 ? (
                            <span className="text-emerald-500">🟢 Adequate Rainfall</span>
                          ) : (
                            <span className="text-red-500">🔴 Low Precipitation (Triggers Payout)</span>
                          )
                        ) : (
                          <span className="text-slate-400">Perform analysis query</span>
                        )}
                      </div>
                    </div>

                    {/* Card 3: Soil Moisture */}
                    <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm flex flex-col justify-between">
                      <div>
                        <div className="w-10 h-10 rounded-[10px] bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
                          <Tractor className="w-5 h-5" />
                        </div>
                        <p className="text-xs font-black text-slate-400 uppercase tracking-widest">Soil Moisture</p>
                        <p className="text-2xl font-black text-slate-800 mt-2 font-mono">
                          {weatherAnalysis.ndvi !== null ? `${(weatherAnalysis.ndvi * 40).toFixed(0)}%` : '—'}
                        </p>
                      </div>
                      <div className="mt-6 border-t border-slate-50 pt-4 text-xs font-bold">
                        {weatherAnalysis.ndvi !== null ? (
                          weatherAnalysis.ndvi * 40 >= 20 ? (
                            <span className="text-emerald-500">🟢 Normal Moisture Level</span>
                          ) : (
                            <span className="text-red-500">🔴 Severe Soil Drought</span>
                          )
                        ) : (
                          <span className="text-slate-400">Perform analysis query</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* SVG Map grid mockup */}
                  <div className="bg-white rounded-3xl p-8 border border-slate-100 shadow-sm flex flex-col items-center">
                    <p className="text-xs font-extrabold uppercase tracking-wider text-slate-400 mb-6">Spatial H3 Hexagonal Layout Representation</p>
                    <svg width="220" height="200" viewBox="0 0 220 200" className="opacity-90">
                      {/* Hexagon 1: Top Left */}
                      <polygon points="50,20 90,20 110,50 90,80 50,80 30,50" fill="#E2E8F0" stroke="#CBD5E1" strokeWidth="2" />
                      {/* Hexagon 2: Top Right */}
                      <polygon points="130,20 170,20 190,50 170,80 130,80 110,50" fill="#E2E8F0" stroke="#CBD5E1" strokeWidth="2" />
                      {/* Hexagon 3: Center (Target) */}
                      <polygon 
                        points="90,75 130,75 150,105 130,135 90,135 70,105" 
                        fill={weatherAnalysis.ndvi !== null ? (weatherAnalysis.ndvi >= 0.5 ? '#10B981' : weatherAnalysis.ndvi >= 0.35 ? '#F59E0B' : '#EF4444') : '#659A5F'} 
                        stroke="#FFF" 
                        strokeWidth="3" 
                        className="transition-colors duration-500 shadow-lg"
                      />
                      {/* Hexagon 4: Bottom Left */}
                      <polygon points="50,130 90,130 110,160 90,190 50,190 30,160" fill="#E2E8F0" stroke="#CBD5E1" strokeWidth="2" />
                      {/* Hexagon 5: Bottom Right */}
                      <polygon points="130,130 170,130 190,160 170,190 130,190 110,160" fill="#E2E8F0" stroke="#CBD5E1" strokeWidth="2" />
                      
                      <text x="110" y="110" textAnchor="middle" fill="#FFF" className="text-[10px] font-black font-mono">
                        {weatherSearchH3 ? weatherSearchH3.substring(0, 7) : 'GRID'}
                      </text>
                    </svg>
                    <div className="flex gap-4 mt-6 text-xs font-bold text-slate-500">
                      <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-emerald-500"></span> Healthy</div>
                      <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-amber-500"></span> Stressed</div>
                      <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-red-500"></span> Dry / Drought</div>
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === 'resources' && (
                <motion.div key="resources" variants={tabVariants} initial="initial" animate="animate" exit="exit" className="grid md:grid-cols-2 gap-8">
                  {/* Documentation */}
                  <div className="bg-white rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 space-y-6">
                    <h3 className="text-xl font-extrabold text-bima-darkGreen flex items-center gap-2">
                      <BookOpen className="w-5 h-5 text-bima-green" /> Agent Resource Hub
                    </h3>
                    <div className="relative">
                      <input
                        className="input-field pl-10 py-2.5 text-xs"
                        placeholder="Search resource guidelines..."
                        value={resourceSearch}
                        onChange={(e) => setResourceSearch(e.target.value)}
                      />
                      <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                    </div>

                    <div className="space-y-3">
                      <a href="#" className="block p-4 bg-slate-50 hover:bg-bima-lightGreen/10 border border-slate-100 rounded-2xl transition-all">
                        <p className="text-xs font-bold text-bima-darkGreen mb-1">📋 Parametric Crop Protection Guidelines</p>
                        <p className="text-[10px] text-slate-400 font-medium">Standard baseline thresholds, crop choices, and H3 region index metrics.</p>
                      </a>
                      <a href="#" className="block p-4 bg-slate-50 hover:bg-bima-lightGreen/10 border border-slate-100 rounded-2xl transition-all">
                        <p className="text-xs font-bold text-bima-darkGreen mb-1">🔗 Smart Contract Escrow Operations</p>
                        <p className="text-[10px] text-slate-400 font-medium">How policy premiums are locked in decentralized vault escrows and paid out.</p>
                      </a>
                      <a href="#" className="block p-4 bg-slate-50 hover:bg-bima-lightGreen/10 border border-slate-100 rounded-2xl transition-all">
                        <p className="text-xs font-bold text-bima-darkGreen mb-1">📱 USSD Farmer Portal User Guide</p>
                        <p className="text-[10px] text-slate-400 font-medium">Steps for farmers to dial *384*123# to view status and request manual audit review.</p>
                      </a>
                    </div>
                  </div>

                  {/* Premium Calculator */}
                  <div className="bg-white rounded-3xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 flex flex-col justify-between">
                    <div>
                      <h3 className="text-xl font-extrabold text-bima-darkGreen mb-4 flex items-center gap-2">
                        <Tractor className="w-5 h-5 text-bima-green" /> Premium Estimator
                      </h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block mb-1 text-xs font-bold text-slate-700">Acreage</label>
                          <input
                            type="number"
                            className="input-field py-2.5 text-xs"
                            value={calculatorAcreage}
                            onChange={(e) => setCalculatorAcreage(e.target.value)}
                          />
                        </div>
                        <div>
                          <label className="block mb-1 text-xs font-bold text-slate-700">Crop Type</label>
                          <select
                            className="input-field py-2.5 text-xs appearance-none bg-white"
                            value={calculatorCrop}
                            onChange={(e) => setCalculatorCrop(e.target.value)}
                          >
                            <option value="maize">Maize (KES 322 / Acre)</option>
                            <option value="beans">Beans (KES 280 / Acre)</option>
                            <option value="wheat">Wheat (KES 350 / Acre)</option>
                            <option value="rice">Rice (KES 400 / Acre)</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <div className="mt-8 bg-bima-lightGreen/10 border border-bima-green/10 rounded-2xl p-4 flex justify-between items-center">
                      <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Estimated Premium</span>
                        <p className="text-2xl font-black text-bima-darkGreen">
                          {formatCurrency(parseFloat(calculatorAcreage || '0') * (calculatorCrop === 'maize' ? 322 : calculatorCrop === 'beans' ? 280 : calculatorCrop === 'wheat' ? 350 : 400))}
                        </p>
                      </div>
                      <span className="text-[10px] font-mono font-bold bg-white text-bima-darkGreen px-2.5 py-1 rounded-md border border-slate-200">
                        180 Days Term
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}
              
              {activeTab === 'settings' && (
                <motion.div key="settings" variants={tabVariants} initial="initial" animate="animate" exit="exit" className="max-w-2xl bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 p-8 sm:p-10 relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-bima-green/10 to-transparent rounded-bl-full -z-10"></div>
                  <h2 className="text-2xl font-black text-bima-darkGreen flex items-center gap-3 mb-8 tracking-tight">
                    <div className="p-2.5 bg-bima-green/20 rounded-xl text-bima-green">
                       <Sliders className="w-5 h-5" />
                    </div>
                    Profile Settings
                  </h2>
                  <div className="space-y-6">
                    <div className="grid sm:grid-cols-2 gap-6">
                      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                        <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1">Full Name</p>
                        <p className="text-lg font-bold text-bima-darkGreen">{user?.profile?.full_name || user?.username || '—'}</p>
                      </div>
                      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                        <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1">Username</p>
                        <p className="text-lg font-bold text-bima-darkGreen">{user?.username || '—'}</p>
                      </div>
                      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                        <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1">Email Address</p>
                        <p className="text-lg font-bold text-bima-darkGreen">{user?.email || '—'}</p>
                      </div>
                      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                        <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1">Phone Number</p>
                        <p className="text-lg font-bold text-bima-darkGreen">{user?.profile?.phone_number || '—'}</p>
                      </div>
                      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                        <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1">Account Role</p>
                        <p className="text-lg font-bold text-bima-darkGreen capitalize">{user?.profile?.role || 'Customer'}</p>
                      </div>
                      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                        <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1">Preferred Language</p>
                        <p className="text-lg font-bold text-bima-darkGreen">{user?.profile?.preferred_language === 'sw' ? 'Swahili (Kiswahili)' : 'English'}</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </main>
      </div>

      <RegisterFarmerModal
        isOpen={isRegisterModalOpen}
        onClose={() => setIsRegisterModalOpen(false)}
        onSuccess={() => void loadDashboard(true)}
      />

      {/* Policy Detail Modal */}
      {selectedPolicyForDetail && (
        <AnimatePresence>
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
              onClick={() => setSelectedPolicyForDetail(null)}
            />
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white border border-slate-100 rounded-[1.5rem] p-6 sm:p-8 w-full max-w-2xl max-h-[85vh] overflow-y-auto relative z-10 shadow-2xl"
            >
              <div className="absolute top-0 left-0 w-full h-2 bg-bima-green rounded-t-[1.5rem]" />
              
              <div className="flex justify-between items-start gap-4 mb-6 border-b border-slate-100 pb-4">
                <div>
                  <span className="text-[10px] font-black bg-bima-lightGreen/50 text-bima-darkGreen px-2 py-0.5 rounded uppercase tracking-wider">
                    Policy Plan File
                  </span>
                  <h3 className="text-2xl font-black text-bima-darkGreen mt-1 tracking-tight">
                    {selectedPolicyForDetail.policy_number}
                  </h3>
                </div>
                <button 
                  onClick={() => setSelectedPolicyForDetail(null)}
                  className="p-1.5 bg-slate-50 hover:bg-slate-100 rounded-lg text-slate-400 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="grid sm:grid-cols-2 gap-6 text-sm border-b border-slate-100 pb-6 mb-6">
                <div>
                  <span className="text-slate-400 font-bold text-xs uppercase tracking-wider">Farmer Full Name</span>
                  <p className="font-extrabold text-slate-800 text-lg mt-1">{selectedPolicyForDetail.farmer_name || 'Jane Doe'}</p>
                </div>
                <div>
                  <span className="text-slate-400 font-bold text-xs uppercase tracking-wider">Registered Phone</span>
                  <p className="font-bold text-slate-800 text-lg mt-1">{selectedPolicyForDetail.farmer_phone || '—'}</p>
                </div>
                <div>
                  <span className="text-slate-400 font-bold text-xs uppercase tracking-wider">Crop Category</span>
                  <p className="font-bold text-slate-800 capitalize mt-1">{selectedPolicyForDetail.crop}</p>
                </div>
                <div>
                  <span className="text-slate-400 font-bold text-xs uppercase tracking-wider">Land Acreage</span>
                  <p className="font-bold text-slate-800 mt-1">{selectedPolicyForDetail.insured_acreage} Acres</p>
                </div>
                <div>
                  <span className="text-slate-400 font-bold text-xs uppercase tracking-wider">Coverage Grid (H3 Index)</span>
                  <p className="font-mono text-xs font-bold text-slate-700 bg-slate-50 px-2 py-1 rounded border border-slate-200 mt-1 inline-block">
                    {selectedPolicyForDetail.coverage_h3}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400 font-bold text-xs uppercase tracking-wider">Premium Amount</span>
                  <p className="font-black text-bima-darkGreen text-xl mt-1">{formatCurrency(selectedPolicyForDetail.premium_amount)}</p>
                </div>
                <div>
                  <span className="text-slate-400 font-bold text-xs uppercase tracking-wider">Plan Term Dates</span>
                  <p className="font-medium text-slate-600 mt-1">
                    {formatDate(selectedPolicyForDetail.coverage_start)} to {formatDate(selectedPolicyForDetail.coverage_end)}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400 font-bold text-xs uppercase tracking-wider">Blockchain Status</span>
                  <span className="block mt-1"><StatusBadge status={selectedPolicyForDetail.status} /></span>
                </div>

                {/* Farmer Location Details */}
                {(selectedPolicyForDetail.county_name || selectedPolicyForDetail.subcounty_name || selectedPolicyForDetail.constituency_name || selectedPolicyForDetail.ward_name) && (
                  <div className="col-span-2 bg-slate-50 rounded-xl p-3 border border-slate-100 grid grid-cols-2 gap-3 text-xs mt-2">
                    <div>
                      <span className="text-slate-400 font-bold text-[10px] uppercase tracking-wider block">County / Sub-county</span>
                      <p className="font-extrabold text-bima-darkGreen mt-0.5">
                        {selectedPolicyForDetail.county_name || '—'} / {selectedPolicyForDetail.subcounty_name || '—'}
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-bold text-[10px] uppercase tracking-wider block">Constituency / Ward</span>
                      <p className="font-extrabold text-bima-darkGreen mt-0.5">
                        {selectedPolicyForDetail.constituency_name || '—'} / {selectedPolicyForDetail.ward_name || '—'}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Policy Event History */}
              <div className="space-y-4 mb-6">
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-400">Policy Lifecycle Events</h4>
                <div className="relative border-l border-slate-100 pl-4 space-y-4">
                  {selectedPolicyForDetail.events && selectedPolicyForDetail.events.length > 0 ? (
                    selectedPolicyForDetail.events.map((evt, idx) => (
                      <div key={idx} className="relative">
                        <span className="absolute -left-[21px] top-1.5 w-2.5 h-2.5 rounded-full bg-bima-green border border-white" />
                        <p className="text-xs font-black text-bima-darkGreen capitalize">{evt.event_type}</p>
                        <p className="text-[10px] text-slate-400 font-mono mt-0.5">{formatDate(evt.created_at)}</p>
                      </div>
                    ))
                  ) : (
                    <div className="relative">
                      <span className="absolute -left-[21px] top-1.5 w-2.5 h-2.5 rounded-full bg-slate-300 border border-white" />
                      <p className="text-xs font-black text-slate-600">Policy Draft Issued</p>
                      <p className="text-[10px] text-slate-400 font-mono mt-0.5">{formatDate(selectedPolicyForDetail.created_at)}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Documents Section */}
              <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-400 mb-3">Verified Documents</h4>
                <div className="grid sm:grid-cols-2 gap-3 text-xs">
                  <div className="flex items-center justify-between bg-white p-3 rounded-xl border border-slate-100">
                    <span className="font-semibold text-slate-700 truncate max-w-[150px]">Title_Deed_Signed.pdf</span>
                    <button className="text-bima-green font-bold hover:underline">Download</button>
                  </div>
                  <div className="flex items-center justify-between bg-white p-3 rounded-xl border border-slate-100">
                    <span className="font-semibold text-slate-700 truncate max-w-[150px]">ID_Verification.pdf</span>
                    <button className="text-bima-green font-bold hover:underline">Download</button>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </AnimatePresence>
      )}
    </div>
  );
}
