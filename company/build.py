"""Build odumacorp.com from company/src/ and the data lists.

    python company/build.py

Pages are written to company/public/ (the folder Render publishes):
  index.html                    homepage (src/home.html): the founders-and-investors platform first
  products/index.html           every product
  products/<slug>/index.html    one page per product (src/product.html + optional src/products/*.html)
  gallery/index.html            event photos and videos (src/gallery.html + src/gallery.js)

Products are data: company/data/products.json. Add one entry (and its cover image in
public/img/products/) and it appears on the homepage showcase, /products/, the footer and its own page.

Gallery photos/videos and partner logos are NOT built here: admins add them in the app at
app.odumacorp.com/gallery/manage/ and app.odumacorp.com/partners/manage/. The homepage and
/gallery/ load them live (api/public-stats/, api/public-gallery/); the files are on Cloudinary.

It also makes the logo sizes, favicons and the 1200x630 share image (img/og.png)
from loading/logo.png the first time, and checks the page for leftovers.
"""
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PUB = HERE / 'public'          # the folder Render publishes
IMG = PUB / 'img'
OG_FONT = Path(sys.argv[1]) if len(sys.argv) > 1 else None   # optional DM Sans TTF, only for og.png
esc = lambda s: html.escape(str(s), quote=True)
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']


def icon(name, cls='i'):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


# ── Static assets made once from the round logo ─────────────────────────────
def assets():
    IMG.mkdir(exist_ok=True)
    logo = Image.open(ROOT / 'loading' / 'logo.png').convert('RGBA')
    side = max(logo.size)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(logo, ((side - logo.width) // 2, (side - logo.height) // 2))
    for size, name, fmt in ((96, 'logo-96.webp', 'WEBP'), (320, 'logo-320.webp', 'WEBP'),
                            (320, 'logo-320.png', 'PNG'), (32, 'favicon-32.png', 'PNG')):
        out = IMG / name
        if not out.exists():
            sq.resize((size, size), Image.LANCZOS).save(out, fmt, quality=88, method=6) if fmt == 'WEBP' \
                else sq.resize((size, size), Image.LANCZOS).save(out, fmt, optimize=True)
    touch = IMG / 'apple-touch-icon.png'
    if not touch.exists():
        bg = Image.new('RGBA', (180, 180), (251, 250, 247, 255))
        bg.alpha_composite(sq.resize((156, 156), Image.LANCZOS), (12, 12))
        bg.convert('RGB').save(touch, optimize=True)
    if not (IMG / 'og.png').exists():
        og(sq)
    for f in ('404.html',):
        if not (PUB / f).exists():
            shutil.copy(ROOT / 'loading' / f, PUB / f)


def og(logo):
    """1200x630 share card: brand, one line, and the basic-phone menu."""
    W, H = 1200, 630
    im = Image.new('RGB', (W, H))
    top, mid, bot = (0xEE, 0xF3, 0xFC), (0xF5, 0xF2, 0xEC), (0xFC, 0xEB, 0xD5)
    for y in range(H):   # diagonal-ish mist -> sand -> warm tint, like the hero
        t = y / H
        a, b, u = (top, mid, t / .55) if t < .55 else (mid, bot, (t - .55) / .45)
        ImageDraw.Draw(im).line([(0, y), (W, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3)))
    d = ImageDraw.Draw(im)

    def font(size, wght):
        if OG_FONT and OG_FONT.exists():
            f = ImageFont.truetype(str(OG_FONT), size)
            try:
                f.set_variation_by_axes([min(size, 40), wght])
            except Exception:
                pass
            return f
        return ImageFont.load_default(size)
    im.paste(logo.resize((110, 110), Image.LANCZOS), (80, 70), logo.resize((110, 110), Image.LANCZOS))
    d.text((210, 100), 'Oduma Corp', font=font(40, 700), fill=(0x0F, 0x1B, 0x33))
    big = font(72, 700)
    for i, line in enumerate(['Put your project', 'in front of investors.']):
        d.text((80, 220 + i * 84), line, font=big, fill=(0x0F, 0x1B, 0x33) if i == 0 else (0x1F, 0x6F, 0xEB))
    body = font(32, 400)
    d.text((82, 412), 'Founders list projects. Investors find them,', font=body, fill=(0x4A, 0x55, 0x68))
    d.text((82, 456), 'send proposals and book meetings.', font=body, fill=(0x4A, 0x55, 0x68))
    d.rounded_rectangle((80, 528, 500, 586), 29, fill=(0x1F, 0x6F, 0xEB))
    d.text((112, 540), 'Free to join · odumacorp.com', font=font(26, 700), fill=(255, 255, 255))
    # proposal card
    cx, cy = 790, 150
    d.rounded_rectangle((cx, cy, cx + 340, cy + 330), 26, fill=(255, 255, 254), outline=(0xE2, 0xE6, 0xEE), width=2)
    d.text((cx + 26, cy + 24), 'New proposal', font=font(26, 700), fill=(0x0F, 0x1B, 0x33))
    d.rounded_rectangle((cx + 26, cy + 72, cx + 314, cy + 170), 16, fill=(0xEE, 0xF3, 0xFC))
    d.text((cx + 44, cy + 86), 'KSh 1M for 8% equity.', font=font(22, 600), fill=(0x0F, 0x1B, 0x33))
    d.text((cx + 44, cy + 120), 'Can we meet Thursday?', font=font(22, 400), fill=(0x4A, 0x55, 0x68))
    for j, (lbl, fill_, fg) in enumerate([('Accept', (0x1F, 0x6F, 0xEB), (255, 255, 255)), ('Reply', (255, 255, 254), (0x0F, 0x1B, 0x33))]):
        x0 = cx + 26 + j * 150
        d.rounded_rectangle((x0, cy + 200, x0 + 138, cy + 252), 26, fill=fill_, outline=(0xCB, 0xD3, 0xE1), width=2)
        d.text((x0 + 30 + (8 if j else 0), cy + 212), lbl, font=font(22, 700), fill=fg)
    d.text((cx + 26, cy + 280), 'Example', font=font(18, 700), fill=(0x7A, 0x43, 0x00))
    im.save(IMG / 'og.png', optimize=True)


# ── Partner logos ────────────────────────────────────────────────────────────
# ── Event photos ─────────────────────────────────────────────────────────────
SITE = 'https://odumacorp.com'
SRC = HERE / 'src'
PRODUCTS = json.loads((HERE / 'data' / 'products.json').read_text())['products']
INDUSTRIES = [('all', 'All projects', 'globe'), ('tech', 'Technology', 'cpu'), ('telecom', 'Telecommunications', 'phone'),
              ('finance', 'Finance', 'wallet'), ('health', 'Healthcare', 'heart'), ('edu', 'Education', 'book'),
              ('energy', 'Energy', 'bolt'), ('agriculture', 'Agriculture', 'leaf'), ('manufacturing', 'Manufacturing', 'gear')]
NAV_HOME = [('/#how', 'How it works'), ('/#for-you', 'For you'), ('/#projects', 'Projects'),
            ('/#products', 'Products'), ('/#services', 'Services'), ('/#about', 'About')]
ORG = {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Oduma Corp', 'url': SITE + '/',
       'logo': SITE + '/img/logo-320.png', 'email': 'odumacorp@gmail.com', 'telephone': '+254182759166',
       'address': {'@type': 'PostalAddress', 'addressLocality': 'Nairobi', 'addressCountry': 'KE'},
       'sameAs': ['https://www.linkedin.com/company/oduma-corp/', 'https://www.instagram.com/odumacorpltd']}


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace('{{' + k + '}}', v)
    left = re.findall(r'{{[A-Z_]+}}', tpl)
    assert not left, f'unfilled: {left}'
    return tpl


def cover(prod, width=None):
    """640 and 1200px WebP copies of a product cover; returns the <img>."""
    src = IMG / 'products' / prod['cover']
    assert src.exists(), f'missing cover image: {src}'
    out = IMG / 'products' / '_web'
    out.mkdir(exist_ok=True)
    im = Image.open(src).convert('RGB')
    sizes = {}
    for w in (640, 1200):
        f = out / f'{prod["slug"]}-{w}.webp'
        cp = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        if not f.exists() or f.stat().st_mtime < src.stat().st_mtime:
            cp.save(f, 'WEBP', quality=80, method=6)
        sizes[w] = cp.size
    (w6, h6) = sizes[640]
    base = f'/img/products/_web/{prod["slug"]}'
    return (f'<img src="{base}-640.webp" srcset="{base}-640.webp {sizes[640][0]}w, {base}-1200.webp {sizes[1200][0]}w" '
            f'sizes="{width or "(max-width:700px) 92vw, 380px"}" width="{w6}" height="{h6}" alt="" loading="lazy" decoding="async">')


def product_card(p, i):
    url = f'/products/{p["slug"]}/'
    links = f'<a href="{url}">View product {icon("arrow")}</a>'
    if p.get('try_label'):
        links += f'<a href="{url}#try">{esc(p["try_label"])}</a>'
    status = f'<span class="live">{esc(p["status"])}</span>' if p.get('status') else ''
    return (f'<article class="prod rv" style="--d:{min(i, 4) * .08:.2f}s"><div class="prod-cover">{cover(p)}</div><div class="prod-body">'
            f'<div class="prod-meta">{status}<span>{esc(p["category"])}</span></div>'
            f'<h3><a href="{url}">{esc(p["name"])}</a></h3><p>{esc(p["tagline"])}</p>'
            f'<div class="prod-links">{links}</div></div></article>')


def next_card(i):
    return (f'<article class="prod prod-next rv" style="--d:{min(i, 4) * .08:.2f}s"><div><span class="ico">{icon("bulb")}</span>'
            '<h3>Building something?</h3><p>List your project on Oduma Corp and put it in front of investors.</p>'
            '<a class="btn btn-ghost" href="https://app.odumacorp.com/register/?role=innovator&amp;next=/projects/create/">List your project</a></div></article>')


def products_grid():
    return '\n'.join(product_card(p, i) for i, p in enumerate(PRODUCTS)) + '\n' + next_card(len(PRODUCTS))


def nav(items):
    return '\n'.join(f'      <a href="{h}">{t}</a>' for h, t in items)


def page(path, title, desc, content, js_extra='', og='/img/og.png', og_alt='Oduma Corp: put your project in front of investors', jsonld=None):
    assert len(title) <= 70, ('title too long', title)
    css = (SRC / 'site.css').read_text()
    js = (SRC / 'site.js').read_text() + js_extra
    html = fill((SRC / 'base.html').read_text(), TITLE=esc(title), DESC=esc(desc), PATH=path, OG=og, OG_ALT=esc(og_alt),
                JSONLD=json.dumps(jsonld or ORG, separators=(',', ':')), CSS=css, SPRITE=(SRC / 'sprite.svg').read_text(),
                NAV=nav(NAV_HOME), CONTENT=content, JS=js, YEAR=str(datetime.date.today().year), AFTER=LIGHTBOX if 'id="gp-groups"' in content else '',
                FOOTER_PRODUCTS='\n'.join(f'          <li><a href="/products/{p["slug"]}/">{esc(p["name"])}</a></li>' for p in PRODUCTS))
    typed = ''.join(f'<span style="animation-delay:{0.25 + i * 0.14:.2f}s">{c}</span>' for i, c in enumerate('*384*88041#'))
    html = html.replace('<!--@TYPED-->', typed)
    assert 'tel:*384*88041#' not in html, 'encode # as %23 in tel: links'
    assert 'id="top"' not in html, '"Back to top" relies on there being no id="top"'
    for ref in set(re.findall(r'(?:src|href)="(/(?:img|fonts|images)/[^"]+)"', html)):
        assert (PUB / ref.lstrip('/')).exists(), f'missing file for {ref}'
    for ref in set(re.findall(r'href="(/products/[^"#]*)', html)):
        slug = ref.strip('/').split('/')[1:] or ['']
        assert ref == '/products/' or any(p['slug'] == slug[0] for p in PRODUCTS), f'link to unknown product {ref}'
    out = PUB / path.lstrip('/') / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f'wrote {out.relative_to(ROOT)} ({len(html.encode()) // 1024} KB)')
    return html


LIGHTBOX = """<dialog class="lb" id="lb" aria-label="Gallery viewer">
  <div class="lb-bar"><span class="lb-count" id="lb-count"></span><button type="button" data-lb="close" aria-label="Close"><svg class="i" aria-hidden="true" focusable="false"><use href="#i-x"/></svg></button></div>
  <figure class="lb-fig" id="lb-fig"><figcaption id="lb-cap"></figcaption></figure>
  <div><button type="button" class="lb-nav lb-prev" data-lb="prev" aria-label="Previous photo"><svg class="i" aria-hidden="true" focusable="false"><use href="#i-left"/></svg></button><button type="button" class="lb-nav lb-next" data-lb="next" aria-label="Next photo"><svg class="i" aria-hidden="true" focusable="false"><use href="#i-right"/></svg></button></div>
</dialog>"""


def home():
    inds = '\n'.join(f'      <a class="ind-tile" data-ind="{k}" href="https://app.odumacorp.com/projects/{"" if k == "all" else "?industry=" + k}">'
                     f'{icon(ic)}{n}<small>Browse</small></a>' for k, n, ic in INDUSTRIES)
    content = fill((SRC / 'home.html').read_text(), INDUSTRIES=inds, PRODUCT_CARDS=products_grid(),
)
    return page('/', 'Oduma Corp: connect African founders with investors',
                'Publish your project and get proposals from angel investors, or browse early-stage African projects to back. '
                'Free to join. Based in Nairobi, Kenya.', content)


def gallery_page():
    """/gallery/: admin-posted photos and videos, loaded from the app's public feed (src/gallery.js)."""
    return page('/gallery/', 'Gallery | Oduma Corp',
                'Photos and videos from pitch events, meetups and expos Oduma Corp has taken part in.',
                (SRC / 'gallery.html').read_text(), js_extra=(SRC / 'gallery.js').read_text())


def products_index():
    content = f"""<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap"><ol><li><a href="/">Home</a></li><li aria-current="page">Products</li></ol></div></nav>
<section class="page-hero" aria-labelledby="h-all">
  <div class="wrap">
    <span class="eyebrow">Built by Oduma Corp</span>
    <h1 id="h-all">Our products</h1>
    <p class="lead">Besides the platform that connects founders and investors, our team builds and runs products of its own. Open one to see how it works and try it.</p>
  </div>
</section>
<section aria-labelledby="h-list">
  <div class="wrap"><h2 class="sr" id="h-list">All products</h2><div class="prods">
{products_grid()}
  </div></div>
</section>"""
    return page('/products/', 'Products by Oduma Corp', 'Products built and run by Oduma Corp in Nairobi, Kenya, including Remote Phonebook.', content)


def product_page(p):
    btns = '\n'.join(f'        <a class="btn btn-{b.get("style", "solid")}" href="{esc(b["url"])}">{esc(b["label"])}</a>' for b in p.get('buttons', []))
    art = (SRC / 'products' / p['art']).read_text() if p.get('art') else \
        f'    <figure class="prod-art">{cover(p, "(max-width:860px) 92vw, 520px")}</figure>'
    feats = '\n'.join(f'      <article class="card lift rv" style="--d:{i * .08:.2f}s"><div class="ico">{icon(f.get("icon", "check"))}</div>'
                      f'<h3>{esc(f["title"])}</h3><p>{esc(f["text"])}</p></article>' for i, f in enumerate(p.get('features', [])))
    extra = (SRC / 'products' / p['extra']).read_text() if p.get('extra') else ''
    others = [o for o in PRODUCTS if o is not p]
    other = ''
    if others:
        other = ('<section class="mist" aria-labelledby="h-other"><div class="wrap"><div class="sec-head rv"><span class="eyebrow">More from Oduma Corp</span>'
                 '<h2 id="h-other">Other products</h2></div><div class="prods">' + ''.join(product_card(o, i) for i, o in enumerate(others)) + '</div></div></section>')
    content = fill((SRC / 'product.html').read_text(), NAME=esc(p['name']), CATEGORY=esc(p['category']), SUMMARY=esc(p['summary']),
                   HERO_BUTTONS=btns, HERO_EXTRA=p.get('hero_extra', ''), ART=art, FEATURES_TITLE=esc(p.get('features_title', 'Features')),
                   FEATURES=feats, EXTRA=extra, OTHER=other)
    ld = {'@context': 'https://schema.org', '@type': 'SoftwareApplication', 'name': p['name'], 'applicationCategory': p['category'],
          'operatingSystem': 'Any', 'url': SITE + f'/products/{p["slug"]}/', 'description': p['summary'],
          'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'KES'}, 'publisher': ORG}
    if p.get('website'):
        ld['sameAs'] = [p['website']]
    js = (SRC / 'sim.js').read_text() if p.get('demo') else ''
    og = f'/img/og-{p["slug"]}.png'
    return page(f'/products/{p["slug"]}/', f'{p["name"]}: a product by Oduma Corp', p['tagline'], content, js_extra=js,
                og=og if (PUB / og.lstrip('/')).exists() else '/img/og.png', og_alt=f'{p["name"]} by Oduma Corp', jsonld=ld)


def main():
    assets()
    for f in ('cohort-480.avif', 'cohort-800.avif', 'cohort-1200.avif', 'cohort-480.webp', 'cohort-800.webp', 'cohort-1200.webp'):
        if not (IMG / f).exists():
            shutil.copy(ROOT / 'loading' / 'img' / f, IMG / f)
    seen = set()
    for p in PRODUCTS:
        for k in ('slug', 'name', 'category', 'tagline', 'summary', 'cover'):
            assert p.get(k), f'products.json: "{k}" is required ({p.get("name")})'
        assert re.fullmatch(r'[a-z0-9-]+', p['slug']) and p['slug'] not in seen, f'bad or repeated slug {p["slug"]}'
        seen.add(p['slug'])
    pages = [home(), products_index(), gallery_page()] + [product_page(p) for p in PRODUCTS]
    # remove pages of products that were taken out of the list
    for d in (PUB / 'products').iterdir():
        if d.is_dir() and d.name not in seen and (d / 'index.html').exists():
            shutil.rmtree(d)
            print('removed', d.relative_to(ROOT))
    copy = sum(h.count(' data-ex') for h in pages)
    if copy:
        print(f'NOTE: {copy} example text block(s) marked data-ex in src/ are still on the site.')


if __name__ == '__main__':
    main()
