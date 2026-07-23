import React from 'react';
import Navbar from '../components/landing/Navbar.jsx';
import Hero from '../components/landing/Hero.jsx';
import Features from '../components/landing/Features.jsx';
import HowItWorks from '../components/landing/HowItWorks.jsx';
import Stats from '../components/landing/Stats.jsx';
import Testimonials from '../components/landing/Testimonials.jsx';
import AboutDeveloper from '../components/landing/AboutDeveloper.jsx';
import Footer from '../components/landing/Footer.jsx';

export default function LandingPage({ isDark, onToggleTheme }) {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)', color: 'var(--color-text)', transition: 'background 0.3s, color 0.3s' }}>
      <Navbar isDark={isDark} onToggleTheme={onToggleTheme} />
      <Hero />
      <Features />
      <HowItWorks />
      <Stats />
      <AboutDeveloper />
      <Testimonials />
      <Footer />
    </div>
  );
}
