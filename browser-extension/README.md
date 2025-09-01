# 🌐 Browser Extension - Accessibility Toolkit

A powerful browser extension that provides real-time accessibility scanning and enhancement for any webpage. Instantly detect accessibility issues and apply temporary fixes to improve your browsing experience.

## ✨ Features

### 🔍 **Real-Time Accessibility Scanning**
- **Instant Analysis**: Scan any webpage with one click
- **Comprehensive Detection**: 20+ accessibility checks covering all WCAG criteria
- **Smart Categorization**: Issues organized by accessibility category (Visual, Auditory, Cognitive, Navigation, Forms, Content)
- **Severity Levels**: Critical, Moderate, and Low priority issues

### 🛠️ **Smart Auto-Fixes**
- **Font Size Control**: Increase/decrease text size for better readability
- **Contrast Enhancement**: Improve color contrast for better visibility
- **Focus Highlighting**: Enhanced focus indicators for keyboard navigation
- **Reading Mode**: Distraction-free reading experience
- **Layout Simplification**: Hide decorative elements and reduce clutter

### 🎨 **User-Friendly Interface**
- **Modern Popup**: Clean, intuitive design with dark mode support
- **Floating Toolbar**: Always-accessible accessibility controls
- **Interactive Reports**: Detailed issue descriptions with suggested fixes
- **Export Functionality**: Generate reports for team review
- **Customizable Settings**: Personalized accessibility experience

### 🔒 **Privacy & Security**
- **Local Processing**: All scanning happens in your browser
- **No Data Collection**: Zero telemetry or external requests
- **Session-Only**: Changes only affect your current browsing session
- **Secure**: No permissions to read your browsing history

## 🚀 Installation

### Chrome/Edge Installation
1. **Download the Extension**
   - Navigate to the `browser-extension/` folder in this repository
   - Or download the latest release from GitHub

2. **Load Unpacked Extension**
   - Open Chrome/Edge and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `browser-extension/` folder

3. **Pin the Extension**
   - Click the puzzle piece icon in the toolbar
   - Find "Accessibility Toolkit" and click the pin icon
   - The extension icon will now appear in your toolbar

### Firefox Installation
1. **Load Temporary Add-on**
   - Open Firefox and go to `about:debugging`
   - Click "This Firefox" tab
   - Click "Load Temporary Add-on"
   - Select the `manifest.json` file from the `browser-extension/` folder

## 📱 Usage

### **Basic Scanning**
1. **Navigate** to any webpage you want to scan
2. **Click** the Accessibility Toolkit extension icon
3. **Click** "Scan Page" to start accessibility analysis
4. **Review** the detected issues and their severity levels
5. **Apply fixes** for issues you want to resolve

### **Accessibility Toolbar**
1. **Right-click** anywhere on the page
2. **Select** "Show Accessibility Toolbar" from context menu
3. **Use the floating toolbar** for quick accessibility adjustments:
   - **Font Size**: Increase/decrease text size
   - **Contrast**: Toggle high contrast mode
   - **Focus**: Highlight focus indicators
   - **Reading**: Enable distraction-free reading mode

### **Keyboard Shortcuts**
- **Ctrl+Shift+A** (or Cmd+Shift+A on Mac): Toggle accessibility toolbar
- **Ctrl+Shift+F**: Increase font size
- **Ctrl+Shift+G**: Decrease font size
- **Ctrl+Shift+C**: Toggle high contrast
- **Ctrl+Shift+R**: Toggle reading mode

## 🎯 Accessibility Categories

Our extension organizes issues into comprehensive categories:

### **👁️ Visual Accessibility**
- **Alt Text**: Missing or inadequate image descriptions
- **Color Contrast**: Insufficient contrast ratios
- **Focus Indicators**: Missing or invisible focus styles
- **Text Size**: Inadequate font sizes for readability

### **🔊 Auditory Accessibility**
- **Media Captions**: Missing video/audio captions
- **Transcripts**: No text alternatives for audio content
- **Autoplay Controls**: Media that plays without user consent

### **🧠 Cognitive & Neurological**
- **Navigation**: Complex or inconsistent navigation
- **Content Structure**: Poor heading hierarchy
- **Time Limits**: Unreasonable session timeouts
- **Reduced Motion**: No controls for animations

### **⌨️ Keyboard Navigation**
- **Focus Management**: Missing or broken focus indicators
- **Keyboard Traps**: Elements that trap keyboard users
- **Tab Order**: Illogical tab navigation sequence
- **Skip Links**: Missing skip navigation options

### **📝 Form Accessibility**
- **Labels**: Missing or unclear form field labels
- **Error Handling**: Inadequate error messages
- **Validation**: Missing required field indicators
- **ARIA Support**: Insufficient ARIA attributes

### **🔗 Link & Content**
- **Descriptive Text**: Vague link labels like "Click here"
- **Heading Structure**: Improper heading hierarchy
- **Language**: Missing HTML language attributes
- **Page Titles**: Generic or missing page titles

## ⚙️ Configuration

### **Extension Options**
1. **Right-click** the extension icon
2. **Select** "Options" or "Manage Extension"
3. **Customize** your accessibility preferences:
   - **Auto-fix Settings**: Choose which fixes to apply automatically
   - **UI Preferences**: Dark mode, animations, notifications
   - **Scanning Options**: Customize scan behavior
   - **Privacy Settings**: Control data storage and permissions

### **Custom Accessibility Rules**
You can customize the extension's behavior by modifying the configuration:

```javascript
// Example custom configuration
const customConfig = {
  autoFix: {
    fontSizeIncrease: true,
    contrastImprovement: true,
    focusHighlighting: true,
    readingMode: false
  },
  scanning: {
    includeHiddenElements: false,
    maxScanTime: 30000,
    retryFailedScans: true
  }
};
```

## 📊 Report Generation

### **Export Options**
- **HTML Reports**: Professional, interactive reports with issue details
- **JSON Export**: Machine-readable data for analysis
- **CSV Export**: Spreadsheet-friendly format for team review
- **Summary Reports**: Quick overview of accessibility status

### **Report Contents**
Each report includes:
- **Issue Summary**: Count and severity breakdown
- **Detailed Findings**: Specific issues with element locations
- **Suggested Fixes**: Actionable recommendations for developers
- **WCAG References**: Relevant accessibility guidelines
- **Category Breakdown**: Issues organized by accessibility type

## 🧪 Testing & Development

### **Local Development**
1. **Clone** the repository
2. **Navigate** to `browser-extension/` folder
3. **Make changes** to extension files
4. **Reload** the extension in your browser
5. **Test** changes on various websites

### **File Structure**
```
browser-extension/
├── manifest.json          # Extension configuration
├── background/            # Service worker scripts
├── content/               # Content scripts for page interaction
├── popup/                 # Extension popup UI
├── options/               # Extension options page
└── icons/                 # Extension icons
```

### **Key Components**
- **`manifest.json`**: Extension metadata and permissions
- **`background.js`**: Service worker for extension lifecycle
- **`content.js`**: Page scanning and issue detection
- **`accessibility-enhancer.js`**: Real-time accessibility improvements
- **`popup/`**: User interface for scan results and controls

## 🔧 Troubleshooting

### **Common Issues**

**Extension not loading**
- Ensure Developer mode is enabled
- Check for syntax errors in manifest.json
- Try reloading the extension

**Scanning not working**
- Verify the extension has necessary permissions
- Check browser console for error messages
- Ensure the webpage is fully loaded

**Auto-fixes not applying**
- Check if the webpage has restrictive Content Security Policy
- Verify the extension has scripting permissions
- Try refreshing the page and reapplying fixes

**Performance issues**
- Disable auto-fixes for complex pages
- Reduce scan depth in extension options
- Close unnecessary browser tabs

### **Getting Help**
- **Check Console**: Look for error messages in browser console
- **Review Permissions**: Ensure extension has required permissions
- **Test on Simple Pages**: Try scanning basic HTML pages first
- **Report Issues**: Open an issue on GitHub with details

## 🌟 Advanced Features

### **Custom Accessibility Checks**
The extension can be extended with custom accessibility rules:

```javascript
// Example custom check
class CustomAccessibilityCheck {
  check(pageContent) {
    const issues = [];
    // Your custom logic here
    return issues;
  }
}
```

### **Integration with Python Toolkit**
- **Export scan results** to use with the Python toolkit
- **Import custom rules** from Python configuration
- **Generate comprehensive reports** combining both tools

### **API Integration**
- **Webhook support** for automated accessibility monitoring
- **REST API endpoints** for programmatic access
- **WebSocket connections** for real-time updates

## 🤝 Contributing

### **How to Contribute**
1. **Fork** the repository
2. **Create** a feature branch
3. **Make changes** and test thoroughly
4. **Submit** a pull request with detailed description

### **Areas for Improvement**
- **Additional accessibility checks**
- **Enhanced auto-fix capabilities**
- **Better UI/UX design**
- **Performance optimizations**
- **Cross-browser compatibility**

### **Development Guidelines**
- **Follow accessibility best practices** in the extension itself
- **Test on various websites** and browsers
- **Maintain backward compatibility** when possible
- **Document all changes** clearly

## 📄 License

This browser extension is part of the Accessibility Toolkit project and is licensed under the MIT License. See the main [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- **WCAG Guidelines**: Web Content Accessibility Guidelines
- **Browser Extension APIs**: Chrome, Firefox, and Edge extension platforms
- **Accessibility Community**: Ongoing feedback and contributions
- **Open Source Tools**: Libraries and frameworks that make this possible

---

## 🎉 Get Started Today!

Transform your web browsing experience with instant accessibility insights and real-time improvements. The Accessibility Toolkit browser extension puts professional accessibility testing at your fingertips.

**Install now and make the web more accessible for everyone!** 🌐♿

---

*For more information, see the main [README.md](../README.md) or visit our [GitHub repository](https://github.com/yourusername/pythonic-accessibility-toolkit).*
