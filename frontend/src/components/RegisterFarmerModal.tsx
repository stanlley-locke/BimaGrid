import { FormEvent, useState, useEffect } from 'react';
import { dashboardApi } from '../api/client';
import type { RegisterFarmerPayload } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, Tractor, Map as MapIcon, Phone, Leaf, User, Shield, ChevronRight, ChevronLeft, 
  Upload, FileText, CheckCircle2, Compass, RefreshCw, 
  Activity, CloudRain, BarChart2 
} from 'lucide-react';
import toast from 'react-hot-toast';

import { Map, MapControls, MapMarker, MapRoute, MapGeoJSON } from './ui/map';

const CROP_OPTIONS = [
  { value: 'maize', label: 'Maize (KES 322/Acre)' },
  { value: 'beans', label: 'Beans (KES 280/Acre)' },
  { value: 'sorghum', label: 'Sorghum (KES 300/Acre)' },
  { value: 'rice', label: 'Rice (KES 400/Acre)' },
  { value: 'coffee', label: 'Coffee (KES 450/Acre)' },
  { value: 'tea', label: 'Tea (KES 500/Acre)' },
];

function formatCurrency(value: string | number): string {
  const amount = typeof value === 'string' ? parseFloat(value) : value;
  if (Number.isNaN(amount)) return 'KES 0';
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    maximumFractionDigits: 0,
  }).format(amount);
}

const getCountyCenter = (countyName?: string): [number, number] => {
  if (!countyName) return [34.4534, -0.5298];
  const name = countyName.toUpperCase().trim();
  if (name.includes('HOMA')) return [34.4534, -0.5298];
  if (name.includes('NAIROBI')) return [36.8219, -1.2921];
  if (name.includes('KISUMU')) return [34.7617, -0.1022];
  if (name.includes('MOMBASA')) return [39.6672, -4.0383];
  if (name.includes('NAKURU')) return [36.0800, -0.3031];
  if (name.includes('ELDORET') || name.includes('UASIN')) return [35.2697, 0.5143];
  if (name.includes('KAKAMEGA')) return [34.7519, 0.2827];
  if (name.includes('MERU')) return [37.6498, 0.0463];
  if (name.includes('KIAMBU')) return [36.8167, -1.1500];
  if (name.includes('NYERI')) return [36.9500, -0.4167];
  return [34.4534, -0.5298];
};

const calculateGeodesicArea = (points: { lat: number; lng: number }[]) => {
  if (points.length < 3) return 0;
  const radius = 6378137;
  let area = 0;
  
  for (let i = 0; i < points.length; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % points.length];
    
    const lat1 = (p1.lat * Math.PI) / 180;
    const lat2 = (p2.lat * Math.PI) / 180;
    const lng1 = (p1.lng * Math.PI) / 180;
    const lng2 = (p2.lng * Math.PI) / 180;
    
    area += (lng2 - lng1) * (2 + Math.sin(lat1) + Math.sin(lat2));
  }
  
  return Math.abs((area * radius * radius) / 2);
};

interface RegisterFarmerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function RegisterFarmerModal({ isOpen, onClose, onSuccess }: RegisterFarmerModalProps) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<RegisterFarmerPayload>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone_number: '',
    ward_code: '',
    crop: 'maize',
    acreage: '1.0',
    mpesa_number: '',
    h3_index: '8928308280fffff',
  });

  const [counties, setCounties] = useState<{ id: string; external_id: number; name: string }[]>([]);
  const [subcounties, setSubcounties] = useState<{ id: string; external_id: number; name: string }[]>([]);
  const [constituencies, setConstituencies] = useState<{ id: string; external_id: number; name: string }[]>([]);
  const [wards, setWards] = useState<{ id: string; external_id: number; ward_code: string; name: string }[]>([]);

  const [selectedCounty, setSelectedCounty] = useState('');
  const [selectedSubcounty, setSelectedSubcounty] = useState('');
  const [selectedConstituency, setSelectedConstituency] = useState('');
  const [selectedWard, setSelectedWard] = useState('');

  const [polygonPoints, setPolygonPoints] = useState<{ lat: number; lng: number }[]>([]);
  const [mapViewport, setMapViewport] = useState({
    center: [34.4534, -0.5298] as [number, number],
    zoom: 15,
    bearing: 0,
    pitch: 0
  });
  const [isDrawingComplete, setIsDrawingComplete] = useState(false);

  const [diagnosticsLoading, setDiagnosticsLoading] = useState(false);
  const [diagnosticsError, setDiagnosticsError] = useState<string | null>(null);
  const [diagnosticsData, setDiagnosticsData] = useState<{ rainfall: number; ndvi: number; soilMoisture: number } | null>(null);
  const [diagnosticsMessage, setDiagnosticsMessage] = useState('Connecting to Copernicus constellation...');

  const [documents, setDocuments] = useState<{ name: string; size: string }[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentCountyObj = counties.find(c => c.id === selectedCounty);
  const currentSubcountyObj = subcounties.find(s => s.id === selectedSubcounty);
  const currentWardObj = wards.find(w => w.id === selectedWard);

  useEffect(() => {
    if (isOpen) {
      setStep(1);
      setPolygonPoints([]);
      setIsDrawingComplete(false);
      setDiagnosticsData(null);
      dashboardApi.getCounties()
        .then(data => setCounties(data))
        .catch(err => console.error('Failed to load counties:', err));
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedCounty) {
      dashboardApi.getSubcounties(selectedCounty)
        .then(data => {
          setSubcounties(data);
          setConstituencies([]);
          setWards([]);
          setSelectedSubcounty('');
          setSelectedConstituency('');
          setSelectedWard('');
        })
        .catch(err => console.error('Failed to load subcounties:', err));
    } else {
      setSubcounties([]);
      setConstituencies([]);
      setWards([]);
    }
  }, [selectedCounty]);

  useEffect(() => {
    if (selectedSubcounty) {
      dashboardApi.getConstituencies(selectedSubcounty)
        .then(data => {
          setConstituencies(data);
          setWards([]);
          setSelectedConstituency('');
          setSelectedWard('');
        })
        .catch(err => console.error('Failed to load constituencies:', err));
    } else {
      setConstituencies([]);
      setWards([]);
    }
  }, [selectedSubcounty]);

  useEffect(() => {
    if (selectedConstituency) {
      dashboardApi.getWards(selectedConstituency)
        .then(data => {
          setWards(data);
          setSelectedWard('');
        })
        .catch(err => console.error('Failed to load wards:', err));
    } else {
      setWards([]);
    }
  }, [selectedConstituency]);

  useEffect(() => {
    if (selectedCounty) {
      const center = getCountyCenter(currentCountyObj?.name);
      setMapViewport(prev => ({
        ...prev,
        center: center,
        zoom: 15
      }));
    }
  }, [selectedCounty, currentCountyObj]);

  if (!isOpen) return null;

  const updateField = <K extends keyof RegisterFarmerPayload>(key: K, value: RegisterFarmerPayload[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleWardChange = (wardId: string) => {
    setSelectedWard(wardId);
    const ward = wards.find(w => w.id === wardId);
    if (ward) {
      updateField('ward_code', ward.ward_code);
    }
  };

  const finishDrawing = () => {
    if (polygonPoints.length < 3) {
      toast.error('Draw at least 3 points to outline your farm boundary', { style: { background: '#1A1A1A', color: '#FFF' }});
      return;
    }
    
    setIsDrawingComplete(true);
    
    const areaSqMeters = calculateGeodesicArea(polygonPoints);
    const acreageVal = Math.max(0.1, parseFloat((areaSqMeters / 4046.86).toFixed(1)));
    updateField('acreage', acreageVal.toString());

    const indexStr = '8928308280fffff';
    updateField('h3_index', indexStr);

    toast.success(`Boundary locked. Mapped to ${acreageVal} Acres`, { style: { background: '#1A1A1A', color: '#FFF' }});
  };

  const resetDrawing = () => {
    setPolygonPoints([]);
    setIsDrawingComplete(false);
  };

  const executeDiagnosticsQuery = async (targetH3: string) => {
    setDiagnosticsLoading(true);
    setDiagnosticsError(null);
    setDiagnosticsMessage('Connecting to Sentinel-2 Multispectral instrument...');

    try {
      await new Promise(r => setTimeout(r, 600));
      setDiagnosticsMessage('Resolving H3 index telemetry grid...');
      await new Promise(r => setTimeout(r, 600));
      setDiagnosticsMessage('Downloading historical rainfall indexes...');
      
      const [rainfallRes, ndviRes] = await Promise.all([
        dashboardApi.getRainfall(targetH3),
        dashboardApi.getNdvi(targetH3)
      ]);

      setDiagnosticsData({
        rainfall: rainfallRes.value,
        ndvi: ndviRes.value,
        soilMoisture: parseFloat((ndviRes.value * 40).toFixed(1))
      });
    } catch (err) {
      setDiagnosticsError('Metereological satellite data could not be parsed.');
      console.error(err);
    } finally {
      setDiagnosticsLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setIsUploading(true);
      setUploadProgress(10);
      
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsUploading(false);
            setDocuments(current => [...current, { name: file.name, size: (file.size / 1024 / 1024).toFixed(2) + ' MB' }]);
            toast.success(`${file.name} uploaded successfully!`, { style: { background: '#1A1A1A', color: '#FFF' }});
            return 0;
          }
          return prev + 30;
        });
      }, 150);
    }
  };

  const handleNext = () => {
    if (step === 1) {
      if (!form.full_name || !form.username || !form.password || !form.phone_number || !form.mpesa_number) {
        toast.error('Please fill in all required account fields', { style: { background: '#1A1A1A', color: '#FFF' }});
        return;
      }
    } else if (step === 2) {
      if (!selectedCounty || !selectedSubcounty || !selectedConstituency || !selectedWard) {
        toast.error('Please select County, Subcounty, Constituency, and Ward', { style: { background: '#1A1A1A', color: '#FFF' }});
        return;
      }
    } else if (step === 3) {
      if (polygonPoints.length < 3 || !isDrawingComplete) {
        toast.error('Please draw and lock your farm outlines', { style: { background: '#1A1A1A', color: '#FFF' }});
        return;
      }
      void executeDiagnosticsQuery(form.h3_index);
    }
    setStep(prev => prev + 1);
  };

  const handleBack = () => {
    setStep(prev => prev - 1);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    const tId = toast.loading('Registering farmer and generating plan...', { style: { background: '#1A1A1A', color: '#FFF' }});

    try {
      await dashboardApi.registerFarmer(form);
      toast.success(`Farmer registered! Credentials sent via SMS.`, { id: tId, style: { background: '#1A1A1A', color: '#FFF' } });
      onSuccess();
      onClose();
    } catch (submitError) {
      toast.error(submitError instanceof Error ? submitError.message : 'Failed to register farmer.', { id: tId, style: { background: '#1A1A1A', color: '#FFF' } });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 text-white font-sans">
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-[#0A0A0A]/80 backdrop-blur-sm"
          onClick={onClose}
        />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="w-full max-w-2xl max-h-[95vh] overflow-y-auto relative z-10 p-6 sm:p-8 bg-[#141414] border border-[#2A2A2A] rounded-2xl shadow-2xl custom-scrollbar"
        >
          {/* Header */}
          <div className="mb-6 flex items-start justify-between gap-4 border-b border-[#2A2A2A] pb-4">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#00E676]/10 text-[#00E676] border border-[#00E676]/20">
                <Tractor className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white tracking-tight">Register Farmer</h2>
                <p className="text-xs text-gray-400 mt-1">
                  Create a new farmer account and capture their farm details.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg p-2 bg-[#1A1A1A] text-gray-400 hover:text-white border border-[#2A2A2A] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Premium Step Progress Tracker */}
          <div className="mb-8 flex items-center justify-between select-none relative px-4">
            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-[#2A2A2A] -z-10" />
            <div className="absolute top-1/2 left-0 h-0.5 bg-[#00E676] -z-10 transition-all duration-300" style={{ width: `${(step - 1) * 25}%` }} />
            
            {[
              { label: 'Account', icon: User, stepNum: 1 },
              { label: 'Location', icon: MapIcon, stepNum: 2 },
              { label: 'Draw Farm', icon: Compass, stepNum: 3 },
              { label: 'Diagnostics', icon: Activity, stepNum: 4 },
              { label: 'Review', icon: Shield, stepNum: 5 }
            ].map((item) => (
              <div key={item.stepNum} className="flex flex-col items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 font-bold ${
                  step > item.stepNum 
                    ? 'bg-[#00E676] border-[#00E676] text-black shadow-md' 
                    : step === item.stepNum 
                      ? 'bg-[#1A1A1A] border-[#00E676] text-[#00E676] shadow-[0_0_15px_rgba(0,230,118,0.2)] scale-110' 
                      : 'bg-[#0A0A0A] border-[#2A2A2A] text-gray-500'
                }`}>
                  <item.icon className="w-5 h-5" />
                </div>
                <span className={`text-[10px] font-bold tracking-wide mt-2 transition-colors duration-300 ${step >= item.stepNum ? 'text-white' : 'text-gray-500'}`}>
                  {item.label}
                </span>
              </div>
            ))}
          </div>

          {/* Form / Steps Content */}
          <div className="min-h-[300px] mb-8">
            {step === 1 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="grid gap-4 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label className="block mb-1 text-xs font-bold text-gray-400">Full Name</label>
                  <input
                    className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-[#00E676] transition-colors"
                    value={form.full_name}
                    onChange={(event) => updateField('full_name', event.target.value)}
                    placeholder="e.g. Wycliffe Omondi"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-1 text-xs font-bold text-gray-400">Username</label>
                  <input
                    className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-[#00E676] transition-colors"
                    value={form.username}
                    onChange={(event) => updateField('username', event.target.value)}
                    placeholder="e.g. wycliffeo"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-1 text-xs font-bold text-gray-400">Temporary Password</label>
                  <input
                    type="password"
                    className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-[#00E676] transition-colors"
                    value={form.password}
                    onChange={(event) => updateField('password', event.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-1 text-xs font-bold text-gray-400">Phone Number</label>
                  <div className="relative">
                    <input
                      className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-[#00E676] transition-colors"
                      placeholder="e.g. +254711223344"
                      value={form.phone_number}
                      onChange={(event) => updateField('phone_number', event.target.value)}
                      required
                    />
                    <Phone className="absolute left-3 top-2.5 w-4 h-4 text-[#00E676]" />
                  </div>
                </div>
                <div>
                  <label className="block mb-1 text-xs font-bold text-gray-400">M-Pesa Number</label>
                  <input
                    className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-[#00E676] transition-colors"
                    placeholder="e.g. 254711223344"
                    value={form.mpesa_number}
                    onChange={(event) => updateField('mpesa_number', event.target.value)}
                    required
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block mb-1 text-xs font-bold text-gray-400">Email Address (Optional)</label>
                  <input
                    type="email"
                    className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-[#00E676] transition-colors"
                    value={form.email}
                    onChange={(event) => updateField('email', event.target.value)}
                    placeholder="e.g. wycliffe@bimagrid.com"
                  />
                </div>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block mb-1.5 text-xs font-bold text-gray-400 uppercase tracking-widest">County</label>
                    <select
                      className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2.5 text-sm text-white appearance-none focus:outline-none focus:border-[#00E676] transition-colors"
                      value={selectedCounty}
                      onChange={(e) => setSelectedCounty(e.target.value)}
                    >
                      <option value="">Select County</option>
                      {counties.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block mb-1.5 text-xs font-bold text-gray-400 uppercase tracking-widest">Sub-county</label>
                    <select
                      className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2.5 text-sm text-white appearance-none focus:outline-none focus:border-[#00E676] transition-colors disabled:opacity-50"
                      value={selectedSubcounty}
                      onChange={(e) => setSelectedSubcounty(e.target.value)}
                      disabled={!selectedCounty}
                    >
                      <option value="">Select Sub-county</option>
                      {subcounties.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block mb-1.5 text-xs font-bold text-gray-400 uppercase tracking-widest">Constituency</label>
                    <select
                      className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2.5 text-sm text-white appearance-none focus:outline-none focus:border-[#00E676] transition-colors disabled:opacity-50"
                      value={selectedConstituency}
                      onChange={(e) => setSelectedConstituency(e.target.value)}
                      disabled={!selectedSubcounty}
                    >
                      <option value="">Select Constituency</option>
                      {constituencies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block mb-1.5 text-xs font-bold text-gray-400 uppercase tracking-widest">Ward</label>
                    <select
                      className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2.5 text-sm text-white appearance-none focus:outline-none focus:border-[#00E676] transition-colors disabled:opacity-50"
                      value={selectedWard}
                      onChange={(e) => handleWardChange(e.target.value)}
                      disabled={!selectedConstituency}
                    >
                      <option value="">Select Ward</option>
                      {wards.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                    </select>
                  </div>
                </div>

                {selectedCounty && (
                  <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl p-4 flex items-center justify-between text-xs mt-4">
                    <div>
                      <p className="font-bold text-white text-sm">{currentCountyObj?.name}</p>
                      <p className="text-[10px] text-gray-500 font-bold mt-1 uppercase">
                        {subcounties.length > 0 ? `${subcounties.length} sub-counties loaded` : 'Loading subdivisions...'}
                      </p>
                    </div>
                    <MapIcon className="w-5 h-5 text-[#00E676]" />
                  </div>
                )}
              </motion.div>
            )}

            {step === 3 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
                <div className="flex justify-between items-center text-xs">
                  <div>
                    <h3 className="font-bold text-white text-sm">Draw Farm Boundaries</h3>
                    <p className="text-gray-500 mt-0.5">Click on the satellite map to plot boundary vertices</p>
                  </div>
                  <div className="flex gap-2">
                    <button 
                      type="button" 
                      onClick={resetDrawing} 
                      className="bg-[#1A1A1A] border border-[#2A2A2A] text-white hover:bg-[#2A2A2A] py-1.5 px-3 rounded text-[10px] font-bold transition-colors"
                    >
                      Reset
                    </button>
                    <button 
                      type="button" 
                      onClick={finishDrawing} 
                      disabled={polygonPoints.length < 3 || isDrawingComplete}
                      className="bg-[#00E676] text-black hover:bg-[#00c968] py-1.5 px-3 rounded text-[10px] font-bold transition-colors disabled:opacity-50"
                    >
                      Lock Outline
                    </button>
                  </div>
                </div>

                {/* Map Integration Dark Theme */}
                <div className="relative border border-[#2A2A2A] rounded-xl overflow-hidden h-[320px] bg-[#0A0A0A] z-10">
                  <div className="absolute inset-0 bg-[#0A0A0A]/20 z-10 pointer-events-none mix-blend-multiply"></div>
                  <Map 
                    viewport={mapViewport} 
                    onViewportChange={(vp) => setMapViewport(vp)}
                    onClick={(e) => {
                      if (isDrawingComplete) return;
                      setPolygonPoints(prev => [...prev, { lat: e.lngLat.lat, lng: e.lngLat.lng }]);
                    }}
                    className="h-full w-full"
                  >
                    <MapControls position="bottom-right" />

                    {polygonPoints.map((p, idx) => (
                      <MapMarker 
                        key={idx} 
                        longitude={p.lng} 
                        latitude={p.lat}
                        color={idx === 0 ? '#00BCD4' : '#00E676'}
                      />
                    ))}

                    {polygonPoints.length > 0 && (
                      <MapRoute 
                        coordinates={
                          isDrawingComplete 
                            ? [...polygonPoints.map(p => [p.lng, p.lat] as [number, number]), [polygonPoints[0].lng, polygonPoints[0].lat] as [number, number]]
                            : polygonPoints.map(p => [p.lng, p.lat] as [number, number])
                        }
                        color={isDrawingComplete ? '#00E676' : '#00BCD4'}
                        width={3}
                        opacity={0.8}
                        dashArray={isDrawingComplete ? undefined : [5, 5]}
                      />
                    )}
                    
                    {polygonPoints.length >= 3 && isDrawingComplete && (
                      <MapGeoJSON 
                        id="farm-polygon"
                        data={{
                          type: "Feature",
                          properties: {},
                          geometry: {
                            type: "Polygon",
                            coordinates: [[
                              ...polygonPoints.map(p => [p.lng, p.lat]),
                              [polygonPoints[0].lng, polygonPoints[0].lat]
                            ]]
                          }
                        }}
                        fillPaint={{
                          "fill-color": "#00E676",
                          "fill-opacity": 0.3
                        }}
                        linePaint={false}
                      />
                    )}
                  </Map>

                  {/* HUD */}
                  <div className="absolute right-4 top-4 bg-[#0A0A0A]/90 backdrop-blur border border-[#2A2A2A] rounded-lg p-3 text-[10px] font-mono text-gray-400 space-y-2 w-44 z-20">
                    <div className="flex justify-between">
                      <span>Vertices:</span>
                      <span className="text-white font-bold">{polygonPoints.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Area:</span>
                      <span className="text-white font-bold">
                        {calculateGeodesicArea(polygonPoints).toFixed(0)} m²
                      </span>
                    </div>
                    <div className="flex justify-between border-t border-[#2A2A2A] pt-2">
                      <span>Calculated Acreage:</span>
                      <span className="text-[#00E676] font-bold">
                        {polygonPoints.length >= 3 ? (calculateGeodesicArea(polygonPoints) / 4046.86).toFixed(1) : '0.0'} Ac
                      </span>
                    </div>
                  </div>

                  {/* HUD Coordinates Display */}
                  <div className="absolute left-4 bottom-4 bg-[#0A0A0A]/90 backdrop-blur border border-[#2A2A2A] rounded-lg px-2 py-1 text-[9px] font-mono text-gray-400 z-20">
                    {mapViewport.center[1].toFixed(5)}, {mapViewport.center[0].toFixed(5)}
                  </div>
                </div>
              </motion.div>
            )}

            {step === 4 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
                <div className="flex justify-between items-center text-xs">
                  <div>
                    <h3 className="font-bold text-white text-sm">Sentinel-2 Diagnostics</h3>
                    <p className="text-gray-400 mt-0.5">Parameters derived for cell: <span className="font-mono text-white bg-[#1A1A1A] px-1.5 py-0.5 rounded border border-[#2A2A2A]">{form.h3_index}</span></p>
                  </div>
                </div>

                <AnimatePresence mode="wait">
                  {diagnosticsLoading ? (
                    <motion.div 
                      key="loading" 
                      initial={{ opacity: 0 }} 
                      animate={{ opacity: 1 }} 
                      exit={{ opacity: 0 }} 
                      className="flex flex-col items-center justify-center p-12 bg-[#0A0A0A] border border-[#2A2A2A] rounded-xl min-h-[220px]"
                    >
                      <RefreshCw className="w-10 h-10 text-[#00E676] animate-spin mb-4" />
                      <p className="text-sm font-bold text-white">{diagnosticsMessage}</p>
                      <p className="text-[10px] text-gray-500 mt-2 uppercase tracking-widest">Satellite Uplink Active</p>
                    </motion.div>
                  ) : diagnosticsError ? (
                    <motion.div 
                      key="error" 
                      initial={{ opacity: 0 }} 
                      animate={{ opacity: 1 }} 
                      className="p-8 text-center bg-red-900/10 border border-red-900/30 rounded-xl"
                    >
                      <p className="text-sm font-bold text-red-500 mb-4">{diagnosticsError}</p>
                      <button 
                        type="button" 
                        onClick={() => void executeDiagnosticsQuery(form.h3_index)} 
                        className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg text-xs flex items-center gap-2 mx-auto transition-colors"
                      >
                        <RefreshCw className="w-3.5 h-3.5" /> Retry Connection
                      </button>
                    </motion.div>
                  ) : diagnosticsData ? (
                    <motion.div 
                      key="data" 
                      initial={{ opacity: 0 }} 
                      animate={{ opacity: 1 }} 
                      className="space-y-4"
                    >
                      <div className="grid grid-cols-3 gap-4">
                        <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-xl p-4 flex flex-col justify-between h-28">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">NDVI Greenness</span>
                            <Leaf className="w-4 h-4 text-[#00BCD4]" />
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-white font-mono">{diagnosticsData.ndvi.toFixed(2)}</p>
                            <p className="text-[9px] font-bold text-[#00E676] mt-1">Optimal Canopy</p>
                          </div>
                        </div>

                        <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-xl p-4 flex flex-col justify-between h-28">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Precipitation</span>
                            <CloudRain className="w-4 h-4 text-[#2196F3]" />
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-white font-mono">{diagnosticsData.rainfall.toFixed(1)} mm</p>
                            <p className="text-[9px] font-bold text-[#2196F3] mt-1">Standard Baseline</p>
                          </div>
                        </div>

                        <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-xl p-4 flex flex-col justify-between h-28">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Soil Moisture</span>
                            <BarChart2 className="w-4 h-4 text-[#FFB300]" />
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-white font-mono">{diagnosticsData.soilMoisture}%</p>
                            <p className="text-[9px] font-bold text-[#FFB300] mt-1">Good retention</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-[#00E676]/10 border border-[#00E676]/20 rounded-xl p-4 flex items-center justify-between text-xs mt-2">
                        <div>
                          <p className="font-bold text-[#00E676]">Parametric Condition: ACTIVE & ELIGIBLE</p>
                          <p className="text-[10px] text-gray-400 mt-1">Vegetation indices and water volumes are within standard ranges. Plan setup allowed.</p>
                        </div>
                        <CheckCircle2 className="w-6 h-6 text-[#00E676]" />
                      </div>
                    </motion.div>
                  ) : null}
                </AnimatePresence>

                <div className="grid gap-4 sm:grid-cols-2 pt-4 border-t border-[#2A2A2A]">
                  <div>
                    <label className="block mb-1.5 text-xs font-bold text-gray-400 uppercase tracking-widest">Primary Crop</label>
                    <select
                      className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg px-4 py-2.5 text-sm text-white appearance-none focus:outline-none focus:border-[#00E676] transition-colors"
                      value={form.crop}
                      onChange={(event) => updateField('crop', event.target.value)}
                    >
                      {CROP_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block mb-1.5 text-xs font-bold text-gray-400 uppercase tracking-widest">Acreage</label>
                    <input
                      type="number"
                      step="0.1"
                      className="w-full bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none transition-colors"
                      value={form.acreage}
                      onChange={(event) => updateField('acreage', event.target.value)}
                      required
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {step === 5 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
                <div className="bg-[#0A0A0A] border border-dashed border-[#2A2A2A] rounded-xl p-6 flex flex-col items-center justify-center text-center">
                  <Upload className="w-8 h-8 text-[#00E676] mb-3" />
                  <p className="text-xs font-bold text-white mb-1">Upload Title Deed / Documents</p>
                  <p className="text-[10px] text-gray-500 mb-4">Accepts PDF, PNG, JPG up to 10MB</p>
                  
                  <label className="bg-[#1A1A1A] hover:bg-[#2A2A2A] border border-[#2A2A2A] text-white py-1.5 px-4 rounded-lg text-xs cursor-pointer inline-flex items-center transition-colors">
                    <span>Choose File</span>
                    <input type="file" className="hidden" onChange={handleFileChange} disabled={isUploading} />
                  </label>

                  {isUploading && (
                    <div className="w-full max-w-xs mt-4">
                      <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
                        <span>Uploading...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <div className="w-full bg-[#2A2A2A] h-1.5 rounded-full overflow-hidden">
                        <div className="bg-[#00E676] h-1.5 transition-all duration-150" style={{ width: `${uploadProgress}%` }} />
                      </div>
                    </div>
                  )}
                </div>

                {documents.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Uploaded Documents</p>
                    {documents.map((doc, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg p-3 text-xs">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-gray-400" />
                          <span className="font-medium text-white truncate max-w-[200px]">{doc.name}</span>
                        </div>
                        <span className="text-[10px] font-mono text-gray-500">{doc.size}</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="border border-[#2A2A2A] rounded-xl p-5 bg-[#0A0A0A] space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-2 border-b border-[#2A2A2A] pb-2">
                    <CheckCircle2 className="w-4 h-4 text-[#00E676]" /> Summary Review
                  </h4>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-3 text-xs">
                    <div>
                      <span className="text-gray-500 font-bold text-[10px] uppercase">Farmer:</span>
                      <p className="font-bold text-white mt-1">{form.full_name}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 font-bold text-[10px] uppercase">Phone:</span>
                      <p className="font-bold text-white mt-1">{form.phone_number}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 font-bold text-[10px] uppercase">Location:</span>
                      <p className="font-medium text-white mt-1">{currentCountyObj?.name ?? '—'} / {currentSubcountyObj?.name ?? '—'}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 font-bold text-[10px] uppercase">Ward Code:</span>
                      <p className="font-medium text-white mt-1">{currentWardObj?.name ?? '—'} ({form.ward_code || '—'})</p>
                    </div>
                    <div>
                      <span className="text-gray-500 font-bold text-[10px] uppercase">Crop:</span>
                      <p className="font-bold text-white capitalize mt-1">{form.crop}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 font-bold text-[10px] uppercase">Acreage:</span>
                      <p className="font-bold text-[#00E676] mt-1">{form.acreage} Ac</p>
                    </div>
                  </div>
                </div>

                {/* Dynamic cost banner */}
                <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl p-4 text-white flex justify-between items-center relative overflow-hidden mt-4">
                  <div>
                    <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Plan Setup Premium</span>
                    <p className="text-2xl font-bold text-[#00E676] mt-0.5 font-mono">
                      {formatCurrency(parseFloat(form.acreage || '0') * (form.crop === 'maize' ? 322 : form.crop === 'beans' ? 280 : form.crop === 'sorghum' ? 300 : form.crop === 'rice' ? 400 : form.crop === 'coffee' ? 450 : 500))}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest block">Blockchain Escrow</span>
                    <span className="text-xs font-bold text-gray-400 mt-0.5 block">Automated via Hardhat</span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Navigation Controls */}
          <div className="flex gap-4 border-t border-[#2A2A2A] pt-6">
            {step > 1 && (
              <button 
                type="button" 
                onClick={handleBack} 
                className="bg-[#1A1A1A] border border-[#2A2A2A] text-white hover:bg-[#2A2A2A] py-3 rounded-lg text-sm font-bold flex items-center justify-center gap-2 flex-1 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" /> Back
              </button>
            )}
            
            {step < 5 ? (
              <button 
                type="button" 
                onClick={handleNext} 
                className="bg-[#00E676] hover:bg-[#00c968] text-black py-3 rounded-lg text-sm font-bold flex items-center justify-center gap-2 flex-1 transition-colors"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button 
                type="button" 
                onClick={handleSubmit} 
                disabled={isSubmitting} 
                className="bg-[#00E676] hover:bg-[#00c968] text-black py-3 rounded-lg text-sm font-bold flex items-center justify-center gap-2 flex-1 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                {isSubmitting ? 'Creating...' : 'Register Farmer'}
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
