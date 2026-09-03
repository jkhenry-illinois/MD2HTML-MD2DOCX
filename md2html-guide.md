# Markdown to HTML Converter — User Guide

**Tool**: `md2html.py` + `convert-md.sh`
**Location**: `~/md2html.py`, `~/convert-md.sh`
**Last updated**: 2026-08-06

---

## 1. Overview

The Markdown-to-HTML converter turns `.md` files into styled, standalone HTML pages. It is made of two pieces that work together:

- **`md2html.py`** — the converter. Pure Python, no external dependencies. Parses Markdown and emits HTML.
- **`convert-md.sh`** — an interactive wrapper with a native macOS file/folder picker.

The HTML output uses a University of Illinois–style theme (navy `#13294B` and orange `#E84A27`).

## 2. Requirements

- macOS (the wrapper uses `osascript` for the file picker).
- Python 3 (already on your Mac).
- No pip packages required — `md2html.py` uses only the standard library.

Check Python:

```
python3 --version
```

## 3. Files

| File | Purpose |
|------|---------|
| `~/md2html.py` | The converter (run directly or via the wrapper) |
| `~/convert-md.sh` | Interactive menu + file picker |

## 4. Quick Start

Run the wrapper and pick a file:

```
~/convert-md.sh
```

Choose `1`, select a `.md` file, and an `.html` file appears beside it.

## 5. The Interactive Wrapper (`convert-md.sh`)

Launch it:

```
~/convert-md.sh
```

You get a two-option menu.

### 5.1 Single file (option 1)

- A macOS file chooser opens.
- Pick one `.md` file.
- If an `.html` of the same name already exists, you are asked to confirm overwriting it.
- Output: `<same-name>.html` in the same folder.

### 5.2 Whole directory (option 2)

- A macOS folder chooser opens.
- Every `.md` file in that folder is converted.
- Output goes into a new timestamped folder next to the source: `converted_YYYY-MM-DD_HH-MM-SS/`.
- Each page includes a hamburger navigation menu built from the `##` headings in `index.md` (if present).

## 6. The Converter Script (`md2html.py`)

Run directly for full control.

### Usage

```
python3 ~/md2html.py INPUT [-o OUTPUT] [-s] [-d DIR] [-n]
```

### Options

| Flag | Meaning |
|------|---------|
| `INPUT` | Input Markdown file (required) |
| `-o, --output` | Output HTML file. Omit to print to stdout. |
| `-s, --standalone` | Wrap the HTML in a full document with the UIUC theme |
| `-d, --dir DIR` | Folder to scan for wiki-link matching (default `.`) |
| `-n, --nav` | Add a hamburger nav built from `index.md` `##` headings |

### Examples

Convert one file to a themed page:

```
python3 ~/md2html.py notes.md -o notes.html --standalone
```

Print HTML to the terminal (no styling wrapper):

```
python3 ~/md2html.py notes.md
```

Convert with wiki-link resolution against a folder and a nav bar:

```
python3 ~/md2html.py notes.md -o notes.html -s -d ~/wiki -n
```

## 7. Markdown Features Supported

- Headings `#`–`######` (with anchor IDs)
- **Bold**, *italic*, ***both***, `inline code`
- Links and images
- Ordered and unordered lists (including nested)
- Tables (with header row + separator)
- Blockquotes
- Fenced code blocks (` ``` `)
- Horizontal rules (`---`)
- Wiki-links `[[page-name]]` — fuzzy-matched to `.md` files in `--dir` and rewritten to `.html`
- Markdown links to `.md` files — rewritten to `.html`

## 8. Output Location

- Single file: beside the source, same base name, `.html` extension.
- Directory mode: a new `converted_<timestamp>/` folder beside the source folder.

## 9. Styling

Standalone pages embed a CSS theme:

- Navy `#13294B` headings, orange `#E84A27` accents and horizontal rules.
- Orange top bar across the page.
- Navy blockquotes with an orange left border.
- Monospace code blocks with an orange left border.
- Navy table headers, zebra-striped rows.

Because the CSS is embedded, each `.html` is fully self-contained — no external assets needed.

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| "command not found: python3" | Install Python 3, or invoke it explicitly as `python3` |
| File chooser won't open | Run from Terminal locally; not over a headless SSH session |
| Wiki-links show as plain text | Pass `-d` pointing at the folder containing the linked `.md` files |
| Output is unstyled | Add `--standalone` (`-s`) |

## 11. Maintenance

No cache or generated files to manage. To change behavior or styling, edit `~/md2html.py` directly — changes take effect on the next run.

## 12. Related

- [[md2docx-guide]] — companion tool that converts Markdown to Word documents.
