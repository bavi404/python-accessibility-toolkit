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
        """Get the compact HTML template for reports (grouped by URL with tables)."""
        template_content = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Accessibility Scan Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #f6f7fb; color: #2d3748; }
        .wrap { max-width: 1200px; margin: 0 auto; padding: 24px; }
        .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: all 0.3s ease; }
        .card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-1px); }
        .head { background: linear-gradient(135deg,#5a67d8,#805ad5); color: #fff; padding: 28px; border-radius: 10px; position: relative; overflow: hidden; }
        .head::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(255,255,255,0.1) 100%); animation: shimmer 3s ease-in-out infinite; }
        @keyframes shimmer { 0%, 100% { transform: translateX(-100%); } 50% { transform: translateX(100%); } }
        .head h1 { margin: 0; font-weight: 500; position: relative; z-index: 1; }
        .sub { opacity:.9; margin-top:6px; position: relative; z-index: 1; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(160px,1fr)); gap: 12px; margin-top: 16px; position: relative; z-index: 1; }
        .kpi { background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:14px; text-align:center; transition: all 0.2s ease; cursor: pointer; }
        .kpi:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(90,103,216,0.15); }
        .kpi .n { font-size: 22px; font-weight: 700; color:#5a67d8; }
        .kpi .l { font-size: 12px; color:#718096; margin-top: 4px; }
        .section { margin-top: 24px; }
        .section h2 { margin:0 0 12px 0; font-size:18px; font-weight:600; border-left:4px solid #5a67d8; padding-left:10px; }
        .site { margin-top: 16px; }
        .site .site-head { display:flex; flex-wrap:wrap; gap:8px; justify-content:space-between; align-items:center; padding:14px 16px; background:#f7fafc; border-bottom:1px solid #e2e8f0; border-top-left-radius:10px; border-top-right-radius:10px; }
        .site .url { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background:#fff; border:1px solid #e2e8f0; padding:6px 10px; border-radius:6px; }
        .badge { background:#5a67d8; color:#fff; border-radius:999px; padding:4px 10px; font-size:12px; font-weight:700; }
        .toolbar { display:flex; flex-wrap:wrap; gap:8px; align-items:center; padding:10px 12px; border-bottom:1px solid #edf2f7; background:#fff; }
        .pill { border:1px solid #cbd5e0; border-radius:999px; padding:4px 10px; font-size:12px; cursor:pointer; user-select:none; transition: all 0.2s ease; }
        .pill:hover { background: #f7fafc; transform: translateY(-1px); }
        .pill.active { background:#2b6cb0; color:#fff; border-color:#2b6cb0; }
        .btn { background:#edf2f7; border:1px solid #cbd5e0; border-radius:6px; padding:6px 10px; font-size:12px; cursor:pointer; transition: all 0.2s ease; }
        .btn:hover { background:#e2e8f0; transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width:100%; border-collapse:collapse; }
        th, td { border-bottom:1px solid #edf2f7; text-align:left; padding:10px 8px; vertical-align: top; }
        th { background:#fafafa; font-weight:600; color:#4a5568; position: sticky; top: 0; }
        tr { transition: background-color 0.2s ease; }
        tr:hover { background-color: #f8fafc; }
        .sev { font-weight:700; padding:2px 8px; border-radius:999px; font-size:12px; display:inline-block; }
        .sev.critical { background:#e53e3e; color:#fff; }
        .sev.moderate { background:#dd6b20; color:#fff; }
        .sev.low { background:#38a169; color:#fff; }
        details { background:#fff; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden; transition: all 0.3s ease; }
        details:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        summary { cursor:pointer; list-style:none; padding:10px 12px; font-weight:600; transition: background-color 0.2s ease; }
        summary:hover { background-color: #f7fafc; }
        summary::-webkit-details-marker { display:none; }
        .muted { color:#718096; font-size:12px; }
        .fix { background:#e6fffa; border:1px solid #b2f5ea; color:#234e52; padding:8px 10px; border-radius:6px; }
        .footer { margin-top: 22px; text-align:center; color:#718096; font-size:12px; }
        
        /* Dark mode toggle */
        .theme-toggle { position: fixed; top: 20px; right: 20px; background: #fff; border: 1px solid #e2e8f0; border-radius: 50%; width: 48px; height: 48px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: all 0.3s ease; z-index: 1000; }
        .theme-toggle:hover { transform: scale(1.1); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
        
        /* Dark mode styles */
        body.dark { background: #1a202c; color: #e2e8f0; }
        body.dark .card { background: #2d3748; border-color: #4a5568; }
        body.dark .head { background: linear-gradient(135deg,#2d3748,#4a5568); }
        body.dark .kpi { background: #2d3748; border-color: #4a5568; }
        body.dark .kpi .n { color: #81e6d9; }
        body.dark .site .site-head { background: #2d3748; border-color: #4a5568; }
        body.dark .site .url { background: #4a5568; border-color: #718096; color: #e2e8f0; }
        body.dark .toolbar { background: #2d3748; border-color: #4a5568; }
        body.dark .pill { border-color: #4a5568; color: #e2e8f0; }
        body.dark .pill:hover { background: #4a5568; }
        body.dark .btn { background: #4a5568; border-color: #718096; color: #e2e8f0; }
        body.dark .btn:hover { background: #718096; }
        body.dark th { background: #2d3748; color: #e2e8f0; }
        body.dark tr:hover { background-color: #4a5568; }
        body.dark details { background: #2d3748; border-color: #4a5568; }
        body.dark summary:hover { background-color: #4a5568; }
        body.dark .theme-toggle { background: #2d3748; border-color: #4a5568; color: #e2e8f0; }
        
        @media (max-width: 720px) { .grid { grid-template-columns: repeat(2,1fr);} th:nth-child(5), td:nth-child(5) { display:none; } .theme-toggle { top: 10px; right: 10px; width: 40px; height: 40px; } }
    </style>
</head>
<body>
    <button class="theme-toggle" id="themeToggle" title="Toggle dark mode">🌙</button>
    <div class=\"wrap\">
        <div class=\"head card\"> 
            <h1>Accessibility Scan Report</h1>
            <div class=\"sub\">Generated {{ generated_at }}</div>
            <div class=\"grid\" style=\"margin-top:12px\">
                <div class=\"kpi\"><div class=\"n\">{{ total_urls }}</div><div class=\"l\">URLs</div></div>
                <div class=\"kpi\"><div class=\"n\">{{ successful_scans }}</div><div class=\"l\">Successful</div></div>
                <div class=\"kpi\"><div class=\"n\">{{ summary.total_issues }}</div><div class=\"l\">Total Issues</div></div>
                <div class=\"kpi\"><div class=\"n\">{{ "%.1f"|format(summary.average_accessibility_score) }}</div><div class=\"l\">Avg Score</div></div>
            </div>
        </div>

        <div class=\"section\">
            <h2>Results by URL</h2>
            {% for result in scan_results %}
            <div class=\"site card\">
                <div class=\"site-head\">
                    <div class=\"url\">{{ result.url }}</div>
                    <div class=\"badge\">Score: {{ result.accessibility_score }}/100</div>
                </div>

                {% if result.status != 'completed' %}
                    <div style=\"padding:14px\">Scan failed: {{ result.error_message }}</div>
                {% elif result.issues|length == 0 %}
                    <div style=\"padding:20px; text-align:center; background:#f0f9ff; border:1px solid #0ea5e9; border-radius:8px; margin:12px;\">
                        <div style=\"font-size:48px; margin-bottom:12px;\">🎉</div>
                        <h3 style=\"color:#0c4a6e; margin:0 0 8px 0;\">Great News!</h3>
                        <p style=\"color:#0369a1; margin:0; font-size:14px;\">
                            {% if result.message %}{{ result.message }}{% else %}No accessibility issues found on this page!{% endif %}
                        </p>
                        <p style=\"color:#0c4a6e; margin:8px 0 0 0; font-size:12px;\">Your page meets accessibility standards.</p>
                    </div>
                {% else %}
                <details data-section="crit">
                    <summary>🚨 Critical ({{ result.issues|selectattr('severity.value','equalto','critical')|list|length }})</summary>
                    <div class="toolbar">
                        <span class="pill filter-sev" data-sev="critical">Critical</span>
                        <span class="pill filter-sev" data-sev="moderate">Moderate</span>
                        <span class="pill filter-sev" data-sev="low">Low</span>
                        <span class="pill active" data-filter="all">Show All</span>
                        <span style="flex:1"></span>
                        <button class="btn act-copy-csv">Copy CSV</button>
                        <button class="btn act-download-json">Download JSON</button>
                    </div>
                    <div style=\"padding: 0 12px 12px 12px\">
                        {% set crit = result.issues|selectattr('severity.value','equalto','critical')|list %}
                        {% if crit %}
                        <table>
                            <thead>
                                <tr>
                                    <th style=\"width:120px\">Type</th>
                                    <th>Description</th>
                                    <th style=\"width:22%\">Element</th>
                                    <th style=\"width:16%\">WCAG</th>
                                    <th style=\"width:26%\">Suggested Fix</th>
                                </tr>
                            </thead>
                            <tbody>
                            {% for issue in crit %}
                                <tr data-sev="critical" data-type="{{ issue.issue_type.value }}" data-wcag="{{ issue.wcag_criteria|join(' ') }}">
                                    <td><span class=\"sev critical\">Critical</span> {{ issue.issue_type.value.replace('_',' ').title() }}</td>
                                    <td>{{ issue.description }}</td>
                                    <td><div class=\"muted\">{{ issue.element }}</div></td>
                                    <td>{{ issue.wcag_criteria|join(', ') }}</td>
                                    <td>
                                        <div class=\"fix\">{{ issue.suggested_fix }}</div>
                                        {% if issue.additional_info and issue.additional_info.screenshot %}
                                            <div style=\"margin-top:6px\"><img src=\"{{ issue.additional_info.screenshot }}\" alt=\"screenshot\" style=\"max-width:200px;border:1px solid #e2e8f0;border-radius:6px\"></div>
                                        {% endif %}
                                    </td>
                                </tr>
                            {% endfor %}
                            </tbody>
                        </table>
                        {% else %}
                        <div class=\"muted\" style=\"padding:10px\">No critical issues.</div>
                        {% endif %}
                    </div>
                </details>

                <details data-section="mod">
                    <summary>⚠️ Moderate ({{ result.issues|selectattr('severity.value','equalto','moderate')|list|length }})</summary>
                    <div class="toolbar">
                        <span class="pill filter-sev" data-sev="critical">Critical</span>
                        <span class="pill filter-sev" data-sev="moderate">Moderate</span>
                        <span class="pill filter-sev" data-sev="low">Low</span>
                        <span class="pill active" data-filter="all">Show All</span>
                        <span style="flex:1"></span>
                        <button class="btn act-copy-csv">Copy CSV</button>
                        <button class="btn act-download-json">Download JSON</button>
                    </div>
                    <div style=\"padding: 0 12px 12px 12px\">
                        {% set mod = result.issues|selectattr('severity.value','equalto','moderate')|list %}
                        {% if mod %}
                        <table>
                            <thead>
                                <tr>
                                    <th style=\"width:120px\">Type</th>
                                    <th>Description</th>
                                    <th style=\"width:22%\">Element</th>
                                    <th style=\"width:16%\">WCAG</th>
                                    <th style=\"width:26%\">Suggested Fix</th>
                                </tr>
                            </thead>
                            <tbody>
                            {% for issue in mod %}
                                <tr data-sev="moderate" data-type="{{ issue.issue_type.value }}" data-wcag="{{ issue.wcag_criteria|join(' ') }}">
                                    <td><span class=\"sev moderate\">Moderate</span> {{ issue.issue_type.value.replace('_',' ').title() }}</td>
                                    <td>{{ issue.description }}</td>
                                    <td><div class=\"muted\">{{ issue.element }}</div></td>
                                    <td>{{ issue.wcag_criteria|join(', ') }}</td>
                                    <td>
                                        <div class=\"fix\">{{ issue.suggested_fix }}</div>
                                        {% if issue.additional_info and issue.additional_info.screenshot %}
                                            <div style=\"margin-top:6px\"><img src=\"{{ issue.additional_info.screenshot }}\" alt=\"screenshot\" style=\"max-width:200px;border:1px solid #e2e8f0;border-radius:6px\"></div>
                                        {% endif %}
                                    </td>
                                </tr>
                            {% endfor %}
                            </tbody>
                        </table>
                        {% else %}
                        <div class=\"muted\" style=\"padding:10px\">No moderate issues.</div>
                        {% endif %}
                    </div>
                </details>

                <details data-section="low">
                    <summary>ℹ️ Low ({{ result.issues|selectattr('severity.value','equalto','low')|list|length }})</summary>
                    <div class="toolbar">
                        <span class="pill filter-sev" data-sev="critical">Critical</span>
                        <span class="pill filter-sev" data-sev="moderate">Moderate</span>
                        <span class="pill filter-sev" data-sev="low">Low</span>
                        <span class="pill active" data-filter="all">Show All</span>
                        <span style="flex:1"></span>
                        <button class="btn act-copy-csv">Copy CSV</button>
                        <button class="btn act-download-json">Download JSON</button>
                    </div>
                    <div style=\"padding: 0 12px 12px 12px\">
                        {% set low = result.issues|selectattr('severity.value','equalto','low')|list %}
                        {% if low %}
                        <table>
                            <thead>
                                <tr>
                                    <th style=\"width:120px\">Type</th>
                                    <th>Description</th>
                                    <th style=\"width:22%\">Element</th>
                                    <th style=\"width:16%\">WCAG</th>
                                    <th style=\"width:26%\">Suggested Fix</th>
                                </tr>
                            </thead>
                            <tbody>
                            {% for issue in low %}
                                <tr data-sev="low" data-type="{{ issue.issue_type.value }}" data-wcag="{{ issue.wcag_criteria|join(' ') }}">
                                    <td><span class=\"sev low\">Low</span> {{ issue.issue_type.value.replace('_',' ').title() }}</td>
                                    <td>{{ issue.description }}</td>
                                    <td><div class=\"muted\">{{ issue.element }}</div></td>
                                    <td>{{ issue.wcag_criteria|join(', ') }}</td>
                                    <td>
                                        <div class=\"fix\">{{ issue.suggested_fix }}</div>
                                        {% if issue.additional_info and issue.additional_info.screenshot %}
                                            <div style=\"margin-top:6px\"><img src=\"{{ issue.additional_info.screenshot }}\" alt=\"screenshot\" style=\"max-width:200px;border:1px solid #e2e8f0;border-radius:6px\"></div>
                                        {% endif %}
                                    </td>
                                </tr>
                            {% endfor %}
                            </tbody>
                        </table>
                        {% else %}
                        <div class=\"muted\" style=\"padding:10px\">No low priority issues.</div>
                        {% endif %}
                    </div>
                </details>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        <div class=\"footer\">Generated by Pythonic Accessibility Toolkit • {{ generated_at }}</div>
    </div>
    <script>
      (function(){
        // Remember details open/closed state
        document.querySelectorAll('.site').forEach(function(site){
          const url = site.querySelector('.url')?.textContent?.trim() || Math.random().toString(36);
          site.querySelectorAll('details').forEach(function(d){
            const key = 'a11y_rep_'+url+'_'+d.getAttribute('data-section');
            const saved = localStorage.getItem(key);
            if(saved !== null){ d.open = saved === '1'; }
            d.addEventListener('toggle', function(){ localStorage.setItem(key, d.open ? '1':'0'); });
          });
        });

        // Filters by severity pills within each details
        document.querySelectorAll('.site details').forEach(function(block){
          const table = block.querySelector('table'); if(!table) return;
          const rows = Array.from(table.querySelectorAll('tbody tr'));
          const pillAll = block.querySelector('[data-filter="all"]');
          block.querySelectorAll('.filter-sev').forEach(function(pill){
            pill.addEventListener('click', function(){
              block.querySelectorAll('.pill').forEach(p=>p.classList.remove('active'));
              pill.classList.add('active');
              const sev = pill.getAttribute('data-sev');
              rows.forEach(function(r){ r.style.display = (r.getAttribute('data-sev')===sev)?'':'none'; });
            });
          });
          if(pillAll){ pillAll.addEventListener('click', function(){
            block.querySelectorAll('.pill').forEach(p=>p.classList.remove('active'));
            pillAll.classList.add('active');
            rows.forEach(r=>r.style.display='');
          });}
        });

        function tableToData(table){
          const data = [];
          table.querySelectorAll('tbody tr').forEach(function(tr){
            const tds = tr.querySelectorAll('td');
            data.push({
              severity: tr.getAttribute('data-sev'),
              type: tds[0]?.innerText.trim(),
              description: tds[1]?.innerText.trim(),
              element: tds[2]?.innerText.trim(),
              wcag: tds[3]?.innerText.trim(),
              fix: tds[4]?.innerText.trim(),
            });
          });
          return data;
        }

        function dataToCSV(arr){
          if(!arr.length) return '';
          const cols = Object.keys(arr[0]);
          const esc = s => '"'+String(s).replace(/"/g,'""')+'"';
          const lines = [cols.join(',')].concat(arr.map(o=>cols.map(c=>esc(o[c]||'')).join(',')));
          return lines.join('\n');
        }

        function download(filename, content, mime){
          const blob = new Blob([content], {type: mime});
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url; a.download = filename; document.body.appendChild(a); a.click();
          setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 0);
        }

        // Actions: Copy CSV and Download JSON
        document.querySelectorAll('.site details').forEach(function(block){
          const table = block.querySelector('table'); if(!table) return;
          const data = () => tableToData(table);
          const btnCSV = block.querySelector('.act-copy-csv');
          const btnJSON = block.querySelector('.act-download-json');
          if(btnCSV){ btnCSV.addEventListener('click', function(){
            const csv = dataToCSV(data());
            navigator.clipboard.writeText(csv).then(()=>{ btnCSV.textContent='Copied!'; setTimeout(()=>btnCSV.textContent='Copy CSV',1200); });
          });}
          if(btnJSON){ btnJSON.addEventListener('click', function(){
            const json = JSON.stringify(data(), null, 2);
            download('issues.json', json, 'application/json');
          });}
        });
      })();
    </script>
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
        <div class="metric">Total Duration: {summary.scan_duration:.2f}s        </div>
    </div>
    
    <script>
        // Dark mode toggle
        const themeToggle = document.getElementById('themeToggle');
        const body = document.body;
        
        // Load saved theme preference
        const savedTheme = localStorage.getItem('accessibility-theme');
        if (savedTheme === 'dark') {{
            body.classList.add('dark');
            themeToggle.textContent = '☀️';
        }}
        
        themeToggle.addEventListener('click', () => {{
            body.classList.toggle('dark');
            const isDark = body.classList.contains('dark');
            localStorage.setItem('accessibility-theme', isDark ? 'dark' : 'light');
            themeToggle.textContent = isDark ? '☀️' : '🌙';
        }});
        
        // Interactive features
        document.addEventListener('DOMContentLoaded', () => {{
            // Filter pills functionality
            const filterPills = document.querySelectorAll('.pill');
            filterPills.forEach(pill => {{
                pill.addEventListener('click', () => {{
                    const section = pill.closest('details');
                    const pills = section.querySelectorAll('.pill');
                    pills.forEach(p => p.classList.remove('active'));
                    pill.classList.add('active');
                    
                    // Filter table rows
                    const table = section.querySelector('table');
                    if (table) {{
                        const rows = table.querySelectorAll('tbody tr');
                        const filterType = pill.dataset.filter;
                        const filterSev = pill.dataset.sev;
                        
                        rows.forEach(row => {{
                            if (filterType === 'all' || row.dataset.sev === filterSev) {{
                                row.style.display = '';
                            }} else {{
                                row.style.display = 'none';
                            }}
                        }});
                    }}
                }});
            }});
            
            // Copy CSV functionality
            document.querySelectorAll('.act-copy-csv').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    const section = btn.closest('details');
                    const table = section.querySelector('table');
                    if (table) {{
                        const csv = tableToCSV(table);
                        navigator.clipboard.writeText(csv).then(() => {{
                            btn.textContent = 'Copied!';
                            setTimeout(() => btn.textContent = 'Copy CSV', 2000);
                        }});
                    }}
                }});
            }});
            
            // Download JSON functionality
            document.querySelectorAll('.act-download-json').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    const section = btn.closest('details');
                    const table = section.querySelector('table');
                    if (table) {{
                        const json = tableToJSON(table);
                        downloadJSON(json, 'accessibility_issues.json');
                    }}
                }});
            }});
            
            // Smooth scroll to sections
            document.querySelectorAll('summary').forEach(summary => {{
                summary.addEventListener('click', () => {{
                    setTimeout(() => {{
                        summary.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                    }}, 100);
                }});
            }});
        }});
        
        function tableToCSV(table) {{
            const rows = Array.from(table.querySelectorAll('tr'));
            return rows.map(row => 
                Array.from(row.querySelectorAll('th, td'))
                    .map(cell => `"${{cell.textContent.trim()}}"`)
                    .join(',')
            ).join('\\n');
        }}
        
        function tableToJSON(table) {{
            const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            return rows.map(row => {{
                const cells = Array.from(row.querySelectorAll('td'));
                const obj = {{}};
                headers.forEach((header, index) => {{
                    obj[header] = cells[index] ? cells[index].textContent.trim() : '';
                }});
                return obj;
            }});
        }}
        
        function downloadJSON(data, filename) {{
            const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }}
    </script>
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
