# Markdown to Word Converter — User Guide

**Tool**: `md2docx.py` + `convert-md-docx.sh`
**Location**: `~/md2docx.py`, `~/convert-md-docx.sh`
**Last updated**: 2026-08-06

---

## 1. Overview

The Markdown-to-Word converter turns `.md` files into Microsoft Word `.docx` documents. It is made of two pieces that work together:

- **`md2docx.py`** — the converter. Uses `pandoc` for conversion and a UIUC-branded reference document for styling.
- **`convert-md-docx.sh`** — an interactive wrapper with a native macOS file/folder picker.

The Word output uses a University of Illinois–style theme (navy `#13294B` and orange `#E84A27`).

## 2. Requirements

- macOS (the wrapper uses `osascript` for the file picker).
- Python 3.
- `pandoc` on your PATH (install with Homebrew if missing).
- The `python-docx` Python package (used once to build the reference doc).

Check what you have:

```
python3 --version
pandoc --version | head -1
python3 -c "import docx; print(docx.__version__)"
```

Install pandoc if needed:

```
brew install pandoc
```

## 3. Files

| File | Purpose |
|------|---------|
| `~/md2docx.py` | The converter (run directly or via the wrapper) |
| `~/convert-md-docx.sh` | Interactive menu + file picker |
| `~/.md2docx/reference.docx` | Cached UIUC-styled reference doc (auto-generated) |

## 4. Quick Start

Run the wrapper and pick a file:

```
~/convert-md-docx.sh
```

Choose `1`, select a `.md` file, and a `.docx` file appears beside it. The first run builds the styled reference doc automatically.

## 5. The Interactive Wrapper (`convert-md-docx.sh`)

Launch it:

```
~/convert-md-docx.sh
```

You get a two-option menu.

### 5.1 Single file (option 1)

- A macOS file chooser opens (filtered to `.md`).
- Pick one `.md` file.
- If a `.docx` of the same name already exists, you are asked to confirm overwriting it.
- Output: `<same-name>.docx` in the same folder.
- You are offered to open the document immediately.

### 5.2 Whole directory (option 2)

- A macOS folder chooser opens.
- Every `.md` file in that folder is converted.
- Output goes into a new timestamped folder next to the source: `docx_YYYY-MM-DD_HH-MM-SS/`.
- A success/failure count is shown; you are offered to open the output folder.

## 6. The Converter Script (`md2docx.py`)

Run directly for full control.

### Usage

```
python3 ~/md2docx.py INPUT [-o OUTPUT] [--toc] [--no-reference] [--reference-doc FILE] [--rebuild-ref]
```

### Options

| Flag | Meaning |
|------|---------|
| `INPUT` | Input Markdown file (required) |
| `-o, --output` | Output `.docx` file. Omit to use `<input>.docx`. |
| `--toc` | Insert a table of contents (depth 3) |
| `--no-reference` | Use pandoc's default styling instead of the UIUC theme |
| `--reference-doc FILE` | Use a custom reference `.docx` for styling |
| `--rebuild-ref` | Rebuild the cached UIUC reference doc, then convert |

### Examples

Convert one file (themed, default output name):

```
python3 ~/md2docx.py notes.md
```

Convert with a table of contents and a named output:

```
python3 ~/md2docx.py report.md -o report.docx --toc
```

Rebuild the branded reference doc (e.g., after editing its styling):

```
python3 ~/md2docx.py notes.md --rebuild-ref
```

Use pandoc's plain default styling:

```
python3 ~/md2docx.py notes.md -o notes.docx --no-reference
```

## 7. Markdown Features Supported

Conversion is handled by `pandoc`, so all CommonMark plus many extensions work, including:

- Headings `#`–`######`
- **Bold**, *italic*, `inline code`
- Links and images
- Ordered and unordered lists (including nested)
- Tables (pipe syntax)
- Blockquotes
- Fenced code blocks (` ``` `)
- Horizontal rules (`---`)
- Footnotes, definition lists, and other pandoc extensions where used

Note: unlike the HTML tool, wiki-links `[[page-name]]` are **not** rewritten — they pass through as literal text. Convert wiki-links to standard Markdown links first if you need them to resolve.

## 8. Output Location

- Single file: beside the source, same base name, `.docx` extension.
- Directory mode: a new `docx_<timestamp>/` folder beside the source folder.

## 9. Styling

Styling comes from a reference document (`~/.md2docx/reference.docx`), built once from pandoc's default and restyled with `python-docx`:

- Title and headings in navy `#13294B` (H1–H2) or navy-mid `#1F3564` (H3–H6), Source Sans Pro, bold.
- Body text 11pt, dark gray.
- Code in Menlo with a light gray fill.
- Blockquotes with a light navy tint fill.
- Hyperlinks in orange `#E84A27`, underlined.

To customize, edit the `restyle_reference()` function in `~/md2docx.py` and run with `--rebuild-ref`.

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| "pandoc not found" | `brew install pandoc` |
| `ModuleNotFoundError: docx` | `python3 -m pip install python-docx` |
| Styling looks like pandoc default | The reference doc is missing; rerun with `--rebuild-ref` |
| `[[wiki-links]]` appear as text | Expected — rewrite them as `[text](page.md)` first |
| First run is slow | Normal — it generates the reference doc once; later runs are fast |

## 11. Maintenance

- Rebuild the reference doc any time: `python3 ~/md2docx.py any.md --rebuild-ref`
- Remove all cached styling: `rm -rf ~/.md2docx` (rebuilt automatically on next run).

## 12. Related

- [[md2html-guide]] — companion tool that converts Markdown to HTML pages.
