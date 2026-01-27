'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { fadeInUp, staggerContainer } from '@/lib/animations';

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-16 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Floating background elements */}
      <motion.div
        animate={{
          y: [0, -10, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-20 right-10 w-64 h-64 glass-card rounded-full opacity-50"
      />
      <motion.div
        animate={{
          y: [0, -10, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute bottom-20 left-10 w-48 h-48 glass-card rounded-full opacity-50"
      />

      {/* Content */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={staggerContainer}
        className="relative z-10 max-w-5xl mx-auto text-center"
      >
        <motion.h1
          variants={fadeInUp}
          className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6"
        >
          <span className="bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 bg-clip-text text-transparent">
            Organize Your Life
          </span>
          <br />
          <span className="text-gray-800 dark:text-gray-100">
            with Elegant Simplicity
          </span>
        </motion.h1>

        <motion.p
          variants={fadeInUp}
          className="text-lg sm:text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto"
        >
          A beautiful, modern todo app with powerful features to help you stay organized and productive
        </motion.p>

        <motion.div
          variants={fadeInUp}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            href="/register"
            className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl font-semibold text-lg hover:from-violet-600 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl hover:scale-105 transform"
          >
            Get Started Free
          </Link>
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-4 glass-strong text-purple-700 dark:text-purple-300 rounded-xl font-semibold text-lg hover:scale-105 transform transition-all"
          >
            Sign In
          </Link>
        </motion.div>

        {/* Feature highlights */}
        <motion.div
          variants={fadeInUp}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto"
        >
          {[
            { icon: '✓', text: 'Smart Tasks' },
            { icon: '⚡', text: 'Fast & Responsive' },
            { icon: '🎨', text: 'Beautiful Design' },
            { icon: '🔒', text: 'Secure & Private' }
          ].map((feature, index) => (
            <div
              key={index}
              className="glass-card rounded-xl p-4 text-center"
            >
              <div className="text-3xl mb-2">{feature.icon}</div>
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {feature.text}
              </div>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}
