#!/usr/bin/env python3
"""Simplify the names font-patcher gives to partially patched fonts.

When patching without --complete, font-patcher appends every selected glyph
set to the names (e.g. "Nerd Font Mono Plus Font Awesome Plus Octicons" and
"NordwandMonoNFMAOPSCPL"). This rewrites the names to plain
"NordwandMono Nerd Font" (dropping the redundant "Mono" variant suffix) and
renames the files to match.
"""

import argparse
import re
from pathlib import Path

from fontTools.ttLib import TTFont


PLUS_SUFFIX = re.compile(r" Plus .*$")
PS_SUFFIX = re.compile(r"NFM[A-Z]*(?=-|$)")


def clean_name(value):
    return PLUS_SUFFIX.sub("", value).replace(" Nerd Font Mono", " Nerd Font")


def clean_ps_name(value):
    return PS_SUFFIX.sub("NF", value)


def clean_font(path):
    font = TTFont(path)
    name_table = font["name"]
    for record in name_table.names:
        value = record.toUnicode()
        if record.nameID == 6:
            cleaned = clean_ps_name(value)
        else:
            cleaned = clean_name(value)
        if cleaned != value:
            record.string = cleaned

    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [clean_ps_name(name) for name in cff.fontNames]
        top = cff.topDictIndex[0]
        top.FamilyName = name_table.getDebugName(16) or name_table.getDebugName(1)
        top.FullName = name_table.getDebugName(4)

    ps_name = name_table.getDebugName(6)
    family, _, style = ps_name.partition("-")
    out_path = path.with_name(
        f"{family.replace('NF', 'NerdFont')}-{style or 'Regular'}{path.suffix}"
    )
    font.save(out_path)
    if out_path != path:
        path.unlink()
    print(f"{path.name} -> {out_path.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    for path in sorted(args.directory.glob("*.otf")):
        clean_font(path)


if __name__ == "__main__":
    main()
