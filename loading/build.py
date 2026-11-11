"""Build the static homepage (loading/index.html) from docs/index.html.

The static site serves odumacorp.com instantly from Render's CDN, while the
Django app lives at app.odumacorp.com. Re-run after editing docs/index.html:

    python loading/build.py

What the static page adds on top of the template (the app's base.html provides
these on app.odumacorp.com/, so they are not in the template itself):
  * the <head>: meta, Open Graph/Twitter, canonical, JSON-LD, self-hosted fonts
  * a cookie notice; Google Analytics loads only after "Accept"
  * the Feedback button, its "Toggle widgets" tab and form (posts to the app)
  * the script that loads live counts/projects and wakes the sleeping app
"""
import datetime
import json
import re
from pathlib import Path

APP = 'https://app.odumacorp.com'
SITE = 'https://odumacorp.com'
GA_ID = 'G-11WRZ5D231'
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'docs' / 'index.html'
OUT = ROOT / 'loading' / 'index.html'

URLS = {'index': '/', 'about': APP + '/about/', 'login': APP + '/login/',
        'register': APP + '/register/', 'project_list': APP + '/projects/',
        'privacy_policy': APP + '/privacy/', 'terms': APP + '/terms/',
        'contact': APP + '/contact/'}

src = SRC.read_text()
# One source of truth for colours, shadows and gradients: the app's design-system.css :root block.
TOKENS = re.search(r'^:root\s*{.*?^}', (ROOT / 'core' / 'static' / 'css' / 'design-system.css').read_text(), re.S | re.M).group(0)
block = lambda name: re.search(r'{%% block %s %%}(.*?){%% endblock %%}' % name, src, re.S).group(1)
head, body = block('extra_head'), block('content')
title = block('title').strip()
desc = block('meta_description').strip()
assert len(title) <= 60, ('title too long', len(title))


def sub1(pattern, repl, text, flags=re.S):
    """re.sub that fails loudly when the template markup it relies on has changed."""
    new, n = re.subn(pattern, repl, text, flags=flags)
    assert n, 'pattern not found in docs/index.html: ' + pattern
    return new


# Visitors on the static site are never logged in: keep the guest branch.
body = re.sub(r'{% if user\.is_authenticated %}((?:(?!{% if).)*?){% else %}((?:(?!{% if).)*?){% endif %}',
              r'\2', body, flags=re.S)

# One-line data branches ({% if featured_projects... %}, {% if industry_counts.x %}, {% if all_projects_count %}):
# keep the fallback text. Industry tiles are the exception: the static page shows them all
# neutrally ("Browse") until the feed says which ones have projects.
SIMPLE = r'{%% if (%s)(?:\.[\w.]+)? %%}((?:(?!{%%).)*?){%% else %%}((?:(?!{%%).)*?){%% endif %%}'
body = sub1(SIMPLE % 'industry_counts', lambda m: '' if m.group(3).strip() == 'hidden' else m.group(3), body)
body = sub1(SIMPLE % 'featured_projects|all_projects_count', r'\3', body)
# Guest-only notes stay (static visitors are never logged in).
body = re.sub(r'{% if not user\.is_authenticated %}((?:(?!{%).)*?){% endif %}', r'\1', body, flags=re.S)
# Featured projects: keep the empty state + example card; the script swaps in live cards.
body = sub1(r'{% if featured_projects %}(?:(?!{% if featured_projects %}).)*?{% else %}<!-- empty -->', '', body)
body = sub1(r'<!-- /empty -->{% endif %}', '', body)

# Live counts come from /api/public-stats/. Until they arrive the line stays empty
# (its height is reserved in CSS), so nothing shifts and no "–" is ever shown.
body = sub1(r'<span class="lp-cohort__n" id="lp-cohort-n">.*?</span>',
            '<span class="lp-cohort__n" id="lp-cohort-n"></span>', body)

body = re.sub(r"{% url '(\w+)' %}", lambda m: URLS[m.group(1)], body)
body = sub1(r"{% static 'images/OdumaCorp-icon-small.png' %}", 'icon-72.png', body)
# Photos: the app serves them from core/static/images/home/, the static site from loading/img/.
body = sub1(r"{% static 'images/home/([\w.-]+)' %}", lambda m: 'img/' + m.group(1), body)
for f in re.findall(r'img/([\w.-]+\.(?:avif|webp|jpg))', body):
    assert (ROOT / 'loading' / 'img' / f).exists(), 'missing loading/img/' + f
body = sub1(r'{% now "Y" %}', str(datetime.date.today().year), body)
body = re.sub(r'<script>.*?</script>', '', body, flags=re.S)  # template-only scripts
body = body.replace('<script data-keep>', '<script>')          # shared scripts stay

# Proper landmarks on the static page (the app's base.html already wraps everything in <main>).
body = sub1(r'<div class="lp-main" id="main" tabindex="-1">', '<main class="lp-main" id="main" tabindex="-1">', body)
body = sub1(r'</div><!-- /lp-main -->', '</main>', body)

leftover = re.findall(r'{[%{].*?[%}]}', body + head)
assert not leftover, leftover
for needed in ('id="lp-projects"', 'id="lp-latest-title"', 'id="lp-latest-meta"', 'id="lp-mob"',
               'id="how-it-works"', 'id="for-you"', 'id="projects"', 'id="services"'):
    assert needed in body, 'missing ' + needed

org = {
    '@context': 'https://schema.org', '@type': 'Organization',
    'name': 'Oduma Corp', 'url': SITE + '/', 'logo': SITE + '/logo.png',
    'email': 'info@odumacorp.com',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Nairobi', 'addressCountry': 'KE'},
    'sameAs': ['https://www.linkedin.com/company/oduma-corp/', 'https://www.instagram.com/odumacorpltd'],
}

extras = """
<div class="sx-consent" id="sx-consent" role="region" aria-label="Cookie choice" hidden>
  <p>May we use Google Analytics cookies to count visits and see which parts of this page people use? The page works the same either way. <a href="%(app)s/privacy/#cookies">Cookies in our Privacy Policy</a></p>
  <div class="sx-consent__btns">
    <button type="button" class="sx-btn" data-consent="denied">Reject</button>
    <button type="button" class="sx-btn" data-consent="granted">Accept</button>
  </div>
</div>

<button type="button" class="sx-fb-btn" id="oc-feedback-btn" aria-haspopup="dialog" aria-controls="sx-fb">Feedback</button>
<button type="button" class="sx-dock-tab oc-tab-hidden" id="oc-dock-tab" title="Toggle widgets" aria-label="Toggle widgets">
  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 18 9 12 15 6"/></svg>
</button>
<dialog class="sx-fb" id="sx-fb" aria-labelledby="sx-fb-title">
  <form id="sx-fb-form" novalidate>
    <div class="sx-fb__head">
      <h2 id="sx-fb-title">Share your feedback</h2>
      <button type="button" class="sx-fb__x" data-close aria-label="Close">&times;</button>
    </div>
    <div class="sx-fb__row">
      <div>
        <label for="sx-fb-type">Type</label>
        <select id="sx-fb-type" name="feedback_type">
          <option value="suggestion">Suggestion</option><option value="bug">Bug / Issue</option>
          <option value="praise">Praise</option><option value="question">Question</option><option value="other">Other</option>
        </select>
      </div>
      <div>
        <label for="sx-fb-page">Page</label>
        <input id="sx-fb-page" name="page" type="text" maxlength="100" placeholder="Current page">
      </div>
    </div>
    <label for="sx-fb-section">Section <span>(optional)</span></label>
    <select id="sx-fb-section" name="section">
      <option value="">Whole page</option><option value="navbar">Navigation bar</option><option value="hero">Top of page</option>
      <option value="how-it-works">How it works</option><option value="for-you">For you</option><option value="projects">Projects</option>
      <option value="services">Services</option><option value="footer">Footer</option><option value="other">Other</option>
    </select>
    <label for="sx-fb-text">Your message</label>
    <textarea id="sx-fb-text" name="feedback_text" rows="4" maxlength="5000" required placeholder="Tell us what you think"></textarea>
    <div class="sx-hp" aria-hidden="true"><label for="sx-fb-web">Leave this empty</label><input id="sx-fb-web" name="website" tabindex="-1" autocomplete="off"></div>
    <p class="sx-fb__status" id="sx-fb-status" role="status"></p>
    <div class="sx-fb__btns">
      <button type="submit" class="sx-btn sx-btn--p" id="sx-fb-send">Send feedback</button>
      <button type="button" class="sx-btn" data-close>Cancel</button>
    </div>
  </form>
</dialog>
<p class="sx-toast" id="sx-toast" role="status" aria-live="polite"></p>
""" % {'app': APP}

extras_css = """
  .sx-btn{min-height:44px;padding:10px 18px;border-radius:8px;border:2px solid #9AA8BB;background:#fff;color:#0A1628;font:600 15px 'Inter',system-ui,sans-serif;cursor:pointer;}
  .sx-btn--p{background:#1B5EC7;border-color:#1B5EC7;color:#fff;}
  .sx-btn:focus-visible,.sx-fb-btn:focus-visible,.sx-dock-tab:focus-visible,.sx-fb :focus-visible{outline:3px solid #1B5EC7;outline-offset:2px;}
  .sx-consent{font-family:'Inter',system-ui,sans-serif;line-height:1.5;position:fixed;left:0;right:0;bottom:0;z-index:1500;background:#fff;color:#334155;border-top:1px solid #DCE2EA;box-shadow:0 -4px 20px rgba(10,22,40,.12);padding:14px 16px;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:12px 20px;font-size:15px;}
  .sx-consent[hidden]{display:none;}
  .sx-consent p{margin:0;max-width:44em;}
  .sx-consent a{color:#1B5EC7;text-decoration:underline;}
  .sx-consent__btns{display:flex;gap:10px;}
  .sx-consent__btns .sx-btn{min-width:110px;}
  .sx-fb-btn{position:fixed;right:16px;bottom:calc(var(--sx-bottom,0px) + 16px);z-index:1400;min-height:44px;padding:0 18px;border-radius:22px;border:1px solid #DCE2EA;background:#fff;color:#0A1628;font:600 15px 'Inter',system-ui,sans-serif;box-shadow:0 4px 14px rgba(10,22,40,.18);cursor:pointer;transition:transform .3s,opacity .3s;}
  .sx-fb-btn.oc-docked{transform:translateX(calc(100% + 24px));opacity:0;pointer-events:none;}
  .sx-dock-tab{position:fixed;right:0;bottom:calc(var(--sx-bottom,0px) + 16px);z-index:1400;width:28px;height:44px;border:0;border-radius:8px 0 0 8px;background:#1B5EC7;color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:transform .3s,opacity .3s;}
  .sx-dock-tab.oc-tab-hidden{transform:translateX(120%);opacity:0;pointer-events:none;}
  .sx-fb{width:min(460px,calc(100% - 32px));border:0;border-radius:12px;padding:20px;color:#334155;box-shadow:0 20px 60px rgba(10,22,40,.35);font:15px/1.5 'Inter',system-ui,sans-serif;}
  .sx-fb::backdrop{background:rgba(10,22,40,.55);}
  .sx-fb__head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}
  .sx-fb h2{margin:0;font:700 19px 'Space Grotesk',system-ui,sans-serif;color:#0A1628;}
  .sx-fb__x{width:44px;height:44px;border:0;background:none;font-size:26px;line-height:1;color:#526075;cursor:pointer;}
  .sx-fb label{display:block;margin:10px 0 4px;font-weight:600;color:#0A1628;font-size:14px;}
  .sx-fb label span{font-weight:400;color:#526075;}
  .sx-fb input,.sx-fb select,.sx-fb textarea{width:100%;min-height:44px;padding:8px 10px;border:1px solid #9AA8BB;border-radius:8px;font:inherit;color:#0A1628;background:#fff;}
  .sx-fb__row{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
  .sx-fb__row label{margin-top:0;}
  .sx-fb__btns{display:flex;gap:10px;margin-top:14px;}
  .sx-fb__status{min-height:1.5em;margin:10px 0 0;font-size:14px;}
  .sx-fb__status.is-err{color:#A12020;}
  .sx-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden;}
  .sx-toast{position:fixed;left:50%;top:76px;transform:translateX(-50%);z-index:1600;margin:0;max-width:calc(100% - 32px);background:#0A1628;color:#fff;border:1px solid #3A4D6B;padding:10px 16px;border-radius:8px;font-size:15px;display:none;}
  .sx-toast.show{display:block;}
  @media(prefers-reduced-motion:reduce){.sx-fb-btn,.sx-dock-tab{transition:none;}}
"""

script = """<script>
(function () {
  var APP = '%(app)s', GA = '%(ga)s';
  function $(id) { return document.getElementById(id); }
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function abs(u) { return u && u.charAt(0) === '/' ? APP + u : u; }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function plural(n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); }
  var yr = $('lp-year'); if (yr) yr.textContent = new Date().getFullYear();

  /* ── Toast ── */
  var toastT;
  function toast(msg) { var t = $('sx-toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('show'); }, 6000); }

  /* ── Live data. The same request wakes the app from Render's free-tier sleep. ── */
  var awake = false;
  var LAYERS = '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>';
  function card(p) {
    var url = APP + '/projects/' + p.id + '/';
    var media = p.image ? '<img src="' + esc(abs(p.image)) + '" alt="" class="lp-proj-img" width="640" height="360" loading="lazy" decoding="async">' : LAYERS;
    var av = p.owner_avatar ? '<img src="' + esc(abs(p.owner_avatar)) + '" class="lp-proj-owner-av" alt="" width="28" height="28" loading="lazy">'
      : '<span class="lp-proj-owner-av" aria-hidden="true">' + esc(p.owner_initials) + '</span>';
    return '<article class="lp-card lp-card--hover lp-proj-card"><div class="lp-proj-media">' + media + '</div><div class="lp-proj-body"><div class="lp-proj-tags">' +
      (p.industry ? '<span class="lp-pill">' + esc(p.industry_label || p.industry) + '</span>' : '') +
      (p.stage ? '<span class="lp-pill lp-pill--stage">' + esc(p.stage) + '</span>' : '') +
      '</div><h3><a href="' + url + '" class="lp-proj-title">' + esc(p.title) + '</a></h3>' +
      '<p class="lp-proj-desc">' + esc(p.description) + '</p>' +
      (p.funding ? '<p class="lp-proj-ask">Seeking: ' + esc(p.funding) + '</p>' : '') +
      '</div><div class="lp-proj-footer"><a href="' + APP + '/profile/' + encodeURIComponent(p.owner_username) + '/" class="lp-proj-owner">' + av +
      '<span class="lp-proj-owner-name">' + esc(p.owner_name) + '</span></a>' +
      '<a href="' + url + '" class="lp-proj-arrow">View pitch &rarr;</a></div></article>';
  }
  function text(id, v) { var el = $(id); if (el) { el.textContent = v || ''; el.hidden = !v; } }
  function hero(p) {
    /* Same slots and sizes as the fallback card, so swapping in live data never shifts the layout. */
    $('lp-latest-thumb').innerHTML = p.image ? '<img src="' + esc(abs(p.image)) + '" alt="" width="460" height="120">' : LAYERS;
    $('lp-latest-title').textContent = p.title;
    $('lp-latest-desc').textContent = p.description || '';
    $('lp-latest-meta').textContent = p.owner_name;
    $('lp-latest-av').textContent = p.owner_initials;
    text('lp-latest-ind', p.industry_label || p.industry || 'Project');
    text('lp-latest-stage', p.stage);
    text('lp-latest-ask', p.funding ? 'Seeking ' + p.funding : '');
  }
  function tiles(d) {
    var counts = d.industry_counts || {};
    document.querySelectorAll('#lp-tiles [data-ind]').forEach(function (t) {
      var k = t.getAttribute('data-ind'), n = k === 'all' ? +d.all_projects || 0 : +counts[k] || 0;
      if (k !== 'all') t.hidden = !n;
      if (n) t.querySelector('.lp-tile__n').textContent = plural(n, 'project');
    });
  }
  var ctl = window.AbortController ? new AbortController() : null;
  var stop = setTimeout(function () { if (ctl) ctl.abort(); }, 90000);
  fetch(APP + '/api/public-stats/', { cache: 'no-store', signal: ctl ? ctl.signal : undefined })
    .then(function (r) { if (!r.ok) throw r; return r.json(); })
    .then(function (d) {
      awake = true; clearTimeout(stop);
      var i = +d.innovators || 0, v = +d.investors || 0;
      if (i || v) $('lp-cohort-n').textContent = plural(i, 'innovator') + ' and ' + plural(v, 'investor') + ' so far.';
      if (d.industry_counts) tiles(d);
      if (d.featured && d.featured.length) {
        var grid = $('lp-projects');
        grid.innerHTML = d.featured.map(card).join('');
        if (window.lpReveal) window.lpReveal(grid);
        hero(d.featured[0]);
      }
    })
    .catch(function () { /* app still asleep or unreachable: the page already reads complete without numbers */ });

  /* ── Links into the app: say so if it is still waking; ignore repeat clicks. ── */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="' + APP + '"]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
    if (a.classList.contains('is-busy')) { e.preventDefault(); return; }
    a.classList.add('is-busy'); a.setAttribute('aria-busy', 'true');
    if (!awake) toast('Opening the app. This can take up to a minute if nobody has visited recently.');
    setTimeout(function () { a.classList.remove('is-busy'); a.removeAttribute('aria-busy'); }, 8000);
  });
  window.addEventListener('pageshow', function () {
    document.querySelectorAll('a.is-busy').forEach(function (a) { a.classList.remove('is-busy'); a.removeAttribute('aria-busy'); });
  });

  /* ── Cookie choice. Google Analytics loads only after Accept. ── */
  var banner = $('sx-consent'), settings = $('lp-cookie-settings');
  function bottom() { document.documentElement.style.setProperty('--sx-bottom', banner.hidden ? '0px' : banner.offsetHeight + 'px'); }
  function loadGA() {
    if (window.__ga) return; window.__ga = 1;
    window.dataLayer = window.dataLayer || []; window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date()); gtag('config', GA);
    var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA; document.head.appendChild(s);
  }
  function clearGA() {
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim();
      if (/^_ga/.test(n)) ['', '; domain=' + location.hostname, '; domain=.' + location.hostname.replace(/^www\\./, '')].forEach(function (d) {
        document.cookie = n + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + d;
      });
    });
  }
  var choice = store('lp-consent');
  if (choice === 'granted') loadGA(); else if (choice !== 'denied') banner.hidden = false;
  settings.hidden = false;
  settings.addEventListener('click', function () { banner.hidden = false; bottom(); banner.querySelector('button').focus(); });
  banner.addEventListener('click', function (e) {
    var b = e.target.closest('[data-consent]'); if (!b) return;
    var val = b.getAttribute('data-consent'), was = store('lp-consent');
    store('lp-consent', val); banner.hidden = true; bottom();
    if (val === 'granted') loadGA(); else { clearGA(); if (was === 'granted') location.reload(); }
  });
  bottom(); window.addEventListener('resize', bottom);

  /* ── Feedback button + "Toggle widgets" tab (same behaviour as the app: hides after 5 s). ── */
  var fbBtn = $('oc-feedback-btn'), tab = $('oc-dock-tab'), dlg = $('sx-fb'), form = $('sx-fb-form'),
      status = $('sx-fb-status'), send = $('sx-fb-send'), dockT;
  function dock(h) { fbBtn.classList.toggle('oc-docked', h); tab.classList.toggle('oc-tab-hidden', !h); }
  function peek() { clearTimeout(dockT); dock(false); dockT = setTimeout(function () { if (!dlg.open && document.activeElement !== fbBtn) dock(true); }, 5000); }
  peek();
  tab.addEventListener('click', function () { peek(); fbBtn.focus(); });
  fbBtn.addEventListener('blur', peek);
  fbBtn.addEventListener('click', function () {
    $('sx-fb-page').value = location.pathname; status.textContent = ''; status.className = 'sx-fb__status';
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    $('sx-fb-text').focus();
  });
  dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target.closest('[data-close]')) dlg.close(); });
  dlg.addEventListener('close', function () { fbBtn.focus(); });
  var sending = false;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (sending) return;
    var text = $('sx-fb-text');
    if (!text.value.trim()) { status.textContent = 'Please write a message first.'; status.className = 'sx-fb__status is-err'; text.focus(); return; }
    sending = true; send.disabled = true; send.textContent = 'Sending…';
    status.className = 'sx-fb__status';
    status.textContent = awake ? '' : 'Waking the app. This can take up to a minute.';
    var c = window.AbortController ? new AbortController() : null, t = setTimeout(function () { if (c) c.abort(); }, 90000);
    fetch(APP + '/api/public-feedback/', { method: 'POST', body: new FormData(form), signal: c ? c.signal : undefined })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok || !j.ok) throw j; }); })
      .then(function () {
        awake = true; form.reset(); status.textContent = 'Thanks. We got your feedback.';
        setTimeout(function () { if (dlg.open) dlg.close(); }, 2500);
      })
      .catch(function (j) {
        status.className = 'sx-fb__status is-err';
        status.textContent = (j && j.error) || "Sorry, that didn't send. Please try again, or email info@odumacorp.com.";
      })
      .then(function () { clearTimeout(t); sending = false; send.disabled = false; send.textContent = 'Send feedback'; });
  });
})();
</script>""" % {'app': APP, 'ga': GA_ID}

page = f"""<!DOCTYPE html>
<!-- GENERATED by loading/build.py from docs/index.html. Edit the template, then re-run. -->
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{SITE}/">
  <meta name="theme-color" content="#0A1628">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Oduma Corp">
  <meta property="og:url" content="{SITE}/">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{SITE}/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Oduma Corp: put your project in front of investors">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{SITE}/og-image.png">
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="preconnect" href="{APP}" crossorigin>
  <link rel="preload" href="fonts/space-grotesk-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
  <script type="application/ld+json">{json.dumps(org, separators=(',', ':'))}</script>
  <style>
    /* :root copied from core/static/css/design-system.css by build.py */
    {TOKENS}
    @font-face{{font-family:'Space Grotesk';font-style:normal;font-weight:700;font-display:swap;src:url(fonts/space-grotesk-latin-700-normal.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}}
    @font-face{{font-family:'Inter';font-style:normal;font-weight:400;font-display:swap;src:url(fonts/inter-latin-400-normal.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}}
    @font-face{{font-family:'Inter';font-style:normal;font-weight:600;font-display:swap;src:url(fonts/inter-latin-600-normal.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}}
    html{{-webkit-text-size-adjust:100%;}}
    body{{margin:0;background:#F4F7FB;overflow-x:hidden;}}
{extras_css}
  </style>
{head}
</head>
<body>
{body}
{extras}
{script}
</body>
</html>
"""
OUT.write_text(page)
print('wrote', OUT, f'({len(page.encode()) // 1024} KB)')
