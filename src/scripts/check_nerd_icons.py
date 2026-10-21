"""Check built fonts for Starship language icons from optional Nerd Font sets."""

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont


REQUIRED_ICONS = {
    "Java": 0xE256,
    "Python": 0xE235,
    "Rust": 0xF1617,
    "R": 0xF07D4,
    "Odin": 0xF07E2,
    "Mojo": 0xF0238,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    paths = sorted(args.directory.glob("*.otf"))
    if not paths:
        parser.error(f"No OTF fonts found in {args.directory}")

    for path in paths:
        with TTFont(path) as font:
            cmap = font.getBestCmap()
            missing = [
                f"{name} (U+{codepoint:04X})"
                for name, codepoint in REQUIRED_ICONS.items()
                if codepoint not in cmap
            ]
            if missing:
                parser.exit(1, f"{path.name}: missing {', '.join(missing)}\n")

    print(f"Verified Starship language icons in {len(paths)} fonts.")


if __name__ == "__main__":
    main()
