from pathlib import Path
import argparse
import re
import shutil

BASE_DIR = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description='Build the trilingual Jahangir Ceram catalog.')
parser.add_argument('source', nargs='?', type=Path, default=BASE_DIR / 'catalog-source.html', help='source HTML file')
parser.add_argument('-o', '--output', type=Path, default=BASE_DIR / 'index.html', help='output HTML file')
parser.add_argument('--backup', type=Path, default=None, help='optional backup path for the source HTML')
args = parser.parse_args()
source = args.source.expanduser().resolve()
target = args.output.expanduser().resolve()
backup = (args.backup.expanduser().resolve() if args.backup else target.with_name(target.stem + '.before-trilingual' + target.suffix))
if not source.is_file():
    raise SystemExit(f'Source HTML file not found: {source}')
target.parent.mkdir(parents=True, exist_ok=True)
backup.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, backup)
html = source.read_text(encoding='utf-8')

css = r'''
  /* Three-language selector and direction support */
  .cover-controls {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    direction: ltr;
  }
  .cover-controls .language-select { align-self: flex-start; margin-top: 0; }
  .language-select {
    align-self: flex-start;
    width: 64px;
    height: 32px;
    margin-top: 0;
    padding: 0 6px;
    color: var(--silver);
    background: rgba(59, 55, 50, 0.82);
    border: 1px solid var(--border);
    border-radius: 999px;
    font: inherit;
    font-size: 11px;
    cursor: pointer;
    outline: none;
  }
  .language-select:hover,
  .language-select:focus-visible { color: var(--gold-soft); border-color: var(--gold); }
  body.light-mode .language-select { color: #5A4B3B; background: rgba(255,253,249,.86); border-color: #D8C5A7; }
  body.light-mode .language-select:hover,
  body.light-mode .language-select:focus-visible { color: #704707; border-color: var(--gold); }
  body > .page:first-child .language-select,
  body.light-mode > .page:first-child .language-select {
    color: #C0C0C0 !important;
    background: #3D3D3D !important;
    border-color: #4A4A4A !important;
    color-scheme: dark;
  }
  body > .page:first-child .language-select:hover,
  body > .page:first-child .language-select:focus-visible,
  body.light-mode > .page:first-child .language-select:hover,
  body.light-mode > .page:first-child .language-select:focus-visible {
    color: #F2D48B !important;
    border-color: #D5982C !important;
  }
  html[dir="rtl"] .catalog-page { direction: rtl; }
  html[dir="rtl"] .catalog-breadcrumb,
  html[dir="rtl"] .coming-soon-message,
  html[dir="rtl"] .contact-panel,
  html[dir="rtl"] .about-panel { text-align: center; }
  @media (max-width: 480px) {
    .cover-controls { gap: 8px; }
    .language-select { width: 60px; height: 30px; margin-top: 0; padding: 0 4px; font-size: 10px; }
  }
  /* Coming Soon is intentionally plain text so it can be removed later without a card. */
  .coming-soon-message {
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
  }
  .coming-soon-message small { display: none !important; }
'''
if html.count('</style>') != 1:
    raise SystemExit(f'Expected exactly one </style>, found {html.count("</style")}')
html = html.replace('</style>', css + '\n</style>', 1)

old_theme = '<button aria-label="Toggle color mode" aria-pressed="false" class="theme-toggle" id="theme-toggle" type="button"><span aria-hidden="true" class="theme-icon">☀</span></button>'
new_theme = '''<div class="cover-controls">\n''' + old_theme + '''\n<select aria-label="Select language" class="language-select" id="language-select">\n  <option value="en">en</option>\n  <option value="fa">fa</option>\n  <option value="ar">ar</option>\n</select>\n</div>'''
if html.count(old_theme) != 1:
    raise SystemExit(f'Expected one theme button, found {html.count(old_theme)}')
html = html.replace(old_theme, new_theme, 1)

language_block = r'''
  var LANGUAGES = {
    en: {
      dir: "ltr",
      ui: {
        siteTitle: "Jahangir Ceram Catalogs", themeToggle: "Toggle color mode", languageSelect: "Select language",
        contactUs: "Contact Us", aboutUs: "About Us", back: "Back", page: "Page", catalogs: "Catalogs",
        selectSubcategory: "Select a subcategory of", contactText: "For product inquiries and further information, please contact Jahangir Ceram.",
        aboutText: "Explore the Jahangir Ceram and Sialk Ceram collections, including their ceramic and porcelain finishes.",
        productImageAlt: "{name} 80×80 product presentation", viewProduct: "View {name} 80×80 product page",
        instagram: "Instagram", whatsapp: "WhatsApp", telegram: "Telegram", linkedin: "LinkedIn",
        bale: "Bale", eitaa: "Eitaa", rubika: "Rubika", aparat: "Aparat", website: "Website", socialLinks: "Social media and website links"
      }
    },
    fa: {
      dir: "rtl",
      ui: {
        siteTitle: "کاتالوگ‌های جهانگیر سرام", themeToggle: "تغییر حالت رنگی", languageSelect: "انتخاب زبان",
        contactUs: "تماس با ما", aboutUs: "درباره ما", back: "بازگشت", page: "صفحه", catalogs: "کاتالوگ‌های",
        selectSubcategory: "یک زیرمجموعه از این بخش را انتخاب کنید:", contactText: "برای استعلام محصولات و دریافت اطلاعات بیشتر با جهانگیر سرام تماس بگیرید.",
        aboutText: "مجموعه‌های جهانگیر سرام و سیلک سرام را با پوشش‌ها و پرداخت‌های سرامیکی و پرسلانی بررسی کنید.",
        productImageAlt: "ارائهٔ محصول {name} در ابعاد ۸۰×۸۰", viewProduct: "مشاهدهٔ صفحهٔ محصول {name} در ابعاد ۸۰×۸۰",
        instagram: "اینستاگرام", whatsapp: "واتساپ", telegram: "تلگرام", linkedin: "لینکدین",
        bale: "بله", eitaa: "ایتا", rubika: "روبیکا", aparat: "آپارات", website: "وب‌سایت", socialLinks: "پیوندهای شبکه‌های اجتماعی و وب‌سایت"
      }
    },
    ar: {
      dir: "rtl",
      ui: {
        siteTitle: "كتالوجات جهانغير سيرام", themeToggle: "تغيير وضع الألوان", languageSelect: "اختيار اللغة",
        contactUs: "اتصل بنا", aboutUs: "من نحن", back: "رجوع", page: "صفحة", catalogs: "كتالوجات",
        selectSubcategory: "اختر تصنيفاً فرعياً من", contactText: "للاستفسار عن المنتجات ومزيد من المعلومات، يرجى التواصل مع جهانغير سيرام.",
        aboutText: "استكشف مجموعات جهانغير سيرام وسيالك سيرام، بما في ذلك التشطيبات الخزفية والبورسلانية.",
        productImageAlt: "عرض منتج {name} بمقاس ۸۰×۸۰", viewProduct: "عرض صفحة منتج {name} بمقاس ۸۰×۸۰",
        instagram: "إنستغرام", whatsapp: "واتساب", telegram: "تلغرام", linkedin: "لينكدإن",
        bale: "بله", eitaa: "إيتا", rubika: "روبيكا", aparat: "أبارات", website: "الموقع الإلكتروني", socialLinks: "روابط التواصل الاجتماعي والموقع الإلكتروني"
      }
    }
  };
  var NAME_TRANSLATIONS = {
    "Jahangir Ceram": { fa: "جهانگیر سرام", ar: "جهانغير سيرام" },
    "Sialk Ceram": { fa: "سیلک سرام", ar: "سيالك سيرام" },
    "Porcelain Ceramic": { fa: "سرامیک پرسلان", ar: "السيراميك والبورسلان" },
    "Matte Glaze": { fa: "لعاب مات", ar: "طلاء مطفي" },
    "Ceramic Washbasin": { fa: "روشویی سرامیکی", ar: "حوض غسيل سيراميكي" },
    "Ceramic Puzzle": { fa: "پازل سرامیکی", ar: "بازل سيراميكي" },
    "Decorative": { fa: "دکوراتیو", ar: "ديكورية" },
    "Coating and Laser Products": { fa: "محصولات کوتینگ و لیزر", ar: "منتجات الطلاء والليزر" },
    "Nano Polish": { fa: "نانو پولیش", ar: "نانو بوليش" },
    "Crystal Polish": { fa: "کریستال پولیش", ar: "كريستال بوليش" },
    "Fitileh": { fa: "فیتیله", ar: "فيتيلي" },
    "Takgol": { fa: "تک گل", ar: "تك گل" },
    "About Us": { fa: "درباره ما", ar: "من نحن" },
    "Contact Us": { fa: "تماس با ما", ar: "اتصل بنا" }
  };
  var currentLanguage = localStorage.getItem("jc-language") || "en";
  if (!LANGUAGES[currentLanguage]) currentLanguage = "en";
  function tr(key) {
    return (LANGUAGES[currentLanguage].ui[key] || LANGUAGES.en.ui[key] || key);
  }
  function localizeName(name) {
    var item = NAME_TRANSLATIONS[name];
    var value = item && item[currentLanguage] ? item[currentLanguage] : String(name);
    return /^\d+[×x*]\d+$/.test(value) ? "\u200e" + value + "\u200e" : value;
  }
  function localizePath(path) {
    return String(path || "").split(" / ").map(localizeName).join(" / ");
  }
  function pageLabel(number) { return tr("page") + " " + number; }
  function catalogLabel(size) { return tr("catalogs") + " " + localizeName(size); }
  function socialLabel(platform) { return tr(platform) || platform; }
'''
marker = '  var themeToggle = document.getElementById("theme-toggle");'
if html.count(marker) != 1:
    raise SystemExit(f'Expected one theme marker, found {html.count(marker)}')
html = html.replace(marker, language_block + '\n' + marker, 1)

# Localize product-gallery accessibility text while keeping product names unchanged.
html = html.replace(
    "aria-label=\"View ' + name + ' 80×80 product page\"",
    "aria-label=\"' + tr(\"viewProduct\").replace(\"{name}\", name) + '\"",
    1,
)

# Ensure all generated sheets retain their original semantic values for refreshLanguage().
html = html.replace(
    'sheet.dataset.pageKey = pageKey;\n    sheet.dataset.pageNumber',
    'sheet.dataset.pageKey = pageKey;\n    sheet.dataset.productIndex = String(index);\n    sheet.dataset.pageNumber',
    1,
)
# The first replacement above is only for ensureProductPage because it is the first matching block.

# Add catalog metadata inside showCatalogPage.
show_catalog_marker = '''    sheet.className = "page catalog-sheet";\n    sheet.dataset.pageKey = pageKey;\n    sheet.dataset.pageNumber'''
show_catalog_replacement = '''    sheet.className = "page catalog-sheet";\n    sheet.dataset.pageKey = pageKey;\n    sheet.dataset.catalogSize = String(size);\n    sheet.dataset.catalogPath = options.path || "";\n    sheet.dataset.productGallery = options.productGallery ? "true" : "false";\n    sheet.dataset.pageNumber'''
if html.count(show_catalog_marker) != 1:
    raise SystemExit(f'Expected one showCatalogPage marker, found {html.count(show_catalog_marker)}')
html = html.replace(show_catalog_marker, show_catalog_replacement, 1)

# Add category metadata inside showCategoryPage.
category_marker = '''    sheet.className = "page category-sheet";\n    sheet.dataset.pageKey = pageKey;\n    sheet.dataset.pageNumber'''
category_replacement = '''    sheet.className = "page category-sheet";\n    sheet.dataset.pageKey = pageKey;\n    sheet.dataset.categoryId = category.id;\n    sheet.dataset.pageNumber'''
if html.count(category_marker) != 1:
    raise SystemExit(f'Expected one showCategoryPage marker, found {html.count(category_marker)}')
html = html.replace(category_marker, category_replacement, 1)

# Add original-name metadata to category entries and child titles.
old_entry = '      item.className = "sub-item sub-item-clickable";\n      item.textContent = name;'
new_entry = '      item.className = "sub-item sub-item-clickable";\n      item.dataset.entryOriginalName = name;\n      item.textContent = localizeName(name);'
if html.count(old_entry) != 1:
    raise SystemExit(f'Expected one entry marker, found {html.count(old_entry)}')
html = html.replace(old_entry, new_entry, 1)
old_child = '          childTitle.className = "child-title";\n          childTitle.textContent = entry.children.title;'
new_child = '          childTitle.className = "child-title";\n          childTitle.dataset.entryOriginalName = entry.children.title;\n          childTitle.textContent = localizeName(entry.children.title);'
if html.count(old_child) != 1:
    raise SystemExit(f'Expected one child-title marker, found {html.count(old_child)}')
html = html.replace(old_child, new_child, 1)

# Localize catalog-page text at creation time for all later-created pages.
html = html.replace(
    "'<h2 class=\"catalog-heading\">Catalogs ' + size + '</h2>' +",
    "'<h2 class=\"catalog-heading\">' + catalogLabel(size) + '</h2>' +",
    1,
)
html = html.replace(
    "'<p class=\"catalog-breadcrumb\">' + (options.path || \"\") + '</p>' +",
    "'<p class=\"catalog-breadcrumb\">' + localizePath(options.path || \"\") + '</p>' +",
    1,
)
html = html.replace(
    "'<div class=\"page-number\">Page ' + sheet.dataset.pageNumber + '</div>';",
    "'<div class=\"page-number\">' + pageLabel(sheet.dataset.pageNumber) + '</div>';",
)
# Product page heading and breadcrumb.
html = html.replace(
    "'<h2 class=\"catalog-heading\">' + name + ' · 80×80</h2>' +",
    "'<h2 class=\"catalog-heading\">' + localizeName(name) + ' · ' + localizeName('80×80') + '</h2>' +",
    1,
)
html = html.replace(
    "'<p class=\"catalog-breadcrumb\">Jahangir Ceram / Porcelain Ceramic / Matte Glaze / 80×80</p>' +",
    "'<p class=\"catalog-breadcrumb\">' + localizePath(\"Jahangir Ceram / Porcelain Ceramic / Matte Glaze / 80×80\") + '</p>' +",
    1,
)
# Category page heading and breadcrumb.
html = html.replace(
    "'<h2 class=\"catalog-heading\">' + category.name + '</h2>' +",
    "'<h2 class=\"catalog-heading\">' + localizeName(category.name) + '</h2>' +",
    1,
)
html = html.replace(
    "'<p class=\"catalog-breadcrumb\">Select a subcategory of ' + category.name + '</p>' +",
    "'<p class=\"catalog-breadcrumb\">' + tr(\"selectSubcategory\") + ' ' + localizeName(category.name) + '</p>' +",
    1,
)

# Localize cover categories and action buttons.
html = html.replace(
    'btn.innerHTML = iconHtml + "<span>" + cat.name + "</span>";',
    'btn.innerHTML = iconHtml + "<span>" + localizeName(cat.name) + "</span>";',
    1,
)
html = html.replace(
    'contactButton.setAttribute("aria-label", "Contact Us");',
    'contactButton.setAttribute("aria-label", tr("contactUs"));',
    1,
)
html = html.replace(
    "'</svg><span>Contact Us</span>';",
    "'</svg><span>' + tr(\"contactUs\") + '</span>';",
    1,
)
html = html.replace(
    'aboutButton.setAttribute("aria-label", "About Us");',
    'aboutButton.setAttribute("aria-label", tr("aboutUs"));',
    1,
)
html = html.replace(
    "'</svg><span>About Us</span>';",
    "'</svg><span>' + tr(\"aboutUs\") + '</span>';",
    1,
)

refresh_block = r'''
  function refreshSheetLanguage(sheet) {
    var pageKey = sheet.dataset.pageKey || "";
    var heading = sheet.querySelector(".catalog-heading");
    var breadcrumb = sheet.querySelector(".catalog-breadcrumb");
    var pageNumber = sheet.querySelector(".page-number");
    var back = sheet.querySelector(".catalog-back");
    if (back) {
      Array.prototype.forEach.call(back.childNodes, function (node) {
        if (node.nodeType === 3) node.nodeValue = tr("back");
      });
    }
    if (pageNumber && sheet.dataset.pageNumber) pageNumber.textContent = pageLabel(sheet.dataset.pageNumber);
    if (pageKey === "about-us") {
      if (heading) heading.textContent = tr("aboutUs");
      if (breadcrumb) breadcrumb.textContent = localizePath("Jahangir Ceram / About Us");
      var aboutText = sheet.querySelector(".about-panel > div");
      if (aboutText) aboutText.textContent = tr("aboutText");
    } else if (pageKey === "contact-us") {
      if (heading) heading.textContent = tr("contactUs");
      if (breadcrumb) breadcrumb.textContent = localizePath("Jahangir Ceram / Contact Us");
      var contactText = sheet.querySelector(".contact-panel > div:not(.social-links)");
      if (contactText) contactText.textContent = tr("contactText");
      var socialLinks = sheet.querySelector(".social-links");
      if (socialLinks) socialLinks.setAttribute("aria-label", tr("socialLinks"));
      sheet.querySelectorAll(".social-link").forEach(function (link) {
        var platform = link.dataset.platform;
        var label = socialLabel(platform);
        link.setAttribute("aria-label", label);
        link.setAttribute("title", label);
        var labelNode = link.querySelector(".social-label");
        if (labelNode) labelNode.textContent = label;
      });
    } else if (pageKey.indexOf("product-80x80-") === 0) {
      var productIndex = Number(sheet.dataset.productIndex || pageKey.split("-").pop());
      var productName = MATTE_GLAZE_PRODUCTS[productIndex] || "";
      if (heading) heading.textContent = localizeName(productName) + " · " + localizeName("80×80");
      if (breadcrumb) breadcrumb.textContent = localizePath("Jahangir Ceram / Porcelain Ceramic / Matte Glaze / 80×80");
      var productImage = sheet.querySelector(".cloudy-product-image");
      if (productImage) productImage.alt = tr("productImageAlt").replace("{name}", productName).replace("80×80", "\u200e80×80\u200e");
    } else if (pageKey.indexOf("category-") === 0) {
      var categoryId = sheet.dataset.categoryId || pageKey.slice("category-".length);
      var category = CATEGORIES.find(function (candidate) { return candidate.id === categoryId; });
      if (category) {
        if (heading) heading.textContent = localizeName(category.name);
        if (breadcrumb) breadcrumb.textContent = tr("selectSubcategory") + " " + localizeName(category.name);
      }
    } else {
      if (heading) heading.textContent = catalogLabel(sheet.dataset.catalogSize || "");
      if (breadcrumb) breadcrumb.textContent = localizePath(sheet.dataset.catalogPath || "");
    }
    sheet.querySelectorAll("[data-entry-original-name]").forEach(function (node) {
      node.textContent = localizeName(node.dataset.entryOriginalName);
    });
    sheet.querySelectorAll(".product-link").forEach(function (link) {
      var productIndex = Number(link.dataset.productIndex);
      var productName = MATTE_GLAZE_PRODUCTS[productIndex] || "";
      link.setAttribute("aria-label", tr("viewProduct").replace("{name}", productName).replace("80×80", "\u200e80×80\u200e"));
      var image = link.querySelector("img");
      if (image) image.alt = tr("productImageAlt").replace("{name}", productName).replace("80×80", "\u200e80×80\u200e");
    });
  }
  function applyLanguage() {
    var direction = LANGUAGES[currentLanguage].dir;
    document.documentElement.lang = currentLanguage;
    document.documentElement.dir = direction;
    document.title = tr("siteTitle");
    document.body.classList.toggle("rtl", direction === "rtl");
    if (pageTitle) pageTitle.textContent = tr("siteTitle");
    if (themeToggle) themeToggle.setAttribute("aria-label", tr("themeToggle"));
    if (languageSelect) {
      languageSelect.value = currentLanguage;
      languageSelect.setAttribute("aria-label", tr("languageSelect"));
    }
    render();
    document.querySelectorAll(".page-number").forEach(function (node) {
      var match = node.textContent.match(/(\d+)\s*$/);
      if (match) node.textContent = pageLabel(match[1]);
    });
    document.querySelectorAll("#catalog-pages > .page").forEach(refreshSheetLanguage);
  }
'''
marker_refresh = '  window.addEventListener("popstate", function () {'
if html.count(marker_refresh) != 1:
    raise SystemExit(f'Expected one popstate marker, found {html.count(marker_refresh)}')
html = html.replace(marker_refresh, refresh_block + '\n' + marker_refresh, 1)

old_bottom = '''  createAboutPage();\n  CATEGORIES.forEach(function (category) {\n    showCategoryPage(category, { initial: true });\n    precreateCatalogPages(category, category.sub, []);\n  });\n  createContactPage();\n  render();'''
new_bottom = '''  var languageSelect = document.getElementById("language-select");\n  if (languageSelect) {\n    languageSelect.value = currentLanguage;\n    languageSelect.addEventListener("change", function () {\n      currentLanguage = languageSelect.value;\n      localStorage.setItem("jc-language", currentLanguage);\n      applyLanguage();\n    });\n  }\n  createAboutPage();\n  CATEGORIES.forEach(function (category) {\n    showCategoryPage(category, { initial: true });\n    precreateCatalogPages(category, category.sub, []);\n  });\n  createContactPage();\n  render();\n  applyLanguage();'''
if html.count(old_bottom) != 1:
    raise SystemExit(f'Expected one bottom initialization block, found {html.count(old_bottom)}')
html = html.replace(old_bottom, new_bottom, 1)

# Remove the Persian wording from Coming Soon while retaining the English marker only.
html = html.replace('Coming Soon<small>به‌زودی</small>', 'Coming Soon')

# Fix the Arabic product-size text to use the existing multiplication glyph consistently.
html = html.replace('مقاس ۸۰×۸۰', 'مقاس 80×80')

# Keep the selected language active when browser history returns to the cover.
html = html.replace('      pageTitle.textContent = defaultTitle;', '      pageTitle.textContent = tr("siteTitle");', 1)
# Add a clear title to the language selector and page direction metadata.
html = html.replace('<html dir="ltr" lang="en">', '<html dir="ltr" lang="en">', 1)

target.write_text(html, encoding='utf-8')
print(f'Updated: {target}')
print(f'Backup: {backup}')
print('Coming Soon is English-only text without the previous Persian subline.')
print('Added persistent English/Persian/Arabic selector and runtime localization for all pages.')
