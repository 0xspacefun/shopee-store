#!/usr/bin/env python3
"""Generate static HTML page from products_data.json"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_JSON = SCRIPT_DIR / "data" / "products_data.json"
OUTPUT_HTML = SCRIPT_DIR / "index.html"

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

def stars_html(rating):
    full = int(rating)
    half = 1 if rating - full >= 0.3 else 0
    empty = 5 - full - half
    return '★' * full + ('½' if half else '') + '<span class="star-empty">' + '★' * empty + '</span>'

def product_card(p):
    s = p.get("scraped", {}) or {}
    rating = s.get("rating", 0)
    reviews = s.get("reviews", 0)
    comments = s.get("comments", 0)
    liked = s.get("liked", 0)
    # Use CDN URL (works everywhere) with local fallback
    img = s.get("image_url", p.get("image_local", ""))

    badge = ""
    if p["category"] == "skincare":
        badge = "🧴"
    elif p["category"] == "makeup":
        badge = "💄"
    elif p["category"] == "body_care":
        badge = "🧴"
    elif p["category"] == "parfum":
        badge = "🌸"

    return f'''
    <a href="{p['affiliate_link']}" target="_blank" rel="noopener noreferrer" class="product-card" data-category="{p['category']}" data-sub="{p['sub']}">
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

def category_section(cat_key, cat_label, emoji, products):
    cards = "".join(product_card(p) for p in products if p["category"] == cat_key)
    if not cards:
        return ""
    return f'''
    <section class="category-section" id="{cat_key}">
      <div class="section-header">
        <h2>{emoji} {cat_label}</h2>
      </div>
      <div class="products-grid">
        {cards}
      </div>
    </section>'''

def main():
    with open(DATA_JSON) as f:
        data = json.load(f)

    products = data["products"]
    fetched = data["fetched_at"]
    total = data["total"]

    # Build category sections
    sections = ""
    sections += category_section("skincare", "SKINCARE", "🧴", products)
    sections += category_section("makeup", "MAKEUP", "💄", products)
    sections += category_section("body_care", "BODY CARE", "🧴", products)
    sections += category_section("parfum", "PARFUM", "🌸", products)

    # Category nav
    cats = [
        ("skincare", "🧴", "Skincare"),
        ("makeup", "💄", "Makeup"),
        ("body_care", "🧴", "Body Care"),
        ("parfum", "🌸", "Parfum"),
    ]
    cat_nav = "".join(f'<a href="#{c[0]}" class="cat-pill"><span class="cat-emoji">{c[1]}</span><span>{c[2]}</span></a>' for c in cats)

    html = f'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Merah Jingga Official — Rekomendasi Skincare, Makeup & Parfum</title>
  <meta name="description" content="Temukan produk skincare, makeup, parfum & body care pilihan terbaik dari Merah Jingga Official. Harga terjangkau, kualitas terjamin!">
  <meta property="og:title" content="Merah Jingga Official — Rekomendasi Produk Terbaik">
  <meta property="og:description" content="Skincare, makeup, parfum & body care pilihan dari Merah Jingga Official">
  <meta property="og:type" content="website">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Inter', -apple-system, sans-serif; background: #f5f5f5; color: #333; }}

    /* Header */
    .header {{
      background: linear-gradient(135deg, #ee4d2d 0%, #ff6633 50%, #ff8533 100%);
      padding: 0;
      position: sticky; top: 0; z-index: 100;
      box-shadow: 0 2px 12px rgba(238,77,45,0.3);
    }}
    .header-inner {{
      max-width: 1200px; margin: 0 auto;
      padding: 12px 20px;
      display: flex; align-items: center; gap: 16px;
    }}
    .logo {{
      font-size: 20px; font-weight: 800; color: #fff;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
      white-space: nowrap; text-decoration: none;
    }}
    .logo span {{ font-weight: 400; font-size: 13px; opacity: 0.85; }}

    /* Banner */
    .banner {{
      background: linear-gradient(135deg, #ee4d2d, #ff6633, #ff8533);
      padding: 32px 20px; text-align: center;
    }}
    .banner h1 {{
      font-size: 28px; font-weight: 800; color: #fff;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
      margin-bottom: 6px;
    }}
    .banner p {{ color: rgba(255,255,255,0.85); font-size: 14px; }}

    /* Category Nav */
    .cat-nav {{
      background: #fff; border-bottom: 1px solid #eee;
      position: sticky; top: 52px; z-index: 99;
    }}
    .cat-nav-inner {{
      max-width: 1200px; margin: 0 auto;
      display: flex; gap: 8px; padding: 12px 20px;
      overflow-x: auto; scrollbar-width: none;
    }}
    .cat-nav-inner::-webkit-scrollbar {{ display: none; }}
    .cat-pill {{
      display: flex; align-items: center; gap: 6px;
      padding: 8px 18px; border-radius: 24px;
      background: #fff3ef; color: #ee4d2d;
      font-size: 13px; font-weight: 600;
      text-decoration: none; white-space: nowrap;
      border: 1px solid #ffe0d6;
      transition: all 0.2s;
    }}
    .cat-pill:hover {{ background: #ee4d2d; color: #fff; }}
    .cat-emoji {{ font-size: 16px; }}

    /* Sections */
    .category-section {{
      max-width: 1200px; margin: 0 auto;
      padding: 24px 20px 0;
    }}
    .section-header {{
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 16px;
    }}
    .section-header h2 {{
      font-size: 20px; font-weight: 700; color: #222;
    }}

    /* Product Grid */
    .products-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
      gap: 12px;
    }}
    @media (max-width: 480px) {{
      .products-grid {{ grid-template-columns: repeat(2, 1fr); gap: 8px; }}
    }}

    /* Product Card */
    .product-card {{
      background: #fff; border-radius: 8px;
      overflow: hidden; text-decoration: none; color: inherit;
      border: 1px solid #f0f0f0;
      transition: all 0.25s ease;
      display: flex; flex-direction: column;
    }}
    .product-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }}
    .product-img-wrap {{
      position: relative; width: 100%;
      aspect-ratio: 1; background: #fafafa;
      overflow: hidden;
    }}
    .product-img-wrap img {{
      width: 100%; height: 100%;
      object-fit: cover; transition: transform 0.3s;
    }}
    .product-card:hover .product-img-wrap img {{ transform: scale(1.05); }}
    .badge-cat {{
      position: absolute; top: 6px; left: 6px;
      background: rgba(255,255,255,0.9); border-radius: 50%;
      width: 28px; height: 28px; font-size: 14px;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }}

    .product-info {{ padding: 10px; flex: 1; display: flex; flex-direction: column; }}
    .product-name {{
      font-size: 12px; font-weight: 500; color: #333;
      line-height: 1.4; min-height: 34px;
      display: -webkit-box; -webkit-line-clamp: 2;
      -webkit-box-orient: vertical; overflow: hidden;
    }}
    .product-price {{
      font-size: 16px; font-weight: 700; color: #ee4d2d;
      margin-top: 6px;
    }}
    .product-meta {{
      margin-top: 6px; display: flex; flex-direction: column; gap: 3px;
    }}
    .rating {{
      display: flex; align-items: center; gap: 4px;
      font-size: 11px;
    }}
    .stars {{ color: #ffce3d; letter-spacing: -1px; }}
    .star-empty {{ color: #ddd; }}
    .rating-num {{ color: #ee4d2d; font-weight: 600; }}
    .stats {{
      display: flex; gap: 10px; font-size: 10px; color: #999;
    }}
    .product-cta {{
      margin-top: 8px; padding: 6px 0; text-align: center;
      font-size: 11px; font-weight: 600; color: #fff;
      background: #ee4d2d; border-radius: 4px;
      transition: background 0.2s;
    }}
    .product-card:hover .product-cta {{ background: #d4411c; }}

    /* Footer */
    .footer {{
      max-width: 1200px; margin: 40px auto 0;
      padding: 24px 20px; text-align: center;
      color: #999; font-size: 12px;
      border-top: 1px solid #eee;
    }}

    /* Filter active state */
    .cat-pill.active {{ background: #ee4d2d; color: #fff; }}

    /* Scrollbar hide for cat nav */
    .scrollbar-hide::-webkit-scrollbar {{ display: none; }}
    .scrollbar-hide {{ -ms-overflow-style: none; scrollbar-width: none; }}
  </style>
</head>
<body>

<header class="header">
  <div class="header-inner">
    <a href="/" class="logo">MERAH JINGGA <span>Official</span></a>
  </div>
</header>

<section class="banner">
  <h1>🧴 MERAH JINGGA OFFICIAL 🧴</h1>
  <p>Produk Pilihan • Harga Terjangkau • Kualitas Terjamin</p>
</section>

<nav class="cat-nav">
  <div class="cat-nav-inner scrollbar-hide">
    <a href="#" class="cat-pill" onclick="filterAll(); return false;"><span class="cat-emoji">🔥</span><span>Semua</span></a>
    {cat_nav}
  </div>
</nav>

{sections}

<footer class="footer">
  <p>Merah Jingga Official — Shopee Affiliate</p>
  <p style="margin-top:4px">Data diperbarui: {fetched} • {total} produk</p>
  <p style="margin-top:8px;color:#bbb">Harga dan ketersediaan dapat berubah sewaktu-waktu di Shopee</p>
</footer>

<script>
  function filterAll() {{
    document.querySelectorAll('.category-section').forEach(s => s.style.display = '');
    document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
    document.querySelector('.cat-pill').classList.add('active');
  }}

  document.querySelectorAll('.cat-pill[href^="#"]').forEach(pill => {{
    pill.addEventListener('click', function(e) {{
      e.preventDefault();
      const cat = this.getAttribute('href').substring(1);
      document.querySelectorAll('.category-section').forEach(s => {{
        s.style.display = s.id === cat ? '' : 'none';
      }});
      document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
    }});
  }});

  // Lazy load images with fallback
  document.querySelectorAll('.product-img-wrap img').forEach(img => {{
    img.onerror = function() {{
      this.style.background = '#f5f5f5';
      this.style.objectFit = 'contain';
    }};
  }});
</script>

</body>
</html>'''

    with open(OUTPUT_HTML, "w") as f:
        f.write(html)

    print(f"✅ Generated: {OUTPUT_HTML}")
    print(f"   {total} products, {len([p for p in products if p.get('image_local')])} with images")

if __name__ == "__main__":
    main()
