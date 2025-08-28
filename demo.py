#!/usr/bin/env python3
"""
Demo script for the Pythonic Accessibility Toolkit.
This script demonstrates the toolkit's capabilities with example websites.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from accessibility_toolkit import AccessibilityScanner, ReportGenerator


async def run_demo():
    """Run the accessibility toolkit demo."""
    
    print("🌐 Pythonic Accessibility Toolkit - Live Demo")
    print("=" * 60)
    print("This demo will scan several example websites to showcase")
    print("the toolkit's accessibility checking capabilities.")
    print()
    
    # Example URLs to demonstrate different types of accessibility issues
    demo_urls = [
        "https://httpbin.org/html",  # Simple HTML page
        "https://httpbin.org/forms/post",  # Form page
        "https://httpbin.org/links/10",  # Page with links
    ]
    
    print(f"📡 Scanning {len(demo_urls)} demo websites...")
    print()
    
    try:
        # Initialize scanner
        async with AccessibilityScanner() as scanner:
            # Run the scan
            scan_results = await scanner.scan_multiple(demo_urls)
            
            # Print summary
            scanner.print_summary(scan_results)
            
            # Generate comprehensive report
            generator = ReportGenerator()
            html_report = generator.generate_report(scan_results, "html")
            json_report = generator.generate_report(scan_results, "json")
            
            print(f"\n📄 Reports Generated:")
            print(f"   HTML Report: {html_report}")
            print(f"   JSON Report: {json_report}")
            
            # Show detailed findings
            print(f"\n🔍 Detailed Findings:")
            for i, result in enumerate(scan_results, 1):
                print(f"\n{i}. {result.url}")
                print(f"   Status: {result.status}")
                
                if result.status == "completed":
                    print(f"   Accessibility Score: {result.accessibility_score}/100")
                    print(f"   Issues Found: {result.total_issues}")
                    
                    if result.issues:
                        print("   Issues:")
                        for issue in result.issues:
                            severity_icon = {
                                "critical": "🚨",
                                "moderate": "⚠️",
                                "low": "ℹ️"
                            }.get(issue.severity.value, "❓")
                            
                            print(f"     {severity_icon} {issue.description}")
                            print(f"        Element: {issue.element}")
                            print(f"        Fix: {issue.suggested_fix[:80]}...")
                    else:
                        print("   🎉 No accessibility issues found!")
                else:
                    print(f"   Error: {result.error_message}")
            
            # Show summary statistics
            summary = scanner.get_scan_summary(scan_results)
            print(f"\n📊 Demo Summary:")
            print(f"   Total URLs Scanned: {summary.total_urls_scanned}")
            print(f"   Successful Scans: {summary.successful_scans}")
            print(f"   Failed Scans: {summary.failed_scans}")
            print(f"   Total Issues Found: {summary.total_issues}")
            print(f"   Average Accessibility Score: {summary.average_accessibility_score}/100")
            print(f"   Total Scan Duration: {summary.scan_duration:.2f}s")
            
            print(f"\n💡 Next Steps:")
            print(f"   1. Review the generated HTML report for detailed analysis")
            print(f"   2. Use the JSON report for programmatic processing")
            print(f"   3. Run 'python -m accessibility_toolkit scan <your-url>' to test your own sites")
            print(f"   4. Check the examples/ directory for more usage patterns")
            
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("This might be due to network issues or missing dependencies.")
        print("Make sure you have installed all requirements: pip install -r requirements.txt")
        return 1
    
    return 0


def main():
    """Main entry point for the demo."""
    print("🚀 Starting Accessibility Toolkit Demo...")
    print("Note: This demo requires an internet connection to scan example websites.")
    print()
    
    try:
        exit_code = asyncio.run(run_demo())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
