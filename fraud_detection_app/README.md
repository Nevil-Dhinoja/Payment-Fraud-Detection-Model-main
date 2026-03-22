# 🛡️ Fraud Detection Mobile App

A beautiful, feature-rich Flutter mobile application for real-time payment fraud detection using AI/ML. This app provides an intuitive interface to analyze transactions and detect potential fraud with advanced machine learning models.

## 👨‍💻 Developer

**Manan Monani**

- 📧 Email: [mmmonani747@gmail.com](mailto:mmmonani747@gmail.com)
- 📱 Phone: +91 70168 53244
- 💼 LinkedIn: [linkedin.com/in/mananmonani](https://www.linkedin.com/in/mananmonani)
- 🐙 GitHub: [github.com/manan-monani](https://github.com/manan-monani)
- ▶️ YouTube: [youtube.com/@mananmonani](https://youtube.com/@mananmonani)
- 💻 LeetCode: [leetcode.com/u/mmmonani747](https://leetcode.com/u/mmmonani747)
- 📊 Kaggle: [kaggle.com/mananmonani](https://www.kaggle.com/mananmonani)
- 📍 Location: Jamnagar, Gujarat, India
- 🌐 Portfolio: Coming Soon

## ✨ Features

### Core Features
- **Real-time Fraud Detection** - Instant transaction analysis with ML models
- **Batch Processing** - Analyze multiple transactions at once
- **Prediction History** - Track all past predictions with detailed results
- **Risk Assessment** - Clear risk levels (Low, Medium, High, Critical)

### User Experience
- **Modern UI** - Clean, intuitive Material Design 3 interface
- **Dark/Light Theme** - Automatic and manual theme switching
- **Smooth Animations** - Engaging transitions and feedback
- **Responsive Design** - Works on phones and tablets

### Technical Features
- **API Health Monitoring** - Real-time ML API status
- **Offline History** - Persistent local storage
- **Configurable Threshold** - Adjust fraud detection sensitivity
- **Cross-Platform** - Android, iOS, Web, Windows, macOS, Linux

## 📱 Screenshots

| Home Screen | Transaction Screen | History |
|-------------|-------------------|---------|
| Dashboard with stats | Input transaction data | Past predictions |

| Settings | About | Dark Mode |
|----------|-------|-----------|
| Theme & API config | Developer info | Full dark theme |

## 🚀 Getting Started

### Prerequisites

- Flutter SDK (3.7.0 or later)
- Dart SDK (3.0.0 or later)
- Android Studio / VS Code
- Running ML API server (see [Model/README.md](../Model/README.md))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/manan-monani/Payment-Fraud-Detection-Model.git
   cd Payment-Fraud-Detection-Model/fraud_detection_app
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure API URL**
   
   Edit `lib/config/api_config.dart`:
   ```dart
   // For Android Emulator
   static const String baseUrl = 'http://10.0.2.2:5000';
   
   // For iOS Simulator / Physical Device
   static const String baseUrl = 'http://YOUR_LOCAL_IP:5000';
   
   // For Web
   static const String baseUrl = 'http://localhost:5000';
   ```

4. **Run the app**
   ```bash
   # Android
   flutter run -d android
   
   # iOS
   flutter run -d ios
   
   # Web
   flutter run -d chrome
   
   # Windows
   flutter run -d windows
   ```

## 📂 Project Structure

```
fraud_detection_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── config/
│   │   └── api_config.dart       # API configuration
│   ├── models/
│   │   ├── transaction.dart      # Transaction & prediction models
│   │   └── user.dart             # User model
│   ├── providers/
│   │   ├── theme_provider.dart   # Theme state management
│   │   ├── auth_provider.dart    # Authentication state
│   │   └── transaction_provider.dart  # Transaction state
│   ├── screens/
│   │   ├── splash_screen.dart    # Splash screen
│   │   ├── home_screen.dart      # Main dashboard
│   │   ├── login_screen.dart     # Login page
│   │   ├── register_screen.dart  # Registration page
│   │   ├── transaction_screen.dart  # Transaction input
│   │   ├── history_screen.dart   # Prediction history
│   │   ├── settings_screen.dart  # App settings
│   │   └── about_screen.dart     # About & contact
│   └── services/
│       ├── api_service.dart      # HTTP API client
│       └── storage_service.dart  # Local storage
├── test/
│   └── widget_test.dart          # Widget tests
├── android/                      # Android platform files
├── ios/                          # iOS platform files
├── web/                          # Web platform files
├── windows/                      # Windows platform files
├── linux/                        # Linux platform files
├── macos/                        # macOS platform files
├── pubspec.yaml                  # Dependencies
└── README.md                     # This file
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `provider` | State management |
| `http` | API communication |
| `shared_preferences` | Local storage |
| `google_fonts` | Custom fonts |
| `flutter_animate` | Animations |
| `fl_chart` | Charts (optional) |
| `intl` | Internationalization |
| `url_launcher` | External links |

## 🔧 Configuration

### API Endpoints

The app communicates with the Flask ML API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health check |
| `/predict` | POST | Single prediction |
| `/predict/batch` | POST | Batch predictions |
| `/threshold` | GET/POST | Get/set threshold |
| `/model/info` | GET | Model information |

### Threshold Configuration

Adjust the fraud detection threshold in Settings:
- **Lower threshold (0.1-0.3)**: More sensitive, more false positives
- **Default threshold (0.5)**: Balanced detection
- **Higher threshold (0.7-0.9)**: Less sensitive, fewer false positives

## 🎨 Theming

The app supports three theme modes:
- **Light Mode** - Clean, bright interface
- **Dark Mode** - Easy on the eyes
- **System Mode** - Follows device settings

Theme persistence is handled automatically via SharedPreferences.

## 📱 Platform-Specific Notes

### Android
- Minimum SDK: 21 (Android 5.0)
- Target SDK: 34 (Android 14)
- Internet permission required (auto-added)

### iOS
- Minimum iOS: 12.0
- Add network permissions in Info.plist for HTTP

### Web
- Requires CORS configuration on the API server
- Best performance on Chrome

## 🧪 Testing

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Generate coverage report
genhtml coverage/lcov.info -o coverage/html
```

## 📈 Performance

- **Cold start**: ~1-2 seconds
- **API response**: ~100-500ms
- **Animation FPS**: 60fps
- **Memory usage**: ~50-100MB

## 🛠️ Troubleshooting

### API Connection Issues
1. Verify the ML API is running
2. Check the API URL in config
3. For emulator, use `10.0.2.2` instead of `localhost`
4. Ensure firewall allows connections

### Build Issues
```bash
# Clean build
flutter clean
flutter pub get
flutter run
```

### Performance Issues
- Enable release mode: `flutter run --release`
- Profile with DevTools: `flutter run --profile`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- Flutter team for the amazing framework
- Provider package maintainers
- Google Fonts
- The open-source community

---

<div align="center">
  <strong>Built with ❤️ by Manan Monani</strong>
  <br>
  <sub>Jamnagar, Gujarat, India</sub>
</div>
