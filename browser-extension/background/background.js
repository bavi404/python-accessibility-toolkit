/**
 * Accessibility Assistant Background Service Worker
 * Manages extension lifecycle and communication
 */

class AccessibilityBackground {
    constructor() {
        this.activeTabs = new Map();
        this.extensionState = {
            isEnabled: true,
            autoScan: false,
            notifications: true
        };
        this.init();
    }

    init() {
        // Set up event listeners
        this.setupEventListeners();
        
        // Load saved state
        this.loadExtensionState();
        
        // Initialize badge
        this.updateBadge();
    }

    setupEventListeners() {
        // Extension installation
        chrome.runtime.onInstalled.addListener((details) => {
            this.handleInstallation(details);
        });

        // Tab updates
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            this.handleTabUpdate(tabId, changeInfo, tab);
        });

        // Tab activation
        chrome.tabs.onActivated.addListener((activeInfo) => {
            this.handleTabActivation(activeInfo);
        });

        // Tab removal
        chrome.tabs.onRemoved.addListener((tabId) => {
            this.handleTabRemoval(tabId);
        });

        // Message handling
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sender, sendResponse);
            return true; // Keep message channel open for async response
        });

        // Context menu creation
        chrome.runtime.onStartup.addListener(() => {
            this.createContextMenus();
        });

        chrome.runtime.onInstalled.addListener(() => {
            this.createContextMenus();
        });
    }

    handleInstallation(details) {
        if (details.reason === 'install') {
            // First time installation
            this.showWelcomeNotification();
            this.openOptionsPage();
        } else if (details.reason === 'update') {
            // Extension update
            this.showUpdateNotification();
        }
    }

    async handleTabUpdate(tabId, changeInfo, tab) {
        if (changeInfo.status === 'complete' && tab.url) {
            // Page has finished loading
            this.activeTabs.set(tabId, {
                url: tab.url,
                title: tab.title,
                lastUpdated: Date.now()
            });

            // Auto-scan if enabled
            if (this.extensionState.autoScan && this.isAccessiblePage(tab.url)) {
                await this.autoScanTab(tabId);
            }

            // Update badge
            this.updateBadge();
        }
    }

    handleTabActivation(activeInfo) {
        const tab = this.activeTabs.get(activeInfo.tabId);
        if (tab) {
            // Update badge for active tab
            this.updateBadge(activeInfo.tabId);
        }
    }

    handleTabRemoval(tabId) {
        this.activeTabs.delete(tabId);
        this.updateBadge();
    }

    async handleMessage(request, sender, sendResponse) {
        try {
            switch (request.action) {
                case 'getExtensionState':
                    sendResponse({ success: true, state: this.extensionState });
                    break;

                case 'updateExtensionState':
                    this.extensionState = { ...this.extensionState, ...request.state };
                    await this.saveExtensionState();
                    sendResponse({ success: true });
                    break;

                case 'scanTab':
                    const result = await this.scanTab(request.tabId);
                    sendResponse({ success: true, result });
                    break;

                case 'getTabInfo':
                    const tabInfo = this.activeTabs.get(request.tabId);
                    sendResponse({ success: true, tabInfo });
                    break;

                case 'showNotification':
                    this.showNotification(request.message, request.type);
                    sendResponse({ success: true });
                    break;

                default:
                    sendResponse({ success: false, error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Background script error:', error);
            sendResponse({ success: false, error: error.message });
        }
    }

    async autoScanTab(tabId) {
        try {
            // Wait a bit for the page to fully render
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Send message to content script to scan
            const response = await chrome.tabs.sendMessage(tabId, {
                action: 'scanAccessibility'
            });

            if (response.success && response.issues.length > 0) {
                // Update badge with issue count
                this.updateBadge(tabId, response.issues.length);
                
                // Show notification if enabled
                if (this.extensionState.notifications) {
                    this.showNotification(
                        `Found ${response.issues.length} accessibility issues on this page`,
                        'info'
                    );
                }
            }
        } catch (error) {
            console.error('Auto-scan failed:', error);
        }
    }

    async scanTab(tabId) {
        try {
            const response = await chrome.tabs.sendMessage(tabId, {
                action: 'scanAccessibility'
            });

            if (response.success) {
                return {
                    issues: response.issues,
                    timestamp: Date.now()
                };
            } else {
                throw new Error(response.error || 'Scan failed');
            }
        } catch (error) {
            console.error('Tab scan failed:', error);
            throw error;
        }
    }

    isAccessiblePage(url) {
        // Check if the page is accessible (not a chrome://, file://, etc.)
        try {
            const urlObj = new URL(url);
            return ['http:', 'https:'].includes(urlObj.protocol);
        } catch {
            return false;
        }
    }

    updateBadge(tabId = null) {
        if (tabId) {
            // Update badge for specific tab
            const tab = this.activeTabs.get(tabId);
            if (tab) {
                // This would be updated after scanning
                chrome.action.setBadgeText({ 
                    text: '', 
                    tabId: tabId 
                });
            }
        } else {
            // Update global badge
            const totalIssues = this.getTotalIssues();
            if (totalIssues > 0) {
                chrome.action.setBadgeText({ 
                    text: totalIssues.toString() 
                });
                chrome.action.setBadgeBackgroundColor({ 
                    color: '#dc3545' 
                });
            } else {
                chrome.action.setBadgeText({ text: '' });
            }
        }
    }

    getTotalIssues() {
        // This would be calculated from all active tabs
        // For now, return 0
        return 0;
    }

    showWelcomeNotification() {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: 'Accessibility Assistant Installed!',
            message: 'Thank you for installing the Accessibility Assistant. Click the extension icon to start scanning pages for accessibility issues.'
        });
    }

    showUpdateNotification() {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: 'Accessibility Assistant Updated!',
            message: 'The Accessibility Assistant has been updated with new features and improvements.'
        });
    }

    showNotification(message, type = 'info') {
        // Show in-page notification via content script
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, {
                    action: 'showNotification',
                    message: message,
                    type: type
                }).catch(() => {
                    // Content script not ready, fallback to browser notification
                    chrome.notifications.create({
                        type: 'basic',
                        iconUrl: 'icons/icon128.png',
                        title: 'Accessibility Assistant',
                        message: message
                    });
                });
            }
        });
    }

    createContextMenus() {
        // Create context menu for right-click actions
        chrome.contextMenus.create({
            id: 'scanPage',
            title: 'Scan for Accessibility Issues',
            contexts: ['page']
        });

        chrome.contextMenus.create({
            id: 'accessibilityOptions',
            title: 'Accessibility Options',
            contexts: ['page']
        });

        chrome.contextMenus.create({
            id: 'showAccessibilityToolbar',
            title: 'Show Accessibility Toolbar',
            contexts: ['page']
        });

        // Handle context menu clicks
        chrome.contextMenus.onClicked.addListener((info, tab) => {
            this.handleContextMenuClick(info, tab);
        });
    }

    handleContextMenuClick(info, tab) {
        switch (info.menuItemId) {
            case 'scanPage':
                this.scanTab(tab.id).then(result => {
                    this.showNotification(
                        `Found ${result.issues.length} accessibility issues`,
                        'info'
                    );
                }).catch(error => {
                    this.showNotification('Scan failed: ' + error.message, 'error');
                });
                break;

            case 'accessibilityOptions':
                chrome.runtime.openOptionsPage();
                break;

            case 'showAccessibilityToolbar':
                chrome.tabs.sendMessage(tab.id, { action: 'showToolbar' }).catch(() => {
                    this.showNotification('Please refresh the page to use accessibility features', 'warning');
                });
                break;
        }
    }

    openOptionsPage() {
        chrome.runtime.openOptionsPage();
    }

    async loadExtensionState() {
        try {
            const result = await chrome.storage.sync.get([
                'isEnabled',
                'autoScan',
                'notifications'
            ]);

            this.extensionState = {
                ...this.extensionState,
                ...result
            };
        } catch (error) {
            console.error('Failed to load extension state:', error);
        }
    }

    async saveExtensionState() {
        try {
            await chrome.storage.sync.set(this.extensionState);
        } catch (error) {
            console.error('Failed to save extension state:', error);
        }
    }

    // Utility methods
    getActiveTab() {
        return new Promise((resolve) => {
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                resolve(tabs[0]);
            });
        });
    }

    async injectContentScript(tabId) {
        try {
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                files: ['content/content.js']
            });
        } catch (error) {
            console.error('Failed to inject content script:', error);
        }
    }

    async injectCSS(tabId) {
        try {
            await chrome.scripting.insertCSS({
                target: { tabId: tabId },
                files: ['content/content.css']
            });
        } catch (error) {
            console.error('Failed to inject CSS:', error);
        }
    }
}

// Initialize the background service worker
new AccessibilityBackground();
