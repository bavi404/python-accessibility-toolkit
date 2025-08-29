/**
 * Accessibility Enhancer Content Script
 * Provides real-time accessibility improvements to any website
 */

class AccessibilityEnhancer {
    constructor() {
        this.settings = {
            fontSize: 100,
            contrast: 'normal',
            focusHighlight: true,
            readingMode: false
        };
        
        this.init();
    }
    
    init() {
        this.loadSettings();
        this.createToolbar();
        this.applySettings();
        this.addKeyboardShortcuts();
        
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sendResponse);
            return true;
        });
    }
    
    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get(['accessibilitySettings']);
            if (result.accessibilitySettings) {
                this.settings = { ...this.settings, ...result.accessibilitySettings };
            }
        } catch (error) {
            console.log('Using default accessibility settings');
        }
    }
    
    async saveSettings() {
        try {
            await chrome.storage.sync.set({ accessibilitySettings: this.settings });
        } catch (error) {
            console.error('Failed to save settings:', error);
        }
    }
    
    createToolbar() {
        const existingToolbar = document.getElementById('accessibility-toolbar');
        if (existingToolbar) existingToolbar.remove();
        
        const toolbar = document.createElement('div');
        toolbar.id = 'accessibility-toolbar';
        toolbar.innerHTML = `
            <div class="accessibility-toolbar">
                <div class="toolbar-section">
                    <label>Font Size:</label>
                    <button class="font-size-btn" data-action="decrease">A-</button>
                    <span class="font-size-display">${this.settings.fontSize}%</span>
                    <button class="font-size-btn" data-action="increase">A+</button>
                    <button class="font-size-btn" data-action="reset">Reset</button>
                </div>
                
                <div class="toolbar-section">
                    <label>Contrast:</label>
                    <button class="contrast-btn" data-contrast="normal">Normal</button>
                    <button class="contrast-btn" data-contrast="high">High</button>
                    <button class="contrast-btn" data-contrast="very-high">Very High</button>
                </div>
                
                <div class="toolbar-section">
                    <label>Focus:</label>
                    <button class="focus-btn" data-action="toggle">${this.settings.focusHighlight ? 'Hide' : 'Show'}</button>
                </div>
                
                <div class="toolbar-section">
                    <label>Reading:</label>
                    <button class="reading-btn" data-action="toggle">${this.settings.readingMode ? 'Normal' : 'Reading'}</button>
                </div>
                
                <button class="close-toolbar-btn" title="Close toolbar">×</button>
            </div>
        `;
        
        this.addToolbarEventListeners(toolbar);
        document.body.appendChild(toolbar);
        this.addToolbarStyles();
    }
    
    addToolbarEventListeners(toolbar) {
        // Font size controls
        toolbar.querySelectorAll('.font-size-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                if (action === 'decrease') {
                    this.settings.fontSize = Math.max(50, this.settings.fontSize - 10);
                } else if (action === 'increase') {
                    this.settings.fontSize = Math.min(300, this.settings.fontSize + 10);
                } else if (action === 'reset') {
                    this.settings.fontSize = 100;
                }
                this.applyFontSize();
                this.updateToolbarDisplay();
                this.saveSettings();
            });
        });
        
        // Contrast controls
        toolbar.querySelectorAll('.contrast-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.settings.contrast = e.target.dataset.contrast;
                this.applyContrast();
                this.updateToolbarDisplay();
                this.saveSettings();
            });
        });
        
        // Focus highlight toggle
        toolbar.querySelector('.focus-btn').addEventListener('click', (e) => {
            this.settings.focusHighlight = !this.settings.focusHighlight;
            this.applyFocusHighlight();
            this.updateToolbarDisplay();
            this.saveSettings();
        });
        
        // Reading mode toggle
        toolbar.querySelector('.reading-btn').addEventListener('click', (e) => {
            this.settings.readingMode = !this.settings.readingMode;
            this.applyReadingMode();
            this.updateToolbarDisplay();
            this.saveSettings();
        });
        
        // Close button
        toolbar.querySelector('.close-toolbar-btn').addEventListener('click', () => {
            toolbar.style.display = 'none';
        });
    }
    
    updateToolbarDisplay() {
        const toolbar = document.getElementById('accessibility-toolbar');
        if (!toolbar) return;
        
        toolbar.querySelector('.font-size-display').textContent = `${this.settings.fontSize}%`;
        toolbar.querySelector('.focus-btn').textContent = this.settings.focusHighlight ? 'Hide' : 'Show';
        toolbar.querySelector('.reading-btn').textContent = this.settings.readingMode ? 'Normal' : 'Reading';
        this.updateActiveStates(toolbar);
    }
    
    updateActiveStates(toolbar) {
        toolbar.querySelectorAll('.contrast-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.contrast === this.settings.contrast);
        });
    }
    
    applySettings() {
        this.applyFontSize();
        this.applyContrast();
        this.applyFocusHighlight();
        this.applyReadingMode();
    }
    
    applyFontSize() {
        const style = document.createElement('style');
        style.id = 'accessibility-font-size';
        style.textContent = `* { font-size: ${this.settings.fontSize}% !important; }`;
        this.replaceStyle('accessibility-font-size', style);
    }
    
    applyContrast() {
        const style = document.createElement('style');
        style.id = 'accessibility-contrast';
        
        let contrastRules = '';
        switch (this.settings.contrast) {
            case 'high':
                contrastRules = `
                    * { color: #000000 !important; background-color: #ffffff !important; }
                    a { color: #0000EE !important; }
                    button { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #000000 !important; }
                `;
                break;
            case 'very-high':
                contrastRules = `
                    * { color: #000000 !important; background-color: #ffffff !important; }
                    a { color: #0000EE !important; }
                    button { color: #000000 !important; background-color: #ffffff !important; border: 3px solid #000000 !important; }
                    input, textarea, select { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #000000 !important; }
                `;
                break;
        }
        
        style.textContent = contrastRules;
        this.replaceStyle('accessibility-contrast', style);
    }
    
    applyFocusHighlight() {
        const style = document.createElement('style');
        style.id = 'accessibility-focus';
        
        if (this.settings.focusHighlight) {
            style.textContent = `
                *:focus { outline: 3px solid #ff6b35 !important; outline-offset: 2px !important; background-color: #fff3cd !important; }
                a:focus, button:focus, input:focus, textarea:focus, select:focus { box-shadow: 0 0 0 3px #ff6b35 !important; }
            `;
        } else {
            style.textContent = '';
        }
        
        this.replaceStyle('accessibility-focus', style);
    }
    
    applyReadingMode() {
        const style = document.createElement('style');
        style.id = 'accessibility-reading';
        
        if (this.settings.readingMode) {
            style.textContent = `
                body { max-width: 800px !important; margin: 0 auto !important; padding: 20px !important; line-height: 1.6 !important; font-size: 18px !important; }
                .ad, .advertisement, [class*="ad-"], [id*="ad-"] { display: none !important; }
                nav, .navigation, .sidebar, .footer { display: none !important; }
                img:not([alt]) { display: none !important; }
            `;
        } else {
            style.textContent = '';
        }
        
        this.replaceStyle('accessibility-reading', style);
    }
    
    replaceStyle(id, newStyle) {
        const existing = document.getElementById(id);
        if (existing) existing.remove();
        document.head.appendChild(newStyle);
    }
    
    addToolbarStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .accessibility-toolbar {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #ffffff;
                border: 2px solid #667eea;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                min-width: 300px;
                max-width: 400px;
            }
            
            .toolbar-section {
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
            }
            
            .toolbar-section label {
                font-weight: 600;
                color: #374151;
                min-width: 80px;
            }
            
            .accessibility-toolbar button {
                padding: 6px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: #ffffff;
                color: #374151;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s ease;
            }
            
            .accessibility-toolbar button:hover {
                background: #f3f4f6;
                border-color: #9ca3af;
            }
            
            .accessibility-toolbar button.active {
                background: #667eea;
                color: #ffffff;
                border-color: #667eea;
            }
            
            .font-size-display {
                font-weight: 600;
                color: #667eea;
                min-width: 50px;
                text-align: center;
            }
            
            .close-toolbar-btn {
                position: absolute;
                top: 8px;
                right: 8px;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                border: none;
                background: #ef4444;
                color: white;
                cursor: pointer;
                font-size: 16px;
                line-height: 1;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .close-toolbar-btn:hover {
                background: #dc2626;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    addKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'A') {
                e.preventDefault();
                const toolbar = document.getElementById('accessibility-toolbar');
                if (toolbar) {
                    toolbar.style.display = toolbar.style.display === 'none' ? 'block' : 'none';
                }
            }
            
            if ((e.ctrlKey || e.metaKey) && e.shiftKey) {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.settings.fontSize = Math.min(300, this.settings.fontSize + 10);
                    this.applyFontSize();
                    this.updateToolbarDisplay();
                    this.saveSettings();
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.settings.fontSize = Math.max(50, this.settings.fontSize - 10);
                    this.applyFontSize();
                    this.updateToolbarDisplay();
                    this.saveSettings();
                }
            }
        });
    }
    
    handleMessage(request, sendResponse) {
        switch (request.action) {
            case 'getSettings':
                sendResponse({ settings: this.settings });
                break;
            case 'updateSettings':
                this.settings = { ...this.settings, ...request.settings };
                this.applySettings();
                this.updateToolbarDisplay();
                this.saveSettings();
                sendResponse({ success: true });
                break;
            case 'showToolbar':
                const toolbar = document.getElementById('accessibility-toolbar');
                if (toolbar) toolbar.style.display = 'block';
                sendResponse({ success: true });
                break;
            case 'hideToolbar':
                const toolbar2 = document.getElementById('accessibility-toolbar');
                if (toolbar2) toolbar2.style.display = 'none';
                sendResponse({ success: true });
                break;
            default:
                sendResponse({ error: 'Unknown action' });
        }
    }
}

// Initialize the accessibility enhancer
new AccessibilityEnhancer();
