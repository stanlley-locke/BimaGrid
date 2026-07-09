import { Link, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Search, Phone, ArrowUpRight, ChevronDown } from 'lucide-react';
import { useState, useEffect } from 'react';

function navClassName({ isActive }: { isActive: boolean }) {
  return `text-sm font-bold tracking-wider transition-colors hover:text-[#EAD35B] ${
    isActive ? 'text-[#EAD35B]' : 'text-white'
  }`;
}

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isHome = location.pathname === '/';
  
  // Adjust margin based on scrolled state for a floating effect.
  // Made completely opaque (#1B2B20) when scrolled to prevent seeing the hero cutout sliding underneath
  const navBg = scrolled || !isHome 
    ? 'bg-[#1B2B20] shadow-xl border border-white/10 rounded-[2.5rem] mt-2' 
    : 'bg-transparent mt-4 sm:mt-6 lg:mt-8';

  return (
    <div className="fixed top-0 z-50 w-full transition-all duration-300 px-4 sm:px-6 lg:px-8 pointer-events-none">
      
      <header className={`relative transition-all duration-300 w-full pointer-events-auto ${navBg}`}>
        <div className="relative z-10 mx-auto flex h-24 w-full items-center justify-between px-4 sm:px-8 lg:pl-10 lg:pr-6">
          <Link to="/" className="flex items-center gap-3 group shrink-0">
            <img src="/bimagrid_logo.png" alt="BimaGrid Logo" className="h-12 w-12 rounded-[1rem] object-cover border-2 border-white/10" />
            <div>
              <p className="text-3xl font-extrabold tracking-tight text-white group-hover:text-bima-lightGreen transition-colors font-sans">bimagrid</p>
            </div>
          </Link>

          <nav className="hidden items-center lg:flex gap-4 xl:gap-8">
            <NavLink to="/" end className={navClassName}>HOME</NavLink>
            <span className="w-1.5 h-1.5 rounded-full bg-[#EAD35B]"></span>

            <div className="relative group pointer-events-auto">
              <button className="flex items-center gap-1 font-bold text-sm tracking-wider text-white hover:text-[#EAD35B] transition-colors py-4">
                SERVICES <ChevronDown className="w-4 h-4 opacity-70 group-hover:rotate-180 transition-transform" />
              </button>
              <div className="absolute top-full left-0 mt-0 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 translate-y-2 group-hover:translate-y-0 p-3 flex flex-col gap-1">
                <Link to="#" className="px-4 py-2.5 rounded-xl text-[13px] font-bold text-slate-700 hover:bg-[#F4F1ED] hover:text-[#659A5F] transition-colors">Crop Protection</Link>
                <Link to="#" className="px-4 py-2.5 rounded-xl text-[13px] font-bold text-slate-700 hover:bg-[#F4F1ED] hover:text-[#659A5F] transition-colors">Livestock Cover</Link>
                <Link to="#" className="px-4 py-2.5 rounded-xl text-[13px] font-bold text-slate-700 hover:bg-[#F4F1ED] hover:text-[#659A5F] transition-colors">Weather Index</Link>
              </div>
            </div>
            <span className="w-1.5 h-1.5 rounded-full bg-[#EAD35B]"></span>

            <div className="relative group pointer-events-auto">
              <button className="flex items-center gap-1 font-bold text-sm tracking-wider text-white hover:text-[#EAD35B] transition-colors py-4">
                PAGES <ChevronDown className="w-4 h-4 opacity-70 group-hover:rotate-180 transition-transform" />
              </button>
              <div className="absolute top-full left-0 mt-0 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 translate-y-2 group-hover:translate-y-0 p-3 flex flex-col gap-1">
                <Link to="#" className="px-4 py-2.5 rounded-xl text-[13px] font-bold text-slate-700 hover:bg-[#F4F1ED] hover:text-[#659A5F] transition-colors">About Us</Link>
                <Link to="#" className="px-4 py-2.5 rounded-xl text-[13px] font-bold text-slate-700 hover:bg-[#F4F1ED] hover:text-[#659A5F] transition-colors">Our Farmers</Link>
                <Link to="#" className="px-4 py-2.5 rounded-xl text-[13px] font-bold text-slate-700 hover:bg-[#F4F1ED] hover:text-[#659A5F] transition-colors">Testimonials</Link>
              </div>
            </div>
            <span className="w-1.5 h-1.5 rounded-full bg-[#EAD35B]"></span>
            
            {isAuthenticated ? (
              <NavLink to="/dashboard" className={navClassName}>DASHBOARD</NavLink>
            ) : (
              <NavLink to="/login" className={navClassName}>LOGIN</NavLink>
            )}
          </nav>

          <div className="flex items-center gap-4 xl:gap-6 shrink-0 relative z-20">
            
            <div className="hidden xl:flex items-center gap-4 shrink-0">
              <div className="w-11 h-11 rounded-full border border-bima-yellow flex items-center justify-center">
                <Phone className="w-4 h-4 text-bima-yellow" />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-medium text-white/70">Call us Now</span>
                <span className="text-sm font-bold text-white">*384*123254#</span>
              </div>
            </div>

            <button className="hidden sm:flex w-11 h-11 bg-white rounded-full items-center justify-center hover:bg-slate-100 transition-colors shadow-sm shrink-0">
              <Search className="w-4 h-4 text-bima-darkGreen" />
            </button>

            {isAuthenticated ? (
              <div className="relative flex items-center h-24 pl-6">
                {isHome && (
                  <div className={`absolute right-[-24px] w-[calc(100%+24px)] h-24 bg-white rounded-bl-[2.5rem] rounded-tr-[2.5rem] sm:rounded-tr-[3rem] ring-2 ring-white transition-opacity duration-300 pointer-events-none hidden lg:block -z-10 ${scrolled ? 'opacity-0' : 'opacity-100'}`}>
                    <div className="absolute top-0 -left-6 w-6 h-6 bg-transparent rounded-tr-3xl shadow-[15px_-15px_0_10px_white]"></div>
                  </div>
                )}
                <button 
                  onClick={logout}
                  className="btn-secondary group flex items-center gap-2 rounded-full font-bold px-8 h-12 shrink-0 whitespace-nowrap"
                >
                  Sign out <ArrowUpRight className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="relative flex items-center h-24 pl-6">
                {isHome && (
                  <div className={`absolute right-[-24px] w-[calc(100%+24px)] h-24 bg-white rounded-bl-[2.5rem] rounded-tr-[2.5rem] sm:rounded-tr-[3rem] ring-2 ring-white transition-opacity duration-300 pointer-events-none hidden lg:block -z-10 ${scrolled ? 'opacity-0' : 'opacity-100'}`}>
                    <div className="absolute top-0 -left-6 w-6 h-6 bg-transparent rounded-tr-3xl shadow-[15px_-15px_0_10px_white]"></div>
                  </div>
                )}
                <Link to="/register" className="btn-secondary group flex items-center gap-2 rounded-full font-bold px-8 h-12 bg-[#EAD35B] text-[#1B2B20] hover:bg-[#d8c045] shrink-0 whitespace-nowrap">
                  Get In Touch <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>
    </div>
  );
}
