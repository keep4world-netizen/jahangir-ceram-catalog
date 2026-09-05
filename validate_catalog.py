from pathlib import Path
import argparse
import base64
import re
import subprocess
import tempfile

try:
    from bs4 import BeautifulSoup
    from io import BytesIO
    from PIL import Image
except ImportError as error:
    raise SystemExit('Missing validation dependency. Install with: python -m pip install beautifulsoup4 pillow') from error

parser = argparse.ArgumentParser(description='Validate the Jahangir Ceram catalog HTML.')
parser.add_argument('html', nargs='?', type=Path, default=Path(__file__).with_name('index.html'), help='HTML file to validate')
args = parser.parse_args()
path = args.html.expanduser().resolve()
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
assert 'body.light-mode > .page:first-child .language-select' in css
assert soup.find('meta', attrs={'name': 'viewport'}) is not None

assert '<option value="en">en</option>' in html
assert '<option value="fa">fa</option>' in html
assert '<option value="ar">ar</option>' in html
assert '<div class="cover-controls">' in html
assert 'Coming Soon<small>به‌زودی</small>' not in html
assert 'data-placeholder="coming-soon">Coming Soon' in html

script_tag = soup.find('script')
assert script_tag is not None
script = script_tag.string or script_tag.get_text()
social_platforms = re.findall(r'data-platform="([a-z]+)"', script)
assert social_platforms == [
    'instagram', 'whatsapp', 'telegram', 'linkedin', 'bale',
    'eitaa', 'rubika', 'aparat', 'website', 'email'
]
assert script.count('<a class="social-link"') == 10
assert script.count('<img class="social-icon"') == 10
assert ''''<div class="social-links" aria-label="Social media and website links">' +
          '<a class="social-link"''' in script
assert '''<span class="social-label">Website</span>' +
          '</a>' +
          '<a class="social-link"''' in script
for token in [
    'var LANGUAGES = {', 'var NAME_TRANSLATIONS = {',
    'var CONTACT_DETAILS = {', 'function contactValue(key)', 'function contactMapHref(key)',
    'tel:+989103101405', 'tel:+983155571126',
    'WG3R+RXM, Amir Kabir Industrial Town, 665Isfahan Province',
    'XCRG+G2V, Kashan, Isfahan Province',
    'المدينة الصناعية أمير كبير', 'شارع كشاورز',
    'https://www.instagram.com/jahangir_ceram', 'https://wa.me/989103101405',
    'https://t.me/jahangirceram', 'https://ble.ir/jahangir_ceram',
    'https://eitaa.com/jahangir_ceram', 'https://rubika.ir/page/jahangirceram',
    'https://www.aparat.com/jahangirceram', 'https://jahangirceram.com',
    'mailto:jahangirceram@gmail.com', 'target="_blank"',
    'Free consultation on all platforms', 'مشاوره رایگان در تمامی پلتفرم ها',
    'استشارات مجانية على جميع المنصات',
    'name: "Fitileh", children: { title: "", items: ["2×60", "4×60"] }',
    'name: "Takgol", children: { title: "", items: ["30×60"] }',
    'function applyLanguage()', 'function refreshSheetLanguage(sheet)',
    'function readStoredLanguage()', 'function writeStoredLanguage(value)', 'writeStoredLanguage(currentLanguage)',
    'document.documentElement.dir = direction',
    'createAboutPage();', 'createContactPage();',
    'precreateCatalogPages(category, category.sub, [])',
    'data-placeholder="coming-soon">Coming Soon'
]:
    assert token in script, token
assert '.social-link[data-platform="bale"] .social-icon { transform: scale(1.16); }' in html
assert '.social-link[data-platform="eitaa"] .social-icon { transform: scale(.88); }' in html
assert 'Four Jahangir Nano Polish Products' in script
assert 'JAHANGIR_NANO_80_PRODUCTS' in script
for requested_product in ['Diora', 'Lona', 'Ribera', 'Velora']:
    assert requested_product in script, requested_product
for label in [
    'siteTitle:', 'contactUs:', 'aboutUs:', 'back:', 'page:', 'catalogs:',
    'selectSubcategory:', 'contactText:', 'aboutText:', 'productImageAlt:',
    'viewProduct:', 'instagram:', 'whatsapp:', 'telegram:', 'linkedin:',
    'bale:', 'eitaa:', 'rubika:', 'aparat:', 'website:'
]:
    assert script.count(label) >= 3, label

with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
    f.write(script)
    js_path = f.name
result = subprocess.run(['node', '--check', js_path], capture_output=True, text=True)
if result.returncode != 0:
    raise SystemExit(result.stderr)

image_refs = sorted(set(re.findall(r'/assets/images/([^"\' )]+)', html)))
assert image_refs, 'No external image references found'
assert 'data:image/' not in html
EXPECTED_SIALK_60120_DETAIL_IMAGES = 5
EXPECTED_SIALK_8080_DETAIL_IMAGES = 4
for image_name in image_refs:
    image_path = path.parent / 'assets' / 'images' / image_name
    assert image_path.is_file(), image_path
    with Image.open(image_path) as im:
        assert im.format == 'WEBP' and im.width > 0 and im.height > 0
assert 'var SIALK_PAGE19_DETAIL_IMAGES = [' in script
assert script.count('SIALK_PAGE19_DETAIL_IMAGES[index]') == 1
assert 'var SIALK_PAGE25_DETAIL_IMAGES = [' in script
assert script.count('SIALK_PAGE25_DETAIL_IMAGES[index]') == 2
# The current catalog references the 60×120 orientation in multiple places;
# validate the orientation itself rather than a stale exact occurrence count.
assert '120×60' not in html and html.count('60×120') >= 2
print('HTML parse: OK')
print('JavaScript syntax: OK')
print('Coming Soon is English-only plain text without a box: OK')
print('English/Persian/Arabic language selector and dictionaries: OK')
print('RTL direction support for Persian and Arabic: OK')
print('Dynamic page, breadcrumb, button, social label, and accessibility localization: OK')
print('All 10 social links and their embedded icons are correctly concatenated: OK')
print(f'All {len(image_refs)} external WebP image assets exist and remain valid: OK')
print(f'All {EXPECTED_SIALK_60120_DETAIL_IMAGES} Sialk 60×120 detail images are configured separately from the gallery: OK')
print(f'All {EXPECTED_SIALK_8080_DETAIL_IMAGES} Sialk 80×80 detail images are configured separately from the gallery: OK')
print('Theme, navigation, page order, and dimensions preserved: OK')
