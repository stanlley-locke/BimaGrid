import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { 
  ArrowUpRight, 
  ArrowDown,
  Play,
  Check, 
  Tractor, 
  Leaf, 
  Sprout, 
  Sun,
  ShieldCheck,
  CloudRain,
  Share2,
  ChevronLeft,
  ChevronRight,
  Phone,
  Mail,
  FileText
} from 'lucide-react';

const socialIcons = [
  {
    label: 'Facebook',
    svg: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd" />
      </svg>
    )
  },
  {
    label: 'X (Twitter)',
    svg: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
      </svg>
    )
  },
  {
    label: 'LinkedIn',
    svg: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path fillRule="evenodd" d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" clipRule="evenodd" />
      </svg>
    )
  },
  {
    label: 'Instagram',
    svg: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path fillRule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.46 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clipRule="evenodd" />
      </svg>
    )
  }
];

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="bg-white min-h-screen">
      {/* Hero Section */}
      <section className="pt-4 px-4 sm:pt-6 sm:px-6 lg:pt-8 lg:px-8 pb-10">
        <div className="relative h-[95vh] min-h-[750px] w-full bg-[#1B2B20] overflow-hidden rounded-[2.5rem] sm:rounded-[3rem]">
          {/* Background Image Overlay */}
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-70"
            style={{ backgroundImage: "url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2000&auto=format&fit=crop')" }}
          />
          
          <div className="absolute inset-0 bg-gradient-to-r from-[#1B2B20]/90 via-[#1B2B20]/60 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#1B2B20]/90 via-transparent to-transparent" />

          <div className="relative z-10 mx-auto flex h-full max-w-[1400px] flex-col justify-center px-8 lg:px-16">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="max-w-3xl"
            >
              <div className="mb-6 inline-flex rounded-full border border-white/30 px-5 py-1.5 backdrop-blur-sm">
                <span className="text-[10px] font-bold tracking-widest text-white uppercase">
                  BELIEVE IN QUALITY!
                </span>
              </div>
              
              <h1 className="text-6xl font-bold tracking-tight text-white sm:text-7xl lg:text-[5.5rem] leading-[1.05] mb-8 font-sans">
                Quality Trust: <br />
                Direct to the Farm
              </h1>
              
              <p className="text-lg text-slate-300 mb-10 max-w-xl font-medium leading-relaxed">
                We all need a little space to grow. Give yourself the space you need to find your inner peace and protect what matters most.
              </p>
              
              <div className="flex flex-wrap gap-4">
                {isAuthenticated ? (
                  <Link to="/dashboard" className="inline-flex items-center justify-center rounded-full bg-white px-8 py-4 text-sm font-bold text-[#1B2B20] hover:bg-slate-100 transition-colors gap-2 group">
                    Go to Dashboard <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </Link>
                ) : (
                  <Link to="/register" className="inline-flex items-center justify-center rounded-full bg-white px-8 py-4 text-sm font-bold text-[#1B2B20] hover:bg-slate-100 transition-colors gap-2 group">
                    Contact Us <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </Link>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Committed to Caring Section */}
      <section className="py-20 relative overflow-hidden bg-[#EAD35B]">
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: "url('data:image/svg+xml,%3Csvg width=\\'60\\' height=\\'60\\' viewBox=\\'0 0 60 60\\' xmlns=\\'http://www.w3.org/2000/svg\\'%3E%3Cpath d=\\'M54.627 0l.83.83-53.797 53.797-.83-.83L54.627 0zM29.186 0l.83.83-28.356 28.356-.83-.83L29.186 0zM0 29.186l.83.83-28.356 28.356-.83-.83L0 29.186z\\' fill=\\'%231B2B20\\' fill-opacity=\\'1\\' fill-rule=\\'evenodd\\'/%3E%3C/svg%3E')" }}></div>
        
        <div className="mx-auto max-w-[1400px] px-6 lg:px-8 relative z-10">
          
          {/* Top Header Row */}
          <div className="hidden lg:flex flex-row items-center justify-between mb-12 px-2">
            {/* Left */}
            <div className="flex items-center gap-4">
              <div className="flex -space-x-3">
                <img src="https://i.pravatar.cc/100?img=11" alt="avatar" className="w-11 h-11 rounded-full border-[3px] border-[#EAD35B] shadow-sm relative z-30" />
                <img src="https://i.pravatar.cc/100?img=32" alt="avatar" className="w-11 h-11 rounded-full border-[3px] border-[#EAD35B] shadow-sm relative z-20" />
                <img src="https://i.pravatar.cc/100?img=12" alt="avatar" className="w-11 h-11 rounded-full border-[3px] border-[#EAD35B] shadow-sm relative z-10" />
              </div>
              <div className="text-[#1B2B20] text-[15px] font-semibold leading-snug">
                <p>Any questions? Reach us at</p>
                <p><span className="border-b-2 border-[#1B2B20] font-bold">+254 800 722 000</span> - Toll free</p>
              </div>
            </div>

            {/* Center */}
            <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-sm hover:-translate-y-1 transition-transform cursor-pointer">
              <ArrowDown className="w-7 h-7 text-[#1B2B20]" strokeWidth={1.5} />
            </div>

            {/* Right */}
            <div className="flex items-center gap-5 text-right">
              <p className="text-[#1B2B20] font-bold text-[16px] leading-snug max-w-[200px]">
                Protecting Kenya's Staple Food Supply
              </p>
              <div className="relative w-[150px] h-[80px] rounded-[1.25rem] overflow-hidden shadow-sm group cursor-pointer">
                <img src="/images/kenya_maize_farm_1783596979799.png" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" alt="Tractor" />
                <div className="absolute inset-0 flex items-center justify-center bg-black/10 group-hover:bg-black/20 transition-colors">
                  <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md">
                     <Play className="w-4 h-4 text-[#EAD35B] ml-1" fill="currentColor" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center bg-white rounded-[3rem] p-8 lg:p-14 shadow-lg border border-white/50">
            
            {/* Left Image */}
            <div className="relative rounded-[2.5rem] overflow-hidden h-[500px] lg:h-[650px] w-full bg-slate-100">
              <img 
                src="/images/kenya_male_farmer_1783597008593.png" 
                alt="Kenyan Farmer" 
                className="absolute inset-0 w-full h-full object-cover"
              />
            </div>
            
            {/* Right Content */}
            <div className="flex flex-col justify-center">
              <div className="mb-10 rounded-[1.5rem] overflow-hidden h-48 w-full">
                <img 
                  src="/images/kenya_maize_farm_1783596979799.png" 
                  alt="Maize Farm field" 
                  className="w-full h-full object-cover"
                />
              </div>

              <h2 className="text-4xl lg:text-5xl font-bold text-[#1B2B20] mb-5 leading-tight tracking-tight">We're Committed to Caring.</h2>
              <p className="text-slate-500 mb-10 leading-relaxed text-[15px] lg:text-[16px] font-medium max-w-lg">
                Greetings from BimaGrid. We distribute reliable micro-insurance policies directly to Kenyan farmers, ensuring your staple crops are always protected against unpredictable weather.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-8 mb-12">
                {[
                  "Maize & Wheat Protection", "Fast USSD Claim Processing",
                  "Beans & Legumes Coverage", "Drought & Flood Insurance",
                  "Affordable Premium Plans", "Direct Mobile Payouts"
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full bg-[#EAD35B] flex items-center justify-center shrink-0 shadow-sm">
                      <Check className="w-3.5 h-3.5 text-white stroke-[4]" />
                    </div>
                    <span className="font-bold text-slate-700 text-[13px] lg:text-[14px]">{item}</span>
                  </div>
                ))}
              </div>

              <div>
                <Link to="/login" className="inline-flex items-center justify-center rounded-full bg-[#659A5F] px-8 py-3.5 text-[14px] font-bold text-white hover:bg-[#537e4e] transition-colors gap-2 shadow-sm group">
                  Know More <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </Link>
              </div>
            </div>
            
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-20 bg-[#F4F1ED] relative overflow-hidden">
        {/* Subtle Background Pattern to make it less dry */}
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "url('data:image/svg+xml,%3Csvg width=\\'60\\' height=\\'60\\' viewBox=\\'0 0 60 60\\' xmlns=\\'http://www.w3.org/2000/svg\\'%3E%3Cg fill=\\'none\\' fill-rule=\\'evenodd\\'%3E%3Cg fill=\\'%231B2B20\\' fill-opacity=\\'1\\'%3E%3Cpath d=\\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')" }}></div>

        <style>{`
          @keyframes marquee {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
          }
          .animate-marquee {
            animation: marquee 30s linear infinite;
            display: flex;
            width: max-content;
          }
        `}</style>

        {/* Marquee Banner */}
        <div className="w-full overflow-hidden py-10 mb-10 flex border-y border-[#1B2B20]/5 relative z-10">
          <div className="animate-marquee items-center gap-10 text-6xl lg:text-8xl font-black text-transparent" style={{ WebkitTextStroke: '1.5px #A0B3A6' }}>
            <span>MAIZE</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>WHEAT</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>LIVESTOCK</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>DROUGHT</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>FLOOD</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>PAYOUTS</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            {/* Repeat for seamless loop */}
            <span>MAIZE</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>WHEAT</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>LIVESTOCK</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>DROUGHT</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>FLOOD</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
            <span>PAYOUTS</span> <span className="text-[#659A5F]" style={{ WebkitTextStroke: '0' }}>*</span>
          </div>
        </div>

        <div className="mx-auto max-w-[1400px] px-6 lg:px-8 relative z-10">
          
          {/* Header */}
          <div className="flex flex-col items-center mb-16">
            <div className="bg-white px-5 py-2.5 rounded-full shadow-sm flex items-center gap-2.5 mb-6 border border-[#1B2B20]/5">
              <Leaf className="w-4 h-4 text-[#659A5F]" />
              <span className="text-[11px] font-extrabold text-[#1B2B20] uppercase tracking-wider">Our Service</span>
            </div>
            <h2 className="text-4xl lg:text-[2.75rem] font-extrabold text-[#1B2B20] text-center tracking-tight">Comprehensive Coverage Plans</h2>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            
            {[
              { cat: "STAPLE CROPS", title: "Maize Protection", img: "/images/kenya_maize_farm_1783596979799.png" },
              { cat: "WEATHER", title: "Drought Insurance", img: "/images/kenya_farmer_smartphone_1783596990052.png" },
              { cat: "LIVESTOCK", title: "Cattle & Goat Cover", img: "/images/kenya_cattle_goats_1783596999559.png" },
              { cat: "PAYOUTS", title: "Direct Mobile Money", img: "/images/kenya_female_agent_1783597018347.png" }
            ].map((card, i) => (
              <div key={i} className="bg-white rounded-[2rem] p-6 pb-10 flex flex-col items-center relative group shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer border border-[#1B2B20]/5">
                
                {/* The Cutout Corner */}
                <div className="absolute top-0 right-0 w-[4.5rem] h-[4.5rem] bg-[#F4F1ED] rounded-bl-[1.5rem] z-10 flex items-center justify-center">
                   {/* The yellow button */}
                   <div className="w-10 h-10 rounded-full bg-[#EAD35B] flex items-center justify-center shadow-sm hover:bg-[#d8c045] transition-colors relative z-20 translate-x-1 -translate-y-1">
                     <ArrowUpRight className="w-4 h-4 text-[#1B2B20]" />
                   </div>

                   {/* Inner curves for smooth blend */}
                   <div className="absolute top-0 -left-4 w-4 h-4 bg-transparent rounded-tr-xl shadow-[8px_-8px_0_8px_#F4F1ED]"></div>
                   <div className="absolute -bottom-4 right-0 w-4 h-4 bg-transparent rounded-tr-xl shadow-[8px_-8px_0_8px_#F4F1ED]"></div>
                </div>

                {/* Card Content */}
                <div className="w-48 h-48 sm:w-56 sm:h-56 rounded-full overflow-hidden border-[8px] border-[#659A5F] mb-6 mt-4 relative">
                  <img src={card.img} alt={card.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
                </div>
                
                <div className="flex items-center gap-2 mb-3 text-[#659A5F] font-bold text-[11px] tracking-wider uppercase">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#659A5F]"></span>
                  {card.cat}
                </div>
                
                <h3 className="text-[#1B2B20] font-extrabold text-[1.3rem] mb-2 text-center group-hover:text-[#659A5F] transition-colors">{card.title}</h3>

              </div>
            ))}
            
          </div>
          
          {/* Pagination Dots */}
          <div className="flex justify-center items-center gap-3 mt-16">
            <div className="w-3 h-3 rounded-full bg-[#EAD35B]"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-[#1B2B20]/20 hover:bg-[#1B2B20]/40 cursor-pointer transition-colors"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-[#1B2B20]/20 hover:bg-[#1B2B20]/40 cursor-pointer transition-colors"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-[#1B2B20]/20 hover:bg-[#1B2B20]/40 cursor-pointer transition-colors"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-[#1B2B20]/20 hover:bg-[#1B2B20]/40 cursor-pointer transition-colors"></div>
          </div>
        </div>
      </section>

      {/* 6 Grid Plans Section */}
      <section className="py-24 bg-[#F4F1ED]">
        <div className="mx-auto max-w-[1400px] px-6 lg:px-8">
          
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-[3rem] font-extrabold text-[#1B2B20] max-w-2xl mx-auto leading-tight tracking-tight">
              Flexible Plans For Every Type Of Farmer
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {[
              { title: "Maize &\nStaples", icon: Sprout, desc: "Comprehensive cover for staple crops like maize and wheat against unpredictable weather and severe droughts." },
              { title: "Commercial\nFarming", icon: Tractor, desc: "Large-scale protection plans designed specifically for commercial agriculture and high-yield farming operations." },
              { title: "Cash Crop\nHorticulture", icon: Leaf, desc: "Specialized insurance for high-value cash crops, fresh vegetables, and delicate export-quality produce." },
              { title: "Dairy &\nLivestock", icon: ShieldCheck, desc: "Protect your valuable herds with comprehensive mortality and veterinary cover for cattle, goats, and sheep." },
              { title: "Equipment\nCover", icon: Sun, desc: "Safeguard your essential farming machinery, tractors, and irrigation systems from damage and theft." },
              { title: "Weather\nIndex", icon: CloudRain, desc: "Automatic payouts triggered instantly by satellite weather data without the need for manual claims or farm visits." }
            ].map((plan, i) => (
              <div key={i} className={`rounded-[2rem] p-8 lg:p-10 transition-all duration-300 cursor-pointer border ${i === 1 ? 'bg-white shadow-xl border-white' : 'bg-transparent border-[#1B2B20]/10 hover:bg-white hover:shadow-xl hover:border-white'}`}>
                
                <div className="flex items-start justify-between mb-8">
                  <h3 className="text-2xl font-extrabold text-[#1B2B20] whitespace-pre-line leading-tight">
                    {plan.title}
                  </h3>
                  <div className="w-14 h-14 rounded-full bg-[#EAD35B] flex items-center justify-center shrink-0 shadow-sm transition-transform hover:scale-110">
                    <plan.icon className="w-6 h-6 text-[#1B2B20]" strokeWidth={1.5} />
                  </div>
                </div>

                <div className="w-full h-px bg-[#1B2B20]/10 mb-8"></div>

                <p className="text-slate-500 font-medium leading-relaxed text-[15px]">
                  {plan.desc}
                </p>

              </div>
            ))}
          </div>

        </div>
      </section>
      {/* Meet the Farmers / Agents Section */}
      <section className="py-20 bg-[#F4F1ED]">
        <div className="mx-auto max-w-[1400px] px-6 lg:px-8">
          
          {/* Top Banner Image */}
          <div className="w-full h-64 lg:h-80 rounded-[3rem] relative overflow-hidden mb-16 shadow-sm">
            <img src="/images/kenya_maize_farm_1783596979799.png" alt="Green wheat field" className="absolute inset-0 w-full h-full object-cover" />
            <div className="absolute inset-0 bg-black/40"></div>
            <div className="absolute inset-0 flex flex-col md:flex-row items-center justify-between p-8 lg:p-16">
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 lg:w-20 lg:h-20 rounded-full bg-[#EAD35B] flex items-center justify-center shrink-0 shadow-lg">
                  <Leaf className="w-8 h-8 text-[#1B2B20]" />
                </div>
                <h2 className="text-3xl lg:text-[2.5rem] font-bold text-white max-w-xl leading-tight">
                  Empowering agricultural communities across Kenya
                </h2>
              </div>
              <button className="bg-white rounded-full px-8 py-4 font-bold text-[14px] text-[#1B2B20] hover:bg-[#EAD35B] transition-colors flex items-center gap-2 mt-6 md:mt-0 shadow-lg group">
                Discover More <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </button>
            </div>
          </div>

          {/* Header Row */}
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
            <div>
              <div className="bg-white px-5 py-2.5 rounded-full shadow-sm flex items-center gap-2.5 mb-6 border border-[#1B2B20]/5 inline-flex">
                <Leaf className="w-4 h-4 text-[#659A5F]" />
                <span className="text-[11px] font-extrabold text-[#1B2B20] uppercase tracking-wider">Our Network</span>
              </div>
              <h2 className="text-4xl lg:text-[2.75rem] font-extrabold text-[#1B2B20] tracking-tight">Meet the Farmers</h2>
            </div>
            <div className="flex gap-4 mt-6 md:mt-0">
              <button className="w-12 h-12 rounded-full border border-slate-300 flex items-center justify-center hover:bg-[#1B2B20] hover:text-white hover:border-[#1B2B20] transition-colors bg-white">
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button className="w-12 h-12 rounded-full border border-slate-300 flex items-center justify-center hover:bg-[#1B2B20] hover:text-white hover:border-[#1B2B20] transition-colors bg-white">
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Farmers Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            {[
              { role: "MAIZE FARMER", name: "David Ochieng", img: "/images/kenya_male_farmer_1783597008593.png" },
              { role: "M-PESA AGENT", name: "Grace Wanjiku", img: "/images/kenya_female_agent_1783597018347.png" },
              { role: "AGRONOMIST", name: "Peter Kamau", img: "/images/kenya_farmer_smartphone_1783596990052.png" },
              { role: "COMMUNITY LEADER", name: "Sarah Njoroge", img: "/images/kenya_female_agent_1783597018347.png" }
            ].map((farmer, i) => (
              <div key={i} className="group cursor-pointer">
                <div className="w-full h-80 rounded-[2rem] overflow-hidden mb-5 relative">
                  <img src={farmer.img} alt={farmer.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 bg-slate-200" />
                  <div className="absolute bottom-4 right-4 w-10 h-10 rounded-full bg-[#EAD35B] flex items-center justify-center shadow-md translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
                    <Share2 className="w-4 h-4 text-[#1B2B20]" />
                  </div>
                </div>
                <div className="flex items-center gap-2 mb-2 text-[#659A5F] font-bold text-[11px] tracking-wider uppercase">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#659A5F]"></span>
                  {farmer.role}
                </div>
                <h3 className="text-xl font-extrabold text-[#1B2B20]">{farmer.name}</h3>
              </div>
            ))}
          </div>

          <div className="w-full h-px bg-[#1B2B20]/10 mt-24 mb-16"></div>

          {/* Partner Logos */}
          <div className="flex flex-wrap items-center justify-between gap-8 opacity-40 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-500 pb-10">
            <span className="text-2xl font-black font-serif">AGRA</span>
            <span className="text-3xl font-black tracking-tighter">KALRO</span>
            <span className="text-2xl font-extrabold flex items-center gap-1"><Leaf className="w-6 h-6"/> Safaricom</span>
            <span className="text-xl font-black border-2 border-black px-2 py-1">ONE ACRE FUND</span>
            <span className="text-2xl font-black tracking-wider">KENYA SEED</span>
            <span className="text-2xl font-bold italic">FSD Kenya</span>
          </div>

        </div>
      </section>

      {/* Free Quote Section */}
      <section className="py-20 bg-[#F4F1ED]">
        <div className="mx-auto max-w-[1400px] px-6 lg:px-8">
          <div className="bg-white rounded-[3rem] p-8 lg:p-16 shadow-sm border border-[#1B2B20]/5 flex flex-col lg:flex-row gap-16 items-center relative overflow-hidden">
            
            {/* Left Image */}
            <div className="w-full lg:w-5/12 relative h-[500px] lg:h-[600px] rounded-[2.5rem] overflow-hidden bg-slate-100 z-10">
              <img src="/images/kenya_male_farmer_1783597008593.png" alt="Farmer holding crops" className="w-full h-full object-cover" />
              <div className="absolute top-12 -right-6 lg:-right-8 w-32 h-32 rounded-full bg-[#EAD35B] flex flex-col items-center justify-center shadow-xl z-20 hidden sm:flex">
                <Tractor className="w-8 h-8 text-[#1B2B20] mb-1" strokeWidth={1.5} />
                <span className="text-[11px] font-extrabold text-[#1B2B20] text-center leading-tight">Founded in<br/>2024</span>
                <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-[#EAD35B] rotate-45"></div>
              </div>
            </div>

            {/* Right Form */}
            <div className="w-full lg:w-7/12 z-10">
              <div className="bg-[#F4F1ED] px-5 py-2.5 rounded-full shadow-sm flex items-center gap-2.5 mb-6 inline-flex border border-[#1B2B20]/5">
                <FileText className="w-4 h-4 text-[#659A5F]" />
                <span className="text-[11px] font-extrabold text-[#1B2B20] uppercase tracking-wider">Free Quote</span>
              </div>
              <h2 className="text-4xl lg:text-[2.75rem] font-extrabold text-[#1B2B20] tracking-tight mb-10">Get a free quote</h2>
              
              <form className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <input type="text" placeholder="Your Name" className="w-full bg-[#F4F1ED] rounded-[1.25rem] px-6 py-4 outline-none focus:ring-2 focus:ring-[#659A5F]/50 transition-shadow text-[15px] font-medium" />
                  <input type="text" placeholder="Phone Number" className="w-full bg-[#F4F1ED] rounded-[1.25rem] px-6 py-4 outline-none focus:ring-2 focus:ring-[#659A5F]/50 transition-shadow text-[15px] font-medium" />
                  <input type="email" placeholder="Email Address" className="w-full bg-[#F4F1ED] rounded-[1.25rem] px-6 py-4 outline-none focus:ring-2 focus:ring-[#659A5F]/50 transition-shadow text-[15px] font-medium" />
                  <input type="text" placeholder="Subject" className="w-full bg-[#F4F1ED] rounded-[1.25rem] px-6 py-4 outline-none focus:ring-2 focus:ring-[#659A5F]/50 transition-shadow text-[15px] font-medium" />
                </div>
                <textarea placeholder="Write a message" rows={5} className="w-full bg-[#F4F1ED] rounded-[1.25rem] px-6 py-4 outline-none focus:ring-2 focus:ring-[#659A5F]/50 transition-shadow text-[15px] font-medium resize-none"></textarea>
                <button type="button" className="bg-[#659A5F] hover:bg-[#537e4e] text-white font-bold py-4 px-10 rounded-full transition-colors flex items-center gap-2 group shadow-sm mt-4">
                  Send Message <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </button>
              </form>
            </div>

          </div>
        </div>
      </section>

      {/* Latest Posts */}
      <section className="py-24 bg-[#F4F1ED]">
        <div className="mx-auto max-w-[1400px] px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
            <h2 className="text-4xl lg:text-[2.75rem] font-extrabold text-[#1B2B20] tracking-tight">Latest posts & articles</h2>
            <div className="flex gap-4 mt-6 md:mt-0">
              <button className="w-12 h-12 rounded-full border border-slate-300 flex items-center justify-center hover:bg-[#1B2B20] hover:text-white hover:border-[#1B2B20] transition-colors bg-white">
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button className="w-12 h-12 rounded-full border border-slate-300 flex items-center justify-center hover:bg-[#1B2B20] hover:text-white hover:border-[#1B2B20] transition-colors bg-white">
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { tag: "FOOD CROPS", date: "MARCH 28, 2024", author: "ADMIN", title: "How technology is transforming Kenyan agriculture", img: "/images/kenya_farmer_smartphone_1783596990052.png" },
              { tag: "ORGANIC FARM", date: "APRIL 02, 2024", author: "ADMIN", title: "Why drought insurance is essential for maize farmers", img: "/images/kenya_maize_farm_1783596979799.png" },
              { tag: "FARMING TIPS", date: "APRIL 15, 2024", author: "ADMIN", title: "Preparing your livestock for the upcoming dry season", img: "/images/kenya_cattle_goats_1783596999559.png" }
            ].map((post, i) => (
              <div key={i} className="group cursor-pointer">
                <div className="w-full h-72 rounded-[2rem] overflow-hidden mb-6 relative">
                  <img src={post.img} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 bg-slate-200" />
                  <div className="absolute top-5 left-5 bg-white/95 backdrop-blur-sm rounded-full px-4 py-2 text-[10px] font-extrabold text-[#659A5F] uppercase tracking-wider shadow-sm">
                    {post.tag}
                  </div>
                  <div className="absolute bottom-5 right-5 w-12 h-12 rounded-full bg-[#EAD35B] flex items-center justify-center shadow-md translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
                    <ArrowUpRight className="w-5 h-5 text-[#1B2B20]" />
                  </div>
                </div>
                <div className="flex items-center gap-4 text-slate-500 font-bold text-[10px] tracking-widest mb-3 uppercase">
                  <span className="flex items-center gap-1.5"><Sun className="w-3.5 h-3.5 text-[#659A5F]" /> {post.date}</span>
                  <span className="flex items-center gap-1.5"><Leaf className="w-3.5 h-3.5 text-[#659A5F]" /> {post.author}</span>
                </div>
                <h3 className="text-[1.4rem] font-extrabold text-[#1B2B20] leading-snug group-hover:text-[#659A5F] transition-colors">{post.title}</h3>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Yellow Footer Banner */}
      <section className="bg-[#EAD35B] py-12 border-b border-[#1B2B20]/5">
        <div className="mx-auto max-w-[1400px] px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex flex-wrap items-center gap-5 text-[#1B2B20] font-black text-[13px] tracking-widest uppercase">
            <span>FARMERS</span> <span className="text-white/60 text-lg">•</span>
            <span>ORGANIC</span> <span className="text-white/60 text-lg">•</span>
            <span>FOODS</span> <span className="text-white/60 text-lg">•</span>
            <span>PRODUCT</span>
          </div>
          <div className="flex flex-wrap items-center gap-8">
            <div className="flex items-center gap-3 text-[#1B2B20] font-extrabold text-sm tracking-wide">
              <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-sm">
                <Phone className="w-4 h-4" strokeWidth={2} />
              </div>
              +254 800 722 000
            </div>
            <div className="flex items-center gap-3 text-[#1B2B20] font-extrabold text-sm tracking-wide">
              <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-sm">
                <Mail className="w-4 h-4" strokeWidth={2} />
              </div>
              hello@bimagrid.com
            </div>
          </div>
        </div>
      </section>

      <footer 
        className="bg-white pt-24 relative overflow-hidden"
        style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='3' cy='3' r='2' fill='%231B2B20' fill-opacity='0.15'/%3E%3C/svg%3E\")" }}
      >
        {/* Subtle decorative leaf in background */}
        <div className="absolute -bottom-20 left-1/4 opacity-[0.03] pointer-events-none">
          <Leaf className="w-96 h-96 text-[#1B2B20] -rotate-12" />
        </div>

        <div className="mx-auto max-w-[1400px] px-6 lg:px-8 relative z-10 pb-20">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-20 gap-8">
            <div className="flex flex-col">
              <div className="flex items-center gap-3 mb-6">
                <img src="/bimagrid_logo.png" alt="BimaGrid Logo" className="h-12 w-12 rounded-[1rem] object-cover border border-[#1B2B20]/10" />
                <span className="text-[2rem] font-extrabold tracking-tight text-[#1B2B20] font-sans">bimagrid</span>
              </div>
              <p className="text-slate-500 text-[15px] leading-relaxed font-medium max-w-sm">
                Distributing reliable insurance policies directly to Kenyan farmers. Ensuring that when the weather turns bad, you are always protected.
              </p>
              
              <div className="flex items-center gap-3 mt-8">
                {socialIcons.map(social => (
                  <div key={social.label} aria-label={social.label} className="w-10 h-10 rounded-full bg-[#F4F1ED] flex items-center justify-center hover:bg-[#659A5F] hover:text-white transition-colors cursor-pointer text-[#659A5F]">
                    {social.svg}
                  </div>
                ))}
              </div>
            </div>

            <h2 className="text-3xl lg:text-[2.25rem] font-extrabold text-[#1B2B20] max-w-lg leading-tight tracking-tight">
              Empowering farmers across East Africa with reliable crop protection and climate resilience.
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-12 lg:gap-16 mb-20">
            {/* Empty col for spacing matching the logo side */}
            <div className="hidden md:block"></div>

            {/* Links Col 1 */}
            <div>
              <h4 className="text-[17px] font-extrabold text-[#1B2B20] mb-8">Useful Link</h4>
              <ul className="space-y-4">
                <li><Link to="#" className="text-slate-500 hover:text-[#659A5F] text-[15px] font-medium transition-colors">Company</Link></li>
                <li><Link to="#" className="text-slate-500 hover:text-[#659A5F] text-[15px] font-medium transition-colors">About</Link></li>
                <li><Link to="#" className="text-slate-500 hover:text-[#659A5F] text-[15px] font-medium transition-colors">Contact</Link></li>
              </ul>
            </div>

            {/* Links Col 2 */}
            <div>
              <h4 className="text-[17px] font-extrabold text-[#1B2B20] mb-8">Working Time</h4>
              <ul className="space-y-4">
                <li className="text-slate-500 text-[15px] font-medium">Mon - Fri: 9.00am - 5.00pm</li>
                <li className="text-slate-500 text-[15px] font-medium">Saturday: 10.00am - 6.00pm</li>
                <li className="text-slate-500 text-[15px] font-medium">Sunday Closed</li>
              </ul>
            </div>

            {/* Links Col 3 */}
            <div>
              <h4 className="text-[17px] font-extrabold text-[#1B2B20] mb-8">Our Address</h4>
              <p className="text-slate-500 text-[15px] font-medium leading-relaxed">
                Nairobi Garage, Piedmont Plaza,<br/>
                Ngong Road, Nairobi,<br/>
                Kenya
              </p>
            </div>
          </div>
        </div>

        {/* Dark Green Bottom Bar */}
        <div className="bg-[#1B2B20] w-full py-6 relative z-10 border-t border-white/10">
          <div className="mx-auto max-w-[1400px] px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-6 text-white/70 text-[13px] font-bold tracking-wide">
              <Link to="#" className="hover:text-[#EAD35B] transition-colors">Terms & Conditions</Link>
              <span className="text-white/20">|</span>
              <Link to="#" className="hover:text-[#EAD35B] transition-colors">Privacy Policy</Link>
            </div>
            <div className="text-white/70 text-[13px] font-medium">
              Copyright © 2024 <span className="font-bold text-white">BimaGrid</span>, All Rights Reserved.
            </div>
          </div>
        </div>
      </footer>

    </div>
  );
}
