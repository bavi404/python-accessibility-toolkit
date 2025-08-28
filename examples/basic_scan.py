#!/usr/bin/env python3
"""
Basic example of using the Pythonic Accessibility Toolkit.
"""

import asyncio
from accessibility_toolkit import AccessibilityScanner, ReportGenerator


async def main():
    """Run a basic accessibility scan."""
    
    # URLs to scan
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://httpbin.org/forms/post"
    ]
    
    print("🚀 Pythonic Accessibility Toolkit - Basic Example")
    print("=" * 60)
    
    # Initialize scanner with default configuration
    async with AccessibilityScanner() as scanner:
        print(f"📡 Scanning {len(urls)} URLs for accessibility issues...")
        
        # Run the scan
        scan_results = await scanner.scan_multiple(urls)
        
        # Print summary
        scanner.print_summary(scan_results)
        
        # Generate HTML report
        generator = ReportGenerator()
        report_path = generator.generate_report(scan_results, "html")
        print(f"\n📄 HTML report generated: {report_path}")
        
        # Generate JSON report
        json_path = generator.generate_report(scan_results, "json")
        print(f"📄 JSON report generated: {json_path}")
        
        # Show some detailed results
        print("\n🔍 Detailed Results:")
        for result in scan_results:
            if result.status == "completed":
                print(f"\n✅ {result.url}")
                print(f"   Score: {result.accessibility_score}/100")
                print(f"   Issues: {result.total_issues}")
                
                if result.issues:
                    for issue in result.issues[:3]:  # Show first 3 issues
                        severity_icon = {
                            "critical": "🚨",
                            "moderate": "⚠️", 
                            "low": "ℹ️"
                        }.get(issue.severity.value, "❓")
                        
                        print(f"   {severity_icon} {issue.description}")
                else:
                    print("   🎉 No accessibility issues found!")
            else:
                print(f"\n❌ {result.url}")
                print(f"   Error: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())
