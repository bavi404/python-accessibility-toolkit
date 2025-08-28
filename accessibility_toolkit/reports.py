"""
Report generator for accessibility scan results.
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from jinja2 import Template
from .models import ScanResult, ScanSummary


class ReportGenerator:
    """Generate various report formats for accessibility scan results."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the report generator.
        
        Args:
            config: Configuration dictionary for report generation
        """
        self.config = config or {}
        self.template_dir = self.config.get("template_dir", "templates")
        self.output_dir = self.config.get("output_dir", "reports")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_report(self, scan_results: List[ScanResult], 
                       output_format: str = "html",
                       filename: str = None) -> str:
        """
        Generate a report in the specified format.
        
        Args:
            scan_results: List of ScanResult objects
            output_format: Output format (html, json, csv, txt)
            filename: Optional filename for the report
            
        Returns:
            Path to the generated report file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accessibility_report_{timestamp}.{output_format}"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if output_format.lower() == "html":
            return self._generate_html_report(scan_results, filepath)
        elif output_format.lower() == "json":
            return self._generate_json_report(scan_results, filepath)
        elif output_format.lower() == "csv":
            return self._generate_csv_report(scan_results, filepath)
        elif output_format.lower() == "txt":
            return self._generate_text_report(scan_results, filepath)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_html_report(self, scan_results: List[ScanResult], filepath: str) -> str:
        """Generate an HTML report."""
        summary = ScanSummary.from_scan_results(scan_results)
        
        # Prepare data for template
        report_data = {
            "summary": summary,
            "scan_results": scan_results,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_urls": len(scan_results),
            "successful_scans": summary.successful_scans,
            "failed_scans": summary.failed_scans,
        }
        
        # Group issues by severity
        critical_issues = []
        moderate_issues = []
        low_issues = []
        
        for result in scan_results:
            if result.status == "completed":
                for issue in result.issues:
                    if issue.severity.value == "critical":
                        critical_issues.append((result, issue))
                    elif issue.severity.value == "moderate":
                        moderate_issues.append((result, issue))
                    elif issue.severity.value == "low":
                        low_issues.append((result, issue))
        
        report_data.update({
            "critical_issues": critical_issues,
            "moderate_issues": moderate_issues,
            "low_issues": low_issues,
        })
        
        # Use HTML template
        html_content = self._get_html_template().render(**report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_json_report(self, scan_results: List[ScanResult], filepath: str) -> str:
        """Generate a JSON report."""
        import json
        
        # Convert scan results to dictionary format
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": ScanSummary.from_scan_results(scan_results).to_dict(),
            "scan_results": [result.to_dict() for result in scan_results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def _generate_csv_report(self, scan_results: List[ScanResult], filepath: str) -> str:
        """Generate a CSV report."""
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "URL", "Status", "Page Title", "Total Issues", 
                "Critical Issues", "Moderate Issues", "Low Issues", 
                "Accessibility Score", "Scan Duration", "Error Message"
            ])
            
            # Write data
            for result in scan_results:
                writer.writerow([
                    result.url,
                    result.status,
                    result.page_title,
                    result.total_issues,
                    result.critical_issues_count,
                    result.moderate_issues_count,
                    result.low_issues_count,
                    result.accessibility_score,
                    f"{result.scan_duration:.2f}s",
                    result.error_message or ""
                ])
        
        return filepath
    
    def _generate_text_report(self, scan_results: List[ScanResult], filepath: str) -> str:
        """Generate a plain text report."""
        summary = ScanSummary.from_scan_results(scan_results)
        
        lines = []
        lines.append("=" * 80)
        lines.append("ACCESSIBILITY SCAN REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total URLs Scanned: {summary.total_urls_scanned}")
        lines.append(f"Successful Scans: {summary.successful_scans}")
        lines.append(f"Failed Scans: {summary.failed_scans}")
        lines.append(f"Total Issues: {summary.total_issues}")
        lines.append(f"Critical Issues: {summary.critical_issues}")
        lines.append(f"Moderate Issues: {summary.moderate_issues}")
        lines.append(f"Low Issues: {summary.low_issues}")
        lines.append(f"Average Accessibility Score: {summary.average_accessibility_score}/100")
        lines.append(f"Total Scan Duration: {summary.scan_duration:.2f}s")
        lines.append("")
        
        # Detailed results
        for i, result in enumerate(scan_results, 1):
            lines.append(f"URL {i}: {result.url}")
            lines.append(f"Status: {result.status}")
            
            if result.status == "completed":
                lines.append(f"Page Title: {result.page_title}")
                lines.append(f"Accessibility Score: {result.accessibility_score}/100")
                lines.append(f"Issues: {result.total_issues} (C:{result.critical_issues_count} M:{result.moderate_issues_count} L:{result.low_issues_count})")
                lines.append(f"Scan Duration: {result.scan_duration:.2f}s")
                
                if result.issues:
                    lines.append("Issues Found:")
                    for issue in result.issues:
                        severity_icon = {"critical": "🚨", "moderate": "⚠️", "low": "ℹ️"}.get(issue.severity.value, "❓")
                        lines.append(f"  {severity_icon} {issue.description}")
                        lines.append(f"     Element: {issue.element}")
                        lines.append(f"     Suggested Fix: {issue.suggested_fix}")
                        lines.append("")
            else:
                lines.append(f"Error: {result.error_message}")
                lines.append(f"Scan Duration: {result.scan_duration:.2f}s")
            
            lines.append("-" * 40)
            lines.append("")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return filepath
    
    def _get_html_template(self) -> Template:
        """Get the HTML template for reports."""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Scan Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header .subtitle {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-weight: 300;
        }
        .summary {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        .summary-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .summary-card .label {
            color: #6c757d;
            margin-top: 5px;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #495057;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .issue-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .issue-header {
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .issue-severity {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .severity-critical {
            background: #dc3545;
            color: white;
        }
        .severity-moderate {
            background: #fd7e14;
            color: white;
        }
        .severity-low {
            background: #28a745;
            color: white;
        }
        .issue-content {
            padding: 20px;
        }
        .issue-description {
            font-weight: bold;
            margin-bottom: 10px;
            color: #495057;
        }
        .issue-details {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }
        .issue-details strong {
            color: #495057;
        }
        .issue-fix {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
        }
        .url-section {
            background: #e9ecef;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .url-section h3 {
            margin: 0 0 10px 0;
            color: #495057;
        }
        .url-section .url {
            font-family: monospace;
            background: white;
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid #ced4da;
        }
        .score-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .no-issues {
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 40px;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }
        @media (max-width: 768px) {
            .summary-grid {
                grid-template-columns: 1fr;
            }
            .issue-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Accessibility Scan Report</h1>
            <p class="subtitle">Generated on {{ generated_at }}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Scan Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="number">{{ total_urls }}</div>
                    <div class="label">URLs Scanned</div>
                </div>
                <div class="summary-card">
                    <div class="number">{{ successful_scans }}</div>
                    <div class="label">Successful Scans</div>
                </div>
                <div class="summary-card">
                    <div class="number">{{ summary.total_issues }}</div>
                    <div class="label">Total Issues</div>
                </div>
                <div class="summary-card">
                    <div class="number">{{ "%.1f"|format(summary.average_accessibility_score) }}</div>
                    <div class="label">Avg Score</div>
                </div>
            </div>
            
            <div class="summary-grid" style="margin-top: 20px;">
                <div class="summary-card">
                    <div class="number" style="color: #dc3545;">{{ summary.critical_issues }}</div>
                    <div class="label">Critical Issues</div>
                </div>
                <div class="summary-card">
                    <div class="number" style="color: #fd7e14;">{{ summary.moderate_issues }}</div>
                    <div class="label">Moderate Issues</div>
                </div>
                <div class="summary-card">
                    <div class="number" style="color: #28a745;">{{ summary.low_issues }}</div>
                    <div class="label">Low Issues</div>
                </div>
                <div class="summary-card">
                    <div class="number">{{ "%.1f"|format(summary.scan_duration) }}s</div>
                    <div class="label">Total Duration</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            {% if critical_issues %}
            <div class="section">
                <h2>🚨 Critical Issues ({{ critical_issues|length }})</h2>
                {% for result, issue in critical_issues %}
                <div class="url-section">
                    <h3>URL: {{ result.url }}</h3>
                    <div class="url">{{ result.url }}</div>
                    <div style="margin-top: 10px;">
                        <span class="score-badge">Score: {{ result.accessibility_score }}/100</span>
                    </div>
                </div>
                <div class="issue-card">
                    <div class="issue-header">
                        <span class="issue-severity severity-critical">Critical</span>
                        <span>{{ issue.issue_type.value.replace('_', ' ').title() }}</span>
                    </div>
                    <div class="issue-content">
                        <div class="issue-description">{{ issue.description }}</div>
                        <div class="issue-details">
                            <strong>Element:</strong> {{ issue.element }}<br>
                            <strong>Context:</strong> {{ issue.context }}<br>
                            {% if issue.line_number %}<strong>Line:</strong> {{ issue.line_number }}<br>{% endif %}
                            {% if issue.wcag_criteria %}<strong>WCAG Criteria:</strong> {{ issue.wcag_criteria|join(', ') }}{% endif %}
                        </div>
                        <div class="issue-fix">
                            <strong>Suggested Fix:</strong><br>
                            {{ issue.suggested_fix }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if moderate_issues %}
            <div class="section">
                <h2>⚠️ Moderate Issues ({{ moderate_issues|length }})</h2>
                {% for result, issue in moderate_issues %}
                <div class="url-section">
                    <h3>URL: {{ result.url }}</h3>
                    <div class="url">{{ result.url }}</div>
                    <div style="margin-top: 10px;">
                        <span class="score-badge">Score: {{ result.accessibility_score }}/100</span>
                    </div>
                </div>
                <div class="issue-card">
                    <div class="issue-header">
                        <span class="issue-severity severity-moderate">Moderate</span>
                        <span>{{ issue.issue_type.value.replace('_', ' ').title() }}</span>
                    </div>
                    <div class="issue-content">
                        <div class="issue-description">{{ issue.description }}</div>
                        <div class="issue-details">
                            <strong>Element:</strong> {{ issue.element }}<br>
                            <strong>Context:</strong> {{ issue.context }}<br>
                            {% if issue.line_number %}<strong>Line:</strong> {{ issue.line_number }}<br>{% endif %}
                            {% if issue.wcag_criteria %}<strong>WCAG Criteria:</strong> {{ issue.wcag_criteria|join(', ') }}{% endif %}
                        </div>
                        <div class="issue-fix">
                            <strong>Suggested Fix:</strong><br>
                            {{ issue.suggested_fix }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if low_issues %}
            <div class="section">
                <h2>ℹ️ Low Priority Issues ({{ low_issues|length }})</h2>
                {% for result, issue in low_issues %}
                <div class="url-section">
                    <h3>URL: {{ result.url }}</h3>
                    <div class="url">{{ result.url }}</div>
                    <div style="margin-top: 10px;">
                        <span class="score-badge">Score: {{ result.accessibility_score }}/100</span>
                    </div>
                </div>
                <div class="issue-card">
                    <div class="issue-header">
                        <span class="issue-severity severity-low">Low</span>
                        <span>{{ issue.issue_type.value.replace('_', ' ').title() }}</span>
                    </div>
                    <div class="issue-content">
                        <div class="issue-description">{{ issue.description }}</div>
                        <div class="issue-details">
                            <strong>Element:</strong> {{ issue.element }}<br>
                            <strong>Context:</strong> {{ issue.context }}<br>
                            {% if issue.line_number %}<strong>Line:</strong> {{ issue.line_number }}<br>{% endif %}
                            {% if issue.wcag_criteria %}<strong>WCAG Criteria:</strong> {{ issue.wcag_criteria|join(', ') }}{% endif %}
                        </div>
                        <div class="issue-fix">
                            <strong>Suggested Fix:</strong><br>
                            {{ issue.suggested_fix }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if summary.total_issues == 0 %}
            <div class="section">
                <h2>✅ No Issues Found</h2>
                <div class="no-issues">
                    <p>🎉 Congratulations! No accessibility issues were found in the scanned URLs.</p>
                    <p>Your website appears to be following accessibility best practices.</p>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Generated by Pythonic Accessibility Toolkit</p>
            <p>For more information about web accessibility, visit <a href="https://www.w3.org/WAI/" target="_blank">W3C Web Accessibility Initiative</a></p>
        </div>
    </div>
</body>
</html>
        """
        
        return Template(template_content)
    
    def generate_summary_report(self, scan_results: List[ScanResult], 
                               output_format: str = "html") -> str:
        """
        Generate a summary report with just the key metrics.
        
        Args:
            scan_results: List of ScanResult objects
            output_format: Output format for the summary
            
        Returns:
            Path to the generated summary report
        """
        summary = ScanSummary.from_scan_results(scan_results)
        
        if output_format.lower() == "html":
            return self._generate_html_summary(summary)
        elif output_format.lower() == "json":
            return self._generate_json_summary(summary)
        else:
            raise ValueError(f"Summary reports only support HTML and JSON formats")
    
    def _generate_html_summary(self, summary: ScanSummary) -> str:
        """Generate an HTML summary report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"accessibility_summary_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # Simplified HTML template for summary
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Summary Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
        .metric {{ margin: 10px 0; }}
        .score {{ font-size: 24px; font-weight: bold; color: #007bff; }}
    </style>
</head>
<body>
    <h1>Accessibility Summary Report</h1>
    <div class="summary">
        <div class="metric">Total URLs: {summary.total_urls_scanned}</div>
        <div class="metric">Successful Scans: {summary.successful_scans}</div>
        <div class="metric">Failed Scans: {summary.failed_scans}</div>
        <div class="metric">Total Issues: {summary.total_issues}</div>
        <div class="metric">Critical Issues: {summary.critical_issues}</div>
        <div class="metric">Moderate Issues: {summary.moderate_issues}</div>
        <div class="metric">Low Issues: {summary.low_issues}</div>
        <div class="metric">Average Score: <span class="score">{summary.average_accessibility_score}/100</span></div>
        <div class="metric">Total Duration: {summary.scan_duration:.2f}s</div>
    </div>
</body>
</html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_json_summary(self, summary: ScanSummary) -> str:
        """Generate a JSON summary report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"accessibility_summary_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        import json
        
        summary_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary.to_dict()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        return filepath
