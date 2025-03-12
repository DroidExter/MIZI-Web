"""
A script for converting Markdown content into HTML files, applying templates, 
and generating an output directory for a static site.

This script processes Markdown files, converts them into HTML, and generates a static 
website structure with the following features:

1. Reads and processes Markdown files, including special handling for files prefixed with '_'.
2. Converts Markdown content to HTML using the `markdown` library with extensions for additional functionality.
3. Supports custom link processing through the `md2html_links.CustomLinkExtension`.
4. Copies over static files (e.g., images, non-Markdown files) to the output directory.
5. Loads a base HTML template and replaces placeholders with the generated content.
6. Generates custom CSS for code highlighting using `pygments`.

Configuration variables:
- `BASE_DIR`: Base directory where the script is located.
- `CONTENT_DIR`: Directory containing the Markdown and HTML content files.
- `OUTPUT_DIR`: Directory where the generated HTML files and static assets will be stored.
- `TEMPLATES_DIR`: Directory containing the HTML templates used for the base layout.
- `OUTPUT_CSS_DIR`: Directory for storing the generated CSS for code styling.

Command-line arguments:
- `--noclear`: Skip clearing the output directory before building.
- `--autorefresh`: Automatically reload the page every second during debugging.
"""

from markdown import markdown
from pathlib import Path
import re
import shutil
from pygments.formatters import HtmlFormatter
from md2html_links import CustomLinkExtension as md2html
import sys

BASE_DIR = Path(__file__).parent
CONTENT_DIR = BASE_DIR/'content'
OUTPUT_DIR = BASE_DIR/'output'
TEMPLATES_DIR = BASE_DIR/'templates'
OUTPUT_CSS_DIR = OUTPUT_DIR/'css'

CODE_STYLE = 'default'

extensions=['pymdownx.extra', 'pymdownx.magiclink', 'pymdownx.inlinehilite', md2html()]

extension_configs = {
    'pymdownx.extra': {
        'markdown.extensions.footnotes': {
            'SUPERSCRIPT_TEXT': '[{}]',
        }
    }
}

if '--noclear' not in sys.argv:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for file_path in CONTENT_DIR.iterdir():
    if file_path.suffix != '.md' and file_path.stem[0] != '_':
        if file_path.is_file():
            shutil.copy(file_path, OUTPUT_DIR)
        else:
            shutil.copytree(file_path, OUTPUT_DIR/file_path.stem, dirs_exist_ok=True)

with open(BASE_DIR/'templates'/'base.html') as html_file:
    base_html = html_file.read()

if '--autorefresh' in sys.argv:
    base_html = base_html.replace('{{ debug }}','<script>setInterval(() => {location.reload();}, 1000);</script>')
else:
    base_html = base_html.replace('{{ debug }}','')

for md_path in CONTENT_DIR.glob('_*.md'):
    with open(md_path, 'r', encoding='utf-8') as md_file:
        html = markdown(md_file.read(), extensions=extensions, extension_configs=extension_configs)
    base_html = base_html.replace(f'{{{{ {md_path.stem} }}}}', html)

for html_path in CONTENT_DIR.glob('_*.html'):
    with open(html_path, 'r', encoding='utf-8') as html_file:
        html = html_file.read()
    base_html = base_html.replace(f'{{{{ {html_path.stem} }}}}', html)


for md_path in (path for path in CONTENT_DIR.glob('*.md') if path.stem[0]!='_'):
    with open(md_path, 'r', encoding='utf-8') as md_file:
        md = markdown(md_file.read(), extensions=extensions, extension_configs=extension_configs)

    h1_match = re.search(r'<h1>(.*?)</h1>', md)
    title = h1_match.group(1) if h1_match else md_path.stem

    with open(OUTPUT_DIR/f'{md_path.stem}.html', 'w', encoding='utf-8') as html_file:
        html_file.write(
            base_html
            .replace('{{ content }}', md)
            .replace('{{ title }}', title)
        )


code_css = HtmlFormatter(style=CODE_STYLE).get_style_defs('.highlight')
OUTPUT_CSS_DIR.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_CSS_DIR/'codes.css', 'w') as f:
    f.write(code_css)
