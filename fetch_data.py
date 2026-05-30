#!/usr/bin/env python3
"""
Shopee Product Data Fetcher v3
All data from cloudscraper (og:image + embedded JSON). No browser needed.
"""
import json, os, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".openclaw/workspace/skills/captcha-bypass/venv/lib/python3.12/site-packages"))
import cloudscraper, requests

SCRIPT_DIR = Path(__file__).parent
PRODUCTS_JSON = SCRIPT_DIR / "products.json"
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_JSON = DATA_DIR / "products_data.json"
IMAGES_DIR = SCRIPT_DIR / "img" / "products"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def resolve_affiliate(short_url):
    try:
        resp = requests.head(short_url, allow_redirects=True, timeout=15,
                             headers={"User-Agent": "Mozilla/5.0 Chrome/146.0.0.0"})
        m = re.search(r'shopee\.co\.id/[^/]+/(\d{6,})/(\d{6,})', resp.url)
        if m: return int(m.group(1)), int(m.group(2))
        m = re.search(r'\.i\.(\d+)\.(\d+)', resp.url)
        if m: return int(m.group(1)), int(m.group(2))
        return None, None
    except Exception as e:
        print(f"  [!] Resolve failed: {e}")
        return None, None


def scrape_product(scraper, shop_id, item_id):
    """Get all data from product page HTML."""
    url = f"https://shopee.co.id/product/{shop_id}/{item_id}"
    try:
        resp = scraper.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"  [!] HTTP {resp.status_code}")
            return None
        text = resp.text
        result = {}

        # og:image
        m = re.search(r'og:image.*?content="([^"]+)"', text)
        if m: result["image_url"] = m.group(1)

        # Product name
        m = re.search(r'"name":"([^"]{10,200})"', text)
        if m and not any(x in m.group(1).lower() for x in ['tanstack', 'shopee_', 'react-query']):
            result["full_name"] = m.group(1)

        # Rating
        m = re.search(r'"rating_star":([\d.]+)', text)
        if m: result["rating"] = round(float(m.group(1)), 1)

        # Reviews (total from rating_count array)
        m = re.search(r'"rating_count":\[([^\]]+)\]', text)
        if m:
            counts = [int(x.strip()) for x in m.group(1).split(",")]
            result["reviews"] = sum(counts)

        # Comments
        m = re.search(r'"cmt_count":(\d+)', text)
        if m: result["comments"] = int(m.group(1))

        # Liked
        m = re.search(r'"liked_count":(\d+)', text)
        if m: result["liked"] = int(m.group(1))

        return result if result else None
    except Exception as e:
        print(f"  [!] Scrape failed: {e}")
        return None


def download_image(url, filename):
    local = IMAGES_DIR / filename
    if local.exists():
        return f"img/products/{filename}"
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 Chrome/146.0.0.0",
            "Referer": "https://shopee.co.id/"
        })
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(local, "wb") as f:
                f.write(resp.content)
            print(f"  📷 {filename} ({len(resp.content)//1024}KB)")
            return f"img/products/{filename}"
    except:
        pass
    return ""


def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}jt".replace(".0jt","jt")
    if n >= 1_000:
        v = n/1_000
        return f"{v:.1f}rb".replace(".0rb","rb") if v != int(v) else f"{int(v)}rb"
    return str(n)


def main():
    with open(PRODUCTS_JSON) as f:
        products = json.load(f)["products"]

    print(f"[*] Fetching {len(products)} products\n")
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "mobile": False})

    results = []
    for i, prod in enumerate(products, 1):
        print(f"[{i}/{len(products)}] {prod['short_name']}")

        shop_id, item_id = resolve_affiliate(prod["affiliate_link"])
        if not shop_id:
            print(f"  [!] Link resolve failed")
            results.append({**prod, "scraped": None, "image_local": ""})
            continue

        meta = scrape_product(scraper, shop_id, item_id)
        if meta:
            r = meta.get("rating", "?")
            c = fmt(meta.get("comments", 0))
            l = fmt(meta.get("liked", 0))
            print(f"  ⭐ {r} | 💬 {c} | ❤️ {l}")

            img_local = ""
            if meta.get("image_url"):
                img_local = download_image(meta["image_url"], f"{prod['id']:02d}_{prod['sub']}.jpg")

            results.append({
                **prod,
                "scraped": meta,
                "image_local": img_local,
                "shop_id": shop_id,
                "item_id": item_id,
            })
        else:
            print(f"  [!] Scrape failed")
            results.append({**prod, "scraped": None, "image_local": "", "shop_id": shop_id, "item_id": item_id})

        time.sleep(2)

    output = {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": len(results),
        "with_meta": sum(1 for r in results if r.get("scraped")),
        "with_image": sum(1 for r in results if r.get("image_local")),
        "products": results,
    }
    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"✅ Meta: {output['with_meta']}/{output['total']} | Images: {output['with_image']}/{output['total']}")
    print(f"📄 {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
