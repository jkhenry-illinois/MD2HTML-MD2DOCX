#!/usr/bin/env python3
"""Convert Markdown files to HTML — no external dependencies."""

import argparse
import os
import re
import sys
from difflib import SequenceMatcher


MD_LINK_RE = re.compile(r'<a href="([^"]+\.md)(#[^"]*)?"')
MD_TEXT_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+\.md)(#[^)]*)?\)')
WIKI_LINK_RE = re.compile(r'\[\[([^\]]+)\]\]')


def make_anchor(text: str) -> str:
    anchor = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'\s+', '-', anchor.strip())


def fix_links(html: str) -> str:
    def replace_link(m):
        md_path = m.group(1)
        anchor = m.group(2) or ""
        html_path = md_path[:-3] + ".html"
        return f'<a href="{html_path}{anchor}"'
    return MD_LINK_RE.sub(replace_link, html)


def build_file_map(dir_path: str) -> dict:
    file_map = {}
    for f in os.listdir(dir_path):
        if f.endswith(".md"):
            name = f[:-3]
            base = name.lower().replace("-", "")
            file_map[base] = name
    return file_map


def best_match(wiki_name: str, file_map: dict):
    wiki_lower = wiki_name.lower().replace("-", "").replace(" ", "")
    if wiki_lower in file_map:
        return file_map[wiki_lower]
    best_score = 0
    best_result = None
    for base_name, file_name in file_map.items():
        score = SequenceMatcher(None, wiki_lower, base_name).ratio()
        if score > best_score and score >= 0.55:
            best_score = score
            best_result = file_name
    return best_result


def convert_md_links(md_content: str, file_map: dict) -> str:
    def replace_md_link(m):
        text = m.group(1)
        md_path = m.group(2)
        anchor = m.group(3) or ""
        html_path = md_path[:-3] + ".html"
        return f'[{text}]({html_path}{anchor})'

    md_content = MD_TEXT_LINK_RE.sub(replace_md_link, md_content)

    def replace_wiki_link(m):
        wiki_name = m.group(1)
        matched_name = best_match(wiki_name, file_map)
        if matched_name:
            return f'[{wiki_name}]({matched_name}.html)'
        return wiki_name

    return WIKI_LINK_RE.sub(replace_wiki_link, md_content)


def extract_index_nav(dir_path: str) -> list:
    """Return list of (label, anchor) for each ## heading in index.md."""
    index_path = os.path.join(dir_path, 'index.md')
    if not os.path.isfile(index_path):
        # Try case-insensitive match
        for f in os.listdir(dir_path):
            if f.lower() == 'index.md':
                index_path = os.path.join(dir_path, f)
                break
        else:
            return []

    items = []
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.match(r'^##\s+(.+)$', line.strip())
                if m:
                    label = m.group(1).strip()
                    items.append((label, make_anchor(label)))
    except OSError:
        pass
    return items


def build_nav_html(dir_path: str, is_index: bool) -> str:
    """Build a hamburger nav from ## headings in index.md."""
    sections = extract_index_nav(dir_path)

    home_class = ' class="active"' if is_index else ''
    links = [f'        <a href="index.html"{home_class}>Home</a>']

    for label, anchor in sections:
        links.append(f'        <a href="index.html#{anchor}">{label}</a>')

    menu_items = '\n'.join(links)
    return f'''<nav class="site-nav">
        <button class="nav-toggle" aria-label="Menu" aria-expanded="false">&#9776;</button>
        <div class="nav-menu">
{menu_items}
        </div>
    </nav>'''


def process_inline(s: str) -> str:
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', s)
    s = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'__(.+?)__', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    s = re.sub(r'_(.+?)_', r'<em>\1</em>', s)
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s


def markdown_to_html(text: str) -> str:
    lines = text.split('\n')
    out = []
    in_code = False
    in_table = False
    in_list = False
    list_type = None
    in_blockquote = False
    i = 0

    def close_open(skip_code=False):
        nonlocal in_list, list_type, in_table, in_blockquote
        if in_list:
            out.append(f'</{list_type}>')
            in_list = False
            list_type = None
        if in_table:
            out.append('</tbody></table>')
            in_table = False
        if in_blockquote:
            out.append('</blockquote>')
            in_blockquote = False

    while i < len(lines):
        line = lines[i]

        # Fenced code block toggle
        if line.startswith('```'):
            if in_code:
                out.append('</code></pre>')
                in_code = False
            else:
                close_open()
                lang = line[3:].strip()
                attr = f' class="language-{lang}"' if lang else ''
                out.append(f'<pre><code{attr}>')
                in_code = True
            i += 1
            continue

        if in_code:
            out.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            i += 1
            continue

        # Blank line
        if line.strip() == '':
            close_open()
            i += 1
            continue

        # Heading
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            close_open()
            level = len(m.group(1))
            content = process_inline(m.group(2))
            anchor = make_anchor(m.group(2))
            out.append(f'<h{level} id="{anchor}">{content}</h{level}>')
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}\s*$', line):
            close_open()
            out.append('<hr>')
            i += 1
            continue

        # Table header row (next line is separator)
        if not in_table and '|' in line:
            next_line = lines[i + 1] if i + 1 < len(lines) else ''
            if re.match(r'^[\s|:\-]+$', next_line) and '|' in next_line and '-' in next_line:
                close_open()
                out.append('<table>')
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                out.append('<thead><tr>' + ''.join(f'<th>{process_inline(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                in_table = True
                i += 2
                continue

        # Table body row
        if in_table:
            if '|' in line:
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                out.append('<tr>' + ''.join(f'<td>{process_inline(c)}</td>' for c in cells) + '</tr>')
                i += 1
                continue
            else:
                out.append('</tbody></table>')
                in_table = False

        # Blockquote
        m = re.match(r'^>\s?(.*)', line)
        if m:
            if not in_blockquote:
                close_open()
                out.append('<blockquote>')
                in_blockquote = True
            out.append(f'<p>{process_inline(m.group(1))}</p>')
            i += 1
            continue
        if in_blockquote:
            out.append('</blockquote>')
            in_blockquote = False

        # Unordered list
        m = re.match(r'^[-*+]\s+(.+)$', line)
        if m:
            if list_type != 'ul':
                if in_list:
                    out.append(f'</{list_type}>')
                out.append('<ul>')
                in_list = True
                list_type = 'ul'
            out.append(f'<li>{process_inline(m.group(1))}</li>')
            i += 1
            continue

        # Ordered list
        m = re.match(r'^\d+\.\s+(.+)$', line)
        if m:
            if list_type != 'ol':
                if in_list:
                    out.append(f'</{list_type}>')
                out.append('<ol>')
                in_list = True
                list_type = 'ol'
            out.append(f'<li>{process_inline(m.group(1))}</li>')
            i += 1
            continue

        # Paragraph
        close_open()
        out.append(f'<p>{process_inline(line)}</p>')
        i += 1

    # Close anything still open
    if in_code:
        out.append('</code></pre>')
    if in_list:
        out.append(f'</{list_type}>')
    if in_table:
        out.append('</tbody></table>')
    if in_blockquote:
        out.append('</blockquote>')

    return '\n'.join(out)


def convert_file(input_path: str, output_path, standalone: bool = False,
                 dir_path: str = ".", nav: bool = False) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    file_map = build_file_map(dir_path)
    md_content = convert_md_links(md_content, file_map)
    html = markdown_to_html(md_content)
    html = fix_links(html)

    # Extract page title from first H1 for <title> tag
    title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    page_title = title_match.group(1) if title_match else os.path.splitext(os.path.basename(input_path))[0]

    if standalone:
        is_index = os.path.splitext(os.path.basename(input_path))[0].lower() == 'index'
        nav_html = build_nav_html(dir_path, is_index) if nav else ''

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
        :root {{
            --orange: #e84a27;
            --navy:   #13294b;
            --navy-mid: #1f3564;
            --gray-light: #f5f5f5;
            --gray-border: #d0d0d0;
            --text: #1a1a1a;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: "Source Sans Pro", "Segoe UI", system-ui, sans-serif;
            font-size: 16px;
            line-height: 1.7;
            color: var(--text);
            background: #fff;
        }}

        body::before {{
            content: "";
            display: block;
            height: 6px;
            background: var(--orange);
        }}

        /* Hamburger nav */
        .site-nav {{
            position: fixed;
            top: 12px;
            right: 1.25rem;
            z-index: 200;
        }}
        .nav-toggle {{
            background: var(--navy);
            color: #fff;
            border: none;
            padding: 0.45rem 0.7rem;
            font-size: 1.3rem;
            line-height: 1;
            border-radius: 4px;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        }}
        .nav-toggle:hover {{ background: var(--navy-mid); }}
        .nav-menu {{
            display: none;
            position: absolute;
            right: 0;
            top: calc(100% + 4px);
            background: var(--navy);
            min-width: 200px;
            border-radius: 4px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
            overflow: hidden;
            border-top: 3px solid var(--orange);
        }}
        .site-nav.open .nav-menu {{ display: block; }}
        .nav-menu a {{
            display: block;
            color: rgba(255,255,255,0.85);
            text-decoration: none;
            padding: 0.65rem 1.1rem;
            font-size: 0.9rem;
            font-weight: 600;
            border-left: 3px solid transparent;
            transition: background 0.12s, border-color 0.12s, color 0.12s;
        }}
        .nav-menu a:hover {{
            background: var(--navy-mid);
            color: #fff;
            border-left-color: var(--orange);
        }}
        .nav-menu a.active {{
            color: #fff;
            border-left-color: var(--orange);
        }}

        .content {{
            max-width: 860px;
            margin: 0 auto;
            padding: 2.5rem 2rem 4rem;
        }}

        h1 {{
            font-size: 2.1rem;
            font-weight: 700;
            color: var(--navy);
            margin: 0 0 1.5rem;
            line-height: 1.2;
        }}
        h2 {{
            font-size: 1.45rem;
            font-weight: 700;
            color: var(--navy);
            margin: 2rem 0 0.75rem;
            padding-bottom: 0.4rem;
            border-bottom: 3px solid var(--orange);
            display: inline-block;
        }}
        h3 {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--navy-mid);
            margin: 1.75rem 0 0.5rem;
        }}
        h4, h5, h6 {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--navy-mid);
            margin: 1.5rem 0 0.4rem;
        }}

        p {{ margin: 0 0 1rem; }}

        a {{
            color: var(--navy-mid);
            text-decoration: underline;
        }}
        a:hover {{ color: var(--orange); }}

        blockquote {{
            background: var(--navy-mid);
            color: #fff;
            border-left: 5px solid var(--orange);
            border-radius: 0 6px 6px 0;
            padding: 1rem 1.25rem;
            margin: 1.5rem 0;
        }}
        blockquote p {{ margin: 0 0 0.4rem; }}
        blockquote p:last-child {{ margin: 0; }}
        blockquote a {{ color: var(--orange); }}

        code {{
            background: var(--gray-light);
            color: var(--navy);
            padding: 0.15em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
            font-family: "Menlo", "Consolas", monospace;
        }}
        pre {{
            background: var(--gray-light);
            border-left: 4px solid var(--orange);
            border-radius: 0 4px 4px 0;
            padding: 1rem 1.25rem;
            overflow-x: auto;
            margin: 1.25rem 0;
        }}
        pre code {{
            background: none;
            padding: 0;
            font-size: 0.88em;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.5rem 0;
            font-size: 0.95rem;
        }}
        th {{
            background: var(--navy);
            color: #fff;
            padding: 0.6rem 0.85rem;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            border: 1px solid var(--gray-border);
            padding: 0.55rem 0.85rem;
        }}
        tr:nth-child(even) td {{ background: var(--gray-light); }}

        ul, ol {{ margin: 0.5rem 0 1rem 1.5rem; }}
        li {{ margin-bottom: 0.35rem; }}
        ul li::marker {{ color: var(--orange); }}
        ol li::marker {{ color: var(--navy); font-weight: 600; }}

        hr {{
            border: none;
            border-top: 2px solid var(--orange);
            margin: 2rem 0;
        }}

        img {{
            max-width: 100%;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    {nav_html}
    <div class="content">
{html}
    </div>
    <script>
        var toggle = document.querySelector('.nav-toggle');
        if (toggle) {{
            toggle.addEventListener('click', function(e) {{
                e.stopPropagation();
                var nav = this.closest('.site-nav');
                var open = nav.classList.toggle('open');
                this.setAttribute('aria-expanded', open);
            }});
            document.addEventListener('click', function() {{
                var nav = document.querySelector('.site-nav');
                if (nav) {{ nav.classList.remove('open'); toggle.setAttribute('aria-expanded', false); }}
            }});
        }}
    </script>
</body>
</html>"""

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Written to {output_path}")
    else:
        print(html)


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown files to HTML")
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("-o", "--output", help="Output HTML file (default: stdout)")
    parser.add_argument("-s", "--standalone", action="store_true", help="Wrap in complete HTML document")
    parser.add_argument("-d", "--dir", default=".", help="Directory containing MD files")
    parser.add_argument("-n", "--nav", action="store_true", help="Add navigation from index.md H2 headings")
    args = parser.parse_args()

    convert_file(args.input, args.output, args.standalone, args.dir, args.nav)


if __name__ == "__main__":
    main()
