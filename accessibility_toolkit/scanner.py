"""
Main accessibility scanner that orchestrates all checks.
"""

import asyncio
import time
import os
import platform
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

# Try to import Playwright first, fallback to Pyppeteer
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from pyppeteer import launch
    PYPPETEER_AVAILABLE = True
except ImportError:
    PYPPETEER_AVAILABLE = False

from .models import ScanResult, AccessibilityIssue, ScanSummary
from .checks import (
    AltTextCheck,
    HeadingHierarchyCheck,
    ColorContrastCheck,
    FormAccessibilityCheck,
    LinkAccessibilityCheck,
    AriaCheck,
    LandmarkCheck,
    KeyboardNavigationCheck,
    MediaAccessibilityCheck,
    SkipLinkCheck,
    AutoplayControlsCheck
)
from .utils import deduplicate_issues, filter_visible_elements


class AccessibilityScanner:
    """Main scanner class that performs accessibility checks on web pages."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the accessibility scanner.
        
        Args:
            config: Configuration dictionary for the scanner
        """
        self.config = config or {}
        self.browser = None
        self.session = None
        
        # Initialize all accessibility checks
        self.checks = [
            AltTextCheck(self.config.get("alt_text", {})),
            HeadingHierarchyCheck(self.config.get("headings", {})),
            ColorContrastCheck(self.config.get("color_contrast", {})),
            FormAccessibilityCheck(self.config.get("forms", {})),
            LinkAccessibilityCheck(self.config.get("links", {})),
            AriaCheck(self.config.get("aria", {})),
            LandmarkCheck(self.config.get("landmarks", {})),
            KeyboardNavigationCheck(self.config.get("keyboard", {})),
            MediaAccessibilityCheck(self.config.get("media", {})),
            SkipLinkCheck(self.config.get("skip_links", {})),
            AutoplayControlsCheck(self.config.get("autoplay", {})),
        ]
        
        # Scanner configuration
        self.timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("max_retries", 3)
        self.user_agent = self.config.get("user_agent", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.viewport = self.config.get("viewport", {"width": 1920, "height": 1080})
        self.wait_for = self.config.get("wait_for", 2000)  # milliseconds
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    async def start(self):
        """Start the browser and session."""
        if not self.browser:
            try:
                # Try Playwright first (most reliable for modern JS-heavy sites)
                if PLAYWRIGHT_AVAILABLE:
                    print("🚀 Using Playwright for headless browser rendering")
                    self.playwright = await async_playwright().start()
                    self.browser = await self.playwright.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-accelerated-2d-canvas',
                            '--no-first-run',
                            '--no-zygote',
                            '--disable-gpu'
                        ]
                    )
                    print("✅ Playwright browser initialized successfully")
                    return
                
                # Fallback to Pyppeteer with system Chrome
                if PYPPETEER_AVAILABLE:
                    chrome_paths = [
                        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                        '/Applications/Chromium.app/Contents/MacOS/Chromium',
                        '/usr/bin/google-chrome',
                        '/usr/bin/chromium'
                    ]
                    
                    executable_path = None
                    for path in chrome_paths:
                        if os.path.exists(path):
                            executable_path = path
                            break
                    
                    launch_options = {
                        'headless': True,
                        'args': [
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-accelerated-2d-canvas',
                            '--no-first-run',
                            '--no-zygote',
                            '--disable-gpu'
                        ]
                    }
                    
                    if executable_path:
                        launch_options['executablePath'] = executable_path
                        print(f"✅ Using system Chrome with Pyppeteer: {executable_path}")
                    else:
                        print("⚠️  No system Chrome found, using Pyppeteer's Chromium")
                    
                    self.browser = await launch(**launch_options)
                    print("✅ Pyppeteer browser initialized successfully")
                    return
                
                # No browser available
                print("❌ No browser automation available (Playwright or Pyppeteer)")
                print("   Falling back to HTTP-only mode for basic checks")
                self.browser = None
                
            except Exception as e:
                print(f"❌ Failed to initialize headless browser: {e}")
                print("   Falling back to HTTP-only mode for basic checks")
                self.browser = None
        
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def stop(self):
        """Stop the browser and session."""
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()
            self.playwright = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.session:
            await self.session.close()
            self.session = None
    
    async def scan_url(self, url: str) -> ScanResult:
        """
        Scan a single URL for accessibility issues.
        
        Args:
            url: URL to scan
            
        Returns:
            ScanResult object with all found issues
        """
        start_time = time.time()
        
        try:
            # Validate URL
            if not self._is_valid_url(url):
                return ScanResult(
                    url=url,
                    timestamp=None,
                    status="failed",
                    error_message="Invalid URL format"
                )
            
            # Get page content
            page_content = await self._get_page_content(url)
            if not page_content:
                return ScanResult(
                    url=url,
                    timestamp=None,
                    status="failed",
                    error_message="Failed to retrieve page content"
                )
            
            # Parse HTML
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extract page metadata
            page_title = soup.title.string if soup.title else ""
            page_description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                page_description = meta_desc.get('content', '')
            
            # Filter to only visible elements for scanning
            visible_elements = filter_visible_elements(soup, self.viewport)
            if not visible_elements:
                # If no visible elements found, return success
                return ScanResult(
                    url=url,
                    timestamp=None,
                    issues=[],
                    page_title=page_title,
                    page_description=page_description,
                    scan_duration=time.time() - start_time,
                    status="completed",
                    message="No visible content found to scan"
                )
            
            # Run all accessibility checks
            all_issues = []
            for check in self.checks:
                try:
                    issues = check.check(soup, url)
                    all_issues.extend(issues)
                except Exception as e:
                    print(f"Warning: Check {check.__class__.__name__} failed: {e}")
                    continue
            
            # Apply de-duplication to remove repetitive issues
            all_issues = deduplicate_issues(all_issues)
            
            scan_duration = time.time() - start_time
            
            return ScanResult(
                url=url,
                timestamp=None,
                issues=all_issues,
                page_title=page_title,
                page_description=page_description,
                scan_duration=scan_duration,
                status="completed"
            )
            
        except Exception as e:
            scan_duration = time.time() - start_time
            return ScanResult(
                url=url,
                timestamp=None,
                status="failed",
                error_message=str(e),
                scan_duration=scan_duration
            )
    
    async def scan_multiple(self, urls: List[str]) -> List[ScanResult]:
        """
        Scan multiple URLs for accessibility issues.
        
        Args:
            urls: List of URLs to scan
            
        Returns:
            List of ScanResult objects
        """
        if not urls:
            return []
        
        print(f"🚀 Starting accessibility scan of {len(urls)} URLs...")
        
        # Ensure browser is started
        await self.start()
        
        # Scan URLs concurrently (with rate limiting)
        semaphore = asyncio.Semaphore(3)  # Limit concurrent scans
        
        async def scan_with_semaphore(url):
            async with semaphore:
                return await self.scan_url(url)
        
        tasks = [scan_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        scan_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                scan_results.append(ScanResult(
                    url=urls[i],
                    timestamp=None,
                    status="failed",
                    error_message=str(result)
                ))
            else:
                scan_results.append(result)
        
        print(f"✅ Completed scanning {len(urls)} URLs")
        return scan_results
    
    async def _get_page_content(self, url: str) -> Optional[str]:
        """
        Get the HTML content of a webpage.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if failed
        """
        # If we have a browser (Playwright or Pyppeteer), use it for better JS rendering
        if self.browser:
            return await self._get_page_content_with_browser(url)
        
        # Otherwise, try aiohttp for basic content
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            print(f"aiohttp failed for {url}: {e}")
            return None
    
    async def _get_page_content_with_browser(self, url: str) -> Optional[str]:
        """
        Get page content using browser (Playwright or Pyppeteer) for JavaScript-heavy pages.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if failed
        """
        try:
            # Check if we're using Playwright
            if hasattr(self, 'playwright') and self.playwright:
                # Use Playwright
                context = await self.browser.new_context(
                    user_agent=self.user_agent,
                    viewport=self.viewport,
                )
                page = await context.new_page()
                await page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
                if self.wait_for > 0:
                    await page.wait_for_timeout(self.wait_for)
                content = await page.content()
                await context.close()
                return content
            else:
                # Use Pyppeteer
                page = await self.browser.newPage()
                
                # Set viewport and user agent
                await page.setViewport(self.viewport)
                await page.setUserAgent(self.user_agent)
                
                # Navigate to the page
                await page.goto(url, waitUntil='networkidle0', timeout=self.timeout * 1000)
                
                # Wait for additional time if specified
                if self.wait_for > 0:
                    await page.waitFor(self.wait_for)
                
                # Get the rendered HTML
                content = await page.content()
                
                await page.close()
                return content
                
        except Exception as e:
            print(f"Browser failed for {url}: {e}")
            return None


    
    def _is_valid_url(self, url: str) -> bool:
        """Check if the URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def get_scan_summary(self, scan_results: List[ScanResult]) -> ScanSummary:
        """
        Generate a summary of scan results.
        
        Args:
            scan_results: List of ScanResult objects
            
        Returns:
            ScanSummary object
        """
        return ScanSummary.from_scan_results(scan_results)
    
    def filter_results_by_severity(self, scan_results: List[ScanResult], 
                                 min_severity: str = "low") -> List[ScanResult]:
        """
        Filter scan results by minimum severity level.
        
        Args:
            scan_results: List of ScanResult objects
            min_severity: Minimum severity level to include
            
        Returns:
            Filtered list of ScanResult objects
        """
        severity_order = {"low": 1, "moderate": 2, "critical": 3}
        min_level = severity_order.get(min_severity.lower(), 1)
        
        filtered_results = []
        for result in scan_results:
            if result.status != "completed":
                continue
                
            # Filter issues by severity
            filtered_issues = []
            for issue in result.issues:
                issue_level = severity_order.get(issue.severity.value, 1)
                if issue_level >= min_level:
                    filtered_issues.append(issue)
            
            # Create new result with filtered issues
            filtered_result = ScanResult(
                url=result.url,
                timestamp=result.timestamp,
                issues=filtered_issues,
                page_title=result.page_title,
                page_description=result.page_description,
                scan_duration=result.scan_duration,
                status=result.status,
                error_message=result.error_message,
                metadata=result.metadata
            )
            filtered_results.append(filtered_result)
        
        return filtered_results
    
    def export_results(self, scan_results: List[ScanResult], 
                      format: str = "json") -> str:
        """
        Export scan results in various formats.
        
        Args:
            scan_results: List of ScanResult objects
            format: Output format (json, csv, html)
            
        Returns:
            Exported data as string
        """
        if format.lower() == "json":
            import json
            return json.dumps([result.to_dict() for result in scan_results], indent=2)
        
        elif format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "URL", "Status", "Total Issues", "Critical Issues", 
                "Moderate Issues", "Low Issues", "Accessibility Score"
            ])
            
            # Write data
            for result in scan_results:
                writer.writerow([
                    result.url,
                    result.status,
                    result.total_issues,
                    result.critical_issues_count,
                    result.moderate_issues_count,
                    result.low_issues_count,
                    result.accessibility_score
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def print_summary(self, scan_results: List[ScanResult]):
        """
        Print a human-readable summary of scan results.
        
        Args:
            scan_results: List of ScanResult objects
        """
        summary = self.get_scan_summary(scan_results)
        
        print("\n" + "="*60)
        print("🔍 ACCESSIBILITY SCAN SUMMARY")
        print("="*60)
        print(f"📊 Total URLs Scanned: {summary.total_urls_scanned}")
        print(f"✅ Successful Scans: {summary.successful_scans}")
        print(f"❌ Failed Scans: {summary.failed_scans}")
        print(f"⏱️  Total Scan Duration: {summary.scan_duration:.2f}s")
        print(f"📈 Average Accessibility Score: {summary.average_accessibility_score}/100")
        print()
        
        print("🚨 ISSUE BREAKDOWN:")
        print(f"   Critical Issues: {summary.critical_issues}")
        print(f"   Moderate Issues: {summary.moderate_issues}")
        print(f"   Low Priority Issues: {summary.low_issues}")
        print(f"   Total Issues: {summary.total_issues}")
        print()
        
        if summary.total_issues > 0:
            print("📋 TOP ISSUES BY URL:")
            # Sort by total issues (descending)
            sorted_results = sorted(
                [r for r in scan_results if r.status == "completed"],
                key=lambda x: x.total_issues,
                reverse=True
            )
            
            for i, result in enumerate(sorted_results[:5]):  # Top 5
                print(f"   {i+1}. {result.url}")
                print(f"      Score: {result.accessibility_score}/100")
                print(f"      Issues: {result.total_issues} (C:{result.critical_issues_count} M:{result.moderate_issues_count} L:{result.low_issues_count})")
                print()
        
        print("="*60)
