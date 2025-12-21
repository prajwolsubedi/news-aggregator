
import React from 'react';
import RubiksCube from '../components/RubiksCube.tsx';
import NewsletterForm from '../components/NewsletterForm.tsx';

const Home: React.FC = () => {
  return (
    <div className="pt-32 px-6 md:px-12 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center min-h-[80vh]">
      <div className="order-2 lg:order-1 flex flex-col justify-center">
        <h1 className="text-6xl md:text-8xl font-black uppercase tracking-tighter leading-[0.9] mb-8">
          The TOP  <span className="text-[#ff4d4d]"> <br />AI-News</span> <br /> 
          Distilled <br />
          For Your Inbox.
        </h1>
        <p className="text-lg md:text-xl text-black/60 mb-12 max-w-lg leading-relaxed font-medium">
        An AI-powered newsletter that collects, filters, and summarizes the most important AI news from YouTube and the web daily — so that you can stay informed without information overload.
        </p>
        <NewsletterForm />
      </div>
      
      <div className="order-1 lg:order-2 flex justify-center items-center">
        <div className="relative">
          <div className="absolute inset-0 bg-[#ff4d4d]/5 blur-3xl rounded-full scale-150"></div>
          <RubiksCube />
        </div>
      </div>
    </div>
  );
};

export default Home;
