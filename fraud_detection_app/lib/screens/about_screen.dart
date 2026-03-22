/// About Screen
/// Author: Manan Monani

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:url_launcher/url_launcher.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App Bar with gradient
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text('About'),
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: isDark
                        ? [const Color(0xFF1a1a2e), const Color(0xFF16213e)]
                        : [
                            theme.colorScheme.primary,
                            theme.colorScheme.secondary,
                          ],
                  ),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Icon(
                          Icons.shield_outlined,
                          size: 50,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 50),
                    ],
                  ),
                ),
              ),
            ),
          ),

          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // App Info Card
                  Card(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        children: [
                          Text(
                            'Fraud Detection App',
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Version 1.0.0',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: theme.colorScheme.onSurface.withValues(
                                alpha: 0.6,
                              ),
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'An AI-powered mobile application for real-time payment fraud detection using advanced machine learning algorithms.',
                            textAlign: TextAlign.center,
                            style: theme.textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                  ).animate().fadeIn(duration: 400.ms),

                  const SizedBox(height: 24),

                  // Developer Section
                  Text(
                    'Developer',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Card(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        children: [
                          CircleAvatar(
                            radius: 50,
                            backgroundColor: theme.colorScheme.primary
                                .withValues(alpha: 0.1),
                            child: Text(
                              'MM',
                              style: TextStyle(
                                fontSize: 32,
                                fontWeight: FontWeight.bold,
                                color: theme.colorScheme.primary,
                              ),
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Manan Monani',
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Full Stack & ML Developer',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: theme.colorScheme.onSurface.withValues(
                                alpha: 0.6,
                              ),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(
                                Icons.location_on,
                                size: 16,
                                color: Colors.grey,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                'Jamnagar, Gujarat, India',
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: theme.colorScheme.onSurface.withValues(
                                    alpha: 0.5,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ).animate().fadeIn(delay: 100.ms, duration: 400.ms),

                  const SizedBox(height: 24),

                  // Contact Section
                  Text(
                    'Connect',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Card(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Column(
                      children: [
                        _buildContactTile(
                          context,
                          icon: Icons.email,
                          title: 'Email',
                          subtitle: 'mmmonani747@gmail.com',
                          color: Colors.red,
                          onTap: () =>
                              _launchUrl('mailto:mmmonani747@gmail.com'),
                        ),
                        const Divider(height: 1),
                        _buildContactTile(
                          context,
                          icon: Icons.phone,
                          title: 'Phone',
                          subtitle: '+91 70168 53244',
                          color: Colors.green,
                          onTap: () => _launchUrl('tel:+917016853244'),
                        ),
                        const Divider(height: 1),
                        _buildContactTile(
                          context,
                          icon: Icons.link,
                          title: 'LinkedIn',
                          subtitle: 'linkedin.com/in/mananmonani',
                          color: const Color(0xFF0077B5),
                          onTap: () => _launchUrl(
                            'https://www.linkedin.com/in/mananmonani',
                          ),
                        ),
                        const Divider(height: 1),
                        _buildContactTile(
                          context,
                          icon: Icons.code,
                          title: 'GitHub',
                          subtitle: 'github.com/manan-monani',
                          color: isDark ? Colors.white : Colors.black,
                          onTap: () =>
                              _launchUrl('https://github.com/manan-monani'),
                        ),
                        const Divider(height: 1),
                        _buildContactTile(
                          context,
                          icon: Icons.play_circle,
                          title: 'YouTube',
                          subtitle: 'youtube.com/@mananmonani',
                          color: Colors.red,
                          onTap: () =>
                              _launchUrl('https://youtube.com/@mananmonani'),
                        ),
                        const Divider(height: 1),
                        _buildContactTile(
                          context,
                          icon: Icons.laptop,
                          title: 'LeetCode',
                          subtitle: 'leetcode.com/u/mmmonani747',
                          color: Colors.orange,
                          onTap: () =>
                              _launchUrl('https://leetcode.com/u/mmmonani747'),
                        ),
                        const Divider(height: 1),
                        _buildContactTile(
                          context,
                          icon: Icons.analytics,
                          title: 'Kaggle',
                          subtitle: 'kaggle.com/mananmonani',
                          color: const Color(0xFF20BEFF),
                          onTap: () =>
                              _launchUrl('https://www.kaggle.com/mananmonani'),
                        ),
                        const Divider(height: 1),
                        _buildContactTile(
                          context,
                          icon: Icons.web,
                          title: 'Portfolio',
                          subtitle: 'Coming Soon',
                          color: Colors.teal,
                          onTap: () {},
                        ),
                      ],
                    ),
                  ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

                  const SizedBox(height: 24),

                  // Tech Stack Section
                  Text(
                    'Technology Stack',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Card(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          _buildTechRow(
                            'Mobile App',
                            'Flutter, Dart, Provider',
                          ),
                          _buildTechRow(
                            'ML Pipeline',
                            'Python, XGBoost, LightGBM',
                          ),
                          _buildTechRow('Backend API', 'Flask, REST API'),
                          _buildTechRow('Web Frontend', 'React, Tailwind CSS'),
                          _buildTechRow('Server', 'Node.js, Express, MongoDB'),
                        ],
                      ),
                    ),
                  ).animate().fadeIn(delay: 300.ms, duration: 400.ms),

                  const SizedBox(height: 24),

                  // Features Section
                  Text(
                    'Key Features',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Card(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          _buildFeatureItem(
                            context,
                            Icons.speed,
                            'Real-time Detection',
                            'Instant fraud analysis with ML',
                          ),
                          _buildFeatureItem(
                            context,
                            Icons.psychology,
                            'Ensemble Learning',
                            'RF, XGBoost, LightGBM models',
                          ),
                          _buildFeatureItem(
                            context,
                            Icons.tune,
                            'Optimized Threshold',
                            'Configurable fraud threshold',
                          ),
                          _buildFeatureItem(
                            context,
                            Icons.history,
                            'Prediction History',
                            'Track all past predictions',
                          ),
                          _buildFeatureItem(
                            context,
                            Icons.dark_mode,
                            'Dark/Light Theme',
                            'Comfortable viewing modes',
                          ),
                        ],
                      ),
                    ),
                  ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

                  const SizedBox(height: 40),

                  // Footer
                  Center(
                    child: Column(
                      children: [
                        Text(
                          '© 2024 Manan Monani',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurface.withValues(
                              alpha: 0.5,
                            ),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Made with ❤️ in India',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurface.withValues(
                              alpha: 0.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ).animate().fadeIn(delay: 500.ms, duration: 400.ms),

                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContactTile(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }

  Widget _buildTechRow(String category, String technologies) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              category,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
            ),
          ),
          Expanded(
            child: Text(
              technologies,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureItem(
    BuildContext context,
    IconData icon,
    String title,
    String description,
  ) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: theme.colorScheme.primary, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 12,
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
