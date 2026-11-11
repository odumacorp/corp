"""Build the static homepage (loading/index.html) from docs/index.html.

The static site serves odumacorp.com instantly from Render's CDN, while the
Django app lives at app.odumacorp.com. Re-run after editing docs/index.html:

    python loading/build.py
"""
import re
from pathlib import Path

APP = 'https://app.odumacorp.com'
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'docs' / 'index.html'
OUT = ROOT / 'loading' / 'index.html'

URLS = {'index': '/', 'about': APP + '/about/', 'login': APP + '/login/',
        'register': APP + '/register/', 'project_list': APP + '/projects/'}

src = SRC.read_text()
block = lambda name: re.search(r'{%% block %s %%}(.*?){%% endblock %%}' % name, src, re.S).group(1)
head, body = block('extra_head'), block('content')
title = block('title').strip()
desc = block('meta_description').strip()

# Visitors on the static site are never logged in: keep the guest branch.
body = re.sub(r'{% if user\.is_authenticated %}((?:(?!{% if).)*?){% else %}((?:(?!{% if).)*?){% endif %}',
              r'\2', body, flags=re.S)

# Hero "latest opportunity" card.
body = re.sub(r'<div class="lp-hero__card-title">{% if featured_projects %}.*?{% endif %}</div>',
              '<div class="lp-hero__card-title" id="lp-latest-title">Projects seeking investment</div>', body)
body = re.sub(r'<div class="lp-hero__card-meta">{% if featured_projects %}.*?{% endif %}</div>',
              '<div class="lp-hero__card-meta" id="lp-latest-meta">Browse live opportunities</div>', body)

# Featured projects: keep the sample cards as the no-JS/offline fallback; JS swaps in live ones.
body = re.sub(r'{% if featured_projects %}.*?{% else %}\s*<div class="lp-projects">',
              '<div class="lp-projects" id="lp-projects">', body, count=1, flags=re.S)
body = re.sub(r'(Browse all projects &rarr;</a>\s*</div>)\s*{% endif %}', r'\1', body, count=1)

# Live counts are filled in from /api/public-stats/; never show made-up numbers.
for var, key in [('innovator_count', 'innovators'), ('investor_count', 'investors'), ('project_count', 'projects')]:
    body = re.sub(r'data-count="{{ %s }}">{{ %s }}\+' % (var, var), 'data-stat="%s">&ndash;' % key, body)
    body = body.replace('{{ %s }}+' % var, '<span data-stat="%s">&ndash;</span>' % key)
    body = body.replace('{{ %s }}' % var, '<span data-stat="%s">&ndash;</span>' % key)

body = re.sub(r"{% url '(\w+)' %}", lambda m: URLS[m.group(1)], body)
body = body.replace("{% static 'images/OdumaCorp-icon-small.png' %}", 'logo.png')
body = re.sub(r'<script>.*?</script>', '', body, flags=re.S)  # replaced by our script below

leftover = re.findall(r'{[%{].*?[%}]}', body + head)
assert not leftover, leftover

script = """<script>
(function () {
  var APP = '%(app)s';
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }

  function countUp(el, target) {
    var plus = el.classList.contains('lp-stats__val') ? '+' : '';
    if (!target) { el.textContent = target + plus; return; }
    var cur = 0, step = Math.max(1, Math.ceil(target / 40));
    var t = setInterval(function () { cur = Math.min(cur + step, target); el.textContent = cur + plus; if (cur >= target) clearInterval(t); }, 30);
  }

  function card(p) {
    var url = APP + '/projects/' + p.id + '/';
    var img = p.image ? '<img src="' + esc(p.image) + '" alt="' + esc(p.title) + '" class="lp-proj-img" loading="lazy">'
      : '<div class="lp-proj-img-placeholder"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></div>';
    var av = p.owner_avatar ? '<img src="' + esc(p.owner_avatar) + '" class="lp-proj-owner-av" alt="">'
      : '<div class="lp-proj-owner-av">' + esc(p.owner_initials) + '</div>';
    return '<div class="lp-proj-card">' + img + '<div class="lp-proj-body">' +
      '<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:8px;">' +
      (p.industry ? '<span class="lp-proj-industry">' + esc(p.industry) + '</span>' : '') +
      (p.stage ? '<span style="font-size:1.2rem;font-weight:700;padding:3px 9px;border-radius:100px;background:#fef3c7;color:#92400e;border:1px solid rgba(234,179,8,.15);">' + esc(p.stage) + '</span>' : '') +
      '</div><a href="' + url + '" class="lp-proj-title">' + esc(p.title) + '</a>' +
      '<p class="lp-proj-desc">' + esc(p.description) + '</p>' +
      (p.funding ? '<div style="display:flex;align-items:center;gap:6px;margin-top:auto;padding-top:8px;"><span style="font-size:1.2rem;font-weight:700;color:#059669;background:#d1fae5;padding:3px 10px;border-radius:100px;border:1px solid rgba(5,150,105,.15);">Seeking: ' + esc(p.funding) + '</span></div>' : '') +
      '</div><div class="lp-proj-footer"><a href="' + APP + '/profile/' + encodeURIComponent(p.owner_username) + '/" class="lp-proj-owner">' + av +
      '<span class="lp-proj-owner-name">' + esc(p.owner_name) + '</span></a>' +
      '<a href="' + url + '" class="lp-proj-arrow">View pitch &rarr;</a></div></div>';
  }

  /* One request both loads live data and wakes the app from Render's free-tier sleep,
     so "Log in" / "Create Project" are usually ready by the time someone clicks. */
  fetch(APP + '/api/public-stats/', { cache: 'no-store' })
    .then(function (r) { if (!r.ok) throw r; return r.json(); })
    .then(function (d) {
      document.querySelectorAll('[data-stat]').forEach(function (el) { countUp(el, d[el.dataset.stat] || 0); });
      if (d.featured && d.featured.length) {
        document.getElementById('lp-projects').innerHTML = d.featured.map(card).join('');
        var p = d.featured[0];
        document.getElementById('lp-latest-title').textContent = p.title.length > 40 ? p.title.slice(0, 39) + '\\u2026' : p.title;
        document.getElementById('lp-latest-meta').textContent = p.industry || '';
      }
    })
    .catch(function () { /* app still waking: keep placeholders */ });

  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var el = document.getElementById(this.getAttribute('href').slice(1));
      if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth', block: 'start' }); document.getElementById('lp-mob').classList.remove('open'); }
    });
  });
  var nav = document.querySelector('.lp-nav');
  window.addEventListener('scroll', function () { nav.style.boxShadow = window.scrollY > 10 ? '0 2px 24px rgba(0,0,0,.4)' : 'none'; }, { passive: true });

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) { entry.target.style.opacity = '1'; entry.target.style.transform = 'translateY(0)'; observer.unobserve(entry.target); }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.lp-step,.lp-testi,.lp-svc').forEach(function (el) {
    el.style.opacity = '0'; el.style.transform = 'translateY(24px)'; el.style.transition = 'opacity .5s ease, transform .5s ease';
    observer.observe(el);
  });
})();
</script>""" % {'app': APP}

page = f"""<!DOCTYPE html>
<!-- GENERATED by loading/build.py from docs/index.html. Edit the template, then re-run. -->
<html lang="en">
<head>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-11WRZ5D231"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-11WRZ5D231');</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="https://odumacorp.com/logo.png">
  <link rel="canonical" href="https://odumacorp.com/">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="preconnect" href="{APP}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* Base the template normally inherits from styles.css / design-system.css */
    html {{ font-size: 0.7em; scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }}
    body {{ font-family: 'Inter', system-ui, sans-serif; background: #fff; color: #0A1628; overflow-x: hidden; }}
    a {{ color: inherit; }}
    img {{ max-width: 100%; }}
  </style>
{head}
</head>
<body class="no-navbar">
<main>
{body}
</main>
{script}
</body>
</html>
"""
OUT.write_text(page)
print('wrote', OUT)
