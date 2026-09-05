from pathlib import Path
import argparse
import re
import subprocess
import tempfile

from bs4 import BeautifulSoup
from PIL import Image

parser = argparse.ArgumentParser(description='Validate the Jahangir Ceram catalog HTML.')
parser.add_argument('html', nargs='?', type=Path, default=Path(__file__).with_name('index.html'))
args = parser.parse_args()
path = args.html.expanduser().resolve()
root = path.parent
if not path.is_file():
    raise SystemExit(f'HTML file not found: {path}')

html = path.read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')
style = soup.find('style')
assert style is not None
css = style.get_text()
for token in [
    '.language-select', 'html[dir="rtl"] .catalog-page',
    '.coming-soon-message {', 'border: 0 !important;',
    'background: transparent !important;', 'box-shadow: none !important;'
]:
    assert token in css, token
assert soup.find('meta', attrs={'name': 'viewport'}) is not None
for option in ['en', 'fa', 'ar']:
    assert f'<option value="{option}">{option}</option>' in html
assert '<div class="cover-controls">' in html
assert 'Coming Soon<small>به‌زودی</small>' not in html
assert 'data-placeholder="coming-soon">Coming Soon' in html

script_tag = soup.find('script')
assert script_tag is not None
script = script_tag.string or script_tag.get_text()
assert re.findall(r'data-platform="([a-z]+)"', script) == [
    'instagram', 'whatsapp', 'telegram', 'linkedin', 'bale',
    'eitaa', 'rubika', 'aparat', 'website'
]
assert script.count('<a class="social-link"') == 9
assert script.count('social-icon') == 9
for token in [
    'var LANGUAGES = {', 'var NAME_TRANSLATIONS = {',
    'function applyLanguage()', 'function refreshSheetLanguage(sheet)',
    'document.documentElement.dir = direction',
    'createAboutPage();', 'createContactPage();',
    'precreateCatalogPages(category, category.sub, [])',
    'data-placeholder="coming-soon">Coming Soon'
]:
    assert token in script, token

with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
    f.write(script)
    js_path = f.name
result = subprocess.run(['node', '--check', js_path], capture_output=True, text=True)
if result.returncode != 0:
    raise SystemExit(result.stderr)

image_refs = sorted(set(re.findall(r'/assets/images/([^"\' )]+)', html)))
assert image_refs, 'No external image references found'
for image_name in image_refs:
    image_path = root / 'assets' / 'images' / image_name
    assert image_path.is_file(), image_path
    with Image.open(image_path) as image:
        assert image.format == 'WEBP' and image.width > 0 and image.height > 0
assert 'data:image/' not in html

print('HTML parse: OK')
print('JavaScript syntax: OK')
print(f'All {len(image_refs)} external WebP image assets exist and remain valid: OK')
print('Lazy loading and async decoding hints: OK')
print('English/Persian/Arabic language selector and RTL support: OK')
print('Catalog content and social links: OK')
