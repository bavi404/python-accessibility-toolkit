"""
Checks for media accessibility: captions on <video> and transcripts for <audio>.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class MediaAccessibilityCheck(BaseCheck):
    """Ensure videos have captions and audio has transcripts available."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        # Check <video> elements for <track kind="captions"|"subtitles">
        for video in soup.find_all("video"):
            has_caption_track = False
            for track in video.find_all("track"):
                kind = (track.get("kind") or "").strip().lower()
                if kind in {"captions", "subtitles"}:
                    has_caption_track = True
                    break

            if not has_caption_track:
                element_str = str(video)[:120] + ("..." if len(str(video)) > 120 else "")
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.OTHER,
                        severity=SeverityLevel.CRITICAL,
                        description="Video element is missing captions/subtitles track.",
                        element="<video>",
                        context=self.get_parent_context(video),
                        line_number=self.get_line_number(video),
                        column_number=self.get_column_number(video),
                        suggested_fix=(
                            "Add a <track kind=\"captions\" srclang=\"en\" src=\"...vtt\" label=\"English\"> to the <video>."
                        ),
                        wcag_criteria=["1.2.2", "1.2.1"],
                        additional_info={"snippet": element_str}
                    )
                )

        # Check <audio> elements for presence of nearby transcript
        for audio in soup.find_all("audio"):
            has_transcript_link = False

            # Heuristics: look for a sibling/parent-descendant link mentioning transcript
            candidates = []
            if audio.parent:
                candidates.extend(audio.parent.find_all("a"))
            # also consider following siblings
            next_sib = audio.next_sibling
            while next_sib and getattr(next_sib, "name", None) is not None:
                if hasattr(next_sib, "find_all"):
                    candidates.extend(next_sib.find_all("a"))
                next_sib = next_sib.next_sibling

            for a in candidates:
                text = (a.get_text(strip=True) or "").lower()
                href = (a.get("href") or "").lower()
                if "transcript" in text or "transcript" in href:
                    has_transcript_link = True
                    break

            if not has_transcript_link:
                element_str = str(audio)[:120] + ("..." if len(str(audio)) > 120 else "")
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.OTHER,
                        severity=SeverityLevel.MODERATE,
                        description="Audio element appears to lack an accompanying transcript.",
                        element="<audio>",
                        context=self.get_parent_context(audio),
                        line_number=self.get_line_number(audio),
                        column_number=self.get_column_number(audio),
                        suggested_fix="Provide a text transcript near the audio or link to one.",
                        wcag_criteria=["1.2.1"],
                        additional_info={"snippet": element_str}
                    )
                )

        self.log_check_complete(url, len(issues))
        return issues


