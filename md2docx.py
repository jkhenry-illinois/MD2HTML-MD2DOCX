#!/usr/bin/env python3
"""Convert Markdown files to Microsoft Word (.docx) via pandoc.

Pandoc does the conversion; a UIUC-branded reference document (generated
with python-docx) supplies consistent styling. The reference doc is built
automatically on first run and cached in ~/.md2docx/reference.docx.

Requires: pandoc on PATH (or /opt/homebrew/bin/pandoc), python-docx.
"""

import argparse
import os
import shutil
import subprocess
import sys

PANDOC_CANDIDATES = ["pandoc", "/opt/homebrew/bin/pandoc", "/usr/local/bin/pandoc"]

REF_DIR = os.path.expanduser("~/.md2docx")
REF_DOC = os.path.join(REF_DIR, "reference.docx")

# UIUC palette (matches md2html.py)
NAVY = "13294B"
NAVY_MID = "1F3564"
ORANGE = "E84A27"
CODE_FILL = "F2F2F2"
QUOTE_FILL = "E8EDF5"


def find_pandoc():
    for cand in PANDOC_CANDIDATES:
        if os.path.sep in cand:
            if os.path.isfile(cand):
                return cand
        else:
            found = shutil.which(cand)
            if found:
                return found
    return None


def _shade(style_el, fill):
    """Add a background shading fill to a style's <w:pPr>."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    pPr = style_el.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        rPr = style_el.find(qn("w:rPr"))
        if rPr is not None:
            style_el.insert(list(style_el).index(rPr), pPr)
        else:
            style_el.append(pPr)
    for old in pPr.findall(qn("w:shd")):
        pPr.remove(old)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def restyle_reference(ref_path):
    """Customize the default pandoc reference doc with UIUC branding."""
    from docx import Document
    from docx.shared import Pt, RGBColor

    doc = Document(ref_path)
    styles = doc.styles

    def hex_rgb(h):
        return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def style_font(name, color=None, size=None, bold=None, font_name=None):
        try:
            s = styles[name]
        except KeyError:
            return
        if color is not None:
            s.font.color.rgb = hex_rgb(color)
        if size is not None:
            s.font.size = Pt(size)
        if bold is not None:
            s.font.bold = bold
        if font_name is not None:
            s.font.name = font_name

    body_font = "Source Sans Pro"

    # Body text
    style_font("Normal", color="1A1A1A", size=11, font_name=body_font)
    style_font("Body Text", color="1A1A1A", size=11, font_name=body_font)
    style_font("First Paragraph", color="1A1A1A", size=11, font_name=body_font)

    # Headings (navy / navy-mid, bold)
    style_font("Title", color=NAVY, size=26, bold=True, font_name=body_font)
    style_font("Heading 1", color=NAVY, size=18, bold=True, font_name=body_font)
    style_font("Heading 2", color=NAVY, size=15, bold=True, font_name=body_font)
    style_font("Heading 3", color=NAVY_MID, size=13, bold=True, font_name=body_font)
    style_font("Heading 4", color=NAVY_MID, size=12, bold=True, font_name=body_font)
    style_font("Heading 5", color=NAVY_MID, size=11, bold=True, font_name=body_font)
    style_font("Heading 6", color=NAVY_MID, size=11, bold=True, font_name=body_font)

    # Inline + block code: monospace, light gray fill
    for code_style in ("Source Code", "Verbatim Char"):
        try:
            s = styles[code_style]
            s.font.name = "Menlo"
            rpr = s.element.find(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr"
            )
            # ensure eastAsia/cs also pick up the font
        except KeyError:
            pass
    try:
        _shade(styles["Source Code"].element, CODE_FILL)
    except Exception:
        pass

    # Blockquote: light navy tint fill
    try:
        _shade(styles["Block Text"].element, QUOTE_FILL)
    except Exception:
        pass

    # Hyperlinks: orange
    try:
        s = styles["Hyperlink"]
        s.font.color.rgb = hex_rgb(ORANGE)
        s.font.underline = True
    except KeyError:
        pass

    doc.save(ref_path)


def ensure_reference_doc(pandoc_path, force=False):
    """Build the cached reference doc if missing (or if force=True)."""
    if os.path.isfile(REF_DOC) and not force:
        return REF_DOC
    os.makedirs(REF_DIR, exist_ok=True)
    with open(REF_DOC, "wb") as f:
        subprocess.run(
            [pandoc_path, "--print-default-data-file", "reference.docx"],
            stdout=f,
            check=True,
        )
    try:
        restyle_reference(REF_DOC)
    except Exception as e:
        # Heading restyle failed; the default reference doc still works.
        print(f"  (warning: could not fully restyle reference doc: {e})", file=sys.stderr)
    return REF_DOC


def convert_file(input_path, output_path, pandoc_path, reference_doc=None, toc=False):
    cmd = [pandoc_path, input_path, "--from", "markdown", "-o", output_path]
    if reference_doc:
        cmd += ["--reference-doc", reference_doc]
    if toc:
        cmd += ["--toc", "--toc-depth=3"]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to Microsoft Word (.docx)"
    )
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument(
        "-o", "--output", help="Output .docx file (default: same name as input, .docx)"
    )
    parser.add_argument(
        "--toc", action="store_true", help="Add a table of contents (depth 3)"
    )
    parser.add_argument(
        "--reference-doc", help="Use a custom reference .docx for styling"
    )
    parser.add_argument(
        "--no-reference",
        action="store_true",
        help="Use pandoc's default styling (skip UIUC reference doc)",
    )
    parser.add_argument(
        "--rebuild-ref",
        action="store_true",
        help="Rebuild the cached UIUC reference doc, then convert",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"Error: input file not found: {args.input}")

    pandoc_path = find_pandoc()
    if not pandoc_path:
        sys.exit(
            "Error: pandoc not found. Install it with:  brew install pandoc\n"
            "       (or ensure it is on your PATH)"
        )

    if args.no_reference:
        reference_doc = None
    elif args.reference_doc:
        reference_doc = args.reference_doc
        if not os.path.isfile(reference_doc):
            sys.exit(f"Error: reference doc not found: {reference_doc}")
    else:
        reference_doc = ensure_reference_doc(pandoc_path, force=args.rebuild_ref)

    if args.output:
        output_path = args.output
    else:
        output_path = os.path.splitext(args.input)[0] + ".docx"

    convert_file(args.input, output_path, pandoc_path, reference_doc, args.toc)
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
