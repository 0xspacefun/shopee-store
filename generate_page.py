#!/usr/bin/env python3
"""Generate paginated static HTML pages from products_data.json"""
import json, math
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_JSON = SCRIPT_DIR / "data" / "products_data.json"
OUTPUT_DIR = SCRIPT_DIR
PER_PAGE = 10

def fmt_num(n):
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"{v:.1f}jt".replace(".0jt", "jt")
    if n >= 1_000:
        v = n / 1_000
        return f"{v:.1f}rb".replace(".0rb", "rb") if v != int(v) else f"{int(v)}rb"
    return str(n)

def fmt_price(p):
    return f"Rp{p:,.0f}".replace(",", ".")

def product_card(p):
    s = p.get("scraped", {}) or {}
    rating = s.get("rating", 0)
    comments = s.get("comments", 0)
    liked = s.get("liked", 0)
    img = s.get("image_url", p.get("image_local", ""))

    badge = {"skincare":"🧴","makeup":"💄","body_care":"🧴","parfum":"🌸","skintific":"💎","cleansing":"🫧"}.get(p["category"], "🛒")

    return f'''
    <a href="{p['affiliate_link']}" target="_blank" rel="noopener noreferrer" class="product-card" data-category="{p['category']}">
      <div class="product-img-wrap">
        <img src="{img}" alt="{p['short_name']}" loading="lazy" />
        <span class="badge-cat">{badge}</span>
      </div>
      <div class="product-info">
        <h3 class="product-name">{p['short_name']}</h3>
        <div class="product-price">{fmt_price(p['price'])}</div>
        <div class="product-meta">
          <div class="rating">
            <span class="stars">{'★' * int(round(rating))}</span>
            <span class="rating-num">{rating}</span>
          </div>
          <div class="stats">
            <span class="sold">💬 {fmt_num(comments)}</span>
            <span class="liked">❤️ {fmt_num(liked)}</span>
          </div>
        </div>
        <div class="product-cta">Beli di Shopee →</div>
      </div>
    </a>'''

def get_css():
    return '''
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, sans-serif; background: #f5f5f5; color: #333; }
    .header { background: linear-gradient(135deg, #ee4d2d 0%, #ff6633 50%, #ff8533 100%); position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 12px rgba(238,77,45,0.3); }
    .header-inner { max-width: 1200px; margin: 0 auto; padding: 12px 20px; display: flex; align-items: center; gap: 16px; }
    .logo { font-size: 20px; font-weight: 800; color: #fff; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); white-space: nowrap; text-decoration: none; }
    .logo span { font-weight: 400; font-size: 13px; opacity: 0.85; }
    .banner { background: linear-gradient(135deg, #ee4d2d, #ff6633, #ff8533); padding: 24px 20px; text-align: center; }
    .banner h1 { font-size: 24px; font-weight: 800; color: #fff; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); margin-bottom: 4px; }
    .banner p { color: rgba(255,255,255,0.85); font-size: 13px; }
    .cat-nav { background: #fff; border-bottom: 1px solid #eee; position: sticky; top: 48px; z-index: 99; }
    .cat-nav-inner { max-width: 1200px; margin: 0 auto; display: flex; gap: 8px; padding: 10px 20px; overflow-x: auto; scrollbar-width: none; }
    .cat-nav-inner::-webkit-scrollbar { display: none; }
    .cat-pill { display: flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 24px; background: #fff3ef; color: #ee4d2d; font-size: 13px; font-weight: 600; text-decoration: none; white-space: nowrap; border: 1px solid #ffe0d6; transition: all 0.2s; cursor: pointer; }
    .cat-pill:hover, .cat-pill.active { background: #ee4d2d; color: #fff; }
    .cat-emoji { font-size: 16px; }
    .page-header { max-width: 1200px; margin: 0 auto; padding: 16px 20px 0; display: flex; align-items: center; justify-content: space-between; }
    .page-header h2 { font-size: 18px; font-weight: 700; color: #222; }
    .page-header .count { font-size: 13px; color: #999; }
    .products-grid { max-width: 1200px; margin: 0 auto; padding: 12px 20px 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 12px; }
    @media (max-width: 480px) { .products-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; } }
    .product-card { background: #fff; border-radius: 8px; overflow: hidden; text-decoration: none; color: inherit; border: 1px solid #f0f0f0; transition: all 0.25s ease; display: flex; flex-direction: column; }
    .product-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
    .product-img-wrap { position: relative; width: 100%; aspect-ratio: 1; background: #fafafa; overflow: hidden; }
    .product-img-wrap img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
    .product-card:hover .product-img-wrap img { transform: scale(1.05); }
    .badge-cat { position: absolute; top: 6px; left: 6px; background: rgba(255,255,255,0.9); border-radius: 50%; width: 28px; height: 28px; font-size: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
    .product-info { padding: 10px; flex: 1; display: flex; flex-direction: column; }
    .product-name { font-size: 12px; font-weight: 500; color: #333; line-height: 1.4; min-height: 34px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .product-price { font-size: 16px; font-weight: 700; color: #ee4d2d; margin-top: 6px; }
    .product-meta { margin-top: 6px; display: flex; flex-direction: column; gap: 3px; }
    .rating { display: flex; align-items: center; gap: 4px; font-size: 11px; }
    .stars { color: #ffce3d; letter-spacing: -1px; }
    .star-empty { color: #ddd; }
    .rating-num { color: #ee4d2d; font-weight: 600; }
    .stats { display: flex; gap: 10px; font-size: 10px; color: #999; }
    .product-cta { margin-top: 8px; padding: 6px 0; text-align: center; font-size: 11px; font-weight: 600; color: #fff; background: #ee4d2d; border-radius: 4px; transition: background 0.2s; }
    .product-card:hover .product-cta { background: #d4411c; }
    .pagination { max-width: 1200px; margin: 24px auto; padding: 0 20px; display: flex; justify-content: center; gap: 6px; flex-wrap: wrap; }
    .pagination a, .pagination span { padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; text-decoration: none; border: 1px solid #ddd; color: #333; transition: all 0.2s; }
    .pagination a:hover { background: #ee4d2d; color: #fff; border-color: #ee4d2d; }
    .pagination .current { background: #ee4d2d; color: #fff; border-color: #ee4d2d; }
    .footer { max-width: 1200px; margin: 20px auto 0; padding: 20px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee; }
    '''

def generate_page_html(page_num, total_pages, products_on_page, all_products, category_filter=None):
    cat_name = category_filter or "All Products"
    cat_display = {
        "skincare": "🧴 Skincare",
        "makeup": "💄 Makeup",
        "body_care": "🧴 Body Care",
        "cleansing": "🫧 Cleansing",
        "parfum": "🌸 Parfum",
        "skintific": "💎 Skintific",
    }.get(category_filter, "🔥 All Products")

    # Category nav
    cats = [
        ("", "🔥", "All"),
        ("skincare", "🧴", "Skincare"),
        ("makeup", "💄", "Makeup"),
        ("body_care", "🧴", "Body Care"),
        ("cleansing", "🫧", "Cleansing"),
        ("parfum", "🌸", "Parfum"),
        ("skintific", "💎", "Skintific"),
    ]

    cat_nav = ""
    for c in cats:
        prefix = f"{c[0]}_" if c[0] else ""
        active = "active" if c[0] == (category_filter or "") else ""
        cat_nav += f'<a href="{prefix}page1.html" class="cat-pill {active}"><span class="cat-emoji">{c[1]}</span><span>{c[2]}</span></a>'

    # Pagination
    pagination = ""
    if total_pages > 1:
        prefix = f"{category_filter}_" if category_filter else ""
        for p in range(1, total_pages + 1):
            if p == page_num:
                pagination += f'<span class="current">{p}</span>'
            else:
                pagination += f'<a href="{prefix}page{p}.html">{p}</a>'

    # Product cards
    cards = "".join(product_card(p) for p in products_on_page)

    # Stats
    start = (page_num - 1) * PER_PAGE + 1
    end = min(page_num * PER_PAGE, len(all_products))
    total = len(all_products)

    filename = f"{category_filter}_page{page_num}.html" if category_filter else f"page{page_num}.html"

    return f'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SweetFinds — {cat_display}</title>
  <meta name="description" content="SweetFinds — curated {cat_name} picks. Harga terjangkau, kualitas terjamin!">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>{get_css()}</style>
</head>
<body>

<header class="header">
  <div class="header-inner">
    <a href="page1.html" class="logo">SWEETFINDS <span>Beauty Picks</span></a>
  </div>
</header>

<section class="banner">
  <h1>✨ SWEETFINDS ✨</h1>
  <p>Curated Beauty Picks • Harga Terjangkau • Kualitas Terjamin</p>
</section>

<nav class="cat-nav">
  <div class="cat-nav-inner">
    {cat_nav}
  </div>
</nav>

<div class="page-header">
  <h2>{cat_display}</h2>
  <span class="count">Menampilkan {start}–{end} dari {total} produk</span>
</div>

<div class="products-grid">
  {cards}
</div>

<div class="pagination">
  {pagination}
</div>

<footer class="footer">
  <p>SweetFinds — Shopee Affiliate Picks</p>
  <p style="margin-top:4px">Halaman {page_num}/{total_pages} • {total} produk</p>
</footer>

<script>
document.querySelectorAll('.product-img-wrap img').forEach(img => {{
  img.onerror = function() {{ this.style.background='#f5f5f5'; this.style.objectFit='contain'; }};
}});
</script>

</body>
</html>''', filename


def main():
    with open(DATA_JSON) as f:
        data = json.load(f)

    products = data["products"]
    total = len(products)
    total_pages = math.ceil(total / PER_PAGE)

    # Group by category
    categories = {}
    for p in products:
        cat = p["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)

    generated = []

    # Generate "All" pages
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * PER_PAGE
        end = start + PER_PAGE
        page_products = products[start:end]
        html, filename = generate_page_html(page_num, total_pages, page_products, products)
        (OUTPUT_DIR / filename).write_text(html)
        generated.append(filename)

    # Generate category pages
    for cat, cat_products in categories.items():
        cat_pages = math.ceil(len(cat_products) / PER_PAGE)
        for page_num in range(1, cat_pages + 1):
            start = (page_num - 1) * PER_PAGE
            end = start + PER_PAGE
            page_products = cat_products[start:end]
            html, filename = generate_page_html(page_num, cat_pages, page_products, cat_products, category_filter=cat)
            (OUTPUT_DIR / filename).write_text(html)
            generated.append(filename)

    # Redirect index.html to page1.html
    (OUTPUT_DIR / "index.html").write_text('''<!DOCTYPE html>
<html><head><meta http-equiv="refresh" content="0;url=page1.html"></head></html>''')

    print(f"✅ Generated {len(generated)} pages for {total} products")
    for f in sorted(generated):
        print(f"   📄 {f}")


if __name__ == "__main__":
    main()
