/**
 * Accessibility Assistant Options Page JavaScript
 * Manages user preferences and settings
 */

class OptionsManager {
    constructor() {
        this.settings = {};
        this.defaultSettings = {
            // General Settings
            enableExtension: true,
            autoScan: false,
            notifications: true,
            
            // Scanning Preferences
            scanImages: true,
            scanForms: true,
            scanHeadings: true,
            scanLinks: true,
            scanARIA: true,
            scanContrast: true,
            
            // Auto-Fix Preferences
            autoFixAltText: false,
            autoFixContrast: false,
            autoFixLabels: false,
            autoFixARIA: false,
            
            // Visual Preferences
            showIssueIndicators: true,
            showFixIndicators: true,
            highContrastMode: false,
            largeFontMode: false,
            
            // Advanced Settings
            debugMode: false,
            performanceMode: false,
            strictMode: false,
            
            // Data Management
            saveScanHistory: true,
            syncSettings: true
        };
        
        this.init();
    }

    async init() {
        try {
            // Load saved settings
            await this.loadSettings();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Populate form with current settings
            this.populateForm();
            
            // Set up auto-save
            this.setupAutoSave();
            
        } catch (error) {
            console.error('Failed to initialize options:', error);
            this.showError('Failed to load settings');
        }
    }

    setupEventListeners() {
        // Save button
        document.getElementById('saveSettingsBtn').addEventListener('click', () => {
            this.saveSettings();
        });

        // Cancel button
        document.getElementById('cancelBtn').addEventListener('click', () => {
            this.resetForm();
        });

        // Export settings
        document.getElementById('exportSettingsBtn').addEventListener('click', () => {
            this.exportSettings();
        });

        // Import settings
        document.getElementById('importSettingsBtn').addEventListener('click', () => {
            this.importSettings();
        });

        // Reset to defaults
        document.getElementById('resetSettingsBtn').addEventListener('click', () => {
            this.resetToDefaults();
        });

        // Clear all data
        document.getElementById('clearDataBtn').addEventListener('click', () => {
            this.clearAllData();
        });

        // Individual setting changes
        this.setupSettingChangeListeners();
    }

    setupSettingChangeListeners() {
        const checkboxes = document.querySelectorAll('.setting-checkbox');
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (event) => {
                const settingId = event.target.id;
                const value = event.target.checked;
                
                // Update settings object
                this.settings[settingId] = value;
                
                // Mark as changed
                this.markSettingChanged(settingId, value);
                
                // Auto-save if enabled
                if (this.autoSaveEnabled) {
                    this.debouncedSave();
                }
            });
        });
    }

    setupAutoSave() {
        // Debounced save function
        this.debouncedSave = this.debounce(() => {
            this.saveSettings();
        }, 1000);

        // Enable auto-save by default
        this.autoSaveEnabled = true;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get(Object.keys(this.defaultSettings));
            
            // Merge with defaults
            this.settings = { ...this.defaultSettings, ...result };
            
        } catch (error) {
            console.error('Failed to load settings:', error);
            // Use default settings if loading fails
            this.settings = { ...this.defaultSettings };
        }
    }

    async saveSettings() {
        try {
            // Save to Chrome storage
            await chrome.storage.sync.set(this.settings);
            
            // Update background script
            await this.updateBackgroundScript();
            
            // Show success message
            this.showSuccess('Settings saved successfully!');
            
            // Clear changed indicators
            this.clearChangedIndicators();
            
        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showError('Failed to save settings');
        }
    }

    async updateBackgroundScript() {
        try {
            await chrome.runtime.sendMessage({
                action: 'updateExtensionState',
                state: this.settings
            });
        } catch (error) {
            console.error('Failed to update background script:', error);
        }
    }

    populateForm() {
        // Set all checkbox values
        Object.keys(this.settings).forEach(settingId => {
            const checkbox = document.getElementById(settingId);
            if (checkbox) {
                checkbox.checked = this.settings[settingId];
            }
        });
    }

    resetForm() {
        // Reset form to current saved settings
        this.populateForm();
        this.clearChangedIndicators();
        this.showInfo('Form reset to current settings');
    }

    async resetToDefaults() {
        if (confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
            try {
                // Reset settings to defaults
                this.settings = { ...this.defaultSettings };
                
                // Save to storage
                await chrome.storage.sync.set(this.settings);
                
                // Update background script
                await this.updateBackgroundScript();
                
                // Update form
                this.populateForm();
                
                // Clear changed indicators
                this.clearChangedIndicators();
                
                this.showSuccess('Settings reset to defaults successfully!');
                
            } catch (error) {
                console.error('Failed to reset settings:', error);
                this.showError('Failed to reset settings');
            }
        }
    }

    async clearAllData() {
        if (confirm('Are you sure you want to clear all data? This will remove all scan history and settings. This cannot be undone.')) {
            try {
                // Clear all storage
                await chrome.storage.sync.clear();
                await chrome.storage.local.clear();
                
                // Reset to defaults
                this.settings = { ...this.defaultSettings };
                
                // Update background script
                await this.updateBackgroundScript();
                
                // Update form
                this.populateForm();
                
                this.showSuccess('All data cleared successfully!');
                
            } catch (error) {
                console.error('Failed to clear data:', error);
                this.showError('Failed to clear data');
            }
        }
    }

    exportSettings() {
        try {
            const exportData = {
                version: '1.0.0',
                timestamp: new Date().toISOString(),
                settings: this.settings
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                type: 'application/json'
            });

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `accessibility-assistant-settings-${new Date().toISOString().split('T')[0]}.json`;
            a.click();

            URL.revokeObjectURL(url);
            this.showSuccess('Settings exported successfully!');
            
        } catch (error) {
            console.error('Failed to export settings:', error);
            this.showError('Failed to export settings');
        }
    }

    importSettings() {
        const fileInput = document.getElementById('importFileInput');
        fileInput.click();
        
        fileInput.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            try {
                const text = await file.text();
                const importData = JSON.parse(text);

                // Validate import data
                if (!this.validateImportData(importData)) {
                    throw new Error('Invalid settings file format');
                }

                // Import settings
                this.settings = { ...this.defaultSettings, ...importData.settings };
                
                // Save to storage
                await chrome.storage.sync.set(this.settings);
                
                // Update background script
                await this.updateBackgroundScript();
                
                // Update form
                this.populateForm();
                
                this.showSuccess('Settings imported successfully!');
                
            } catch (error) {
                console.error('Failed to import settings:', error);
                this.showError('Failed to import settings: ' + error.message);
            }

            // Reset file input
            fileInput.value = '';
        });
    }

    validateImportData(data) {
        return data && 
               data.version && 
               data.settings && 
               typeof data.settings === 'object';
    }

    markSettingChanged(settingId, value) {
        const settingItem = document.getElementById(settingId).closest('.setting-item');
        if (settingItem) {
            settingItem.classList.add('changed');
            
            // Remove changed indicator after a delay
            setTimeout(() => {
                settingItem.classList.remove('changed');
            }, 2000);
        }
    }

    clearChangedIndicators() {
        const changedItems = document.querySelectorAll('.setting-item.changed');
        changedItems.forEach(item => {
            item.classList.remove('changed');
        });
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '6px',
            color: 'white',
            zIndex: '10000',
            maxWidth: '300px',
            animation: 'slideInRight 0.3s ease-out'
        });

        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.background = '#28a745';
                break;
            case 'error':
                notification.style.background = '#dc3545';
                break;
            case 'info':
            default:
                notification.style.background = '#007acc';
                break;
        }

        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    // Utility methods
    getSetting(settingId) {
        return this.settings[settingId] || this.defaultSettings[settingId];
    }

    setSetting(settingId, value) {
        this.settings[settingId] = value;
    }

    async refreshSettings() {
        await this.loadSettings();
        this.populateForm();
    }
}

// Initialize options manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new OptionsManager();
});

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
