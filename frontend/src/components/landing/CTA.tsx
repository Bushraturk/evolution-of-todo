'use client';

import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';
import Link from 'next/link';
import { scaleIn } from '@/lib/animations';

export default function CTA() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="py-20 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial="hidden"
        animate={isInView ? "visible" : "hidden"}
        variants={scaleIn}
        className="max-w-4xl mx-auto"
      >
        <div className="glass-strong rounded-3xl p-8 sm:p-12 text-center border-2 border-purple-300/30 dark:border-purple-500/30">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-6">
            <span className="bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
              Ready to Get Organized?
            </span>
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of users who have transformed their productivity with our elegant todo app
          </p>
          <Link
            href="/register"
            className="inline-block px-10 py-4 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl font-semibold text-lg hover:from-violet-600 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl hover:scale-105 transform"
          >
            Get Started Free
          </Link>
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
            No credit card required • Free forever
          </p>
        </div>
      </motion.div>
    </section>
  );
}
