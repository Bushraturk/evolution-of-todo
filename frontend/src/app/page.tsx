'use client';

import { LandingNav, Hero, Features, CTA, Footer } from '@/components/landing';

export default function LandingPage() {
  return (
    <div className="landing-bg min-h-screen">
      <LandingNav />
      <Hero />
      <Features />
      <CTA />
      <Footer />
    </div>
  );
}
