import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Shield, 
  Zap, 
  Lock, 
  Globe, 
  Cpu, 
  BarChart3, 
  ArrowRight,
  CheckCircle,
  Sparkles
} from 'lucide-react';

const features = [
  {
    icon: Shield,
    title: 'Real-time Detection',
    description: 'Advanced AI algorithms analyze transactions in milliseconds to detect fraudulent patterns.',
    color: 'from-green-500 to-emerald-600'
  },
  {
    icon: Cpu,
    title: 'Machine Learning',
    description: 'Self-learning models that continuously improve fraud detection accuracy over time.',
    color: 'from-blue-500 to-cyan-600'
  },
  {
    icon: Lock,
    title: 'Secure Transactions',
    description: 'Bank-grade encryption ensures your transaction data remains safe and private.',
    color: 'from-purple-500 to-violet-600'
  },
  {
    icon: Globe,
    title: 'Location Tracking',
    description: 'Geolocation verification to identify suspicious transactions from unusual locations.',
    color: 'from-orange-500 to-amber-600'
  },
  {
    icon: Zap,
    title: 'Instant Alerts',
    description: 'Get immediate notifications when suspicious activity is detected on your account.',
    color: 'from-pink-500 to-rose-600'
  },
  {
    icon: BarChart3,
    title: 'Analytics Dashboard',
    description: 'Comprehensive transaction analytics and fraud detection reports at your fingertips.',
    color: 'from-teal-500 to-cyan-600'
  }
];

const stats = [
  { value: '99.9%', label: 'Detection Accuracy' },
  { value: '<100ms', label: 'Response Time' },
  { value: '24/7', label: 'Monitoring' },
  { value: '10K+', label: 'Transactions Protected' }
];

export const Home = () => {
  const { isLoggedIn } = useAuth();

  return (
    <div className="min-h-screen bg-white dark:bg-dark-950">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-accent-50 dark:from-dark-900 dark:via-dark-950 dark:to-dark-900" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gradient-to-br from-primary-500/20 to-accent-500/20 rounded-full blur-3xl" />
        
        {/* Floating Elements */}
        <div className="absolute top-32 left-10 w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl rotate-12 opacity-10 animate-float" />
        <div className="absolute bottom-32 right-10 w-32 h-32 bg-gradient-to-br from-accent-500 to-accent-600 rounded-full opacity-10 animate-float" style={{ animationDelay: '2s' }} />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/30 rounded-full text-primary-700 dark:text-primary-300 text-sm font-medium mb-8 animate-fadeIn">
              <Sparkles className="w-4 h-4" />
              <span>AI-Powered Fraud Protection</span>
            </div>

            {/* Heading */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold font-display text-dark-900 dark:text-white mb-6 animate-fadeIn" style={{ animationDelay: '0.1s' }}>
              Protect Your Transactions with{' '}
              <span className="bg-gradient-to-r from-primary-600 to-primary-500 dark:from-primary-400 dark:to-primary-300 bg-clip-text text-transparent">
                AI-Powered
              </span>{' '}
              Fraud Detection
            </h1>

            {/* Subheading */}
            <p className="text-lg sm:text-xl text-dark-600 dark:text-dark-300 mb-10 max-w-2xl mx-auto animate-fadeIn" style={{ animationDelay: '0.2s' }}>
              Defraudo uses advanced machine learning algorithms to analyze digital transactions 
              in real-time, protecting your payments from fraudulent activities.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fadeIn" style={{ animationDelay: '0.3s' }}>
              {isLoggedIn ? (
                <Link to="/transactions" className="btn-primary flex items-center gap-2">
                  Go to Dashboard
                  <ArrowRight className="w-5 h-5" />
                </Link>
              ) : (
                <>
                  <Link to="/register" className="btn-primary flex items-center gap-2">
                    Get Started Free
                    <ArrowRight className="w-5 h-5" />
                  </Link>
                  <Link to="/login" className="btn-secondary">
                    Sign In
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Hero Image/Demo */}
          <div className="mt-16 lg:mt-24 relative animate-fadeIn" style={{ animationDelay: '0.4s' }}>
            <div className="absolute inset-0 bg-gradient-to-t from-white dark:from-dark-950 to-transparent z-10 h-1/3 bottom-0 top-auto" />
            <div className="relative bg-white dark:bg-dark-800 rounded-2xl shadow-2xl border border-dark-100 dark:border-dark-700 overflow-hidden">
              <div className="bg-dark-100 dark:bg-dark-700 px-4 py-3 flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <div className="p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-dark-900 dark:text-white">Transaction Analysis</h3>
                    <p className="text-sm text-dark-500">Real-time fraud detection</p>
                  </div>
                </div>
                <div className="space-y-4">
                  {[
                    { label: 'Amount', value: '$5,000.00', status: 'analyzing' },
                    { label: 'Location', value: 'Jamnagar, India', status: 'verified' },
                    { label: 'Device', value: 'Trusted Device', status: 'verified' },
                    { label: 'Risk Score', value: 'Low (0.02)', status: 'safe' }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-dark-50 dark:bg-dark-700/50 rounded-xl">
                      <span className="text-dark-600 dark:text-dark-400">{item.label}</span>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-dark-900 dark:text-white">{item.value}</span>
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-dark-900 dark:bg-dark-950 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-900/20 to-accent-900/20" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-2">
                  {stat.value}
                </div>
                <div className="text-dark-400 text-sm sm:text-base">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 lg:py-32 bg-dark-50 dark:bg-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold font-display text-dark-900 dark:text-white mb-4">
              Why Choose Defraudo?
            </h2>
            <p className="text-dark-600 dark:text-dark-400 max-w-2xl mx-auto">
              Our advanced fraud detection system combines cutting-edge AI technology with 
              real-time analysis to keep your transactions safe.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group card p-6 card-hover"
              >
                <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center shadow-lg mb-5 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-dark-900 dark:text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-dark-600 dark:text-dark-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-32 bg-gradient-to-br from-primary-600 to-primary-700 dark:from-primary-900 dark:to-dark-900 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')]" />
        
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-white mb-6">
            Ready to Secure Your Transactions?
          </h2>
          <p className="text-lg text-primary-100 mb-10 max-w-2xl mx-auto">
            Join thousands of users who trust Defraudo to protect their digital payments 
            from fraud. Get started for free today.
          </p>
          
          {!isLoggedIn && (
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/register"
                className="px-8 py-4 bg-white text-primary-600 font-semibold rounded-xl shadow-lg hover:shadow-xl hover:bg-primary-50 transition-all duration-300 flex items-center gap-2"
              >
                Create Free Account
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/about"
                className="px-8 py-4 bg-primary-500/20 text-white font-semibold rounded-xl border border-primary-400/30 hover:bg-primary-500/30 transition-all duration-300"
              >
                Learn More
              </Link>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Home;
