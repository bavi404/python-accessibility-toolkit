#!/usr/bin/env python3
"""
Example of creating custom accessibility checks.
"""

import asyncio
from bs4 import BeautifulSoup
from accessibility_toolkit import AccessibilityScanner, ReportGenerator
from accessibility_toolkit.checks import BaseCheck
from accessibility_toolkit.models import AccessibilityIssue, IssueType, SeverityLevel


class CustomSocialMediaCheck(BaseCheck):
    """Custom check for social media accessibility."""
    
    def check(self, soup: BeautifulSoup, url: str):
        """Check for social media accessibility issues."""
        issues = []
        
        # Check for social media links without proper labels
        social_media_links = soup.find_all("a", href=lambda x: x and any(
            platform in x.lower() for platform in 
            ["facebook.com", "twitter.com", "instagram.com", "linkedin.com"]
        ))
        
        for link in social_media_links:
            link_text = link.get_text(strip=True)
            
            # Check if link text is descriptive
            if not link_text or link_text.lower() in ["follow us", "social", "share"]:
                issues.append(self.create_issue(
                    issue_type=IssueType.OTHER,
                    severity=SeverityLevel.MODERATE,
                    description="Social media link has non-descriptive text",
                    element=f"<a href='{link.get('href', '')}'>{link_text}</a>",
                    context=self.get_parent_context(link),
                    line_number=self.get_line_number(link),
                    column_number=self.get_column_number(link),
                    suggested_fix=(
                        "Make social media link text more descriptive. "
                        "Instead of 'Follow us', use 'Follow us on Facebook' "
                        "or 'Connect with us on LinkedIn'."
                    ),
                    wcag_criteria=["2.4.4"],
                    additional_info=self.get_element_info(link)
                ))
        
        return issues


class CustomPerformanceCheck(BaseCheck):
    """Custom check for performance-related accessibility issues."""
    
    def check(self, soup: BeautifulSoup, url: str):
        """Check for performance issues that affect accessibility."""
        issues = []
        
        # Check for large images without optimization
        images = soup.find_all("img")
        for img in images:
            src = img.get("src", "")
            
            # Check for common performance issues
            if src and not src.startswith("data:"):
                # Check for missing width/height attributes
                if not img.get("width") and not img.get("height"):
                    issues.append(self.create_issue(
                        issue_type=IssueType.OTHER,
                        severity=SeverityLevel.LOW,
                        description="Image missing width/height attributes",
                        element=f"<img src='{src}'>",
                        context=self.get_parent_context(img),
                        line_number=self.get_line_number(img),
                        column_number=self.get_column_number(img),
                        suggested_fix=(
                            "Add width and height attributes to images to prevent "
                            "layout shifts during page load, which improves "
                            "accessibility for users with motor impairments."
                        ),
                        wcag_criteria=["2.2.2"],
                        additional_info=self.get_element_info(img)
                    ))
        
        return issues


async def main():
    """Run accessibility scan with custom checks."""
    
    # URLs to scan
    urls = [
        "https://example.com",
        "https://httpbin.org/html"
    ]
    
    print("🚀 Custom Accessibility Checks Example")
    print("=" * 60)
    
    # Create custom configuration with our custom checks
    custom_config = {
        "custom_checks": [
            CustomSocialMediaCheck(),
            CustomPerformanceCheck()
        ]
    }
    
    # Initialize scanner with custom configuration
    async with AccessibilityScanner(custom_config) as scanner:
        print(f"📡 Scanning {len(urls)} URLs with custom checks...")
        
        # Run the scan
        scan_results = await scanner.scan_multiple(urls)
        
        # Print summary
        scanner.print_summary(scan_results)
        
        # Generate report
        generator = ReportGenerator()
        report_path = generator.generate_report(scan_results, "html")
        print(f"\n📄 Report generated: {report_path}")
        
        # Show custom check results
        print("\n🔍 Custom Check Results:")
        for result in scan_results:
            if result.status == "completed" and result.issues:
                custom_issues = [
                    issue for issue in result.issues 
                    if "social media" in issue.description.lower() or 
                       "performance" in issue.description.lower()
                ]
                
                if custom_issues:
                    print(f"\n📱 {result.url} - Custom Issues Found:")
                    for issue in custom_issues:
                        print(f"   ⚠️  {issue.description}")


if __name__ == "__main__":
    asyncio.run(main())
