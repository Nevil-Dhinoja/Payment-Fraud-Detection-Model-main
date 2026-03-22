import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Shield, 
  Code2, 
  Database, 
  Brain, 
  Server, 
  Globe,
  Mail,
  Phone,
  MapPin,
  ExternalLink,
  Heart,
  Sparkles
} from 'lucide-react';

// Custom SVG Icons
const LinkedInIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
);

const GitHubIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
  </svg>
);

const YouTubeIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
  </svg>
);

const LeetCodeIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path d="M13.483 0a1.374 1.374 0 0 0-.961.438L7.116 6.226l-3.854 4.126a5.266 5.266 0 0 0-1.209 2.104 5.35 5.35 0 0 0-.125.513 5.527 5.527 0 0 0 .062 2.362 5.83 5.83 0 0 0 .349 1.017 5.938 5.938 0 0 0 1.271 1.818l4.277 4.193.039.038c2.248 2.165 5.852 2.133 8.063-.074l2.396-2.392c.54-.54.54-1.414.003-1.955a1.378 1.378 0 0 0-1.951-.003l-2.396 2.392a3.021 3.021 0 0 1-4.205.038l-.02-.019-4.276-4.193c-.652-.64-.972-1.469-.948-2.263a2.68 2.68 0 0 1 .066-.523 2.545 2.545 0 0 1 .619-1.164L9.13 8.114c1.058-1.134 3.204-1.27 4.43-.278l3.501 2.831c.593.48 1.461.387 1.94-.207a1.384 1.384 0 0 0-.207-1.943l-3.5-2.831c-.8-.647-1.766-1.045-2.774-1.202l2.015-2.158A1.384 1.384 0 0 0 13.483 0zm-2.866 12.815a1.38 1.38 0 0 0-1.38 1.382 1.38 1.38 0 0 0 1.38 1.382H20.79a1.38 1.38 0 0 0 1.38-1.382 1.38 1.38 0 0 0-1.38-1.382z"/>
  </svg>
);

const KaggleIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
    <path d="M18.825 23.859c-.022.092-.117.141-.281.141h-3.139c-.187 0-.351-.082-.492-.248l-5.178-6.589-1.448 1.374v5.111c0 .235-.117.352-.351.352H5.505c-.236 0-.354-.117-.354-.352V.353c0-.233.118-.353.354-.353h2.431c.234 0 .351.12.351.353v14.343l6.203-6.272c.165-.165.33-.246.495-.246h3.239c.144 0 .236.06.285.18.046.149.034.255-.036.315l-6.555 6.344 6.836 8.507c.095.104.117.208.071.358"/>
  </svg>
);

const technologies = [
  {
    category: 'Frontend',
    icon: Globe,
    color: 'from-blue-500 to-cyan-600',
    items: ['React 18', 'Tailwind CSS', 'React Router', 'Axios', 'Lucide Icons', 'Framer Motion']
  },
  {
    category: 'Backend',
    icon: Server,
    color: 'from-green-500 to-emerald-600',
    items: ['Node.js', 'Express.js', 'JWT Authentication', 'RESTful APIs', 'CORS']
  },
  {
    category: 'Database',
    icon: Database,
    color: 'from-purple-500 to-violet-600',
    items: ['MongoDB', 'Mongoose ODM', 'MongoDB Atlas']
  },
  {
    category: 'Machine Learning',
    icon: Brain,
    color: 'from-orange-500 to-amber-600',
    items: ['Python', 'Flask', 'Scikit-learn', 'Pandas', 'NumPy', 'TensorFlow']
  }
];

const socialLinks = [
  {
    name: 'LinkedIn',
    href: 'https://www.linkedin.com/in/mananmonani',
    icon: LinkedInIcon,
    hoverColor: 'hover:bg-[#0077B5] hover:border-[#0077B5]'
  },
  {
    name: 'GitHub',
    href: 'https://github.com/manan-monani',
    icon: GitHubIcon,
    hoverColor: 'hover:bg-dark-700 dark:hover:bg-white dark:hover:text-dark-900 hover:border-dark-700 dark:hover:border-white'
  },
  {
    name: 'YouTube',
    href: 'https://youtube.com/@mananmonani?si=Ox8sAcMclkKlKTix',
    icon: YouTubeIcon,
    hoverColor: 'hover:bg-[#FF0000] hover:border-[#FF0000]'
  },
  {
    name: 'LeetCode',
    href: 'https://leetcode.com/u/mmmonani747',
    icon: LeetCodeIcon,
    hoverColor: 'hover:bg-[#FFA116] hover:border-[#FFA116]'
  },
  {
    name: 'Kaggle',
    href: 'https://www.kaggle.com/mananmonani',
    icon: KaggleIcon,
    hoverColor: 'hover:bg-[#20BEFF] hover:border-[#20BEFF]'
  }
];

const About = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-dark-950">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-accent-50 dark:from-dark-900 dark:via-dark-950 dark:to-dark-900" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-gradient-to-br from-primary-500/20 to-accent-500/20 rounded-full blur-3xl" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/30 rounded-full text-primary-700 dark:text-primary-300 text-sm font-medium mb-8">
              <Sparkles className="w-4 h-4" />
              <span>About This Project</span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl font-bold font-display text-dark-900 dark:text-white mb-6">
              About{' '}
              <span className="bg-gradient-to-r from-primary-600 to-primary-500 dark:from-primary-400 dark:to-primary-300 bg-clip-text text-transparent">
                Defraudo
              </span>
            </h1>
            
            <p className="text-lg text-dark-600 dark:text-dark-300 leading-relaxed">
              Defraudo is an AI-powered fraud detection system designed to analyze digital transactions 
              in real-time and protect against fraudulent activities using advanced machine learning algorithms.
            </p>
          </div>
        </div>
      </section>

      {/* Project Overview */}
      <section className="py-16 bg-dark-50 dark:bg-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold font-display text-dark-900 dark:text-white mb-6">
                How It Works
              </h2>
              <div className="space-y-4">
                {[
                  {
                    step: '01',
                    title: 'Transaction Initiation',
                    description: 'User initiates a transaction with amount and automatically detected device/location data.'
                  },
                  {
                    step: '02',
                    title: 'AI Analysis',
                    description: 'Our ML model analyzes the transaction against historical patterns and fraud indicators.'
                  },
                  {
                    step: '03',
                    title: 'Risk Assessment',
                    description: 'The system calculates a risk score based on multiple features like location, device, timing, and amount.'
                  },
                  {
                    step: '04',
                    title: 'Decision & Action',
                    description: 'Legitimate transactions proceed instantly; suspicious ones are flagged for verification.'
                  }
                ].map((item, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/25">
                      <span className="text-white font-bold text-sm">{item.step}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-dark-900 dark:text-white mb-1">
                        {item.title}
                      </h3>
                      <p className="text-dark-600 dark:text-dark-400 text-sm">
                        {item.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="card p-6 lg:p-8">
              <h3 className="text-xl font-semibold text-dark-900 dark:text-white mb-4">
                Key Features
              </h3>
              <ul className="space-y-3">
                {[
                  'Real-time fraud detection using AI models',
                  'Location-based transaction verification',
                  'Device ID tracking for user identification',
                  'Secure authentication with JWT tokens',
                  'Beautiful responsive UI with dark mode',
                  'Transaction history and analytics'
                ].map((feature, index) => (
                  <li key={index} className="flex items-center gap-3 text-dark-600 dark:text-dark-400">
                    <Shield className="w-5 h-5 text-primary-500" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold font-display text-dark-900 dark:text-white mb-4">
              Tech Stack
            </h2>
            <p className="text-dark-600 dark:text-dark-400 max-w-2xl mx-auto">
              Built with modern technologies for optimal performance, scalability, and developer experience.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {technologies.map((tech, index) => (
              <div key={index} className="card p-6 card-hover">
                <div className={`w-12 h-12 bg-gradient-to-br ${tech.color} rounded-xl flex items-center justify-center mb-4 shadow-lg`}>
                  <tech.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-dark-900 dark:text-white mb-3">
                  {tech.category}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {tech.items.map((item, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 text-xs font-medium bg-dark-100 dark:bg-dark-700 text-dark-600 dark:text-dark-300 rounded-lg"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Developer Section */}
      <section className="py-16 bg-gradient-to-br from-primary-600 to-primary-700 dark:from-dark-800 dark:to-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="text-white">
              <h2 className="text-3xl font-bold font-display mb-4">
                Developer
              </h2>
              <h3 className="text-4xl font-bold mb-6">
                Manan Monani
              </h3>
              <p className="text-primary-100 dark:text-dark-300 mb-8 leading-relaxed">
                A passionate software developer with expertise in full-stack development, 
                machine learning, and building scalable applications. This project showcases 
                the integration of AI/ML with modern web technologies for real-world applications.
              </p>
              
              {/* Social Links */}
              <div className="flex flex-wrap gap-3 mb-8">
                {socialLinks.map((social) => (
                  <a
                    key={social.name}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`p-3 rounded-xl border-2 border-white/30 bg-white/10 text-white hover:text-white transition-all duration-300 ${social.hoverColor}`}
                    aria-label={social.name}
                    title={social.name}
                  >
                    <social.icon />
                  </a>
                ))}
              </div>

              {/* Contact Info */}
              <div className="space-y-3">
                <a
                  href="mailto:mmmonani747@gmail.com"
                  className="flex items-center gap-3 text-primary-100 dark:text-dark-300 hover:text-white transition-colors"
                >
                  <Mail className="w-5 h-5" />
                  <span>mmmonani747@gmail.com</span>
                </a>
                <a
                  href="tel:+917016853244"
                  className="flex items-center gap-3 text-primary-100 dark:text-dark-300 hover:text-white transition-colors"
                >
                  <Phone className="w-5 h-5" />
                  <span>🇮🇳 +91 70168 53244</span>
                </a>
                <div className="flex items-center gap-3 text-primary-100 dark:text-dark-300">
                  <MapPin className="w-5 h-5" />
                  <span>Jamnagar, Gujarat, India</span>
                </div>
                <div className="flex items-center gap-3 text-primary-100 dark:text-dark-300">
                  <ExternalLink className="w-5 h-5" />
                  <span>Portfolio: Coming Soon</span>
                </div>
              </div>
            </div>

            <div className="card p-8">
              <div className="text-center">
                <div className="w-32 h-32 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl">
                  <Code2 className="w-16 h-16 text-white" />
                </div>
                <h4 className="text-xl font-bold text-dark-900 dark:text-white mb-2">
                  Manan Monani
                </h4>
                <p className="text-dark-500 dark:text-dark-400 mb-6">
                  Full-Stack Developer & ML Enthusiast
                </p>
                
                <div className="flex flex-wrap justify-center gap-2">
                  {['React', 'Node.js', 'Python', 'MongoDB', 'ML/AI', 'Tailwind CSS'].map((skill, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 text-sm font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-dark-50 dark:bg-dark-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold font-display text-dark-900 dark:text-white mb-4">
            Want to See It in Action?
          </h2>
          <p className="text-dark-600 dark:text-dark-400 mb-8">
            Create an account and experience the AI-powered fraud detection system yourself.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link to="/register" className="btn-primary">
              Get Started Free
            </Link>
            <a
              href="https://github.com/manan-monani"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary flex items-center justify-center gap-2"
            >
              <GitHubIcon />
              View on GitHub
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
