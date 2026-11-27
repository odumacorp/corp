  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var yr = $('#yr'); if (yr) yr.textContent = new Date().getFullYear();

  /* ── Mobile drawer ── */
  var drawer = $('#drawer'), scrim = $('#scrim'), opener = $('.hdr .burger'), closeT;
  function openDrawer() {
    clearTimeout(closeT);
    drawer.hidden = scrim.hidden = false;
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      drawer.classList.add('on'); scrim.classList.add('on');
    }); });
    opener.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
    setTimeout(function () { $('nav a', drawer).focus({ preventScroll: true }); }, 60);
  }
  function closeDrawer(refocus) {
    if (drawer.hidden) return;
    drawer.classList.remove('on'); scrim.classList.remove('on');
    opener.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    closeT = setTimeout(function () { drawer.hidden = scrim.hidden = true; }, reduce ? 0 : 300);
    if (refocus) opener.focus();
  }
  opener.addEventListener('click', openDrawer);
  scrim.addEventListener('click', function () { closeDrawer(true); });
  drawer.addEventListener('click', function (e) {
    if (e.target.closest('[data-close]')) closeDrawer(true);
    else if (e.target.closest('a')) closeDrawer(false);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !drawer.hidden) closeDrawer(true); });
  drawer.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab') return;
    var f = $$('a,button', drawer), first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
  matchMedia('(min-width:1024px)').addEventListener && matchMedia('(min-width:1024px)').addEventListener('change', function (m) { if (m.matches) closeDrawer(false); });

  /* ── Scroll reveal (once, staggered by --d) ── */
  var rv = $$('.rv');
  if (reduce || !('IntersectionObserver' in window)) rv.forEach(function (el) { el.classList.add('in'); });
  else {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    rv.forEach(function (el) { io.observe(el); });
  }

  /* ── Photo behind the sign-up band: load only when it comes near ── */
  var band = $('.band-photo');
  if (band) {
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es, o) { if (es[0].isIntersecting) { band.classList.add('bg-on'); o.disconnect(); } }, { rootMargin: '400px 0px' }).observe(band);
    else band.classList.add('bg-on');
  }

  /* ── Tabs (WAI-ARIA): arrows, Home, End; sliding indicator ── */
  $$('[role="tablist"]').forEach(function (list) {
    var tabs = $$('[role="tab"]', list), ind = $('.ind', list);
    var place = function (t) {
      if (!ind) return;
      requestAnimationFrame(function () {
        ind.style.transform = 'translateX(' + t.offsetLeft + 'px) scaleX(' + (t.offsetWidth / 100) + ')';
        list.classList.add('ready');
      });
    };
    var select = function (t, focus) {
      tabs.forEach(function (x) {
        var on = x === t;
        x.setAttribute('aria-selected', String(on)); x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute('aria-controls')).classList.toggle('on', on);
      });
      if (focus) t.focus();
      place(t);
    };
    list.addEventListener('click', function (e) { var t = e.target.closest('[role="tab"]'); if (t) select(t); });
    list.addEventListener('keydown', function (e) {
      var i = tabs.indexOf(document.activeElement); if (i < 0) return;
      var n = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (n === undefined) return;
      e.preventDefault(); select(tabs[(n + tabs.length) % tabs.length], true);
    });
    place($('[aria-selected="true"]', list));
    window.addEventListener('resize', function () { place($('[aria-selected="true"]', list)); });
  });

  /* ── Live data from the platform. The same request wakes the app (Render free tier sleeps),
        so sign-up links open quickly. Works only from odumacorp.com (CORS); elsewhere the page
        keeps its static content. ── */
  var APP = 'https://app.odumacorp.com';
  var esc = function (s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; };
  var abs = function (u) { return u && u.charAt(0) === '/' ? APP + u : u; };
  var plural = function (n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); };
  var projCard = function (p) {
    var url = APP + (p.url || '/projects/' + p.id + '/');
    var media = p.image ? '<img src="' + esc(abs(p.image)) + '" alt="" width="640" height="360" loading="lazy" decoding="async">'
      : '<svg class="i" aria-hidden="true" focusable="false"><use href="#i-layers"/></svg>';
    var av = p.owner_avatar ? '<img src="' + esc(abs(p.owner_avatar)) + '" alt="" width="30" height="30" loading="lazy">'
      : '<span class="av" aria-hidden="true">' + esc(p.owner_initials) + '</span>';
    var owner = p.owner_profile_public === false ? '<span class="owner">' + av + esc(p.owner_name) + '</span>'
      : '<a class="owner" href="' + APP + '/profile/' + encodeURIComponent(p.owner_username) + '/">' + av + esc(p.owner_name) + '</a>';
    return '<article class="proj rv in"><div class="proj-media">' + media + '</div><div class="proj-body"><div class="mock-tags">' +
      (p.industry_label ? '<span>' + esc(p.industry_label) + '</span>' : '') + (p.stage ? '<span class="st">' + esc(p.stage) + '</span>' : '') +
      '</div><h3><a href="' + url + '">' + esc(p.title) + '</a></h3><p>' + esc(p.description) + '</p>' +
      (p.funding ? '<p class="proj-ask">Seeking: ' + esc(p.funding) + '</p>' : '') +
      '</div><div class="proj-foot">' + owner + '<a href="' + url + '" aria-label="View pitch: ' + esc(p.title) + '">View pitch <svg class="i" aria-hidden="true" focusable="false"><use href="#i-arrow"/></svg></a></div></article>';
  };
  var fed = false, feed = function () {
    if (fed) return; fed = true;
    var c = window.AbortController ? new AbortController() : null;
    setTimeout(function () { if (c) c.abort(); }, 90000);
    fetch(APP + '/api/public-stats/', { cache: 'no-store', signal: c ? c.signal : undefined })
      .then(function (r) { if (!r.ok) throw r; return r.json(); })
      .then(function (d) {
        var i = +d.innovators || 0, v = +d.investors || 0, n = $('#cohort-n');
        if (n && (i || v)) n.textContent = plural(i, 'innovator') + ' and ' + plural(v, 'investor') + ' so far.';
        var counts = d.industry_counts || {};
        $$('#inds [data-ind]').forEach(function (t) {
          var k = t.getAttribute('data-ind'), m = k === 'all' ? +d.all_projects || 0 : +counts[k] || 0;
          if (k !== 'all') t.hidden = !m;
          if (m) $('small', t).textContent = plural(m, 'project');
        });
        var grid = $('#projs');
        if (grid && d.featured && d.featured.length) grid.innerHTML = d.featured.slice(0, 6).map(projCard).join('');
      })
      .catch(function () { /* app asleep or not allowed from this origin: static content stays */ });
  };
  if ($('#cohort-n') || $('#projs')) feed();
  document.addEventListener('pointerover', function (e) { if (e.target.closest && e.target.closest('a[href^="' + APP + '"]')) feed(); }, { passive: true });
  document.addEventListener('focusin', function (e) { if (e.target.closest && e.target.closest('a[href^="' + APP + '"]')) feed(); });

  /* ── Events: year filter with sliding indicator ── */
  var chips = $('#chips'), tiles = $$('#gal .tile');
  if (chips) {
    var ind = $('.ind', chips);
    var place = function (btn) {
      requestAnimationFrame(function () {
        var x = btn.offsetLeft, w = btn.offsetWidth;
        ind.style.transform = 'translateX(' + x + 'px) scaleX(' + (w / 100) + ')';
        chips.classList.add('ready');
      });
    };
    chips.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      $$('button', chips).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      var y = b.getAttribute('data-year');
      tiles.forEach(function (t) { t.classList.toggle('hide', y !== 'all' && t.getAttribute('data-year') !== y); });
      place(b);
    });
    place($('[aria-pressed="true"]', chips));
    window.addEventListener('resize', function () { place($('[aria-pressed="true"]', chips)); });
  }

  /* ── Events: lightbox ── */
  var lb = $('#lb'), links = $$('#gal a[data-i]');
  if (lb && links.length && lb.showModal) {
    var img = $('#lb-img'), cap = $('#lb-cap'), count = $('#lb-count'), cur = 0, from = null;
    var visible = function () { return links.filter(function (a) { return !a.closest('.tile').classList.contains('hide'); }); };
    var render = function () {
      var v = visible(), a = v[cur];
      img.src = a.getAttribute('href'); img.alt = a.querySelector('img').alt;
      img.width = +a.getAttribute('data-w'); img.height = +a.getAttribute('data-h');
      cap.innerHTML = ''; var b = document.createElement('b'); b.textContent = a.getAttribute('data-event');
      var s = document.createElement('span'); s.textContent = a.getAttribute('data-meta');
      cap.appendChild(b); cap.appendChild(s);
      count.textContent = 'Photo ' + (cur + 1) + ' of ' + v.length;
      var multi = v.length > 1; $$('.lb-nav', lb).forEach(function (n) { n.hidden = !multi; });
    };
    var step = function (d) { var n = visible().length; cur = (cur + d + n) % n; render(); };
    links.forEach(function (a) {
      a.addEventListener('click', function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey) return;
        e.preventDefault(); from = a; cur = visible().indexOf(a); render(); lb.showModal();
        $('[data-lb="close"]', lb).focus();
      });
    });
    lb.addEventListener('close', function () { if (from) from.focus(); });
    lb.addEventListener('click', function (e) {
      var b = e.target.closest('[data-lb]');
      if (b) { var k = b.getAttribute('data-lb'); k === 'close' ? lb.close() : step(k === 'next' ? 1 : -1); }
      else if (e.target === lb || e.target.id === 'lb-fig') lb.close();
    });
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') step(1); else if (e.key === 'ArrowLeft') step(-1);
      else if (e.key === 'Tab') {
        var f = $$('button:not([hidden])', lb), first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    var sx = null;
    lb.addEventListener('pointerdown', function (e) { sx = e.clientX; });
    lb.addEventListener('pointerup', function (e) {
      if (sx === null) return; var dx = e.clientX - sx; sx = null;
      if (Math.abs(dx) > 50 && visible().length > 1) step(dx < 0 ? 1 : -1);
    });
  }