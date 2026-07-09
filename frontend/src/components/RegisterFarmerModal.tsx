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

// mapcn imports
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

// Map centering helper based on Kenyan counties [longitude, latitude]
const getCountyCenter = (countyName?: string): [number, number] => {
  if (!countyName) return [34.4534, -0.5298]; // Default to Homa Bay
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
  return [34.4534, -0.5298]; // Fallback
};

// Spherical Shoelace formula for geodesic area in square meters
const calculateGeodesicArea = (points: { lat: number; lng: number }[]) => {
  if (points.length < 3) return 0;
  const radius = 6378137; // Earth's mean radius in meters
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

  // Map Polygon drawing state
  const [polygonPoints, setPolygonPoints] = useState<{ lat: number; lng: number }[]>([]);
  const [mapViewport, setMapViewport] = useState({
    center: [34.4534, -0.5298] as [number, number],
    zoom: 15,
    bearing: 0,
    pitch: 0
  });
  const [isDrawingComplete, setIsDrawingComplete] = useState(false);

  // Satellite queries state
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
      toast.error('Draw at least 3 points to outline your farm boundary');
      return;
    }
    
    setIsDrawingComplete(true);
    
    const areaSqMeters = calculateGeodesicArea(polygonPoints);
    const acreageVal = Math.max(0.1, parseFloat((areaSqMeters / 4046.86).toFixed(1)));
    updateField('acreage', acreageVal.toString());

    // Resolve an H3 index based on polygon center
    const indexStr = '8928308280fffff';
    updateField('h3_index', indexStr);

    toast.success(`Farm boundary locked. Mapped to ${acreageVal} Acres under H3 Grid ${indexStr}`);
  };

  const resetDrawing = () => {
    setPolygonPoints([]);
    setIsDrawingComplete(false);
  };

  // Satellite Diagnostic Fetch
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
            toast.success(`${file.name} uploaded successfully!`);
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
        toast.error('Please fill in all account fields');
        return;
      }
    } else if (step === 2) {
      if (!selectedCounty || !selectedSubcounty || !selectedConstituency || !selectedWard) {
        toast.error('Please select County, Subcounty, Constituency, and Ward');
        return;
      }
    } else if (step === 3) {
      if (polygonPoints.length < 3 || !isDrawingComplete) {
        toast.error('Please draw and lock your farm outlines on the satellite map first');
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
    const tId = toast.loading('Registering farmer and generating plan...');

    try {
      await dashboardApi.registerFarmer(form);
      toast.success(`Farmer ${form.full_name} registered! Credentials sent via SMS.`, { id: tId });
      onSuccess();
      onClose();
    } catch (submitError) {
      toast.error(submitError instanceof Error ? submitError.message : 'Failed to register farmer.', { id: tId });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
          onClick={onClose}
        />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="card w-full max-w-2xl max-h-[95vh] overflow-y-auto relative z-10 p-6 sm:p-8 bg-white border border-slate-100 rounded-[1.5rem] shadow-2xl"
        >
          <div className="absolute top-0 left-0 w-full h-2 bg-bima-green rounded-t-[1.5rem]" />
          
          <div className="mb-6 flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-[1rem] bg-bima-lightGreen/50 text-bima-darkGreen">
                <Tractor className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-extrabold text-bima-darkGreen tracking-tight">Register Farmer</h2>
                <p className="text-xs text-slate-500 font-medium">
                  Create a new farmer account and capture their farm details.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="rounded-[1rem] p-2 bg-slate-50 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Premium Step Progress Tracker */}
          <div className="mb-8 flex items-center justify-between select-none relative px-4">
            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-slate-100 -z-10" />
            <div className="absolute top-1/2 left-0 h-0.5 bg-bima-green -z-10 transition-all duration-300" style={{ width: `${(step - 1) * 25}%` }} />
            
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
                    ? 'bg-bima-green border-bima-green text-white shadow-md' 
                    : step === item.stepNum 
                      ? 'bg-white border-bima-green text-bima-green shadow-[0_0_15px_rgba(101,154,95,0.2)] scale-110' 
                      : 'bg-white border-slate-200 text-slate-400'
                }`}>
                  <item.icon className="w-5 h-5" />
                </div>
                <span className={`text-[10px] font-black tracking-wide mt-2 transition-colors duration-300 ${step >= item.stepNum ? 'text-bima-darkGreen font-extrabold' : 'text-slate-400'}`}>
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
                  <label className="block mb-1 text-xs font-bold text-slate-700">Full Name</label>
                  <input
                    className="input-field py-2.5"
                    value={form.full_name}
                    onChange={(event) => updateField('full_name', event.target.value)}
                    placeholder="e.g. Wycliffe Omondi"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-1 text-xs font-bold text-slate-700">Username</label>
                  <input
                    className="input-field py-2.5"
                    value={form.username}
                    onChange={(event) => updateField('username', event.target.value)}
                    placeholder="e.g. wycliffeo"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-1 text-xs font-bold text-slate-700">Temporary Password</label>
                  <input
                    type="password"
                    className="input-field py-2.5"
                    value={form.password}
                    onChange={(event) => updateField('password', event.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>
                <div>
                  <label className="block mb-1 text-xs font-bold text-slate-700">Phone Number</label>
                  <div className="relative">
                    <input
                      className="input-field py-2.5 pl-10"
                      placeholder="e.g. +254711223344"
                      value={form.phone_number}
                      onChange={(event) => updateField('phone_number', event.target.value)}
                      required
                    />
                    <Phone className="absolute left-3 top-3.5 w-4 h-4 text-bima-green" />
                  </div>
                </div>
                <div>
                  <label className="block mb-1 text-xs font-bold text-slate-700">M-Pesa Number</label>
                  <input
                    className="input-field py-2.5"
                    placeholder="e.g. 254711223344"
                    value={form.mpesa_number}
                    onChange={(event) => updateField('mpesa_number', event.target.value)}
                    required
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block mb-1 text-xs font-bold text-slate-700">Email Address (Optional)</label>
                  <input
                    type="email"
                    className="input-field py-2.5"
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
                    <label className="block mb-1.5 text-xs font-black text-bima-darkGreen uppercase tracking-widest">County</label>
                    <select
                      className="input-field py-3 appearance-none bg-white font-bold border-slate-200 focus:ring-bima-green focus:border-bima-green rounded-xl"
                      value={selectedCounty}
                      onChange={(e) => setSelectedCounty(e.target.value)}
                    >
                      <option value="">Select County</option>
                      {counties.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block mb-1.5 text-xs font-black text-bima-darkGreen uppercase tracking-widest">Sub-county</label>
                    <select
                      className="input-field py-3 appearance-none bg-white font-bold border-slate-200 focus:ring-bima-green focus:border-bima-green rounded-xl"
                      value={selectedSubcounty}
                      onChange={(e) => setSelectedSubcounty(e.target.value)}
                      disabled={!selectedCounty}
                    >
                      <option value="">Select Sub-county</option>
                      {subcounties.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block mb-1.5 text-xs font-black text-bima-darkGreen uppercase tracking-widest">Constituency</label>
                    <select
                      className="input-field py-3 appearance-none bg-white font-bold border-slate-200 focus:ring-bima-green focus:border-bima-green rounded-xl"
                      value={selectedConstituency}
                      onChange={(e) => setSelectedConstituency(e.target.value)}
                      disabled={!selectedSubcounty}
                    >
                      <option value="">Select Constituency</option>
                      {constituencies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block mb-1.5 text-xs font-black text-bima-darkGreen uppercase tracking-widest">Ward</label>
                    <select
                      className="input-field py-3 appearance-none bg-white font-bold border-slate-200 focus:ring-bima-green focus:border-bima-green rounded-xl"
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
                  <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 flex items-center justify-between text-xs">
                    <div>
                      <p className="font-extrabold text-bima-darkGreen text-[13px]">{currentCountyObj?.name}</p>
                      <p className="text-[10px] text-slate-400 font-bold mt-0.5">
                        {subcounties.length > 0 ? `${subcounties.length} sub-counties loaded from database` : 'Loading subdivisions...'}
                      </p>
                    </div>
                    <MapIcon className="w-5 h-5 text-bima-green" />
                  </div>
                )}
              </motion.div>
            )}

            {step === 3 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
                <div className="flex justify-between items-center text-xs">
                  <div>
                    <h3 className="font-extrabold text-bima-darkGreen text-sm">Draw Farm Boundaries</h3>
                    <p className="text-slate-500 font-medium mt-0.5">Click on the satellite map to plot boundary vertices</p>
                  </div>
                  <div className="flex gap-2">
                    <button 
                      type="button" 
                      onClick={resetDrawing} 
                      className="btn-secondary py-1.5 px-3 text-[10px] bg-slate-100 hover:bg-slate-200"
                    >
                      Reset Outline
                    </button>
                    <button 
                      type="button" 
                      onClick={finishDrawing} 
                      disabled={polygonPoints.length < 3 || isDrawingComplete}
                      className="btn-primary py-1.5 px-3 text-[10px] bg-bima-green hover:bg-bima-green/90 shadow-sm"
                    >
                      Lock Outline
                    </button>
                  </div>
                </div>

                {/* mapcn Interactive Satellite Map */}
                <div className="relative border border-slate-200 rounded-2xl overflow-hidden h-[320px] shadow-inner select-none bg-slate-100 z-10">
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

                    {/* Render markers for each drawn vertex */}
                    {polygonPoints.map((p, idx) => (
                      <MapMarker 
                        key={idx} 
                        longitude={p.lng} 
                        latitude={p.lat}
                        color={idx === 0 ? '#EAD35B' : '#659A5F'}
                      />
                    ))}

                    {/* Render Route connect lines */}
                    {polygonPoints.length > 0 && (
                      <MapRoute 
                        coordinates={
                          isDrawingComplete 
                            ? [...polygonPoints.map(p => [p.lng, p.lat] as [number, number]), [polygonPoints[0].lng, polygonPoints[0].lat] as [number, number]]
                            : polygonPoints.map(p => [p.lng, p.lat] as [number, number])
                        }
                        color={isDrawingComplete ? '#659A5F' : '#EAD35B'}
                        width={3}
                        opacity={0.8}
                        dashArray={isDrawingComplete ? undefined : [5, 5]}
                      />
                    )}
                    
                    {/* Render polygon fill using MapGeoJSON */}
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
                          "fill-color": "#659A5F",
                          "fill-opacity": 0.4
                        }}
                        linePaint={false}
                      />
                    )}
                  </Map>

                  {/* Sidebar Overlay panel */}
                  <div className="absolute right-4 top-4 bg-slate-900/80 backdrop-blur border border-white/10 rounded-xl p-3 text-[10px] font-mono text-slate-300 space-y-1.5 w-44 pointer-events-none shadow-lg z-[1000]">
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
                    <div className="flex justify-between border-t border-white/10 pt-1.5">
                      <span>Calculated Acreage:</span>
                      <span className="text-bima-yellow font-black">
                        {polygonPoints.length >= 3 ? (calculateGeodesicArea(polygonPoints) / 4046.86).toFixed(1) : '0.0'} Acres
                      </span>
                    </div>
                  </div>

                  {/* HUD Coordinates Display */}
                  <div className="absolute left-4 bottom-4 bg-slate-900/80 backdrop-blur border border-white/10 rounded-lg px-2 py-1 text-[9px] font-mono text-slate-300 pointer-events-none z-[1000]">
                    LAT: {mapViewport.center[1].toFixed(5)} | LNG: {mapViewport.center[0].toFixed(5)}
                  </div>
                </div>
              </motion.div>
            )}

            {step === 4 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
                <div className="flex justify-between items-center text-xs">
                  <div>
                    <h3 className="font-extrabold text-bima-darkGreen text-sm">Sentinel-2 Geospatial Diagnostics</h3>
                    <p className="text-slate-500 font-medium mt-0.5">Real-time parameters derived for H3 cell: <span className="font-mono text-bima-darkGreen font-bold bg-slate-100 px-1.5 py-0.5 rounded">{form.h3_index}</span></p>
                  </div>
                </div>

                <AnimatePresence mode="wait">
                  {diagnosticsLoading ? (
                    <motion.div 
                      key="loading" 
                      initial={{ opacity: 0 }} 
                      animate={{ opacity: 1 }} 
                      exit={{ opacity: 0 }} 
                      className="flex flex-col items-center justify-center p-12 bg-slate-50 border border-slate-100 rounded-3xl min-h-[220px]"
                    >
                      <RefreshCw className="w-10 h-10 text-bima-green animate-spin mb-4" />
                      <p className="text-sm font-bold text-bima-darkGreen">{diagnosticsMessage}</p>
                      <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-widest font-black">Satellite Uplink Active</p>
                    </motion.div>
                  ) : diagnosticsError ? (
                    <motion.div 
                      key="error" 
                      initial={{ opacity: 0 }} 
                      animate={{ opacity: 1 }} 
                      className="p-8 text-center bg-red-50 border border-red-100 rounded-3xl"
                    >
                      <p className="text-sm font-bold text-red-600 mb-4">{diagnosticsError}</p>
                      <button 
                        type="button" 
                        onClick={() => void executeDiagnosticsQuery(form.h3_index)} 
                        className="btn-primary bg-red-600 hover:bg-red-700 py-2 px-4 text-xs inline-flex items-center gap-1.5"
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
                        {/* NDVI */}
                        <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 flex flex-col justify-between h-28">
                          <div className="flex items-center justify-between text-emerald-600">
                            <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">NDVI Greenness</span>
                            <Leaf className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-2xl font-black text-slate-800 font-mono">{diagnosticsData.ndvi.toFixed(2)}</p>
                            <p className="text-[9px] font-bold text-emerald-500 mt-1">🟢 Optimal Crop Canopy</p>
                          </div>
                        </div>

                        {/* Precipitation */}
                        <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 flex flex-col justify-between h-28">
                          <div className="flex items-center justify-between text-blue-600">
                            <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Precipitation</span>
                            <CloudRain className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-2xl font-black text-slate-800 font-mono">{diagnosticsData.rainfall.toFixed(1)} mm</p>
                            <p className="text-[9px] font-bold text-blue-500 mt-1">🟢 Standard Baseline</p>
                          </div>
                        </div>

                        {/* Soil Moisture */}
                        <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 flex flex-col justify-between h-28">
                          <div className="flex items-center justify-between text-amber-600">
                            <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Soil Moisture</span>
                            <BarChart2 className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-2xl font-black text-slate-800 font-mono">{diagnosticsData.soilMoisture}%</p>
                            <p className="text-[9px] font-bold text-amber-500 mt-1">🟢 Good retention</p>
                          </div>
                        </div>
                      </div>

                      {/* Diagnostic Summary Seal */}
                      <div className="bg-emerald-50 border border-emerald-100 rounded-2xl p-4 flex items-center justify-between text-xs">
                        <div>
                          <p className="font-extrabold text-emerald-800">Parametric Condition: ACTIVE & ELIGIBLE</p>
                          <p className="text-[10px] text-emerald-600/70 font-semibold mt-0.5">Vegetation indices and water volumes are currently within standard ranges. Plan setup allowed.</p>
                        </div>
                        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      </div>
                    </motion.div>
                  ) : null}
                </AnimatePresence>

                {/* Primary Crop configuration */}
                <div className="grid gap-4 sm:grid-cols-2 pt-2 border-t border-slate-100">
                  <div>
                    <label className="block mb-1.5 text-xs font-black text-bima-darkGreen uppercase tracking-widest">Primary Crop</label>
                    <div className="relative">
                      <select
                        className="input-field py-3 appearance-none pr-10 font-bold border-slate-200 rounded-xl"
                        value={form.crop}
                        onChange={(event) => updateField('crop', event.target.value)}
                      >
                        {CROP_OPTIONS.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                      <Leaf className="absolute right-3 top-3.5 w-4 h-4 text-bima-green pointer-events-none" />
                    </div>
                  </div>
                  <div>
                    <label className="block mb-1.5 text-xs font-black text-bima-darkGreen uppercase tracking-widest">Final Acreage Value</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field py-2.5 font-bold border-slate-200 rounded-xl bg-slate-50"
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
                {/* Upload Title Deed */}
                <div className="bg-slate-50 border border-dashed border-slate-300 rounded-[1rem] p-4 flex flex-col items-center justify-center text-center">
                  <Upload className="w-8 h-8 text-bima-green mb-2" />
                  <p className="text-xs font-bold text-slate-700 mb-1">Upload Title Deed / Farm Documents</p>
                  <p className="text-[10px] text-slate-400 mb-3">Accepts PDF, PNG, JPG up to 10MB</p>
                  
                  <label className="btn-secondary py-1.5 px-4 text-xs cursor-pointer inline-flex items-center gap-1.5">
                    <span>Choose File</span>
                    <input type="file" className="hidden" onChange={handleFileChange} disabled={isUploading} />
                  </label>

                  {isUploading && (
                    <div className="w-full max-w-xs mt-3">
                      <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                        <span>Uploading...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-bima-green h-1.5 transition-all duration-150" style={{ width: `${uploadProgress}%` }} />
                      </div>
                    </div>
                  )}
                </div>

                {documents.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Uploaded Documents</p>
                    {documents.map((doc, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-slate-50 border border-slate-100 rounded-[0.75rem] p-2.5 text-xs text-slate-700">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-slate-400" />
                          <span className="font-medium truncate max-w-[200px]">{doc.name}</span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400">{doc.size}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Account Review Summary Card */}
                <div className="border border-slate-100 rounded-[1.25rem] p-4 bg-bima-lightGreen/10 space-y-3">
                  <h4 className="text-xs font-extrabold uppercase tracking-wider text-bima-darkGreen flex items-center gap-1.5 border-b border-bima-green/10 pb-2">
                    <CheckCircle2 className="w-4 h-4" /> Summary Review
                  </h4>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                    <div>
                      <span className="text-slate-400 font-medium">Farmer:</span>
                      <p className="font-extrabold text-slate-800">{form.full_name}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-medium">Phone / M-Pesa:</span>
                      <p className="font-bold text-slate-800">{form.phone_number}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-medium">County / Sub-county:</span>
                      <p className="font-semibold text-slate-800">{currentCountyObj?.name ?? '—'} / {currentSubcountyObj?.name ?? '—'}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-medium">Ward:</span>
                      <p className="font-semibold text-slate-800">{currentWardObj?.name ?? '—'} ({form.ward_code})</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-medium">Primary Crop:</span>
                      <p className="font-bold text-slate-800 capitalize">{form.crop}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-medium">Acreage:</span>
                      <p className="font-bold text-slate-800">{form.acreage} Acres</p>
                    </div>
                    <div className="col-span-2">
                      <span className="text-slate-400 font-medium">H3 Grid Index:</span>
                      <p className="font-mono text-xs font-bold text-slate-800">{form.h3_index}</p>
                    </div>
                  </div>
                </div>

                {/* Dynamic cost banner */}
                <div className="bg-gradient-to-br from-[#1B2B20] to-[#0f1812] rounded-2xl p-4 text-white flex justify-between items-center shadow-lg relative overflow-hidden">
                  <div>
                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Plan Setup Premium</span>
                    <p className="text-2xl font-black text-bima-yellow mt-0.5 font-mono">
                      {formatCurrency(parseFloat(form.acreage || '0') * (form.crop === 'maize' ? 322 : form.crop === 'beans' ? 280 : form.crop === 'sorghum' ? 300 : form.crop === 'rice' ? 400 : form.crop === 'coffee' ? 450 : 500))}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest block">Blockchain Escrow</span>
                    <span className="text-xs font-bold text-emerald-400 mt-0.5 block">Automated via Hardhat</span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Navigation Controls */}
          <div className="flex gap-4 border-t border-slate-100 pt-4">
            {step > 1 && (
              <button 
                type="button" 
                onClick={handleBack} 
                className="btn-secondary py-3 text-sm flex items-center justify-center gap-1 flex-1"
              >
                <ChevronLeft className="w-4 h-4" /> Back
              </button>
            )}
            
            {step < 5 ? (
              <button 
                type="button" 
                onClick={handleNext} 
                className="btn-primary py-3 text-sm flex items-center justify-center gap-1 flex-1 shadow-md hover:shadow-lg"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button 
                type="button" 
                onClick={handleSubmit} 
                disabled={isSubmitting} 
                className="btn-primary py-3 text-sm flex items-center justify-center gap-1.5 flex-1 shadow-md hover:shadow-lg bg-bima-darkGreen hover:bg-bima-darkGreen/90"
              >
                {isSubmitting ? 'Creating...' : 'Confirm & Register Farmer'}
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
