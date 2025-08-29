/**
 * Accessibility Assistant Content Script
 * Runs on web pages to scan for accessibility issues and apply fixes
 */

class AccessibilityScanner {
    constructor() {
        this.originalStyles = new Map();
        this.appliedFixes = [];
        this.scanResults = [];
        this.init();
    }

    init() {
        // Listen for messages from popup
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sender, sendResponse);
            return true; // Keep message channel open for async response
        });

        // Initialize accessibility scanning
        this.initializeScanner();
    }

    async handleMessage(request, sender, sendResponse) {
        try {
            switch (request.action) {
                case 'scanAccessibility':
                    const issues = await this.scanPage();
                    sendResponse({ success: true, issues });
                    break;
                    
                case 'applyFixes':
                    const appliedFixes = await this.applyFixes(request.issues);
                    sendResponse({ success: true, appliedFixes });
                    break;
                    
                case 'revertFixes':
                    const reverted = await this.revertFixes();
                    sendResponse({ success: true, reverted });
                    break;
                
                case 'showNotification':
                    this.showInPageNotification(request.message, request.type);
                    sendResponse({ success: true });
                    break;
                    
                default:
                    sendResponse({ success: false, error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Content script error:', error);
            sendResponse({ success: false, error: error.message });
        }
    }

    showInPageNotification(message, type = 'info') {
        try {
            const existing = document.querySelector('.a11y-assistant-toast');
            if (existing) existing.remove();

            const toast = document.createElement('div');
            toast.className = `a11y-assistant-toast a11y-${type}`;
            toast.textContent = message;

            const style = document.createElement('style');
            style.textContent = `
                .a11y-assistant-toast {
                    position: fixed;
                    bottom: 16px;
                    right: 16px;
                    z-index: 2147483647;
                    background: #1f2937;
                    color: #fff;
                    padding: 10px 14px;
                    border-radius: 6px;
                    font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
                    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
                    opacity: 0;
                    transform: translateY(8px);
                    transition: opacity .2s ease, transform .2s ease;
                    max-width: 60vw;
                }
                .a11y-assistant-toast.a11y-success { background: #166534; }
                .a11y-assistant-toast.a11y-error { background: #991b1b; }
                .a11y-assistant-toast.a11y-info { background: #1f2937; }
            `;
            document.documentElement.appendChild(style);
            document.documentElement.appendChild(toast);

            requestAnimationFrame(() => {
                toast.style.opacity = '1';
                toast.style.transform = 'translateY(0)';
            });

            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(8px)';
                setTimeout(() => toast.remove(), 200);
            }, 3000);
        } catch (e) {
            // swallow
        }
    }

    async initializeScanner() {
        // Wait for page to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupAccessibilityMonitoring();
            });
        } else {
            this.setupAccessibilityMonitoring();
        }
    }

    setupAccessibilityMonitoring() {
        // Monitor for dynamic content changes
        const observer = new MutationObserver((mutations) => {
            // Re-scan if significant changes occur
            let shouldRescan = false;
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    shouldRescan = true;
                }
            });
            
            if (shouldRescan) {
                // Debounce re-scanning
                clearTimeout(this.rescanTimeout);
                this.rescanTimeout = setTimeout(() => {
                    this.scanPage();
                }, 1000);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    async scanPage() {
        try {
            this.scanResults = [];
            
            // Run all accessibility checks
            await this.checkAltText();
            await this.checkColorContrast();
            await this.checkHeadingStructure();
            await this.checkFormLabels();
            await this.checkLinkDescriptiveness();
            await this.checkARIA();
            await this.checkLandmarks();
            await this.checkKeyboardNavigation();
            
            return this.scanResults;
        } catch (error) {
            console.error('Scan failed:', error);
            return [];
        }
    }

    async checkAltText() {
        const images = document.querySelectorAll('img');
        
        images.forEach((img) => {
            if (!img.alt && !img.getAttribute('aria-hidden')) {
                this.scanResults.push({
                    type: 'missing_alt_text',
                    severity: 'critical',
                    description: 'Image missing alt text',
                    element: img.outerHTML.substring(0, 100),
                    context: this.getElementContext(img),
                    suggestedFix: 'Add descriptive alt text to the image',
                    fixable: true
                });
            }
        });
    }

    async checkColorContrast() {
        // This is a simplified contrast check
        // In a real implementation, you'd want to use a proper contrast calculation library
        const textElements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6, a, label');
        
        textElements.forEach((element) => {
            const style = window.getComputedStyle(element);
            const color = style.color;
            const backgroundColor = style.backgroundColor;
            
            // Check for common low-contrast combinations
            if (this.hasLowContrast(color, backgroundColor)) {
                this.scanResults.push({
                    type: 'poor_color_contrast',
                    severity: 'moderate',
                    description: 'Text has insufficient color contrast',
                    element: element.outerHTML.substring(0, 100),
                    context: this.getElementContext(element),
                    suggestedFix: 'Improve color contrast to meet WCAG standards',
                    fixable: true
                });
            }
        });
    }

    hasLowContrast(color, backgroundColor) {
        // Simplified contrast detection
        const lowContrastCombos = [
            ['#666666', '#ffffff'], // Gray on white
            ['#999999', '#ffffff'], // Light gray on white
            ['#cccccc', '#000000'], // Light gray on black
        ];
        
        return lowContrastCombos.some(([fg, bg]) => 
            color.includes(fg) || backgroundColor.includes(bg)
        );
    }

    async checkHeadingStructure() {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        let previousLevel = 0;
        
        headings.forEach((heading) => {
            const level = parseInt(heading.tagName.charAt(1));
            
            if (level > previousLevel + 1) {
                this.scanResults.push({
                    type: 'improper_heading_hierarchy',
                    severity: 'moderate',
                    description: `Heading level jumps from H${previousLevel} to H${level}`,
                    element: heading.outerHTML.substring(0, 100),
                    context: this.getElementContext(heading),
                    suggestedFix: 'Fix heading hierarchy to follow logical order',
                    fixable: true
                });
            }
            
            previousLevel = level;
        });
    }

    async checkFormLabels() {
        const inputs = document.querySelectorAll('input, select, textarea');
        
        inputs.forEach((input) => {
            if (input.type !== 'hidden' && !this.hasProperLabel(input)) {
                this.scanResults.push({
                    type: 'missing_form_labels',
                    severity: 'critical',
                    description: 'Form element missing label',
                    element: input.outerHTML.substring(0, 100),
                    context: this.getElementContext(input),
                    suggestedFix: 'Add proper label or aria-label to form element',
                    fixable: true
                });
            }
        });
    }

    hasProperLabel(input) {
        // Check for explicit label association
        if (input.id) {
            const label = document.querySelector(`label[for="${input.id}"]`);
            if (label) return true;
        }
        
        // Check for wrapped label
        if (input.parentElement.tagName === 'LABEL') return true;
        
        // Check for aria-label
        if (input.getAttribute('aria-label')) return true;
        
        // Check for aria-labelledby
        if (input.getAttribute('aria-labelledby')) return true;
        
        return false;
    }

    async checkLinkDescriptiveness() {
        const links = document.querySelectorAll('a');
        
        links.forEach((link) => {
            const text = link.textContent.trim();
            
            if (this.isNonDescriptiveLink(text)) {
                this.scanResults.push({
                    type: 'non_descriptive_links',
                    severity: 'moderate',
                    description: 'Link text is not descriptive',
                    element: link.outerHTML.substring(0, 100),
                    context: this.getElementContext(link),
                    suggestedFix: 'Make link text more descriptive',
                    fixable: false // Can't automatically fix this
                });
            }
        });
    }

    isNonDescriptiveLink(text) {
        const nonDescriptive = [
            'click here', 'here', 'more', 'read more', 'learn more',
            'continue', 'next', 'previous', 'back', 'forward'
        ];
        
        return nonDescriptive.some(phrase => 
            text.toLowerCase().includes(phrase)
        );
    }

    async checkARIA() {
        const elements = document.querySelectorAll('[role], [aria-label], [aria-labelledby]');
        
        elements.forEach((element) => {
            const role = element.getAttribute('role');
            
            if (role && !this.isValidRole(role)) {
                this.scanResults.push({
                    type: 'invalid_aria',
                    severity: 'moderate',
                    description: `Invalid ARIA role: ${role}`,
                    element: element.outerHTML.substring(0, 100),
                    context: this.getElementContext(element),
                    suggestedFix: 'Use valid ARIA role values',
                    fixable: true
                });
            }
        });
    }

    isValidRole(role) {
        const validRoles = [
            'button', 'link', 'menuitem', 'tab', 'checkbox', 'radio',
            'textbox', 'combobox', 'listbox', 'option', 'grid', 'gridcell'
        ];
        
        return validRoles.includes(role);
    }

    async checkLandmarks() {
        const landmarks = document.querySelectorAll('main, nav, header, footer, aside');
        
        if (landmarks.length === 0) {
            this.scanResults.push({
                type: 'missing_landmarks',
                severity: 'moderate',
                description: 'Page missing landmark elements',
                element: '<body>',
                context: 'Entire page',
                suggestedFix: 'Add semantic landmark elements',
                fixable: false
            });
        }
    }

    async checkKeyboardNavigation() {
        const interactiveElements = document.querySelectorAll('a, button, input, select, textarea');
        
        interactiveElements.forEach((element) => {
            if (!this.isKeyboardAccessible(element)) {
                this.scanResults.push({
                    type: 'keyboard_navigation',
                    severity: 'moderate',
                    description: 'Element not keyboard accessible',
                    element: element.outerHTML.substring(0, 100),
                    context: this.getElementContext(element),
                    suggestedFix: 'Ensure element is keyboard accessible',
                    fixable: true
                });
            }
        });
    }

    isKeyboardAccessible(element) {
        // Check if element can receive focus
        if (element.tagName === 'A' && !element.href) return false;
        if (element.disabled) return false;
        
        return true;
    }

    getElementContext(element) {
        const parent = element.parentElement;
        if (parent) {
            return `${parent.tagName.toLowerCase()} > ${element.tagName.toLowerCase()}`;
        }
        return element.tagName.toLowerCase();
    }

    async applyFixes(issues) {
        this.appliedFixes = [];
        
        for (const issue of issues) {
            if (issue.fixable) {
                const fix = await this.applyFix(issue);
                if (fix) {
                    this.appliedFixes.push(fix);
                }
            }
        }
        
        return this.appliedFixes;
    }

    async applyFix(issue) {
        try {
            switch (issue.type) {
                case 'missing_alt_text':
                    return this.fixMissingAltText(issue);
                case 'poor_color_contrast':
                    return this.fixColorContrast(issue);
                case 'improper_heading_hierarchy':
                    return this.fixHeadingHierarchy(issue);
                case 'missing_form_labels':
                    return this.fixFormLabels(issue);
                case 'invalid_aria':
                    return this.fixInvalidARIA(issue);
                case 'keyboard_navigation':
                    return this.fixKeyboardNavigation(issue);
                default:
                    return null;
            }
        } catch (error) {
            console.error(`Failed to apply fix for ${issue.type}:`, error);
            return null;
        }
    }

    fixMissingAltText(issue) {
        // Find the image element
        const img = this.findElementFromIssue(issue);
        if (!img) return null;
        
        // Store original state
        this.storeOriginalState(img, 'alt');
        
        // Apply temporary alt text
        const tempAlt = this.generateAltText(img);
        img.setAttribute('alt', tempAlt);
        
        return {
            type: 'missing_alt_text',
            element: img,
            originalValue: null,
            newValue: tempAlt,
            description: `Added temporary alt text: ${tempAlt}`
        };
    }

    fixColorContrast(issue) {
        const element = this.findElementFromIssue(issue);
        if (!element) return null;
        
        // Store original styles
        this.storeOriginalState(element, 'style');
        
        // Apply high-contrast styles
        element.style.color = '#000000';
        element.style.backgroundColor = '#ffffff';
        element.style.border = '1px solid #000000';
        
        return {
            type: 'poor_color_contrast',
            element: element,
            originalValue: this.originalStyles.get(element),
            newValue: 'High contrast applied',
            description: 'Applied high contrast colors'
        };
    }

    fixHeadingHierarchy(issue) {
        const heading = this.findElementFromIssue(issue);
        if (!heading) return null;
        
        // Store original state
        this.storeOriginalState(heading, 'tagName');
        
        // Adjust heading level
        const currentLevel = parseInt(heading.tagName.charAt(1));
        const newLevel = Math.min(currentLevel + 1, 6);
        const newTagName = `H${newLevel}`;
        
        // Create new element with adjusted level
        const newHeading = document.createElement(newTagName);
        newHeading.innerHTML = heading.innerHTML;
        newHeading.className = heading.className;
        newHeading.id = heading.id;
        
        // Replace the element
        heading.parentNode.replaceChild(newHeading, heading);
        
        return {
            type: 'improper_heading_hierarchy',
            element: newHeading,
            originalValue: heading.tagName,
            newValue: newTagName,
            description: `Adjusted heading level from ${heading.tagName} to ${newTagName}`
        };
    }

    fixFormLabels(issue) {
        const input = this.findElementFromIssue(issue);
        if (!input) return null;
        
        // Store original state
        this.storeOriginalState(input, 'aria-label');
        
        // Add temporary aria-label
        const tempLabel = this.generateFormLabel(input);
        input.setAttribute('aria-label', tempLabel);
        
        return {
            type: 'missing_form_labels',
            element: input,
            originalValue: null,
            newValue: tempLabel,
            description: `Added temporary aria-label: ${tempLabel}`
        };
    }

    fixInvalidARIA(issue) {
        const element = this.findElementFromIssue(issue);
        if (!element) return null;
        
        // Store original state
        this.storeOriginalState(element, 'role');
        
        // Remove invalid role
        const originalRole = element.getAttribute('role');
        element.removeAttribute('role');
        
        return {
            type: 'invalid_aria',
            element: element,
            originalValue: originalRole,
            newValue: null,
            description: 'Removed invalid ARIA role'
        };
    }

    fixKeyboardNavigation(issue) {
        const element = this.findElementFromIssue(issue);
        if (!element) return null;
        
        // Store original state
        this.storeOriginalState(element, 'tabindex');
        
        // Make element keyboard accessible
        element.setAttribute('tabindex', '0');
        
        return {
            type: 'keyboard_navigation',
            element: element,
            originalValue: null,
            newValue: '0',
            description: 'Added tabindex for keyboard navigation'
        };
    }

    findElementFromIssue(issue) {
        // Try to find the element based on the stored HTML
        const elements = document.querySelectorAll('*');
        
        for (const element of elements) {
            if (element.outerHTML.includes(issue.element.substring(0, 50))) {
                return element;
            }
        }
        
        return null;
    }

    storeOriginalState(element, property) {
        if (!this.originalStyles.has(element)) {
            this.originalStyles.set(element, {});
        }
        
        const elementState = this.originalStyles.get(element);
        
        switch (property) {
            case 'alt':
                elementState.alt = element.getAttribute('alt');
                break;
            case 'style':
                elementState.style = {
                    color: element.style.color,
                    backgroundColor: element.style.backgroundColor,
                    border: element.style.border
                };
                break;
            case 'tagName':
                elementState.tagName = element.tagName;
                break;
            case 'aria-label':
                elementState['aria-label'] = element.getAttribute('aria-label');
                break;
            case 'role':
                elementState.role = element.getAttribute('role');
                break;
            case 'tabindex':
                elementState.tabindex = element.getAttribute('tabindex');
                break;
        }
    }

    generateAltText(img) {
        // Generate descriptive alt text based on context
        const src = img.src || '';
        const className = img.className || '';
        const parentText = img.parentElement?.textContent?.trim() || '';
        
        if (parentText) {
            return `Image related to: ${parentText.substring(0, 50)}`;
        } else if (className) {
            return `Image with class: ${className}`;
        } else if (src) {
            const filename = src.split('/').pop().split('.')[0];
            return `Image: ${filename}`;
        } else {
            return 'Image';
        }
    }

    generateFormLabel(input) {
        const type = input.type || 'text';
        const placeholder = input.placeholder || '';
        const name = input.name || '';
        
        if (placeholder) {
            return placeholder;
        } else if (name) {
            return `${name.charAt(0).toUpperCase() + name.slice(1)} field`;
        } else {
            return `${type.charAt(0).toUpperCase() + type.slice(1)} input field`;
        }
    }

    async revertFixes() {
        for (const fix of this.appliedFixes) {
            await this.revertFix(fix);
        }
        
        this.appliedFixes = [];
        return true;
    }

    async revertFix(fix) {
        try {
            const element = fix.element;
            const originalState = this.originalStyles.get(element);
            
            if (!originalState) return;
            
            switch (fix.type) {
                case 'missing_alt_text':
                    if (originalState.alt === null) {
                        element.removeAttribute('alt');
                    } else {
                        element.setAttribute('alt', originalState.alt);
                    }
                    break;
                    
                case 'poor_color_contrast':
                    if (originalState.style) {
                        element.style.color = originalState.style.color;
                        element.style.backgroundColor = originalState.style.backgroundColor;
                        element.style.border = originalState.style.border;
                    }
                    break;
                    
                case 'improper_heading_hierarchy':
                    // This is complex to revert, so we'll skip it
                    break;
                    
                case 'missing_form_labels':
                    if (originalState['aria-label'] === null) {
                        element.removeAttribute('aria-label');
                    } else {
                        element.setAttribute('aria-label', originalState['aria-label']);
                    }
                    break;
                    
                case 'invalid_aria':
                    if (originalState.role) {
                        element.setAttribute('role', originalState.role);
                    }
                    break;
                    
                case 'keyboard_navigation':
                    if (originalState.tabindex === null) {
                        element.removeAttribute('tabindex');
                    } else {
                        element.setAttribute('tabindex', originalState.tabindex);
                    }
                    break;
            }
            
            // Remove from original styles
            this.originalStyles.delete(element);
            
        } catch (error) {
            console.error('Failed to revert fix:', error);
        }
    }
}

// Initialize the accessibility scanner
new AccessibilityScanner();
