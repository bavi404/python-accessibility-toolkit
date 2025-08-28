"""
Command-line interface for the accessibility toolkit.
"""

import asyncio
import click
import yaml
from pathlib import Path
from typing import List, Optional

from .scanner import AccessibilityScanner
from .reports import ReportGenerator


@click.group()
@click.version_option(version="1.0.0")
def main():
    """Pythonic Accessibility Toolkit - Automated website accessibility testing."""
    pass


@main.command()
@click.argument('url', required=False)
@click.option('--urls', '-u', help='File containing URLs to scan (one per line)')
@click.option('--output', '-o', default='html', 
              type=click.Choice(['html', 'json', 'csv', 'txt']),
              help='Output format for the report')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--timeout', '-t', default=30, type=int, help='Timeout in seconds')
@click.option('--max-retries', '-r', default=3, type=int, help='Maximum retry attempts')
@click.option('--min-severity', '-s', default='low',
              type=click.Choice(['low', 'moderate', 'critical']),
              help='Minimum severity level to include in results')
def scan(url, urls, output, config, timeout, max_retries, min_severity):
    """Scan website(s) for accessibility issues."""
    
    # Load configuration
    config_data = load_config(config) if config else {}
    
    # Override config with CLI options
    config_data.update({
        'timeout': timeout,
        'max_retries': max_retries
    })
    
    # Get URLs to scan
    urls_to_scan = []
    
    if url:
        urls_to_scan.append(url)
    
    if urls:
        urls_from_file = load_urls_from_file(urls)
        urls_to_scan.extend(urls_from_file)
    
    if not urls_to_scan:
        click.echo("❌ No URLs specified. Use --url or --urls option.")
        return
    
    # Remove duplicates and validate URLs
    urls_to_scan = list(set(urls_to_scan))
    valid_urls = [u for u in urls_to_scan if is_valid_url(u)]
    
    if len(valid_urls) != len(urls_to_scan):
        invalid_count = len(urls_to_scan) - len(valid_urls)
        click.echo(f"⚠️  Warning: {invalid_count} invalid URLs were skipped.")
    
    if not valid_urls:
        click.echo("❌ No valid URLs to scan.")
        return
    
    click.echo(f"🚀 Starting accessibility scan of {len(valid_urls)} URLs...")
    
    # Run the scan
    asyncio.run(run_scan(valid_urls, config_data, output, min_severity))


@main.command()
@click.argument('report_file')
@click.option('--output', '-o', default='html',
              type=click.Choice(['html', 'json', 'csv', 'txt']),
              help='Output format for the converted report')
def convert(report_file, output):
    """Convert an existing report to a different format."""
    
    if not Path(report_file).exists():
        click.echo(f"❌ Report file not found: {report_file}")
        return
    
    click.echo(f"🔄 Converting report to {output} format...")
    
    # Load the report file
    try:
        if report_file.endswith('.json'):
            import json
            with open(report_file, 'r') as f:
                data = json.load(f)
            
            # Extract scan results
            if 'scan_results' in data:
                scan_results = data['scan_results']
                # Convert back to ScanResult objects
                from .models import ScanResult
                results = [ScanResult(**result) for result in scan_results]
                
                # Generate new report
                generator = ReportGenerator()
                output_path = generator.generate_report(results, output)
                click.echo(f"✅ Report converted and saved to: {output_path}")
            else:
                click.echo("❌ Invalid report format. Expected 'scan_results' key.")
        else:
            click.echo("❌ Only JSON reports can be converted currently.")
    
    except Exception as e:
        click.echo(f"❌ Error converting report: {e}")


@main.command()
@click.option('--config', '-c', help='Configuration file path')
def config(config):
    """Show current configuration."""
    
    if config:
        config_data = load_config(config)
        click.echo("📋 Configuration:")
        click.echo(yaml.dump(config_data, default_flow_style=False))
    else:
        click.echo("📋 Default Configuration:")
        default_config = {
            'timeout': 30,
            'max_retries': 3,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'viewport': {'width': 1920, 'height': 1080},
            'wait_for': 2000,
            'alt_text': {'ignore_decorative': True, 'require_descriptive': True},
            'headings': {'require_h1': True, 'max_heading_level': 6},
            'color_contrast': {'min_contrast_ratio': 4.5, 'large_text_ratio': 3.0},
            'forms': {'require_labels': True, 'check_required_fields': True},
            'links': {'check_descriptive_text': True, 'check_empty_links': True},
            'aria': {'check_required_attributes': True, 'check_invalid_attributes': True},
            'landmarks': {'require_main': True, 'require_navigation': True},
            'keyboard': {'check_focusable_elements': True, 'check_tab_order': True}
        }
        click.echo(yaml.dump(default_config, default_flow_style=False))


async def run_scan(urls: List[str], config: dict, output_format: str, min_severity: str):
    """Run the accessibility scan."""
    
    try:
        # Initialize scanner
        async with AccessibilityScanner(config) as scanner:
            # Run the scan
            scan_results = await scanner.scan_multiple(urls)
            
            # Filter results by severity if needed
            if min_severity != 'low':
                scan_results = scanner.filter_results_by_severity(scan_results, min_severity)
            
            # Print summary
            scanner.print_summary(scan_results)
            
            # Generate report
            generator = ReportGenerator()
            report_path = generator.generate_report(scan_results, output_format)
            
            click.echo(f"📄 Report generated: {report_path}")
            
            # Show summary
            summary = scanner.get_scan_summary(scan_results)
            click.echo(f"\n🎯 Overall Accessibility Score: {summary.average_accessibility_score}/100")
            
            if summary.total_issues > 0:
                click.echo(f"🔧 Total Issues to Fix: {summary.total_issues}")
                click.echo("💡 Review the generated report for detailed information and suggested fixes.")
            else:
                click.echo("🎉 No accessibility issues found! Your website is following best practices.")
    
    except Exception as e:
        click.echo(f"❌ Error during scan: {e}")
        return 1
    
    return 0


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        click.echo(f"❌ Error loading config file: {e}")
        return {}


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a text file."""
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return urls
    except Exception as e:
        click.echo(f"❌ Error loading URLs file: {e}")
        return []


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


if __name__ == '__main__':
    main()
