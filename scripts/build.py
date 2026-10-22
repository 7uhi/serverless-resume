"""Build the static website from the PDF configured in site.json."""
import html
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    config = json.loads((ROOT / 'site.json').read_text())
    pdf = (ROOT / config['pdf']).resolve()
    if not pdf.is_file():
        raise ValueError(f'Add your exported resume PDF at {pdf}')
    if not pdf.read_bytes().startswith(b'%PDF-'):
        raise ValueError(f'{pdf.name} is not a PDF file')
    if shutil.which('pdftotext') is None:
        raise ValueError('Missing pdftotext. Install Poppler (macOS: brew install poppler); see README.md.')
    # Extract the text from the very same PDF, so no second resume needs editing.
    text = subprocess.check_output(['pdftotext', '-enc', 'UTF-8', '-nopgbrk', str(pdf), '-'], text=True)
    if not text.strip():
        raise ValueError('The PDF has no extractable text. Export a text-based PDF for the accessible view.')
    esc = lambda value: html.escape(str(value), quote=True)
    template = (ROOT / 'web/index.html').read_text()
    values = {'NAME': config['name'], 'DESCRIPTION': config['description'], 'RESUME_TEXT': text.strip()}
    # Replace in a single pass: user text is never interpreted as another template token.
    import re
    page = re.sub(r'\{\{(NAME|DESCRIPTION|RESUME_TEXT)\}\}', lambda m: esc(values[m[1]]), template)
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    shutil.copyfile(pdf, dist / 'resume.pdf')
    shutil.copyfile(ROOT / 'web/style.css', dist / 'style.css')
    (dist / 'index.html').write_text(page)
    print('Built dist/: website, PDF download, and accessible text view.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as error:
        sys.exit(f'Build failed: {error}')
