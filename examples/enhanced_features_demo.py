#!/usr/bin/env python3
"""
Enhanced Features Demo - Showcasing the latest accessibility toolkit capabilities.
"""

import asyncio
import sys
from accessibility_toolkit import AccessibilityScanner
from accessibility_toolkit.checks.links import LinkAccessibilityCheck
from accessibility_toolkit.checks.forms import FormAccessibilityCheck


async def showcase_enhanced_features():
    """Demonstrate all the enhanced accessibility toolkit features."""
    
    print("🚀 Enhanced Accessibility Toolkit - Feature Showcase")
    print("=" * 60)
    print()
    
    # Test URLs that demonstrate different accessibility issues
    test_urls = [
        "https://httpbin.org/html",  # Basic HTML structure
        "https://httpbin.org/forms/post",  # Form accessibility
        "https://httpbin.org/links/10",  # Link accessibility
    ]
    
    print("🎯 Enhanced Features Being Demonstrated:")
    print("   • Enhanced Link Accessibility Check")
    print("   • Smart Issue Deduplication")
    print("   • Visible Content Filtering")
    print("   • Enhanced Report UI with Categories")
    print("   • Comprehensive Accessibility Coverage")
    print()
    
    try:
        # Initialize scanner
        async with AccessibilityScanner() as scanner:
            print("📡 Running comprehensive accessibility scan...")
            print()
            
            # Run the scan
            scan_results = await scanner.scan_multiple(test_urls)
            
            # Print summary
            scanner.print_summary(scan_results)
            
            # Generate enhanced reports
            from accessibility_toolkit import ReportGenerator
            generator = ReportGenerator()
            
            print("\n📄 Generating Enhanced Reports...")
            html_report = generator.generate_report(scan_results, "html")
            json_report = generator.generate_report(scan_results, "json")
            csv_report = generator.generate_report(scan_results, "csv")
            
            print(f"   ✅ HTML Report: {html_report}")
            print(f"   ✅ JSON Report: {json_report}")
            print(f"   ✅ CSV Report: {csv_report}")
            
            # Demonstrate enhanced link accessibility
            print("\n🔗 Enhanced Link Accessibility Demo:")
            print("   Testing advanced detection of vague labels...")
            
            # Create a test HTML with various link issues
            test_html = """
            <html>
            <body>
                <a href="/privacy">Click here</a>
                <a href="/terms">Read more</a>
                <a href="/contact">Here</a>
                <a href="/about">More info</a>
                <a href="/services">Learn more</a>
                <a href="/products">View more</a>
            </body>
            </html>
            """
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(test_html, "html.parser")
            
            # Test enhanced link check
            link_check = LinkAccessibilityCheck(config={"check_descriptive_text": True})
            link_issues = link_check.check(soup, "test://example.com")
            
            print(f"   Found {len(link_issues)} vague link issues:")
            for issue in link_issues:
                print(f"     • {issue.description}")
                print(f"       Fix: {issue.suggested_fix}")
            
            # Demonstrate enhanced form accessibility
            print("\n📝 Enhanced Form Accessibility Demo:")
            print("   Testing comprehensive form validation...")
            
            form_html = """
            <html>
            <body>
                <form>
                    <input type="text" name="username" required>
                    <input type="email" name="email" aria-invalid="true">
                    <div class="error">Invalid email</div>
                    <select name="country" required>
                        <option value="">Select country</option>
                    </select>
                    <button type="submit">Submit</button>
                </form>
            </body>
            </html>
            """
            
            form_soup = BeautifulSoup(form_html, "html.parser")
            form_check = FormAccessibilityCheck(config={"check_error_handling": True})
            form_issues = form_check.check(form_soup, "test://example.com")
            
            print(f"   Found {len(form_issues)} form accessibility issues:")
            for issue in form_issues[:5]:  # Show first 5
                print(f"     • {issue.description}")
                print(f"       Fix: {issue.suggested_fix}")
            
            # Show detailed findings with enhanced categorization
            print(f"\n🔍 Enhanced Report Features:")
            print("   • Accessibility Categories (Visual, Auditory, Cognitive, Navigation, Forms, Content)")
            print("   • WCAG Criteria References")
            print("   • Smart Issue Grouping")
            print("   • Interactive HTML Reports")
            print("   • Professional Styling with Dark Mode")
            
            # Show summary statistics
            summary = scanner.get_scan_summary(scan_results)
            print(f"\n📊 Enhanced Scan Summary:")
            print(f"   Total URLs Scanned: {summary.total_urls_scanned}")
            print(f"   Successful Scans: {summary.successful_scans}")
            print(f"   Failed Scans: {summary.failed_scans}")
            print(f"   Total Issues Found: {summary.total_issues}")
            print(f"   Critical Issues: {summary.critical_issues}")
            print(f"   Moderate Issues: {summary.moderate_issues}")
            print(f"   Low Issues: {summary.low_issues}")
            print(f"   Average Accessibility Score: {summary.average_accessibility_score}/100")
            print(f"   Total Scan Duration: {summary.scan_duration:.2f}s")
            
            print(f"\n💡 Enhanced Toolkit Benefits:")
            print(f"   1. 🎯 Better Issue Detection: Advanced algorithms for vague labels and context")
            print(f"   2. 📊 Smarter Reports: Deduplication and categorization reduce noise")
            print(f"   3. 👁️ Visual Clarity: Beautiful reports with accessibility guidance")
            print(f"   4. 🔧 Actionable Fixes: Specific, contextual suggestions for each issue")
            print(f"   5. 📱 Professional Output: Multiple formats for different use cases")
            
            print(f"\n🚀 Next Steps:")
            print(f"   1. Review the enhanced HTML report for detailed analysis")
            print(f"   2. Use the JSON/CSV reports for programmatic processing")
            print(f"   3. Test the enhanced link and form accessibility checks")
            print(f"   4. Explore the browser extension for real-time scanning")
            print(f"   5. Customize the toolkit for your specific needs")
            
    except Exception as e:
        print(f"❌ Enhanced features demo failed with error: {e}")
        print("This might be due to network issues or missing dependencies.")
        print("Make sure you have installed all requirements: pip install -r requirements.txt")
        return 1
    
    return 0


def main():
    """Main entry point for the enhanced features demo."""
    print("🌟 Enhanced Accessibility Toolkit - Feature Showcase")
    print("Note: This demo showcases the latest toolkit enhancements.")
    print()
    
    try:
        exit_code = asyncio.run(showcase_enhanced_features())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Enhanced features demo interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
