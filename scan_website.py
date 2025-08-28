#!/usr/bin/env python3
"""
Simple script to scan any website for accessibility issues.
Usage: python scan_website.py <url>
"""

import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from accessibility_toolkit.scanner import AccessibilityScanner
from accessibility_toolkit.reports import ReportGenerator

async def scan_website(url: str, output_format: str = "html"):
    """
    Scan a website for accessibility issues.
    
    Args:
        url: URL to scan
        output_format: Output format (html, json, csv, text)
    """
    print(f"🔍 Scanning {url} for accessibility issues...")
    print("=" * 60)
    
    try:
        # Initialize scanner
        scanner = AccessibilityScanner()
        
        # Scan the website
        async with scanner:
            result = await scanner.scan_url(url)
        
        if result.status == "completed":
            print(f"✅ Scan completed successfully!")
            print(f"📊 Found {len(result.issues)} accessibility issues")
            print(f"🎯 Accessibility Score: {result.accessibility_score:.1f}/100")
            
            # Show issue breakdown
            critical = result.critical_issues_count
            moderate = result.moderate_issues_count
            low = result.low_issues_count
            
            print(f"\n🚨 Issue Breakdown:")
            print(f"   Critical: {critical}")
            print(f"   Moderate: {moderate}")
            print(f"   Low: {low}")
            
            # Show top issues
            if result.issues:
                print(f"\n🔍 Top Issues Found:")
                for i, issue in enumerate(result.issues[:5], 1):
                    severity_icon = "🚨" if issue.severity.value == "critical" else "⚠️" if issue.severity.value == "moderate" else "ℹ️"
                    print(f"   {i}. {severity_icon} {issue.description}")
                    print(f"      Element: {issue.element}")
                    print(f"      Fix: {issue.suggested_fix}")
                    print()
            
            # Generate report
            if output_format != "text":
                print(f"📄 Generating {output_format.upper()} report...")
                generator = ReportGenerator()
                
                report_path = generator.generate_report([result], output_format)
                print(f"✅ {output_format.upper()} report saved to: {report_path}")
            
            print(f"\n💡 Tips:")
            print(f"   • Critical issues should be fixed first")
            print(f"   • Use the generated report for detailed analysis")
            print(f"   • Run 'python scan_website.py {url} --help' for more options")
            
        else:
            print(f"❌ Scan failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error scanning {url}: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if the URL is accessible")
        print("   2. Verify your internet connection")
        print("   3. Try a different website")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("🚀 Website Accessibility Scanner")
        print("=" * 40)
        print("Usage: python scan_website.py <url> [format]")
        print("\nFormats: html, json, csv, text (default: html)")
        print("\nExamples:")
        print("  python scan_website.py https://example.com")
        print("  python scan_website.py https://google.com json")
        print("  python scan_website.py https://github.com csv")
        print("\n💡 Tip: The HTML report provides the best visual overview!")
        return
    
    url = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "html"
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Validate output format
    valid_formats = ['html', 'json', 'csv', 'text']
    if output_format not in valid_formats:
        print(f"❌ Invalid output format: {output_format}")
        print(f"   Valid formats: {', '.join(valid_formats)}")
        return
    
    # Run the scan
    asyncio.run(scan_website(url, output_format))

if __name__ == "__main__":
    main()
