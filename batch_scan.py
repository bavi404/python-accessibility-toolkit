#!/usr/bin/env python3
"""
Batch scanner for multiple websites.
Usage: python batch_scan.py urls.txt
"""

import sys
import asyncio
from pathlib import Path
from typing import List

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from accessibility_toolkit.scanner import AccessibilityScanner
from accessibility_toolkit.reports import ReportGenerator

async def batch_scan(urls: List[str], output_format: str = "html"):
    """
    Scan multiple websites in batch.
    
    Args:
        urls: List of URLs to scan
        output_format: Output format for reports
    """
    print(f"🚀 Starting batch scan of {len(urls)} websites...")
    print("=" * 60)
    
    scanner = AccessibilityScanner()
    results = []
    
    async with scanner:
        for i, url in enumerate(urls, 1):
            print(f"\n📡 [{i}/{len(urls)}] Scanning {url}...")
            
            try:
                result = await scanner.scan_url(url)
                results.append(result)
                
                if result.status == "completed":
                    print(f"   ✅ Found {len(result.issues)} issues")
                    print(f"   🎯 Score: {result.accessibility_score:.1f}/100")
                else:
                    print(f"   ❌ Failed: {result.error_message}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
    
    # Generate summary report
    if results:
        print(f"\n📊 BATCH SCAN COMPLETE")
        print("=" * 60)
        
        successful = [r for r in results if r.status == "completed"]
        failed = [r for r in results if r.status != "completed"]
        
        print(f"✅ Successful scans: {len(successful)}")
        print(f"❌ Failed scans: {len(failed)}")
        
        if successful:
            total_issues = sum(len(r.issues) for r in successful)
            avg_score = sum(r.accessibility_score for r in successful) / len(successful)
            
            print(f"📈 Total issues found: {total_issues}")
            print(f"🎯 Average accessibility score: {avg_score:.1f}/100")
            
            # Generate comprehensive report
            print(f"\n📄 Generating {output_format.upper()} report...")
            generator = ReportGenerator()
            report_path = generator.generate_report(successful, output_format)
            print(f"✅ Report saved to: {report_path}")
            
            # Show top issues across all sites
            print(f"\n🔍 TOP ISSUES ACROSS ALL SITES:")
            all_issues = []
            for result in successful:
                for issue in result.issues:
                    all_issues.append((result.url, issue))
            
            # Sort by severity (critical first)
            severity_order = {"critical": 3, "moderate": 2, "low": 1}
            all_issues.sort(key=lambda x: severity_order[x[1].severity.value], reverse=True)
            
            for i, (url, issue) in enumerate(all_issues[:10], 1):
                severity_icon = "🚨" if issue.severity.value == "critical" else "⚠️" if issue.severity.value == "moderate" else "ℹ️"
                print(f"   {i}. {severity_icon} {issue.description}")
                print(f"      Site: {url}")
                print(f"      Fix: {issue.suggested_fix[:100]}...")
                print()

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("🚀 Batch Website Accessibility Scanner")
        print("=" * 40)
        print("Usage: python batch_scan.py <urls_file> [format]")
        print("\nURLs file should contain one URL per line")
        print("Formats: html, json, csv, txt (default: html)")
        print("\nExample URLs file (urls.txt):")
        print("  https://example.com")
        print("  https://google.com")
        print("  https://github.com")
        print("\nUsage:")
        print("  python batch_scan.py urls.txt")
        print("  python batch_scan.py urls.txt json")
        return
    
    urls_file = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "html"
    
    # Validate output format
    valid_formats = ['html', 'json', 'csv', 'txt']
    if output_format not in valid_formats:
        print(f"❌ Invalid output format: {output_format}")
        print(f"   Valid formats: {', '.join(valid_formats)}")
        return
    
    # Read URLs from file
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not urls:
            print(f"❌ No URLs found in {urls_file}")
            return
            
        print(f"📖 Loaded {len(urls)} URLs from {urls_file}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {urls_file}")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Run batch scan
    asyncio.run(batch_scan(urls, output_format))

if __name__ == "__main__":
    main()
