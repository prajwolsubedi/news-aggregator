import React from "react";
import { HashRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import Home from "./pages/Home.tsx";
import About from "./pages/About.tsx";
import Unsubscribe from "./pages/Unsubscribe.tsx";

const Header: React.FC = () => {
  const location = useLocation();

  return (
    <header className="fixed top-0 left-0 w-full z-50 px-6 py-8 md:px-12 pointer-events-none">
      <div className="max-w-7xl mx-auto flex justify-between items-center pointer-events-auto">
        <Link to="/" className="text-xl font-black uppercase tracking-tighter">
          Neural<span className="text-[#ff4d4d]">.</span>Notes
        </Link>
        <nav className="flex space-x-8 font-medium uppercase text-sm tracking-widest">
          <Link
            to="/"
            className={`hover:text-[#ff4d4d] transition-colors ${
              location.pathname === "/" ? "text-[#ff4d4d]" : ""
            }`}
          >
            Home
          </Link>
          <Link
            to="/about"
            className={`hover:text-[#ff4d4d] transition-colors ${
              location.pathname === "/about" ? "text-[#ff4d4d]" : ""
            }`}
          >
            About
          </Link>
        </nav>
      </div>
    </header>
  );
};

const Footer: React.FC = () => (
  <footer className="py-12 px-6 border-t border-black/5 mt-20">
    <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center text-xs uppercase tracking-widest text-black/40 font-bold">
      <p>© 2024 NEURAL NOTES INC.</p>
      <div className="flex space-x-6 mt-4 md:mt-0">
        <a href="#" className="hover:text-black">
          Twitter
        </a>
        <a href="#" className="hover:text-black">
          Substack
        </a>
        <a href="#" className="hover:text-black">
          Privacy
        </a>
      </div>
    </div>
  </footer>
);

const App: React.FC = () => {
  return (
    <HashRouter>
      <div className="min-h-screen selection:bg-[#ff4d4d] selection:text-white">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/unsubscribe/:token" element={<Unsubscribe />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </HashRouter>
  );
};

export default App;
