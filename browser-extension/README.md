# Accessibility Assistant Browser Extension

A powerful browser extension that automatically detects accessibility issues on web pages and provides real-time fixes to improve your browsing experience.

## 🌟 Features

### **Instant Accessibility Scanning**
- **One-click scanning** of any web page
- **Real-time detection** of accessibility issues
- **Comprehensive coverage** including alt text, color contrast, headings, forms, and more

### **Smart Auto-Fixes**
- **Temporary fixes** that don't permanently change websites
- **Intelligent suggestions** for missing alt text, form labels, and ARIA attributes
- **Visual improvements** like high contrast mode and font size adjustments
- **Easy reversion** of all applied fixes

### **User-Friendly Interface**
- **Clean popup interface** with issue categorization by severity
- **Detailed reports** with actionable suggestions
- **Export functionality** for team reviews and documentation
- **Customizable settings** for personalized experience

## 🚀 Installation

### **Chrome/Edge (Chromium-based browsers)**

1. **Download the extension:**
   - Clone this repository or download the `browser-extension` folder
   - Ensure all files are present in the folder structure

2. **Enable Developer Mode:**
   - Open Chrome/Edge and go to `chrome://extensions/`
   - Toggle "Developer mode" in the top right corner

3. **Load the extension:**
   - Click "Load unpacked"
   - Select the `browser-extension` folder
   - The extension should now appear in your extensions list

4. **Pin the extension:**
   - Click the puzzle piece icon in your toolbar
   - Find "Accessibility Assistant" and click the pin icon

### **Firefox**

1. **Download the extension:**
   - Clone this repository or download the `browser-extension` folder

2. **Load the extension:**
   - Open Firefox and go to `about:debugging`
   - Click "This Firefox" tab
   - Click "Load Temporary Add-on"
   - Select the `manifest.json` file from the extension folder

## 📱 Usage

### **Basic Scanning**

1. **Navigate to any website** you want to check
2. **Click the Accessibility Assistant icon** in your browser toolbar
3. **Click "Scan Page"** to start the accessibility analysis
4. **Review the results** organized by severity (Critical, Moderate, Low)
5. **Select fixes** you want to apply by checking the boxes
6. **Click "Apply Selected Fixes"** to implement temporary improvements

### **Understanding Results**

The extension categorizes issues by severity:

- **🔴 Critical**: Missing alt text, form labels, keyboard navigation issues
- **🟠 Moderate**: Color contrast problems, heading structure issues
- **🟢 Low**: Minor accessibility concerns, best practice violations

### **Applying Fixes**

- **Alt Text**: Automatically generates descriptive text for images
- **Color Contrast**: Applies high-contrast colors for better readability
- **Form Labels**: Adds temporary labels to unlabeled form elements
- **ARIA Issues**: Removes invalid ARIA attributes
- **Keyboard Navigation**: Improves focus management

### **Reverting Changes**

- **Click "Revert Changes"** to undo all applied fixes
- **Refresh the page** to completely restore the original state
- **Individual fixes** can be reverted by toggling the checkboxes

## ⚙️ Configuration

### **Accessing Settings**

1. **Click the extension icon** in your toolbar
2. **Click the settings link** (⚙️) in the footer
3. **Customize your experience** with comprehensive options

### **Available Settings**

#### **General Settings**
- Enable/disable the extension
- Auto-scan pages on load
- Show notifications for issues

#### **Scanning Preferences**
- Choose which accessibility checks to run
- Configure scanning behavior
- Set performance vs. thoroughness balance

#### **Auto-Fix Preferences**
- Enable automatic fixes for common issues
- Set default behavior for different issue types
- Configure fix application rules

#### **Visual Preferences**
- Show issue indicators on pages
- Enable high contrast mode
- Adjust font sizes for readability

#### **Advanced Settings**
- Debug mode for developers
- Performance optimization options
- Strict accessibility guidelines

## 🔧 Development

### **Project Structure**

```
browser-extension/
├── manifest.json          # Extension configuration
├── popup/                 # Popup interface
│   ├── popup.html        # Main popup HTML
│   ├── popup.css         # Popup styling
│   └── popup.js          # Popup logic
├── content/               # Content scripts
│   ├── content.js        # Page scanning and fixes
│   └── content.css       # Visual indicators
├── background/            # Background service worker
│   └── background.js     # Extension lifecycle management
├── options/               # Settings page
│   ├── options.html      # Options interface
│   ├── options.css       # Options styling
│   └── options.js        # Options logic
└── icons/                 # Extension icons
    ├── icon16.png        # 16x16 icon
    ├── icon32.png        # 32x32 icon
    ├── icon48.png        # 48x48 icon
    └── icon128.png       # 128x128 icon
```

### **Key Components**

#### **Content Script (`content.js`)**
- Runs on web pages to scan for accessibility issues
- Applies temporary fixes and visual improvements
- Monitors page changes for dynamic content

#### **Popup Interface (`popup/`)**
- User-friendly interface for scanning and results
- Issue categorization and fix selection
- Export and reporting functionality

#### **Background Service Worker (`background.js`)**
- Manages extension lifecycle and state
- Handles communication between components
- Manages tab updates and notifications

#### **Options Page (`options/`)**
- Comprehensive settings management
- Import/export configuration
- User preference storage

### **Adding New Accessibility Checks**

1. **Extend the `AccessibilityScanner` class** in `content.js`
2. **Add new check methods** following the existing pattern
3. **Update the `scanPage()` method** to include your new checks
4. **Add corresponding fix methods** if applicable
5. **Update the popup interface** to display new issue types

### **Example: Adding a New Check**

```javascript
async checkCustomIssue() {
    const elements = document.querySelectorAll('.custom-selector');
    
    elements.forEach((element) => {
        if (this.hasCustomIssue(element)) {
            this.scanResults.push({
                type: 'custom_issue',
                severity: 'moderate',
                description: 'Custom accessibility issue found',
                element: element.outerHTML.substring(0, 100),
                context: this.getElementContext(element),
                suggestedFix: 'Custom fix suggestion',
                fixable: true
            });
        }
    });
}
```

## 🧪 Testing

### **Testing the Extension**

1. **Load the extension** in developer mode
2. **Navigate to test websites** with known accessibility issues
3. **Run scans** and verify issue detection
4. **Apply fixes** and check visual improvements
5. **Test reversion** functionality
6. **Verify settings** persistence and sync

### **Test Websites**

- **Accessibility Test Pages**: Use sites designed to test accessibility tools
- **Real Websites**: Test on popular sites to find real-world issues
- **Complex Applications**: Test on SPAs and dynamic content

### **Debugging**

- **Enable debug mode** in extension settings
- **Check browser console** for detailed logging
- **Use Chrome DevTools** to inspect extension components
- **Monitor network requests** for any API calls

## 📊 Performance

### **Optimization Features**

- **Debounced scanning** to avoid excessive page analysis
- **Selective checking** based on user preferences
- **Performance mode** for faster, less thorough scans
- **Efficient DOM queries** using modern selectors

### **Memory Management**

- **Cleanup of applied fixes** when reverting
- **Efficient storage** of original page state
- **Minimal memory footprint** for long browsing sessions

## 🔒 Privacy & Security

### **Data Handling**

- **No data collection** from web pages
- **Local storage only** for user preferences
- **No external API calls** for scanning
- **Privacy-first design** with user control

### **Security Features**

- **Content script isolation** from web page JavaScript
- **Limited permissions** only for necessary functionality
- **Secure communication** between extension components
- **No persistent tracking** of user behavior

## 🌐 Browser Compatibility

### **Supported Browsers**

- **Chrome 88+** (Manifest V3)
- **Edge 88+** (Chromium-based)
- **Firefox 109+** (with limitations)

### **Feature Support**

| Feature | Chrome | Edge | Firefox |
|---------|--------|------|---------|
| Basic Scanning | ✅ | ✅ | ✅ |
| Auto-Fixes | ✅ | ✅ | ⚠️ |
| Settings Sync | ✅ | ✅ | ⚠️ |
| Notifications | ✅ | ✅ | ⚠️ |
| Context Menus | ✅ | ✅ | ❌ |

## 🤝 Contributing

### **How to Contribute**

1. **Fork the repository**
2. **Create a feature branch** for your changes
3. **Implement improvements** following the existing patterns
4. **Test thoroughly** across different browsers
5. **Submit a pull request** with detailed description

### **Areas for Improvement**

- **Additional accessibility checks** for modern web standards
- **Enhanced fix algorithms** for complex issues
- **Better visual indicators** for different issue types
- **Performance optimizations** for large pages
- **Accessibility improvements** to the extension itself

### **Code Standards**

- **ES6+ JavaScript** with async/await
- **Modern CSS** with flexbox and grid
- **Semantic HTML** for accessibility
- **Consistent naming** conventions
- **Comprehensive error handling**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- **WCAG Guidelines** for accessibility standards
- **Chrome Extensions API** for browser integration
- **Modern web standards** for implementation patterns
- **Accessibility community** for feedback and testing

## 📞 Support

### **Getting Help**

- **Check the documentation** for common issues
- **Review the code** for implementation details
- **Open an issue** for bugs or feature requests
- **Join discussions** in the project community

### **Reporting Issues**

When reporting issues, please include:

- **Browser version** and operating system
- **Extension version** and settings
- **Steps to reproduce** the problem
- **Expected vs. actual behavior**
- **Console errors** or screenshots if applicable

---

**Together, let's make the web more accessible for everyone!** 🌐♿
