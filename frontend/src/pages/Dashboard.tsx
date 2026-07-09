import { useCallback, useEffect, useMemo, useState } from 'react';
import { dashboardApi } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import RegisterFarmerModal from '../components/RegisterFarmerModal';
import StatusBadge from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';
import type { Payout, Policy } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, FileText, Banknote, RefreshCw, Zap, CloudLightning, 
  ArrowUpRight, ArrowDownRight, LayoutDashboard,
  Settings, Server, LogOut, Search, Bell, CloudRain, Shield, BookOpen, Leaf, X, 
  ChevronRight, ChevronLeft, UserPlus
} from 'lucide-react';
import toast from 'react-hot-toast';

import { Map as MapcnMap, MapControls, MapMarker } from '../components/ui/map';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

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

// Chart Mock Data
const overviewData = [
  { name: "Jan", premium: 15000, plans: 120, payouts: 5000 },
  { name: "Feb", premium: 20000, plans: 150, payouts: 8000 },
  { name: "Mar", premium: 18000, plans: 180, payouts: 6000 },
  { name: "Apr", premium: 28000, plans: 200, payouts: 12000 },
  { name: "May", premium: 30000, plans: 250, payouts: 15000 },
  { name: "Jun", premium: 28000, plans: 280, payouts: 14000 },
  { name: "Jul", premium: 35000, plans: 300, payouts: 18000 },
  { name: "Aug", premium: 38000, plans: 320, payouts: 20000 },
  { name: "Sep", premium: 37000, plans: 350, payouts: 19000 },
  { name: "Oct", premium: 42000, plans: 380, payouts: 22000 },
  { name: "Nov", premium: 45000, plans: 400, payouts: 25000 },
  { name: "Dec", premium: 49000, plans: 450, payouts: 28000 },
];

const cropData = [
  { name: "Maize", value: 45, color: "#00E676" },
  { name: "Wheat", value: 25, color: "#00BCD4" },
  { name: "Beans", value: 15, color: "#2196F3" },
  { name: "Coffee", value: 15, color: "#9C27B0" },
];

const sparklineData1 = [{ value: 10 }, { value: 15 }, { value: 12 }, { value: 18 }, { value: 15 }, { value: 22 }, { value: 25 }, { value: 24 }];
const sparklineData2 = [{ value: 20 }, { value: 25 }, { value: 22 }, { value: 28 }, { value: 26 }, { value: 30 }, { value: 32 }, { value: 35 }];
const sparklineData3 = [{ value: 40 }, { value: 35 }, { value: 38 }, { value: 32 }, { value: 36 }, { value: 30 }, { value: 28 }, { value: 26 }];
const sparklineData4 = [{ value: 10 }, { value: 12 }, { value: 15 }, { value: 18 }, { value: 16 }, { value: 20 }, { value: 22 }, { value: 25 }];

const tabVariants = {
  initial: { opacity: 0, y: 15 },
  animate: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 350, damping: 28 } },
  exit: { opacity: 0, y: -15, transition: { duration: 0.15 } }
};

type TabId = 'overview' | 'farmers' | 'claims' | 'weather' | 'resources' | 'system' | 'settings';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
  const [evaluationH3, setEvaluationH3] = useState('8928308280fffff');
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [chartTab, setChartTab] = useState('Premium');
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

  const [weatherViewport, setWeatherViewport] = useState({
    center: [34.4534, -0.5298] as [number, number], // Homa Bay
    zoom: 14,
    bearing: 0,
    pitch: 0
  });

  const getH3Coords = (h3Str: string): [number, number] => {
    if (h3Str.trim() === '8928308280fffff' || h3Str.trim() === '8928308280ffffe') {
      return [34.4534, -0.5298];
    }
    return [36.8219, -1.2921]; // Nairobi fallback
  };

  const loadDashboard = useCallback(async (showToast = false) => {
    if (!showToast) setIsLoading(true);
    
    try {
      const [policyData, payoutData] = await Promise.all([
        dashboardApi.getPolicies(),
        dashboardApi.getPayouts(),
      ]);

      setPolicies(policyData);
      setPayouts(payoutData);

      if (policyData[0]?.coverage_h3) {
        setEvaluationH3(policyData[0].coverage_h3);
      }
      
      if (showToast) {
        toast.success("Dashboard data refreshed", { style: { background: '#1A1A1A', color: '#FFF' }});
      }
    } catch (loadError) {
      toast.error(loadError instanceof Error ? loadError.message : 'Failed to load data.', { style: { background: '#1A1A1A', color: '#FFF' }});
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

      const coords = getH3Coords(weatherSearchH3);
      setWeatherViewport(prev => ({
        ...prev,
        center: coords,
        zoom: 14
      }));

      toast.success(`Weather fetched: ${weatherSearchH3}`, { style: { background: '#1A1A1A', color: '#FFF' }});
    } catch (err) {
      setWeatherAnalysis({
        rainfall: null,
        ndvi: null,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to query'
      });
      toast.error('Failed to query weather metrics.', { style: { background: '#1A1A1A', color: '#FFF' }});
    }
  };

  const totalPremium = useMemo(
    () => policies.reduce((sum, policy) => sum + parseFloat(policy.premium_amount || '0'), 0),
    [policies],
  );

  const totalPayouts = useMemo(
    () => payouts.reduce((sum, payout) => sum + parseFloat(payout.amount || '0'), 0),
    [payouts],
  );

  const activePolicies = useMemo(
    () => policies.filter((policy) => policy.status === 'active'),
    [policies],
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

  const isFarmer = user?.profile?.role === 'farmer';


  const handleSimulateDrought = async () => {
    const tId = toast.loading("Simulating severe drought event...", { style: { background: '#1A1A1A', color: '#FFF' }});
    try {
      await dashboardApi.simulateDrought({ h3_index: evaluationH3, rainfall_mm: 15, ndvi: 0.35 });
      toast.success(`Drought simulation dispatched for region: ${evaluationH3}`, { id: tId, style: { background: '#1A1A1A', color: '#FFF' } });
      await loadDashboard();
    } catch (simError) {
      toast.error(simError instanceof Error ? simError.message : 'Simulation failed.', { id: tId, style: { background: '#1A1A1A', color: '#FFF' } });
    }
  };

  const NavItem = ({ id, icon: Icon, label }: { id: TabId, icon: any, label: string }) => (
    <button 
      onClick={() => setActiveTab(id)}
      title={label}
      className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors text-sm font-medium relative group ${
        activeTab === id 
          ? 'bg-[#1A1A1A] text-[#00E676]' 
          : 'text-gray-400 hover:bg-[#1A1A1A] hover:text-white'
      } ${isSidebarCollapsed ? 'justify-center px-0 w-10 h-10 mx-auto' : ''}`}
    >
      {activeTab === id && !isSidebarCollapsed && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-[#00E676] rounded-r-md"></div>}
      <Icon className={`w-5 h-5 flex-shrink-0 transition-colors ${activeTab === id ? 'text-[#00E676]' : 'text-gray-500 group-hover:text-gray-300'}`} /> 
      {!isSidebarCollapsed && label}
    </button>
  );

  if (isLoading) {
    return (
      <div className="h-screen bg-[#0A0A0A] flex items-center justify-center">
        <LoadingSpinner label="Loading dashboard telemetry…" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#0A0A0A] text-white font-sans selection:bg-[#00E676] selection:text-black overflow-hidden">
      
      {/* Dark Sidebar */}
      <aside className={`${isSidebarCollapsed ? 'w-20' : 'w-64'} bg-[#0A0A0A] border-r border-[#1F1F1F] flex flex-col flex-shrink-0 transition-all duration-300 z-30 relative`}>
        {/* Collapse Toggle Button */}
        <button 
          onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          className="absolute -right-3 top-6 bg-[#1A1A1A] border border-[#2A2A2A] text-gray-400 hover:text-white rounded-full p-1 z-40 transition-colors"
        >
          {isSidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>

        <div className={`p-5 border-b border-[#1F1F1F] flex items-center ${isSidebarCollapsed ? 'justify-center' : 'gap-3'} flex-shrink-0 h-[72px]`}>
          <div className="flex-shrink-0 relative">
            <img src="/bimagrid_logo.png" alt="Logo" className="w-8 h-8 rounded-lg object-cover" />
            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-[#00E676] rounded-full border-2 border-[#0A0A0A]"></div>
          </div>
          {!isSidebarCollapsed && (
            <div>
              <p className="text-base font-bold tracking-tight text-white leading-none">BimaGrid</p>
              <p className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mt-1">
                {isFarmer ? 'Farmer Portal' : 'Agent Dashboard'}
              </p>
            </div>
          )}
        </div>

        <nav className={`p-3 flex flex-col gap-1 font-sans overflow-y-auto overflow-x-hidden flex-1 pb-24 ${isSidebarCollapsed ? 'items-center' : ''}`}>
          {!isSidebarCollapsed ? (
             <div className="pt-4 pb-1 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-widest">Overview</div>
          ) : <div className="h-4"></div>}
          
          <NavItem id="overview" icon={LayoutDashboard} label="Dashboard" />
          <NavItem id="farmers" icon={Users} label={isFarmer ? "My Policies" : "Farmers & Plans"} />
          <NavItem id="claims" icon={Banknote} label="Claims & Payouts" />
          {!isFarmer && <NavItem id="weather" icon={CloudRain} label="Weather Analytics" />}
          
          {!isSidebarCollapsed ? (
             <div className="pt-4 pb-1 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-widest">Management</div>
          ) : <div className="h-4"></div>}
          
          {!isFarmer && <NavItem id="resources" icon={BookOpen} label="Agent Resources" />}
          {!isFarmer && <NavItem id="system" icon={Server} label="System Settings" /> }
          <NavItem id="settings" icon={Settings} label="Profile Settings" />
        </nav>

        {/* User Profile Block */}
        <div className={`absolute bottom-0 w-full p-4 border-t border-[#1F1F1F] bg-[#0A0A0A] flex ${isSidebarCollapsed ? 'justify-center' : 'justify-between items-center'}`}>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-[#00E676] text-black flex items-center justify-center font-bold text-sm flex-shrink-0">
              {user?.profile?.full_name?.charAt(0) || user?.username?.charAt(0) || 'A'}
            </div>
            {!isSidebarCollapsed && (
              <div className="flex flex-col whitespace-nowrap overflow-hidden">
                <span className="text-white font-semibold text-sm truncate">{user?.profile?.full_name || 'Agent'}</span>
                <span className="text-gray-500 text-xs capitalize truncate">{user?.profile?.role || 'Admin'}</span>
              </div>
            )}
          </div>
          {!isSidebarCollapsed && (
            <button onClick={() => void logout()} className="text-gray-500 hover:text-red-500 transition-colors shrink-0">
              <LogOut className="w-5 h-5" />
            </button>
          )}
        </div>
      </aside>

      {/* Main Area */}
      <div className="flex-1 flex flex-col min-h-screen min-w-0 border-l border-[#1F1F1F] overflow-hidden">
        
        {/* Dark Top Nav */}
        <header className="h-[72px] bg-[#0A0A0A] border-b border-[#1F1F1F] flex items-center justify-between px-6 shrink-0 relative z-20">
          <div className="flex items-center gap-4 flex-1">
             <div className="relative max-w-md w-full hidden md:block">
               <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
               <input 
                 type="text" 
                 placeholder="Search anything..." 
                 className="w-full bg-[#141414] border border-[#2A2A2A] rounded-lg pl-10 pr-12 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#00E676] transition-colors"
               />
               <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
                 <kbd className="bg-[#2A2A2A] text-gray-400 px-1.5 py-0.5 rounded text-[10px] font-mono border border-[#3A3A3A]">⌘K</kbd>
               </div>
             </div>
          </div>
          
          <div className="flex items-center gap-4 shrink-0">
            {!isFarmer && (
              <button 
                onClick={() => setIsRegisterModalOpen(true)}
                className="hidden sm:flex items-center gap-2 bg-[#00E676] hover:bg-[#00c968] text-black px-4 py-2 rounded-lg font-bold text-sm transition-colors"
              >
                + New Farmer
              </button>
            )}
            <div className="flex items-center gap-2">
              <button className="p-2 text-gray-400 hover:text-white transition-colors"><Shield className="w-5 h-5" /></button>
              <button className="p-2 text-gray-400 hover:text-white transition-colors relative">
                 <Bell className="w-5 h-5" />
                 <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-[#0A0A0A]"></span>
              </button>
            </div>
            
            <div className="w-8 h-8 rounded-full bg-[#00E676] text-black flex items-center justify-center font-bold text-sm">
               {user?.profile?.full_name?.charAt(0) || 'A'}
            </div>
          </div>
        </header>

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 bg-[#0A0A0A] w-full custom-scrollbar">
          <div className="max-w-[1400px] mx-auto space-y-6">
            
            {/* Header Title */}
            {activeTab === 'overview' && (
              <div className="mb-8 flex justify-between items-end">
                <div>
                  <h1 className="text-2xl font-bold text-white mb-1">Dashboard</h1>
                  <p className="text-sm text-gray-500">Welcome back, {user?.profile?.full_name?.split(' ')[0] || 'Agent'}. Here's what's happening with your plans today.</p>
                </div>
                <button 
                  onClick={() => void loadDashboard(true)}
                  className="bg-[#141414] border border-[#2A2A2A] text-white hover:border-[#00E676] px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" /> Refresh
                </button>
              </div>
            )}

            <AnimatePresence mode="wait">
              {activeTab === 'overview' && (
                <motion.div key="overview" variants={tabVariants} initial="initial" animate="animate" exit="exit" className="space-y-6">
                  
                  {/* Top Metric Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {/* Total Premium */}
                    <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl overflow-hidden relative group">
                      <div className="p-5 pb-0">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-sm font-medium text-gray-500">Total Premium</h3>
                          <div className="w-8 h-8 rounded-full bg-[#00E676]/10 flex items-center justify-center">
                            <Banknote className="w-4 h-4 text-[#00E676]" />
                          </div>
                        </div>
                        <div className="text-3xl font-bold text-white mb-2">{formatCurrency(totalPremium)}</div>
                        <div className="flex items-center text-xs font-medium">
                          <span className="text-[#00E676] flex items-center"><ArrowUpRight className="w-3 h-3 mr-0.5" /> +12.5%</span>
                          <span className="text-gray-500 ml-1">vs last month</span>
                        </div>
                      </div>
                      <div className="h-16 w-full mt-2 relative -bottom-1">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={sparklineData1}>
                            <defs>
                              <linearGradient id="colorSpark1" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#00E676" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#00E676" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <Area type="monotone" dataKey="value" stroke="#00E676" strokeWidth={2} fillOpacity={1} fill="url(#colorSpark1)" isAnimationActive={false} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Active Farmers */}
                    <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl overflow-hidden relative group">
                      <div className="p-5 pb-0">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-sm font-medium text-gray-500">Registered Farmers</h3>
                          <div className="w-8 h-8 rounded-full bg-[#00BCD4]/10 flex items-center justify-center">
                            <Users className="w-4 h-4 text-[#00BCD4]" />
                          </div>
                        </div>
                        <div className="text-3xl font-bold text-white mb-2">{farmerRecords.length}</div>
                        <div className="flex items-center text-xs font-medium">
                          <span className="text-[#00E676] flex items-center"><ArrowUpRight className="w-3 h-3 mr-0.5" /> +8.2%</span>
                          <span className="text-gray-500 ml-1">vs last month</span>
                        </div>
                      </div>
                      <div className="h-16 w-full mt-2 relative -bottom-1">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={sparklineData2}>
                            <defs>
                              <linearGradient id="colorSpark2" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#00BCD4" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#00BCD4" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <Area type="monotone" dataKey="value" stroke="#00BCD4" strokeWidth={2} fillOpacity={1} fill="url(#colorSpark2)" isAnimationActive={false} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Total Policies */}
                    <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl overflow-hidden relative group">
                      <div className="p-5 pb-0">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-sm font-medium text-gray-500">Active Policies</h3>
                          <div className="w-8 h-8 rounded-full bg-[#2196F3]/10 flex items-center justify-center">
                            <FileText className="w-4 h-4 text-[#2196F3]" />
                          </div>
                        </div>
                        <div className="text-3xl font-bold text-white mb-2">{activePolicies.length}</div>
                        <div className="flex items-center text-xs font-medium">
                          <span className="text-red-500 flex items-center"><ArrowDownRight className="w-3 h-3 mr-0.5" /> -3.1%</span>
                          <span className="text-gray-500 ml-1">vs last month</span>
                        </div>
                      </div>
                      <div className="h-16 w-full mt-2 relative -bottom-1">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={sparklineData3}>
                            <defs>
                              <linearGradient id="colorSpark3" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#2196F3" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#2196F3" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <Area type="monotone" dataKey="value" stroke="#2196F3" strokeWidth={2} fillOpacity={1} fill="url(#colorSpark3)" isAnimationActive={false} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Total Payouts */}
                    <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl overflow-hidden relative group">
                      <div className="p-5 pb-0">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-sm font-medium text-gray-500">Total Payouts</h3>
                          <div className="w-8 h-8 rounded-full bg-[#FFB300]/10 flex items-center justify-center">
                            <Zap className="w-4 h-4 text-[#FFB300]" />
                          </div>
                        </div>
                        <div className="text-3xl font-bold text-white mb-2">{formatCurrency(totalPayouts)}</div>
                        <div className="flex items-center text-xs font-medium">
                          <span className="text-[#00E676] flex items-center"><ArrowUpRight className="w-3 h-3 mr-0.5" /> +24.7%</span>
                          <span className="text-gray-500 ml-1">vs last month</span>
                        </div>
                      </div>
                      <div className="h-16 w-full mt-2 relative -bottom-1">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={sparklineData4}>
                            <defs>
                              <linearGradient id="colorSpark4" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#FFB300" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#FFB300" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <Area type="monotone" dataKey="value" stroke="#FFB300" strokeWidth={2} fillOpacity={1} fill="url(#colorSpark4)" isAnimationActive={false} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  {/* Middle Section: Overview Chart & Traffic */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Overview Chart */}
                    <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-5 lg:col-span-2 flex flex-col">
                      <div className="flex justify-between items-start mb-6">
                        <div>
                          <h2 className="text-lg font-bold text-white mb-1">Financial Overview</h2>
                          <p className="text-sm text-gray-500">Monthly performance for the current year</p>
                        </div>
                        <div className="flex items-center bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg p-1">
                          {['Premium', 'Plans', 'Payouts'].map(tab => (
                            <button 
                              key={tab}
                              onClick={() => setChartTab(tab)}
                              className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-colors ${chartTab === tab ? 'bg-[#1A1A1A] text-white shadow-sm' : 'text-gray-500 hover:text-white'}`}
                            >
                              {tab}
                            </button>
                          ))}
                        </div>
                      </div>
                      
                      <div className="flex-1 min-h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={overviewData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                            <defs>
                              <linearGradient id="colorOverview" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#00E676" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#00E676" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 12 }} dy={10} />
                            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 12 }} tickFormatter={(value) => chartTab === 'Plans' ? value : `$${value/1000}k`} />
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#2A2A2A" />
                            <Tooltip 
                              contentStyle={{ backgroundColor: '#1A1A1A', borderColor: '#2A2A2A', borderRadius: '8px', color: '#FFF' }}
                              itemStyle={{ color: '#00E676', fontWeight: 'bold' }}
                            />
                            <Area type="monotone" dataKey={chartTab.toLowerCase()} stroke="#00E676" strokeWidth={3} fillOpacity={1} fill="url(#colorOverview)" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Traffic Sources & Monthly Goals */}
                    <div className="flex flex-col gap-6">
                      {/* Crop Distribution Donut */}
                      <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-5 flex-1 flex flex-col">
                        <h2 className="text-lg font-bold text-white mb-1">Crop Distribution</h2>
                        <p className="text-sm text-gray-500 mb-6">Percentage of insured crops</p>
                        
                        <div className="flex items-center justify-between flex-1">
                          <div className="w-1/2 h-[160px] relative">
                            <ResponsiveContainer width="100%" height="100%">
                              <PieChart>
                                <Pie
                                  data={cropData}
                                  cx="50%"
                                  cy="50%"
                                  innerRadius={50}
                                  outerRadius={70}
                                  stroke="none"
                                  paddingAngle={5}
                                  dataKey="value"
                                >
                                  {cropData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                  ))}
                                </Pie>
                              </PieChart>
                            </ResponsiveContainer>
                            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center mt-1">
                              <div className="text-xl font-bold text-white">100%</div>
                              <div className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider">Total</div>
                            </div>
                          </div>
                          
                          <div className="w-1/2 pl-4 flex flex-col gap-3">
                            {cropData.map(item => (
                              <div key={item.name} className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                                  <span className="text-xs text-gray-400 font-medium">{item.name}</span>
                                </div>
                                <span className="text-xs text-white font-bold">{item.value}%</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Monthly Goals */}
                      <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-5">
                        <h2 className="text-lg font-bold text-white mb-1">Monthly Goals</h2>
                        <p className="text-sm text-gray-500 mb-6">Track progress toward targets</p>
                        
                        <div className="flex flex-col gap-5">
                          <div>
                            <div className="flex justify-between items-end mb-2">
                              <span className="text-xs font-bold text-white">Premium Targets</span>
                              <span className="text-xs font-bold text-gray-500">88%</span>
                            </div>
                            <div className="w-full bg-[#0A0A0A] rounded-full h-2 mb-1 border border-[#2A2A2A]">
                              <div className="bg-[#00E676] h-full rounded-full" style={{ width: '88%' }}></div>
                            </div>
                            <div className="flex justify-between items-center text-[10px] text-gray-500">
                              <span>{formatCurrency(totalPremium)}</span>
                              <span>Target: KES 1M</span>
                            </div>
                          </div>

                          <div>
                            <div className="flex justify-between items-end mb-2">
                              <span className="text-xs font-bold text-white">New Farmers</span>
                              <span className="text-xs font-bold text-gray-500">85%</span>
                            </div>
                            <div className="w-full bg-[#0A0A0A] rounded-full h-2 mb-1 border border-[#2A2A2A]">
                              <div className="bg-[#00BCD4] h-full rounded-full" style={{ width: '85%' }}></div>
                            </div>
                            <div className="flex justify-between items-center text-[10px] text-gray-500">
                              <span>{farmerRecords.length}</span>
                              <span>Target: 50</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Bottom Section: Recent Policies & Activity */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pb-12">
                    {/* Recent Orders Table -> Recent Policies */}
                    <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-5 lg:col-span-2">
                      <div className="flex justify-between items-start mb-6">
                        <div>
                          <h2 className="text-lg font-bold text-white mb-1">Recent Policies</h2>
                          <p className="text-sm text-gray-500">Latest active plans from your farmers</p>
                        </div>
                        <button onClick={() => setActiveTab('farmers')} className="text-[#00E676] text-sm font-semibold flex items-center gap-1 hover:text-[#00c968] transition-colors">
                          View all <ArrowUpRight className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className="border-b border-[#2A2A2A] text-xs font-semibold text-gray-500 uppercase tracking-wider">
                              <th className="pb-3 px-2 font-medium">Farmer</th>
                              <th className="pb-3 px-2 font-medium">Policy ID</th>
                              <th className="pb-3 px-2 font-medium">Crop</th>
                              <th className="pb-3 px-2 font-medium">Status</th>
                              <th className="pb-3 px-2 text-right font-medium">Premium</th>
                            </tr>
                          </thead>
                          <tbody className="text-sm">
                            {policies.slice(0, 5).map((policy, idx) => (
                              <tr key={idx} onClick={() => setSelectedPolicyForDetail(policy)} className="border-b border-[#2A2A2A] last:border-none hover:bg-[#1A1A1A] cursor-pointer transition-colors">
                                <td className="py-4 px-2">
                                  <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-black bg-[#00E676]">
                                      {policy.farmer_name?.charAt(0) || 'F'}
                                    </div>
                                    <div className="flex flex-col">
                                      <span className="text-white font-semibold">{policy.farmer_name || 'Farmer Name'}</span>
                                      <span className="text-gray-500 text-xs">{policy.farmer_phone || 'N/A'}</span>
                                    </div>
                                  </div>
                                </td>
                                <td className="py-4 px-2 text-gray-400 font-mono text-xs">{policy.policy_number}</td>
                                <td className="py-4 px-2 text-white font-medium capitalize">{policy.crop}</td>
                                <td className="py-4 px-2">
                                  <StatusBadge status={policy.status} />
                                </td>
                                <td className="py-4 px-2 text-right text-white font-bold">{formatCurrency(policy.premium_amount)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Recent Activity Timeline */}
                    <div className="bg-[#141414] border border-[#2A2A2A] rounded-xl p-5">
                      <div className="flex justify-between items-start mb-6">
                        <div>
                          <h2 className="text-lg font-bold text-white mb-1">Recent Activity</h2>
                          <p className="text-sm text-gray-500">Latest events from the platform</p>
                        </div>
                      </div>

                      <div className="flex flex-col gap-6 relative">
                        <div className="absolute left-4 top-4 bottom-4 w-px bg-[#2A2A2A] -z-0"></div>
                        
                        <div className="flex gap-4 relative z-10">
                          <div className="w-8 h-8 rounded-full bg-[#00E676]/10 flex items-center justify-center flex-shrink-0 mt-1 border border-[#00E676]/20">
                            <Shield className="w-4 h-4 text-[#00E676]" />
                          </div>
                          <div className="flex flex-col">
                            <span className="text-white font-bold text-sm">Policy Activated</span>
                            <span className="text-gray-400 text-xs mt-0.5 leading-snug">Wycliff secured 3 Acres of Maize</span>
                            <span className="text-gray-600 text-xs mt-1">2 min ago</span>
                          </div>
                        </div>

                        <div className="flex gap-4 relative z-10">
                          <div className="w-8 h-8 rounded-full bg-[#00BCD4]/10 flex items-center justify-center flex-shrink-0 mt-1 border border-[#00BCD4]/20">
                            <UserPlus className="w-4 h-4 text-[#00BCD4]" />
                          </div>
                          <div className="flex flex-col">
                            <span className="text-white font-bold text-sm">New farmer registered</span>
                            <span className="text-gray-400 text-xs mt-0.5 leading-snug">Odiambo created an account</span>
                            <span className="text-gray-600 text-xs mt-1">15 min ago</span>
                          </div>
                        </div>

                        <div className="flex gap-4 relative z-10">
                          <div className="w-8 h-8 rounded-full bg-[#FFB300]/10 flex items-center justify-center flex-shrink-0 mt-1 border border-[#FFB300]/20">
                            <CloudRain className="w-4 h-4 text-[#FFB300]" />
                          </div>
                          <div className="flex flex-col">
                            <span className="text-white font-bold text-sm">Weather Check Executed</span>
                            <span className="text-gray-400 text-xs mt-0.5 leading-snug">Satellite scan on H3 index 89283...</span>
                            <span className="text-gray-600 text-xs mt-1">1 hour ago</span>
                          </div>
                        </div>

                        <div className="flex gap-4 relative z-10">
                          <div className="w-8 h-8 rounded-full bg-[#2196F3]/10 flex items-center justify-center flex-shrink-0 mt-1 border border-[#2196F3]/20">
                            <Banknote className="w-4 h-4 text-[#2196F3]" />
                          </div>
                          <div className="flex flex-col">
                            <span className="text-white font-bold text-sm">Premium received</span>
                            <span className="text-gray-400 text-xs mt-0.5 leading-snug">KES 1,062 from Wycliff</span>
                            <span className="text-gray-600 text-xs mt-1">2 hours ago</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Farmers & Plans Tab (Matches dark theme) */}
              {activeTab === 'farmers' && (
                <motion.div key="farmers" variants={tabVariants} initial="initial" animate="animate" exit="exit">
                   <div className="bg-[#141414] rounded-xl border border-[#2A2A2A] overflow-hidden">
                      <div className="p-6 border-b border-[#2A2A2A] flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                        <div>
                          <h2 className="text-xl font-bold text-white mb-1">Farmers & Plans Directory</h2>
                          <p className="text-sm text-gray-500">View all registered policy contracts.</p>
                        </div>
                        <div className="flex items-center gap-4 w-full sm:w-auto">
                          <div className="relative w-full sm:w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                            <input 
                              type="text" 
                              value={searchQuery}
                              onChange={(e) => setSearchQuery(e.target.value)}
                              placeholder="Search..." 
                              className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#00E676] transition-colors"
                            />
                          </div>
                        </div>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className="bg-[#1A1A1A] border-b border-[#2A2A2A] text-xs font-semibold text-gray-500 uppercase tracking-wider">
                              <th className="py-3 px-6 font-medium">Plan ID</th>
                              {!isFarmer && <th className="py-3 px-6 font-medium">Farmer</th>}
                              <th className="py-3 px-6 font-medium">Crop Protection</th>
                              <th className="py-3 px-6 font-medium">Region Code</th>
                              <th className="py-3 px-6 font-medium">Premium</th>
                              <th className="py-3 px-6 font-medium">Status</th>
                            </tr>
                          </thead>
                          <tbody className="text-sm">
                            {filteredPolicies.map((policy) => (
                              <tr key={policy.id} onClick={() => setSelectedPolicyForDetail(policy)} className="border-b border-[#2A2A2A] last:border-none hover:bg-[#1A1A1A] cursor-pointer transition-colors">
                                <td className="py-4 px-6 text-gray-400 font-mono text-xs">{policy.policy_number}</td>
                                {!isFarmer && <td className="py-4 px-6 text-white font-semibold">{policy.farmer_name || 'Jane Doe'}</td>}
                                <td className="py-4 px-6 text-white font-medium capitalize">{policy.crop}</td>
                                <td className="py-4 px-6 text-gray-500 font-mono text-xs">{policy.coverage_h3}</td>
                                <td className="py-4 px-6 text-white font-bold">{formatCurrency(policy.premium_amount)}</td>
                                <td className="py-4 px-6"><StatusBadge status={policy.status} /></td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                   </div>
                </motion.div>
              )}

              {/* Weather Analytics Tab (Adapted to dark theme) */}
              {activeTab === 'weather' && (
                <motion.div key="weather" variants={tabVariants} initial="initial" animate="animate" exit="exit" className="space-y-6">
                  <div className="bg-[#141414] rounded-xl p-6 border border-[#2A2A2A]">
                    <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
                      <CloudRain className="w-5 h-5 text-[#00E676]" /> Spatial Grid Analysis
                    </h3>
                    <p className="text-sm text-gray-500 mb-6">
                      Query real-time meteorological indexes for any H3 grid cell.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-4 max-w-xl">
                      <input
                        className="flex-1 bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2 text-sm text-white font-mono placeholder-gray-600 focus:outline-none focus:border-[#00E676] transition-colors"
                        value={weatherSearchH3}
                        onChange={(e) => setWeatherSearchH3(e.target.value)}
                        placeholder="H3 Grid Index (e.g. 8928308280fffff)"
                      />
                      <button
                        type="button"
                        onClick={() => void handleQueryWeather()}
                        disabled={weatherAnalysis.loading}
                        className="bg-[#00E676] hover:bg-[#00c968] text-black px-6 py-2 rounded-lg text-sm font-bold transition-colors flex items-center justify-center gap-2"
                      >
                        {weatherAnalysis.loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                        Analyze Grid
                      </button>
                    </div>
                  </div>

                  <div className="grid lg:grid-cols-3 gap-6">
                    {/* Metrics */}
                    <div className="lg:col-span-1 space-y-6">
                      <div className="bg-[#141414] rounded-xl p-5 border border-[#2A2A2A] flex flex-col justify-between h-36">
                        <div>
                          <div className="flex justify-between items-start mb-2">
                             <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">NDVI Metric</h3>
                             <Leaf className="w-4 h-4 text-[#00BCD4]" />
                          </div>
                          <div className="text-3xl font-bold text-white">{weatherAnalysis.ndvi !== null ? weatherAnalysis.ndvi.toFixed(2) : '—'}</div>
                        </div>
                        <div className="text-xs font-bold uppercase tracking-wider mt-auto pt-4 border-t border-[#2A2A2A]">
                          {weatherAnalysis.ndvi !== null ? (
                            weatherAnalysis.ndvi >= 0.5 ? <span className="text-[#00E676]">Healthy Canopy</span> : <span className="text-red-500">Drought Warning</span>
                          ) : <span className="text-gray-600">Pending</span>}
                        </div>
                      </div>

                      <div className="bg-[#141414] rounded-xl p-5 border border-[#2A2A2A] flex flex-col justify-between h-36">
                        <div>
                          <div className="flex justify-between items-start mb-2">
                             <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Precipitation</h3>
                             <CloudRain className="w-4 h-4 text-[#2196F3]" />
                          </div>
                          <div className="text-3xl font-bold text-white">{weatherAnalysis.rainfall !== null ? `${weatherAnalysis.rainfall.toFixed(1)} mm` : '—'}</div>
                        </div>
                        <div className="text-xs font-bold uppercase tracking-wider mt-auto pt-4 border-t border-[#2A2A2A]">
                          {weatherAnalysis.rainfall !== null ? (
                            weatherAnalysis.rainfall >= 20 ? <span className="text-[#00E676]">Adequate</span> : <span className="text-red-500">Deficit</span>
                          ) : <span className="text-gray-600">Pending</span>}
                        </div>
                      </div>
                    </div>

                    {/* Satellite Map */}
                    <div className="lg:col-span-2 bg-[#141414] rounded-xl border border-[#2A2A2A] p-2 h-[310px] relative overflow-hidden">
                      <div className="w-full h-full rounded-lg overflow-hidden relative">
                         {/* Optional overlay to darken map to match dark theme */}
                         <div className="absolute inset-0 bg-[#0A0A0A]/20 z-10 pointer-events-none mix-blend-multiply"></div>
                         
                         <MapcnMap 
                           viewport={weatherViewport}
                           onViewportChange={(vp) => setWeatherViewport(vp)}
                           className="h-full w-full"
                         >
                           <MapControls position="bottom-right" />
                           <MapMarker longitude={weatherViewport.center[0]} latitude={weatherViewport.center[1]} color="#00E676" />
                         </MapcnMap>
                      </div>
                      <div className="absolute left-6 bottom-6 bg-[#0A0A0A]/90 backdrop-blur border border-[#2A2A2A] rounded px-2 py-1 text-[10px] font-mono text-gray-400 z-20">
                        {weatherViewport.center[1].toFixed(4)}, {weatherViewport.center[0].toFixed(4)}
                      </div>
                    </div>
                  </div>
                  
                  {/* Simulate Tool */}
                  <div className="bg-[#1A1A1A] rounded-xl border border-red-900/50 p-6 flex flex-col sm:flex-row items-center gap-6">
                     <div className="p-3 bg-red-500/10 rounded-lg text-red-500 shrink-0">
                        <CloudLightning className="w-6 h-6" />
                     </div>
                     <div className="flex-1">
                        <h3 className="text-base font-bold text-white mb-1">Simulate Drought Event</h3>
                        <p className="text-sm text-gray-400">Trigger a simulated rainfall deficit on a specific grid to test the smart contract payouts.</p>
                     </div>
                     <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                        <input
                          className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2 text-sm text-white font-mono placeholder-gray-600 focus:outline-none focus:border-red-500"
                          value={evaluationH3}
                          onChange={(e) => setEvaluationH3(e.target.value)}
                          placeholder="Region Code"
                        />
                        <button
                          type="button"
                          onClick={() => void handleSimulateDrought()}
                          disabled={!evaluationH3}
                          className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg text-sm font-bold transition-colors whitespace-nowrap"
                        >
                          Trigger Escrow
                        </button>
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

      {/* Policy Detail Slide Panel - Dark Theme */}
      {selectedPolicyForDetail && (
        <AnimatePresence>
          <div className="fixed inset-0 z-[100] flex justify-end overflow-hidden">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-[#0A0A0A]/80 backdrop-blur-sm"
              onClick={() => setSelectedPolicyForDetail(null)}
            />
            
            <motion.div 
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
              className="relative w-full max-w-md md:max-w-lg h-full bg-[#141414] shadow-2xl flex flex-col border-l border-[#2A2A2A] z-10"
            >
              {/* Header */}
              <div className="p-6 border-b border-[#2A2A2A] flex justify-between items-center bg-[#0A0A0A]">
                <div>
                  <span className="text-[10px] font-bold bg-[#00E676]/10 text-[#00E676] px-2 py-0.5 rounded uppercase tracking-wider border border-[#00E676]/20">
                    Policy Document
                  </span>
                  <h3 className="text-xl font-bold text-white mt-2 tracking-tight">
                    {selectedPolicyForDetail.policy_number}
                  </h3>
                </div>
                <button 
                  onClick={() => setSelectedPolicyForDetail(null)}
                  className="p-2 bg-[#1A1A1A] hover:bg-[#2A2A2A] rounded-lg text-gray-400 transition-colors border border-[#2A2A2A]"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Scrollable Body */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                
                {/* Farmer Info */}
                <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-xl p-5 space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-500 text-[10px] uppercase tracking-wider font-bold">Farmer Name</span>
                      <p className="font-bold text-white text-sm mt-1">{selectedPolicyForDetail.farmer_name || 'Jane Doe'}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 text-[10px] uppercase tracking-wider font-bold">Phone Number</span>
                      <p className="font-bold text-white text-sm mt-1">{selectedPolicyForDetail.farmer_phone || '—'}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 text-[10px] uppercase tracking-wider font-bold">Crop Type</span>
                      <p className="font-bold text-white text-sm capitalize mt-1">{selectedPolicyForDetail.crop}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 text-[10px] uppercase tracking-wider font-bold">Acreage</span>
                      <p className="font-bold text-white text-sm mt-1">{selectedPolicyForDetail.insured_acreage} Acres</p>
                    </div>
                  </div>
                </div>

                {/* Premium Details */}
                <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-xl p-5 space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="text-gray-500 text-[10px] uppercase tracking-wider font-bold">Premium Amount</span>
                      <p className="font-bold text-[#00E676] text-lg mt-1">{formatCurrency(selectedPolicyForDetail.premium_amount)}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-gray-500 text-[10px] uppercase tracking-wider font-bold">Region H3 Index</span>
                      <p className="font-mono text-xs text-gray-300 bg-[#1A1A1A] px-2 py-1 rounded border border-[#2A2A2A] mt-1 inline-block">
                        {selectedPolicyForDetail.coverage_h3}
                      </p>
                    </div>
                  </div>
                  <div className="border-t border-[#2A2A2A] pt-4 flex justify-between items-center">
                    <div>
                      <span className="text-gray-500 text-[10px] uppercase tracking-wider font-bold">Coverage Period</span>
                      <p className="font-medium text-gray-300 text-xs mt-1">
                        {formatDate(selectedPolicyForDetail.coverage_start)} - {formatDate(selectedPolicyForDetail.coverage_end)}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="block mt-1"><StatusBadge status={selectedPolicyForDetail.status} /></span>
                    </div>
                  </div>
                </div>

                {/* Lifecycle */}
                <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-xl p-5 space-y-4">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest text-gray-500 border-b border-[#2A2A2A] pb-2">Blockchain Lifecycle</h4>
                  <div className="relative border-l border-[#2A2A2A] pl-4 space-y-4 ml-2">
                    {selectedPolicyForDetail.events && selectedPolicyForDetail.events.length > 0 ? (
                      selectedPolicyForDetail.events.map((evt, idx) => (
                        <div key={idx} className="relative">
                          <span className="absolute -left-[21px] top-1.5 w-2 h-2 rounded-full bg-[#00E676]" />
                          <p className="text-xs font-bold text-white capitalize">{evt.event_type}</p>
                          <p className="text-[10px] text-gray-500 font-mono mt-1">{formatDate(evt.created_at)}</p>
                        </div>
                      ))
                    ) : (
                      <div className="relative">
                        <span className="absolute -left-[21px] top-1.5 w-2 h-2 rounded-full bg-gray-600" />
                        <p className="text-xs font-bold text-gray-400">Policy Draft Issued</p>
                        <p className="text-[10px] text-gray-600 font-mono mt-1">{formatDate(selectedPolicyForDetail.created_at)}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Footer */}
              <div className="p-6 border-t border-[#2A2A2A] bg-[#0A0A0A] flex justify-end">
                <button 
                  type="button" 
                  onClick={() => setSelectedPolicyForDetail(null)}
                  className="bg-[#1A1A1A] border border-[#2A2A2A] hover:bg-[#2A2A2A] text-white py-2 px-6 rounded-lg text-sm font-medium transition-colors"
                >
                  Close View
                </button>
              </div>
            </motion.div>
          </div>
        </AnimatePresence>
      )}
    </div>
  );
}
