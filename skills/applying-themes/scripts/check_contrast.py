#!/usr/bin/env python3
"""Verify WCAG contrast ratios for theme files or ad-hoc color pairs.

Theme files declare their required pairs in a fenced ```contrast block:

    ```contrast
    ink        on base      AA        # body text, needs 4.5:1
    ink-2      on surface   AA
    accent-ink on accent    AA
    ink-3      on base      AA-large  # meta text at >=24px, needs 3:1
    accent     on base      UI        # non-text boundary, needs 3:1
    ```

Token values are read from the file's `| token | #hex |` palette table.

Usage:
    python3 check_contrast.py themes/ocean-depths.md
    python3 check_contrast.py themes/*.md
    python3 check_contrast.py --pair "#55504a" "#f4f1ea"
"""

import argparse
import re
import sys
from pathlib import Path

LEVELS = {"AA": 4.5, "AA-large": 3.0, "UI": 3.0, "AAA": 7.0, "AAA-large": 4.5}


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    """WCAG 2.x relative luminance of an #rgb or #rrggbb color."""
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6:
        raise ValueError(f"not a hex color: {hex_color!r}")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return (0.2126 * _srgb_to_linear(r)
            + 0.7152 * _srgb_to_linear(g)
            + 0.0722 * _srgb_to_linear(b))


def contrast(fg: str, bg: str) -> float:
    lo, hi = sorted((luminance(fg), luminance(bg)))
    return (hi + 0.05) / (lo + 0.05)


def parse_palette(text: str) -> dict[str, str]:
    """Collect `| token | #hex |` rows from any markdown table in the file."""
    palette = {}
    for token, value in re.findall(
        r"^\|\s*`?([a-z0-9-]+)`?\s*\|[^|]*?(#[0-9a-fA-F]{3,6})\b", text, re.MULTILINE
    ):
        palette.setdefault(token, value)
    return palette


def parse_requirements(text: str) -> list[tuple[str, str, str]]:
    block = re.search(r"```contrast\n(.*?)```", text, re.DOTALL)
    if not block:
        return []
    reqs = []
    for line in block.group(1).splitlines():
        line = line.split("#")[0].strip()
        m = re.match(r"^(\S+)\s+on\s+(\S+)\s+(\S+)$", line)
        if m:
            reqs.append(m.groups())
    return reqs


def check_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    palette = parse_palette(text)
    reqs = parse_requirements(text)

    if not reqs:
        print(f"{path.name}: no ```contrast block — nothing to verify", file=sys.stderr)
        return False

    print(f"\n{path.name}")
    ok = True
    for fg, bg, level in reqs:
        need = LEVELS.get(level)
        if need is None:
            print(f"  ?? {fg} on {bg}: unknown level {level!r}")
            ok = False
            continue
        if fg not in palette or bg not in palette:
            missing = [t for t in (fg, bg) if t not in palette]
            print(f"  ?? {fg} on {bg}: token(s) not in palette table: {', '.join(missing)}")
            ok = False
            continue
        ratio = contrast(palette[fg], palette[bg])
        passed = ratio >= need
        ok &= passed
        print(f"  {'PASS' if passed else 'FAIL'} {fg:<11} on {bg:<9} "
              f"{ratio:5.2f}:1  (needs {need}:1 for {level})")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path, help="theme markdown files")
    ap.add_argument("--pair", nargs=2, metavar=("FG", "BG"),
                    help="check two hex colors directly")
    args = ap.parse_args()

    if args.pair:
        ratio = contrast(*args.pair)
        verdict = ("AAA" if ratio >= 7 else "AA" if ratio >= 4.5
                   else "AA-large/UI only" if ratio >= 3 else "FAIL")
        print(f"{args.pair[0]} on {args.pair[1]}: {ratio:.2f}:1 — {verdict}")
        return 0 if ratio >= 4.5 else 1

    if not args.files:
        ap.error("provide theme files or --pair")

    return 0 if all([check_file(f) for f in args.files]) else 1


if __name__ == "__main__":
    sys.exit(main())
