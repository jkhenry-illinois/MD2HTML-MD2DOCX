# How to Use md2html.py

## What does this script do?

It takes a Markdown file (`.md`) and creates an HTML version of it (`.html`) that you can open in a web browser. That's it.

**Your original `.md` file is never touched, never deleted, never changed.** The script only ever *reads* your Markdown file and *creates* a brand new HTML file alongside it. You can always run it again safely.

---

## Do I type the command and then get asked questions?

No. You type the whole thing on one line and press Enter. The script runs and finishes — no back-and-forth prompts.

---

## The basic building blocks of every command

Every command you type will look like this:

```
python3 md2html.py  [the file you want to convert]  [any options]
```

You always have to name the file you want to convert. Everything else is optional.

---

## Example 1 — Just see if it works (safest first try)

This prints the HTML to your screen instead of saving it anywhere. Nothing gets saved, nothing gets deleted. Good for testing.

```bash
python3 md2html.py notes.md
```

You'll see a wall of HTML code scroll past. If you see HTML and no error message, it's working.

---

## Example 2 — Save the HTML to a file

Add `-o` followed by the name you want for the new file. The script creates that file (or overwrites it if it already exists — your `.md` is still untouched).

```bash
python3 md2html.py notes.md -o notes.html
```

After this runs, you'll have:
- `notes.md` — your original, unchanged
- `notes.html` — the new HTML file you can open in a browser

---

## Example 3 — Make a nicer-looking page

Without anything extra, the HTML has no styling — it looks plain and bare in a browser. Add `--standalone` (or just `-s`) to get a page that looks readable, with proper fonts and spacing.

```bash
python3 md2html.py notes.md -o notes.html --standalone
```

This is probably the command you'll use most often.

---

## Example 4 — Converting a file that's not in your current folder

If your file is in a different folder, just give the full path:

```bash
python3 md2html.py /Users/su-jkhenry/Documents/project/notes.md -o /Users/su-jkhenry/Documents/project/notes.html --standalone
```

---

## "How does it know where to save the file?"

It doesn't guess — you tell it with `-o`. Whatever you write after `-o` is exactly where the file gets saved and what it gets named. If you don't use `-o` at all, nothing is saved (the HTML just prints to the screen).

---

## What about links between my Markdown files?

If your Markdown files link to *each other* (like `[See also](other-topic.md)`), those links will break in HTML because there's no `other-topic.md` anymore — only `other-topic.html`.

The script fixes this automatically. When you run it, it rewrites any link that points to a `.md` file so it points to the matching `.html` file instead.

**The catch:** it needs to know where all your Markdown files live so it can find the right matches. You tell it with `--dir`:

```bash
python3 md2html.py notes.md -o notes.html --standalone --dir /Users/su-jkhenry/Documents/project
```

The `--dir` path should be the folder that contains all your interlinked `.md` files. The script scans that folder and uses it to fix up the links.

If all your files are in the same folder you're already working in, you can leave `--dir` out — it defaults to the current folder.

---

## Converting a whole folder of files

The script converts one file at a time, so for a folder of ten files you'd run it ten times. A simple way to do all of them at once in Terminal:

```bash
for f in /Users/su-jkhenry/Documents/project/*.md; do
    python3 ~/md2html.py "$f" -o "${f%.md}.html" --standalone --dir /Users/su-jkhenry/Documents/project
done
```

This loops through every `.md` file in the folder and creates a matching `.html` file next to it. After it runs:
- Every `.md` file is still there, unchanged
- Every `.md` file now has a `.html` twin sitting next to it
- All the links between files point to the correct `.html` versions

---

## Quick reference card

| What you want to do | Command |
|---|---|
| Test that it works | `python3 md2html.py myfile.md` |
| Save as HTML | `python3 md2html.py myfile.md -o myfile.html` |
| Save as a nice-looking page | `python3 md2html.py myfile.md -o myfile.html --standalone` |
| Fix links between files too | add `--dir /path/to/your/md/folder` |

---

## Will my original files be deleted?

No. The script has no ability to delete files. It can only read `.md` files and write `.html` files. The worst that could happen is it overwrites an `.html` file you already made — and even then you can just run the script again to recreate it.
