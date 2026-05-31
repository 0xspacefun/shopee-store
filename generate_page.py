#!/usr/bin/env python3
"""SweetFinds v2 -- Premium affiliate store generator"""
import json, math, html as h
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_JSON = SCRIPT_DIR / "data" / "products_data.json"
OUTPUT_DIR = SCRIPT_DIR
CSS_FILE = SCRIPT_DIR / "style.css"
PER_PAGE = 12

CATS = [
    ("", "🔥", "All", "Semua Produk"),
    ("skincare", "🧴", "Skincare", "Perawatan Wajah"),
    ("makeup", "💄", "Makeup", "Riasan Cantik"),
    ("body_care", "🫧", "Body Care", "Perawatan Tubuh"),
    ("hair_care", "💇‍♀️", "Hair Care", "Perawatan Rambut"),
    ("parfum", "🌸", "Parfum", "Wangi Tahan Lama"),
    ("set_bundle", "💎", "Bundle", "Paket Hemat"),
]

CAT_D = {
    "skincare": "🧴 Skincare", "makeup": "💄 Makeup",
    "body_care": "🫧 Body Care", "cleansing": "🫧 Cleansing",
    "parfum": "🌸 Parfum", "set_bundle": "💎 Bundle",
    "hair_care": "💇‍♀️ Hair Care",
}

CAT_SUB = {
    None: "Koleksi produk kecantikan pilihan — harga terjangkau, kualitas terjamin ✨",
    "skincare": "Kulit sehat & glowing dimulai dari sini ✨",
    "makeup": "Riasan flawless untuk setiap momen 💋",
    "body_care": "Perawatan tubuh lembut & wangi sepanjang hari 🫧",
    "hair_care": "Rambut sehat, kuat, & berkilau 💆‍♀️",
    "parfum": "Wangi tahan lama yang bikin pede seharian 🌸",
    "set_bundle": "Paket hemat, hasil maksimal 💎",
}

BADGE = {
    "skincare": "🧴", "makeup": "💄", "body_care": "🫧",
    "parfum": "🌸", "set_bundle": "💎", "cleansing": "🫧",
    "hair_care": "💇‍♀️",
}


def fmt_n(n):
    if n >= 1e6:
        return f"{n / 1e6:.1f}jt".replace(".0jt", "jt")
    if n >= 1e3:
        v = n / 1e3
        return f"{v:.1f}rb".replace(".0rb", "rb") if v != int(v) else f"{int(v)}rb"
    return str(n)


def fmt_p(p):
    return f"Rp{p:,.0f}".replace(",", ".")


def stars(r):
    s = int(round(r))
    out = []
    for i in range(5):
        if i < s:
            out.append('<span class="sf">★</span>')
        else:
            out.append('<span class="se">★</span>')
    return "".join(out)


def card(p):
    s = p.get("scraped", {}) or {}
    r = s.get("rating", 0)
    c = s.get("comments", 0)
    l = s.get("liked", 0)
    rv = s.get("reviews", 0)
    img = s.get("image_url", "")
    b = BADGE.get(p["category"], "🛒")
    nm = h.escape(p["short_name"])
    hot = '<span class="hot">🔥 Hot</span>' if l > 50000 else ""
    return (
        '<a href="' + p["affiliate_link"] + '" target="_blank" rel="noopener" class="pc" '
        'data-cat="' + p["category"] + '" data-nm="' + p["short_name"].lower() + '">'
        '<div class="pi"><img src="' + img + '" alt="' + nm + '" loading="lazy"/>'
        '<span class="badge">' + b + '</span>' + hot + '</div>'
        '<div class="pb"><h3 class="pn">' + nm + '</h3>'
        '<div class="pp">' + fmt_p(p.get("price", 0)) + '</div>'
        '<div class="pm"><div class="pr">' + stars(r)
        + '<span class="rv">' + str(r) + '</span>'
        '<span class="rc">(' + fmt_n(rv) + ')</span></div>'
        '<div class="ps"><span>💬 ' + fmt_n(c) + '</span>'
        '<span>❤️ ' + fmt_n(l) + '</span></div></div>'
        '<div class="cta"><span>Beli di Shopee</span>'
        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2.5" stroke-linecap="round">'
        '<path d="M5 12h14M12 5l7 7-7 7"/></svg></div></div></a>'
    )


def get_css():
    if CSS_FILE.exists():
        return CSS_FILE.read_text()
    return ""


JS_CODE = """const prog=document.getElementById("prog");
window.addEventListener("scroll",function(){var h=document.documentElement;var s=h.scrollTop/(h.scrollHeight-h.clientHeight)*100;prog.style.width=s+"%"});
var search=document.getElementById("search");var grid=document.getElementById("product-grid");
search.addEventListener("input",function(){var q=search.value.toLowerCase();grid.querySelectorAll(".pc").forEach(function(c){var nm=c.dataset.nm||"";var cat=c.dataset.cat||"";c.style.display=(nm.includes(q)||cat.includes(q))?"":"none"})});
document.querySelectorAll(".pi img").forEach(function(img){img.onerror=function(){this.style.background="#f5f5f5";this.style.objectFit="contain"}});"""


def gen_page(page_num, total_pages, products_on_page, all_products, cat_filter=None):
    cat_disp = CAT_D.get(cat_filter, "🔥 All Products")
    cat_sub = CAT_SUB.get(cat_filter, CAT_SUB[None])

    cats_html = ""
    for c in CATS:
        prefix = c[0] + "_" if c[0] else ""
        act = "a" if c[0] == (cat_filter or "") else ""
        cats_html += '<a href="' + prefix + 'page1.html" class="cp ' + act + '">' \
                     '<span>' + c[1] + '</span><span>' + c[2] + '</span></a>'

    pgn_html = ""
    if total_pages > 1:
        prefix = cat_filter + "_" if cat_filter else ""
        for p in range(1, total_pages + 1):
            if p == page_num:
                pgn_html += '<span class="cur">' + str(p) + '</span>'
            else:
                pgn_html += '<a href="' + prefix + 'page' + str(p) + '.html">' + str(p) + '</a>'

    cards = "".join(card(p) for p in products_on_page)
    start = (page_num - 1) * PER_PAGE + 1
    end = min(page_num * PER_PAGE, len(all_products))
    total = len(all_products)
    filename = cat_filter + "_page" + str(page_num) + ".html" if cat_filter else "page" + str(page_num) + ".html"

    no_results = ""
    if not products_on_page:
        no_results = '<div class="no-results"><div class="emoji">🔍</div><p>Produk tidak ditemukan</p></div>'

    html = '<!DOCTYPE html>\n<html lang="id">\n<head>\n'
    html += '<meta charset="UTF-8">\n'
    html += '<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
    html += '<title>SweetFinds — ' + cat_disp + '</title>\n'
    html += '<meta name="description" content="SweetFinds — ' + cat_sub + '">\n'
    html += '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    html += '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    html += '<style>' + get_css() + '</style>\n'
    html += '</head>\n<body>\n'
    html += '<div class="prog" id="prog"></div>\n'

    # Header
    html += '<header class="hdr"><div class="hi">\n'
    html += '<a href="page1.html" class="lw"><div class="li">S</div>'
    html += '<div><div class="lt">SWEET<span>FINDS</span></div>'
    html += '<div class="ls">Beauty Picks</div></div></a>\n'
    html += '<div class="sw"><svg class="sico" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
    html += '<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>'
    html += '<input type="text" class="si" placeholder="Cari produk..." id="search" autocomplete="off"/></div>\n'
    html += '</div></header>\n'

    # Hero
    html += '<section class="hero">\n'
    html += '<span class="hd">✨</span><span class="hd">💄</span><span class="hd">🌸</span><span class="hd">💎</span>\n'
    html += '<div class="hc">\n'
    html += '<div class="hbadge">✨ Curated Beauty Picks</div>\n'
    html += '<h1>Temukan Produk <span class="ac">Kecantikan Terbaik</span><br/>Harga Terjangkau</h1>\n'
    html += '<p class="hsub">' + cat_sub + '</p>\n'
    html += '<div class="hstats">'
    html += '<div><div class="hsn">' + str(total) + '</div><div class="hsl">Produk</div></div>'
    html += '<div><div class="hsn">7</div><div class="hsl">Kategori</div></div>'
    html += '<div><div class="hsn">⭐ 4.8+</div><div class="hsl">Rating</div></div>'
    html += '</div>\n</div>\n</section>\n'

    # Nav
    html += '<nav class="cnav"><div class="cni">' + cats_html + '</div></nav>\n'

    # Section
    html += '<section class="sec">\n'
    html += '<div class="sh"><div>'
    html += '<div class="st">' + cat_disp + '</div>'
    html += '<div class="ss">Menampilkan ' + str(start) + '–' + str(end) + ' dari ' + str(total) + ' produk</div>'
    html += '</div><span class="cb">' + str(total) + ' produk</span></div>\n'
    html += '<div class="pg" id="product-grid">' + cards + no_results + '</div>\n'
    html += '</section>\n'

    # Pagination
    html += '<div class="pgn">' + pgn_html + '</div>\n'

    # Footer
    html += '<footer class="ftr">'
    html += '<div class="ftr-brand">SWEET<span>FINDS</span></div>'
    html += '<p>Shopee Affiliate Picks • Halaman ' + str(page_num) + '/' + str(total_pages) + ' • ' + str(total) + ' produk</p>'
    html += '<p style="margin-top:4px;font-size:11px;color:#bbb">Harga dan ketersediaan dapat berubah sewaktu-waktu</p>'
    html += '</footer>\n'

    # JS
    html += '<script>' + JS_CODE + '</script>\n'
    html += '</body></html>'

    return html, filename


def main():
    with open(DATA_JSON) as f:
        data = json.load(f)
    products = data["products"]
    total = len(products)
    total_pages = math.ceil(total / PER_PAGE)
    categories = {}
    for p in products:
        cat = p["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)
    generated = []

    # All pages
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * PER_PAGE
        end = start + PER_PAGE
        html_content, filename = gen_page(page_num, total_pages, products[start:end], products)
        (OUTPUT_DIR / filename).write_text(html_content, encoding="utf-8")
        generated.append(filename)

    # Category pages
    for cat, cat_products in categories.items():
        cat_pages = math.ceil(len(cat_products) / PER_PAGE)
        for page_num in range(1, cat_pages + 1):
            start = (page_num - 1) * PER_PAGE
            end = start + PER_PAGE
            html_content, filename = gen_page(page_num, cat_pages, cat_products[start:end], cat_products, cat_filter=cat)
            (OUTPUT_DIR / filename).write_text(html_content, encoding="utf-8")
            generated.append(filename)

    # Index redirect
    (OUTPUT_DIR / "index.html").write_text(
        '<!DOCTYPE html>\n<html><head><meta http-equiv="refresh" content="0;url=page1.html"></head></html>',
        encoding="utf-8"
    )

    print(f"✅ Generated {len(generated)} pages for {total} products")
    for f in sorted(generated):
        print(f"   📄 {f}")


if __name__ == "__main__":
    main()
