"""Markdown code block analyzer for technical drafts."""
import re

def analyze_technical_draft(markdown_text: str) -> dict:
    if not markdown_text or not markdown_text.strip():
        return {"code_to_text_ratio": 0.0, "languages": [], "total_code_lines": 0, "total_lines": 0}

    lines = markdown_text.split("\n")
    total_lines = len(lines)
    code_lines_count = 0
    in_code_block = False
    languages: list[str] = []
    pattern = re.compile(r"^```(\w*)")

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                match = pattern.match(stripped)
                if match and match.group(1):
                    languages.append(match.group(1).lower())
            else:
                in_code_block = False
        elif in_code_block:
            code_lines_count += 1

    return {
        "code_to_text_ratio": round(code_lines_count / max(total_lines, 1), 3),
        "languages": sorted(set(languages)),
        "total_code_lines": code_lines_count,
        "total_lines": total_lines,
    }
