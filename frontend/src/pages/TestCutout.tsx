export default function TestCutout() {
  return (
    <div className="bg-white min-h-screen p-8">
      <div className="relative h-[600px] w-full bg-slate-900 rounded-[2.5rem] overflow-hidden">
        {/* Cutout Container */}
        <div className="absolute top-0 right-0 w-80 h-28 bg-white rounded-bl-[2.5rem] z-20">
          {/* Inner corner top-left of the cutout */}
          <div className="absolute top-0 -left-6 w-6 h-6 bg-transparent rounded-tr-[1.5rem] shadow-[12px_-12px_0_12px_white]"></div>
          {/* Inner corner bottom-right of the cutout */}
          <div className="absolute -bottom-6 right-0 w-6 h-6 bg-transparent rounded-tr-[1.5rem] shadow-[12px_-12px_0_12px_white]"></div>
          
          <div className="absolute inset-0 flex items-center justify-center">
            <button className="bg-yellow-400 px-6 py-3 rounded-full text-black font-bold">Get In Touch</button>
          </div>
        </div>
      </div>
    </div>
  );
}
