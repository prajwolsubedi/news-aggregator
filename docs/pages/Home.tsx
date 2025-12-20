
import React from 'react';
import RubiksCube from '../components/RubiksCube.tsx';
import NewsletterForm from '../components/NewsletterForm.tsx';

const Home: React.FC = () => {
  return (
    <div className="pt-32 px-6 md:px-12 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center min-h-[80vh]">
      <div className="order-2 lg:order-1 flex flex-col justify-center">
        <h1 className="text-6xl md:text-8xl font-black uppercase tracking-tighter leading-[0.9] mb-8">
          The <span className="text-[#ff4d4d]">Future</span> <br /> 
          Of Intelligence <br />
          In Your Inbox.
        </h1>
        <p className="text-lg md:text-xl text-black/60 mb-12 max-w-lg leading-relaxed font-medium">
          A weekly dispatch of high-signal AI developments, distilled for the modern builder. No fluff. Just hard logic and clean code.
        </p>
        <NewsletterForm />
      </div>
      
      <div className="order-1 lg:order-2 flex justify-center items-center">
        <div className="relative">
          <div className="absolute inset-0 bg-[#ff4d4d]/5 blur-3xl rounded-full scale-150"></div>
          <RubiksCube />
          <div className="absolute -bottom-10 -right-10 hidden md:block">
            <div className="bg-black text-white p-4 uppercase text-[10px] font-black tracking-widest rotate-12 shadow-xl">
              100% MINIMALIST AI
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
