# 🎥 VidPulse - Advanced Social Media Video Downloader

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2025.6.30-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy on Railway](https://img.shields.io/badge/Deploy%20on-Railway-blue.svg)](https://railway.app/)
[![Deploy on Render](https://img.shields.io/badge/Deploy%20on-Render-green.svg)](https://render.com/)

> **VidPulse** is a powerful, modern web application that allows users to download videos from multiple social media platforms with an intuitive, beautiful interface. Built with Flask and yt-dlp, it provides lightning-fast downloads with automatic format detection and quality selection.

## ✨ Features

### 🚀 **Core Functionality**
- **Multi-Platform Support**: Download from YouTube, TikTok, Instagram, Twitter, Facebook, and more
- **Smart Format Detection**: Automatically identifies available video and audio formats
- **Quality Selection**: Choose from multiple resolution options (4K, 1080p, 720p, etc.)
- **Audio Extraction**: Download audio-only files in MP3 format
- **Automatic Download**: Streamlined process with auto-download after processing

### 🎨 **User Experience**
- **Modern UI/UX**: Beautiful, responsive design with glass-morphism effects
- **Real-time Progress**: Live progress bar showing download status
- **Smart Validation**: URL validation with visual feedback
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Dark Theme**: Eye-friendly dark interface with gradient accents

### 🔧 **Technical Features**
- **Asynchronous Processing**: Background download queue for better performance
- **Format Optimization**: Intelligent format selection for best compatibility
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **SSL Support**: Handles SSL certificate issues automatically
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 📱 **Supported Platforms**
- **YouTube** - Full video and audio support
- **TikTok** - Video downloads with quality options
- **Instagram** - Posts, Reels, and Stories
- **Twitter/X** - Video tweets and threads
- **Facebook** - Video posts and stories
- **And many more** - Any platform supported by yt-dlp

## 🛠️ Technology Stack

### **Backend**
- **Python 3.8+** - Core programming language
- **Flask 3.1.1** - Lightweight web framework
- **yt-dlp 2025.6.30** - Advanced video downloader library
- **Flask-CORS 6.0.1** - Cross-origin resource sharing support

### **Frontend**
- **HTML5** - Semantic markup
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript (ES6+)** - Modern JavaScript with async/await
- **Font Awesome** - Icon library
- **Google Fonts** - Typography (Inter font family)

### **Infrastructure**
- **Threading** - Background task processing
- **Queue System** - Download task management
- **File System** - Local file storage and serving
- **RESTful API** - Clean API endpoints

## 📋 Prerequisites

Before running this application, ensure you have:

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **FFmpeg** (for audio processing and format conversion)
- **Git** (for cloning the repository)

### **FFmpeg Installation**

#### **macOS (using Homebrew)**
```bash
brew install ffmpeg
```

#### **Ubuntu/Debian**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### **Windows**
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

## 🚀 Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/Social-Media-Video-Downloader.git
cd Social-Media-Video-Downloader
```

### **2. Create Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run the Application**
```bash
python main.py
```

The application will be available at `http://localhost:5001`

## 🌐 Usage

### **Basic Workflow**

1. **Paste URL**: Enter any supported video URL in the input field
2. **Analyze**: Click "Analyze Video" to extract video information
3. **Select Format**: Choose your preferred quality and format
4. **Download**: Click "Download Now" - the file downloads automatically after processing

### **Supported URL Formats**

```
YouTube:     https://youtube.com/watch?v=VIDEO_ID
             https://youtu.be/VIDEO_ID
TikTok:      https://tiktok.com/@user/video/VIDEO_ID
Instagram:   https://instagram.com/p/POST_ID
Twitter:     https://twitter.com/user/status/TWEET_ID
Facebook:    https://facebook.com/video.php?v=VIDEO_ID
```

### **Format Options**

- **Video Formats**: MP4, WebM, AVI with various resolutions
- **Audio Formats**: MP3, M4A, OGG with different bitrates
- **Quality Options**: 4K, 1080p, 720p, 480p, and more
- **Auto-Merge**: Automatic video+audio merging for better compatibility

## 🏗️ Project Structure

```
Social-Media-Video-Downloader/
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── start.sh               # Startup script for deployment
├── LICENSE                # MIT License
├── README.md              # Read me file   
├── downloads/             # Downloaded files directory
└── templates/
    └── index.html         # Main HTML template
```

## 🔧 Configuration

### **Environment Variables**

The application can be configured using environment variables:

```bash
# Port configuration (default: 5001)
PORT=5001

# Download directory (default: ./downloads)
DOWNLOAD_DIRECTORY=/path/to/downloads

# Python version (for deployment)
PYTHON_VERSION=3.11.0
```

### **Customization Options**

- **Download Directory**: Modify `DOWNLOAD_DIRECTORY` in `main.py`
- **Port**: Change the port in the `main.py` file or use environment variables
- **Format Preferences**: Adjust format selection logic in the `get_video_info()` function
- **UI Theme**: Modify CSS variables in `templates/index.html`

## 🚀 Deployment

### **Railway Deployment**

1. **Fork/Clone** this repository
2. **Connect** to Railway
3. **Deploy** automatically using `railway.json`

### **Docker Deployment**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Start application
CMD ["python", "main.py"]
```

## 🧪 Testing

### **Manual Testing**

1. **Start the application**: `python main.py`
2. **Open browser**: Navigate to `http://localhost:5001`
3. **Test with various URLs**:
   - YouTube videos
   - TikTok content
   - Instagram posts
   - Twitter videos

### **API Testing**

```bash
# Test video info endpoint
curl -X POST http://localhost:5001/api/info \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtu.be/VIDEO_ID"}'

# Test download endpoint
curl -X POST http://localhost:5001/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtu.be/VIDEO_ID", "format_id": "best"}'
```

## 🔒 Security Considerations

- **Input Validation**: All URLs are validated before processing
- **File Access**: Downloads are served with proper headers
- **Error Handling**: Sensitive information is not exposed in error messages
- **CORS**: Configured for development (adjust for production)

## 🐛 Troubleshooting

### **Common Issues**

#### **"Command not found: python"**
```bash
# Use python3 instead
python3 main.py

# Or create an alias
alias python=python3
```

#### **"FFmpeg not found"**
```bash
# Install FFmpeg (see Prerequisites section)
# Verify installation
ffmpeg -version
```

#### **"Port already in use"**
```bash
# Change port in main.py
# Or kill the process using the port
lsof -ti:5001 | xargs kill -9
```

#### **"SSL Certificate Error"**
- The application handles SSL issues automatically
- If persistent, check your system's certificate store

### **Performance Issues**

- **Large Files**: Downloads are processed in the background
- **Multiple Downloads**: Queue system handles concurrent requests
- **Memory Usage**: Files are streamed to avoid memory issues

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### **Development Setup**

```bash
# Clone your fork
git clone https://github.com/yourusername/Social-Media-Video-Downloader.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available

# Run tests
python -m pytest  # If tests are available

# Start development server
python main.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - The powerful video downloader library
- **[Flask](https://flask.palletsprojects.com/)** - The web framework for Python
- **[Tailwind CSS](https://tailwindcss.com/)** - The utility-first CSS framework
- **[Font Awesome](https://fontawesome.com/)** - The icon library
- **[Google Fonts](https://fonts.google.com/)** - The typography service

## 📞 Support

If you encounter any issues or have questions:

- **Create an Issue** on GitHub
- **Check the Troubleshooting** section above
- **Review the Documentation** in this README

## 🔮 Future Enhancements

- [ ] **User Authentication**: User accounts and download history
- [ ] **Batch Downloads**: Download multiple videos simultaneously
- [ ] **Playlist Support**: Download entire playlists
- [ ] **Cloud Storage**: Integration with Google Drive, Dropbox
- [ ] **Mobile App**: Native iOS and Android applications
- [ ] **API Rate Limiting**: Prevent abuse and ensure fair usage
- [ ] **Download Scheduling**: Schedule downloads for off-peak hours
- [ ] **Format Conversion**: Convert between different video formats
- [ ] **Subtitle Support**: Download and embed subtitles
- [ ] **Analytics Dashboard**: Download statistics and usage metrics

## 📊 Project Statistics

- **Lines of Code**: 1,000+ (Python + HTML/JS)
- **Dependencies**: 3 main Python packages
- **Supported Platforms**: 10+ social media platforms
- **File Formats**: 15+ video and audio formats
- **Deployment Options**: 5+ cloud platforms

---

<div align="center">

**Made with ❤️ by Rayan Haroon**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/1rayanharoon)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](linkedin.com/in/1rayan-haroon)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://x.com/Rayantwt133034)

**⭐ Star this repository if you found it helpful!**

</div>
