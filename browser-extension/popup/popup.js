/**
 * Accessibility Assistant Popup JavaScript
 * Handles the popup interface, scanning, and fix application
 */

class AccessibilityPopup {
    constructor() {
        this.currentTab = null;
        this.scanResults = [];
        this.appliedFixes = [];
        this.init();
    }

    async init() {
        try {
            // Get current active tab
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            this.currentTab = tabs[0];
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load user preferences
            await this.loadPreferences();
            
            // Auto-scan if enabled
            if (await this.shouldAutoScan()) {
                this.startScan();
            }
        } catch (error) {
            console.error('Failed to initialize popup:', error);
            this.showError('Failed to initialize extension');
        }
    }

    setupEventListeners() {
        // Scan button
        document.getElementById('scanBtn').addEventListener('click', () => {
            this.startScan();
        });

        // Apply fixes button
        document.getElementById('applyFixesBtn').addEventListener('click', () => {
            this.applySelectedFixes();
        });

        // Revert fixes button
        document.getElementById('revertFixesBtn').addEventListener('click', () => {
            this.revertFixes();
        });

        // Export report button
        document.getElementById('exportReportBtn').addEventListener('click', () => {
            this.exportReport();
        });

        // Retry button
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.startScan();
        });

        // Toolbar controls
        document.getElementById('showToolbarBtn').addEventListener('click', () => {
            this.showToolbar();
        });

        document.getElementById('hideToolbarBtn').addEventListener('click', () => {
            this.hideToolbar();
        });

        // Filters: severity chips
        const chips = [
            'chipAll', 'chipCritical', 'chipModerate', 'chipLow'
        ];
        chips.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('click', (e) => {
                    chips.forEach(cid => document.getElementById(cid).classList.remove('active'));
                    e.currentTarget.classList.add('active');
                    this.applyFilters();
                });
            }
        });

        // Filters: search
        const search = document.getElementById('searchInput');
        if (search) {
            search.addEventListener('input', () => this.applyFilters());
        }
    }

    async startScan() {
        try {
            this.showLoading();
            
            // Send message to content script to start scanning
            const response = await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'scanAccessibility'
            });

            if (response.success) {
                this.scanResults = response.issues;
                this.displayResults();
            } else {
                throw new Error(response.error || 'Scan failed');
            }
        } catch (error) {
            console.error('Scan error:', error);
            this.showError('Failed to scan page. Make sure the page is fully loaded.');
        }
    }

    displayResults() {
        this.hideAllStates();
        
        if (this.scanResults.length === 0) {
            this.showNoIssues();
            return;
        }

        // Show results container with animation
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.style.display = 'block';
        resultsContainer.style.opacity = '0';
        resultsContainer.style.transform = 'translateY(20px)';
        
        // Update summary stats
        this.updateSummaryStats();
        
        // Populate issues list
        this.populateIssuesList();
        
        // Show/hide apply fixes button based on selectable fixes
        this.updateApplyButton();
        
        // Animate in
        setTimeout(() => {
            resultsContainer.style.transition = 'all 0.5s ease';
            resultsContainer.style.opacity = '1';
            resultsContainer.style.transform = 'translateY(0)';
        }, 100);
    }

    updateSummaryStats() {
        const critical = this.scanResults.filter(issue => issue.severity === 'critical').length;
        const moderate = this.scanResults.filter(issue => issue.severity === 'moderate').length;
        const low = this.scanResults.filter(issue => issue.severity === 'low').length;

        document.getElementById('criticalCount').textContent = critical;
        document.getElementById('moderateCount').textContent = moderate;
        document.getElementById('lowCount').textContent = low;
    }

    populateIssuesList() {
        const issuesList = document.getElementById('issuesList');
        const template = document.getElementById('issueTemplate');
        
        // Clear existing issues
        issuesList.innerHTML = '';
        
        this.filteredResults = this.getFilteredResults();
        this.filteredResults.forEach((issue, index) => {
            const issueElement = this.createIssueElement(issue, index, template);
            issueElement.style.opacity = '0';
            issueElement.style.transform = 'translateX(-20px)';
            issuesList.appendChild(issueElement);
            
            // Staggered animation
            setTimeout(() => {
                issueElement.style.transition = 'all 0.4s ease';
                issueElement.style.opacity = '1';
                issueElement.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }

    getFilteredResults() {
        const activeChip = document.querySelector('.chip.active');
        const severity = activeChip ? activeChip.dataset.severity : 'all';
        const q = (document.getElementById('searchInput')?.value || '').toLowerCase();

        return this.scanResults.filter(issue => {
            const matchSeverity = severity === 'all' ? true : issue.severity === severity;
            const hay = `${issue.type} ${issue.description} ${issue.element} ${issue.context} ${issue.suggestedFix}`.toLowerCase();
            const matchQuery = q ? hay.includes(q) : true;
            return matchSeverity && matchQuery;
        });
    }

    applyFilters() {
        this.populateIssuesList();
        this.updateApplyButton();
        this.updateSummaryStats();
    }

    createIssueElement(issue, index, template) {
        const clone = template.content.cloneNode(true);
        const issueItem = clone.querySelector('.issue-item');
        
        // Set issue data
        issueItem.dataset.issueId = index;
        issueItem.dataset.issueType = issue.type;
        
        // Set severity badge
        const severityBadge = issueItem.querySelector('.severity-badge');
        severityBadge.textContent = issue.severity;
        severityBadge.className = `severity-badge ${issue.severity}`;
        
        // Set issue type
        issueItem.querySelector('.issue-type').textContent = issue.type.replace(/_/g, ' ');
        
        // Set description
        issueItem.querySelector('.issue-description').textContent = issue.description;
        
        // Set element info
        issueItem.querySelector('.element-text').textContent = issue.element || 'N/A';
        
        // Set context
        issueItem.querySelector('.context-text').textContent = issue.context || 'N/A';
        
        // Set suggested fix
        issueItem.querySelector('.fix-text').textContent = issue.suggestedFix || 'No specific fix suggested.';
        
        // Set up fix checkbox
        const fixToggle = issueItem.querySelector('.fix-toggle');
        fixToggle.addEventListener('change', () => {
            this.updateApplyButton();
        });
        
        // Only show checkbox if fix is applicable
        const fixCheckbox = issueItem.querySelector('.fix-checkbox');
        if (!this.isFixApplicable(issue)) {
            fixCheckbox.style.display = 'none';
        }
        
        return issueItem;
    }

    isFixApplicable(issue) {
        // Check if this issue type can have fixes applied
        const applicableTypes = [
            'missing_alt_text',
            'poor_color_contrast',
            'improper_heading_hierarchy',
            'missing_form_labels',
            'non_descriptive_links'
        ];
        
        return applicableTypes.includes(issue.type);
    }

    updateApplyButton() {
        const applyBtn = document.getElementById('applyFixesBtn');
        const selectedFixes = document.querySelectorAll('.fix-toggle:checked');
        
        if (selectedFixes.length > 0) {
            applyBtn.disabled = false;
            applyBtn.textContent = `Apply ${selectedFixes.length} Fix(es)`;
        } else {
            applyBtn.disabled = true;
            applyBtn.textContent = 'Apply Selected Fixes';
        }
    }

    async applySelectedFixes() {
        try {
            const selectedIssues = [];
            const checkboxes = document.querySelectorAll('.fix-toggle:checked');
            
            checkboxes.forEach(checkbox => {
                const issueId = parseInt(checkbox.closest('.issue-item').dataset.issueId);
                const issue = this.scanResults[issueId];
                if (issue) {
                    selectedIssues.push(issue);
                }
            });

            if (selectedIssues.length === 0) {
                return;
            }

            // Send message to content script to apply fixes
            const response = await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'applyFixes',
                issues: selectedIssues
            });

            if (response.success) {
                this.appliedFixes = response.appliedFixes;
                this.showFixesApplied(selectedIssues);
                this.updateApplyButton();
            } else {
                throw new Error(response.error || 'Failed to apply fixes');
            }
        } catch (error) {
            console.error('Failed to apply fixes:', error);
            this.showError('Failed to apply fixes. Please try again.');
        }
    }

    showFixesApplied(issues) {
        // Show revert button
        document.getElementById('revertFixesBtn').style.display = 'block';
        
        // Update apply button
        const applyBtn = document.getElementById('applyFixesBtn');
        applyBtn.textContent = '✅ Fixes Applied';
        applyBtn.disabled = true;
        
        // Show success message
        this.showNotification(`${issues.length} fix(es) applied successfully!`, 'success');
    }

    async revertFixes() {
        try {
            // Send message to content script to revert fixes
            const response = await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'revertFixes'
            });

            if (response.success) {
                this.appliedFixes = [];
                this.hideRevertButton();
                this.resetApplyButton();
                this.showNotification('All fixes have been reverted.', 'success');
            } else {
                throw new Error(response.error || 'Failed to revert fixes');
            }
        } catch (error) {
            console.error('Failed to revert fixes:', error);
            this.showError('Failed to revert fixes. Please refresh the page.');
        }
    }

    hideRevertButton() {
        document.getElementById('revertFixesBtn').style.display = 'none';
    }

    resetApplyButton() {
        const applyBtn = document.getElementById('applyFixesBtn');
        applyBtn.textContent = 'Apply Selected Fixes';
        applyBtn.disabled = true;
        
        // Reset all checkboxes
        document.querySelectorAll('.fix-toggle').forEach(checkbox => {
            checkbox.checked = false;
        });
    }

    async exportReport() {
        try {
            const report = {
                url: this.currentTab.url,
                timestamp: new Date().toISOString(),
                issues: this.scanResults,
                appliedFixes: this.appliedFixes
            };

            const blob = new Blob([JSON.stringify(report, null, 2)], {
                type: 'application/json'
            });

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `accessibility-report-${new Date().toISOString().split('T')[0]}.json`;
            a.click();

            URL.revokeObjectURL(url);
            this.showNotification('Report exported successfully!', 'success');
        } catch (error) {
            console.error('Failed to export report:', error);
            this.showError('Failed to export report');
        }
    }

    showLoading() {
        this.hideAllStates();
        document.getElementById('loadingState').style.display = 'block';
    }

    showNoIssues() {
        this.hideAllStates();
        const noIssuesState = document.getElementById('noIssuesState');
        noIssuesState.style.display = 'block';
        noIssuesState.style.opacity = '0';
        noIssuesState.style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            noIssuesState.style.transition = 'all 0.5s ease';
            noIssuesState.style.opacity = '1';
            noIssuesState.style.transform = 'scale(1)';
        }, 100);
    }

    showError(message) {
        this.hideAllStates();
        document.getElementById('errorState').style.display = 'block';
        document.getElementById('errorMessage').textContent = message;
    }

    hideAllStates() {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('resultsContainer').style.display = 'none';
        document.getElementById('noIssuesState').style.display = 'none';
        document.getElementById('errorState').style.display = 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    async loadPreferences() {
        try {
            const result = await chrome.storage.sync.get(['autoScan', 'defaultFixes']);
            // Store preferences for later use
            this.preferences = result;
        } catch (error) {
            console.error('Failed to load preferences:', error);
            this.preferences = { autoScan: false, defaultFixes: [] };
        }
    }

    async shouldAutoScan() {
        return this.preferences?.autoScan === true;
    }

    async showToolbar() {
        try {
            await chrome.tabs.sendMessage(this.currentTab.id, { action: 'showToolbar' });
            this.showNotification('Accessibility toolbar shown', 'success');
        } catch (error) {
            console.error('Failed to show toolbar:', error);
            this.showNotification('Failed to show toolbar', 'error');
        }
    }

    async hideToolbar() {
        try {
            await chrome.tabs.sendMessage(this.currentTab.id, { action: 'hideToolbar' });
            this.showNotification('Accessibility toolbar hidden', 'success');
        } catch (error) {
            console.error('Failed to hide toolbar:', error);
            this.showNotification('Failed to hide toolbar', 'error');
        }
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AccessibilityPopup();
});
