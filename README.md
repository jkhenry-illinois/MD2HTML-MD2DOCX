# MD2HTML-MD2DOCX

Personal Markdown converter tools: plain and UIUC-themed HTML/DOCX output,
wiki-link resolution, and interactive file-picker wrappers.

## Tools

| Command | Converts | Theme | Notes |
|---|---|---|---|
| `md2html.py` | .md → .html | none (flags) | stdlib-only Python; core engine |
| `md2docx.py` | .md → .docx | none (flags) | pandoc + python-docx; core engine |
| `md2html-uiuc` | .md → .html | UIUC (navy/orange) | wiki-links + nav bar pre-configured |
| `md2docx-uiuc` | .md → .docx | UIUC (navy/orange) | TOC pre-configured |
| `convert-md.sh` | .md → .html | none (flags) | interactive macOS file/folder picker |
| `convert-md-docx.sh` | .md → .docx | none (flags) | interactive macOS file/folder picker |

Full usage/options: `md2html-guide.md`, `md2docx-guide.md`, `md2html-usage.md`,
or `man md2html-uiuc` / `man md2docx-uiuc` once installed.

## Install

These scripts assume `$HOME/md2html.py` and `$HOME/md2docx.py` exist (the
`-uiuc` wrappers and `convert-md*.sh` hardcode that path rather than
resolving relative to their own location, so they keep working no matter
where the wrapper itself is invoked from). Symlink everything from this repo
into place:

```bash
REPO=~/Documents/github-projects/MD2HTML-MD2DOCX

# core scripts + wrappers, discoverable at ~/
for f in md2html.py md2docx.py convert-md.sh convert-md-docx.sh md2html-uiuc md2docx-uiuc; do
  ln -sf "$REPO/$f" ~/"$f"
done

# uiuc commands + man pages on PATH
ln -sf "$REPO/md2html-uiuc" /opt/homebrew/bin/md2html-uiuc
ln -sf "$REPO/md2docx-uiuc" /opt/homebrew/bin/md2docx-uiuc
ln -sf "$REPO/md2html-uiuc.1" /opt/homebrew/share/man/man1/md2html-uiuc.1
ln -sf "$REPO/md2docx-uiuc.1" /opt/homebrew/share/man/man1/md2docx-uiuc.1
```

**Dependencies**: Python 3 (stdlib only for `md2html.py`); `pandoc`
(`brew install pandoc`) and `python-docx`
(`python3 -m pip install python-docx`) for `md2docx.py`. macOS `osascript`
for the interactive `convert-md*.sh` pickers.

**Wiki-link resolution** (`md2html-uiuc`, and `md2html.py -s`) expects a wiki
directory at `~/wiki` with an `index.md`.

**DOCX reference styling** is auto-generated on first run to
`~/.md2docx/reference.docx` (not tracked in this repo — rebuild any time
with `--rebuild-ref`, or delete `~/.md2docx` to reset).

See `~/TOOLS.md` for the fuller personal tool registry entry (status,
known issues, ideas) covering this project.
