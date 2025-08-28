"""
Pythonic Accessibility Toolkit

A comprehensive toolkit for automated website accessibility testing and reporting.
"""

__version__ = "1.0.0"
__author__ = "Pythonic Accessibility Toolkit Team"

from .scanner import AccessibilityScanner
from .models import AccessibilityIssue, ScanResult
from .reports import ReportGenerator

__all__ = [
    "AccessibilityScanner",
    "AccessibilityIssue", 
    "ScanResult",
    "ReportGenerator",
]
