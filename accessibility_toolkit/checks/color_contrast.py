"""
Color contrast accessibility check implementation.
"""

from typing import List, Tuple
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class ColorContrastCheck(BaseCheck):
    """Check for color contrast issues in text and UI elements."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.min_contrast_ratio = config.get("min_contrast_ratio", 4.5)
        self.large_text_ratio = config.get("large_text_ratio", 3.0)
        self.large_text_size = config.get("large_text_size", 18)  # pixels
        self.bold_large_text_size = config.get("bold_large_text_size", 14)  # pixels
    
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Check for color contrast issues.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        self.log_check_start(url)
        issues = []
        
        # Find all text elements that might have color contrast issues
        text_elements = self._find_text_elements(soup)
        
        for element in text_elements:
            # Extract color information
            colors = self._extract_colors(element)
            if not colors or len(colors) < 2:
                continue
            
            # Check contrast ratios
            contrast_issues = self._check_element_contrast(element, colors)
            issues.extend(contrast_issues)
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _find_text_elements(self, soup: BeautifulSoup) -> List:
        """Find elements that contain text and might have color contrast issues."""
        # Common text elements
        text_tags = ["p", "span", "div", "a", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "label"]
        elements = []
        
        for tag in text_tags:
            elements.extend(soup.find_all(tag))
        
        # Also check elements with specific classes that might be text
        text_classes = ["text", "content", "description", "caption", "label"]
        for class_name in text_classes:
            elements.extend(soup.find_all(class_=class_name))
        
        return elements
    
    def _extract_colors(self, element) -> List[Tuple[str, str]]:
        """
        Extract foreground and background colors from an element.
        
        Returns:
            List of (foreground_color, background_color) tuples
        """
        colors = []
        
        # Get computed styles (this is a simplified approach)
        style = element.get("style", "")
        classes = element.get("class", [])
        
        # Check inline styles
        if style:
            fg_color = self._extract_color_from_style(style, "color")
            bg_color = self._extract_color_from_style(style, "background-color")
            
            if fg_color and bg_color:
                colors.append((fg_color, bg_color))
        
        # Check for common color combinations
        # This is a simplified approach - in a real implementation,
        # you'd want to use a proper CSS parser and computed styles
        
        # Look for common problematic color combinations
        problematic_colors = [
            ("#000000", "#666666"),  # Black on dark gray
            ("#333333", "#CCCCCC"),  # Dark gray on light gray
            ("#0066CC", "#FFFFFF"),  # Blue on white (might be too light)
            ("#FF0000", "#FFFFFF"),  # Red on white
            ("#00FF00", "#FFFFFF"),  # Green on white
        ]
        
        # Check if element has any of these color combinations
        for fg, bg in problematic_colors:
            if self._element_has_colors(element, fg, bg):
                colors.append((fg, bg))
        
        return colors
    
    def _extract_color_from_style(self, style: str, property_name: str) -> str:
        """Extract color value from CSS style string."""
        import re
        
        pattern = rf"{property_name}:\s*([^;]+)"
        match = re.search(pattern, style, re.IGNORECASE)
        
        if match:
            color = match.group(1).strip()
            # Convert color names to hex if possible
            return self._normalize_color(color)
        
        return None
    
    def _normalize_color(self, color: str) -> str:
        """Normalize color to hex format."""
        # Common color name to hex mappings
        color_map = {
            "black": "#000000",
            "white": "#FFFFFF",
            "red": "#FF0000",
            "green": "#00FF00",
            "blue": "#0000FF",
            "yellow": "#FFFF00",
            "cyan": "#00FFFF",
            "magenta": "#FF00FF",
            "gray": "#808080",
            "grey": "#808080",
            "silver": "#C0C0C0",
            "maroon": "#800000",
            "olive": "#808000",
            "navy": "#000080",
            "purple": "#800080",
            "teal": "#008080",
            "lime": "#00FF00",
            "aqua": "#00FFFF",
            "fuchsia": "#FF00FF",
        }
        
        color_lower = color.lower().strip()
        
        # If it's already a hex color
        if color_lower.startswith("#"):
            return color_lower
        
        # If it's a named color
        if color_lower in color_map:
            return color_map[color_lower]
        
        # If it's an RGB/RGBA value, try to convert
        if color_lower.startswith("rgb"):
            # This is a simplified conversion - in practice you'd want a proper parser
            return "#808080"  # Default to gray for now
        
        return color_lower
    
    def _element_has_colors(self, element, fg_color: str, bg_color: str) -> bool:
        """Check if element has specific foreground and background colors."""
        # This is a simplified check - in practice you'd want to check computed styles
        style = element.get("style", "")
        
        fg_in_style = fg_color.lower() in style.lower()
        bg_in_style = bg_color.lower() in style.lower()
        
        return fg_in_style and bg_in_style
    
    def _check_element_contrast(self, element, colors: List[Tuple[str, str]]) -> List[AccessibilityIssue]:
        """Check contrast ratios for an element."""
        issues = []
        
        for fg_color, bg_color in colors:
            contrast_ratio = self._calculate_contrast_ratio(fg_color, bg_color)
            
            if contrast_ratio is None:
                continue
            
            # Determine required contrast ratio based on text size
            text_size = self._get_text_size(element)
            is_large_text = self._is_large_text(element, text_size)
            required_ratio = self.large_text_ratio if is_large_text else self.min_contrast_ratio
            
            if contrast_ratio < required_ratio:
                severity = self._get_contrast_severity(contrast_ratio, required_ratio)
                issues.append(self._create_contrast_issue(
                    element, fg_color, bg_color, contrast_ratio, required_ratio, severity
                ))
        
        return issues
    
    def _calculate_contrast_ratio(self, fg_color: str, bg_color: str) -> float:
        """
        Calculate the contrast ratio between two colors.
        
        This is a simplified implementation. In practice, you'd want to use
        a proper color contrast calculation library.
        """
        try:
            # Convert hex to RGB
            fg_rgb = self._hex_to_rgb(fg_color)
            bg_rgb = self._hex_to_rgb(bg_color)
            
            if not fg_rgb or not bg_rgb:
                return None
            
            # Calculate relative luminance
            fg_luminance = self._calculate_luminance(fg_rgb)
            bg_luminance = self._calculate_luminance(bg_rgb)
            
            # Calculate contrast ratio
            if fg_luminance > bg_luminance:
                lighter = fg_luminance
                darker = bg_luminance
            else:
                lighter = bg_luminance
                darker = fg_luminance
            
            ratio = (lighter + 0.05) / (darker + 0.05)
            return round(ratio, 2)
            
        except Exception:
            return None
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        try:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) == 3:
                hex_color = "".join([c + c for c in hex_color])
            
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            return (r, g, b)
        except Exception:
            return None
    
    def _calculate_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of RGB color."""
        r, g, b = rgb
        
        # Convert to sRGB
        r = r / 255
        g = g / 255
        b = b / 255
        
        # Apply gamma correction
        r = r ** 2.2 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g ** 2.2 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b ** 2.2 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        # Calculate luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def _get_text_size(self, element) -> int:
        """Get the text size of an element in pixels."""
        style = element.get("style", "")
        
        # Look for font-size in inline styles
        import re
        size_match = re.search(r"font-size:\s*(\d+)px", style, re.IGNORECASE)
        if size_match:
            return int(size_match.group(1))
        
        # Check for heading tags (they have default sizes)
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            heading_sizes = {"h1": 32, "h2": 24, "h3": 20, "h4": 18, "h5": 16, "h6": 14}
            return heading_sizes.get(element.name, 16)
        
        # Default text size
        return 16
    
    def _is_large_text(self, element, text_size: int) -> bool:
        """Determine if text is considered large for contrast requirements."""
        # Check if text is bold
        is_bold = (
            element.name in ["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"] or
            "font-weight: bold" in element.get("style", "").lower() or
            "font-weight: 700" in element.get("style", "").lower()
        )
        
        # Large text is 18px+ or 14px+ bold
        if is_bold:
            return text_size >= self.bold_large_text_size
        else:
            return text_size >= self.large_text_size
    
    def _get_contrast_severity(self, actual_ratio: float, required_ratio: float) -> SeverityLevel:
        """Determine severity based on how far the contrast ratio is from required."""
        difference = required_ratio - actual_ratio
        
        if difference > 2.0:
            return SeverityLevel.CRITICAL
        elif difference > 1.0:
            return SeverityLevel.MODERATE
        else:
            return SeverityLevel.LOW
    
    def _create_contrast_issue(self, element, fg_color: str, bg_color: str, 
                              actual_ratio: float, required_ratio: float, 
                              severity: SeverityLevel) -> AccessibilityIssue:
        """Create a color contrast issue."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        text_content = element.get_text(strip=True)[:50]
        
        return self.create_issue(
            issue_type=IssueType.POOR_COLOR_CONTRAST,
            severity=severity,
            description=f"Insufficient color contrast: {actual_ratio}:1 (requires {required_ratio}:1)",
            element=f"<{element.name}>{text_content}...</{element.name}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                f"Improve the color contrast ratio from {actual_ratio}:1 to at least {required_ratio}:1. "
                f"Current colors: foreground {fg_color}, background {bg_color}. "
                "Use a color contrast checker to find accessible color combinations."
            ),
            wcag_criteria=["1.4.3"],
            additional_info={
                **element_info,
                "foreground_color": fg_color,
                "background_color": bg_color,
                "actual_contrast": actual_ratio,
                "required_contrast": required_ratio
            }
        )
