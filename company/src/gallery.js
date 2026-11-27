  /* ── Gallery page: loads the admin-posted media from the app, groups it by event,
        newest first. The files themselves are on Cloudinary, so they load even while the app wakes. ── */
  (function () {
    var groupsEl = $('#gp-groups'); if (!groupsEl) return;
    var statusEl = $('#gp-status'), yearsEl = $('#gp-years'), lb = $('#lb');
    var items = [], shown = [], cur = 0, opener = null;
    var esc = function (s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; };
    var plural = function (n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); };
    var meta = function (it) { return [it.place, it.date_label].filter(Boolean).join(' · '); };
    var PLAY = '<span class="gp-play" aria-hidden="true"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"/></svg></span>';

    var slow = setTimeout(function () { statusEl.textContent = 'Loading the gallery. If nobody has visited for a while this can take up to a minute.'; }, 3500);
    var fail = function () {
      clearTimeout(slow);
      groupsEl.setAttribute('aria-busy', 'false');
      groupsEl.innerHTML = '';
      statusEl.innerHTML = 'The gallery could not load just now. <button type="button" class="linkish" id="gp-retry">Try again</button> or open it in the app: <a href="https://app.odumacorp.com/gallery/">app.odumacorp.com/gallery</a>.';
      $('#gp-retry').addEventListener('click', function () { location.reload(); });
    };
    var c = window.AbortController ? new AbortController() : null;
    var stop = setTimeout(function () { if (c) c.abort(); }, 90000);
    fetch('https://app.odumacorp.com/api/public-gallery/', { signal: c ? c.signal : undefined })
      .then(function (r) { if (!r.ok) throw r; return r.json(); })
      .then(function (d) { clearTimeout(stop); clearTimeout(slow); items = d.items || []; build(); })
      .catch(fail);

    function groupsOf(list) {
      /* One group per event (name + place); items without an event are grouped by month. */
      var order = [], map = {};
      list.forEach(function (it) {
        var key = it.event ? 'e|' + it.event + '|' + (it.place || '') : 'm|' + it.date.slice(0, 7);
        if (!map[key]) { map[key] = { key: key, items: [], first: it }; order.push(map[key]); }
        map[key].items.push(it);
      });
      return order;
    }

    function build() {
      groupsEl.setAttribute('aria-busy', 'false');
      statusEl.textContent = '';
      if (!items.length) { groupsEl.innerHTML = '<p class="gp-empty">No photos or videos yet. Check back soon.</p>'; return; }
      var years = []; items.forEach(function (it) { var y = it.date.slice(0, 4); if (years.indexOf(y) < 0) years.push(y); });
      if (years.length > 1) {
        yearsEl.insertAdjacentHTML('beforeend', '<button type="button" aria-pressed="true" data-year="all">All</button>' +
          years.map(function (y) { return '<button type="button" aria-pressed="false" data-year="' + y + '">' + y + '</button>'; }).join(''));
        yearsEl.hidden = false;
        var ind = $('.ind', yearsEl);
        var place = function (b) { requestAnimationFrame(function () { ind.style.transform = 'translateX(' + b.offsetLeft + 'px) scaleX(' + (b.offsetWidth / 100) + ')'; yearsEl.classList.add('ready'); }); };
        yearsEl.addEventListener('click', function (e) {
          var b = e.target.closest('button'); if (!b) return;
          $$('button', yearsEl).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
          render(b.getAttribute('data-year')); place(b);
        });
        place($('[aria-pressed="true"]', yearsEl));
        window.addEventListener('resize', function () { place($('[aria-pressed="true"]', yearsEl)); });
      }
      render('all');
      var m = /^#item-(\d+)$/.exec(location.hash);
      if (m) { var t = document.getElementById('gp-' + m[1]); if (t) { t.scrollIntoView({ block: 'center' }); open(+t.getAttribute('data-i'), t); } }
    }

    function render(year) {
      shown = items.filter(function (it) { return year === 'all' || it.date.slice(0, 4) === year; });
      var n = 0;
      groupsEl.innerHTML = groupsOf(shown).map(function (g) {
        var f = g.first, photos = g.items.filter(function (i) { return i.type !== 'video'; }).length, videos = g.items.length - photos;
        var title = f.event || new Date(f.date + 'T00:00:00').toLocaleDateString('en-KE', { month: 'long', year: 'numeric' });
        var sub = [f.event ? meta(f) : '', photos ? plural(photos, 'photo') : '', videos ? plural(videos, 'video') : ''].filter(Boolean).join(' · ');
        return '<section class="gev rv in"><header class="gev-head"><h2>' + esc(title) + '</h2><p>' + esc(sub) + '</p></header><ul class="gp-grid">' +
          g.items.map(function (it) {
            var i = n++;
            return '<li><button type="button" class="gp-tile" id="gp-' + it.id + '" data-i="' + i + '" aria-label="Open ' + (it.type === 'video' ? 'video' : 'photo') + ': ' + esc(it.title) + '">' +
              '<img src="' + esc(it.thumb) + '" alt="" width="640" height="480" loading="lazy" decoding="async">' + (it.type === 'video' ? PLAY : '') +
              '<span class="gp-cap"><b>' + esc(it.title) + '</b></span></button></li>';
          }).join('') + '</ul></section>';
      }).join('');
    }

    /* ── Viewer (photos and videos) ── */
    if (!lb || !lb.showModal) return;
    var fig = $('#lb-fig'), cap = $('#lb-cap'), count = $('#lb-count');
    function show(i) {
      cur = (i + shown.length) % shown.length;
      var it = shown[cur], el;
      var old = $('#lb-media'); if (old) old.remove();
      if (it.type === 'video') { el = document.createElement('video'); el.controls = true; el.playsInline = true; el.preload = 'metadata'; el.poster = it.thumb; }
      else { el = document.createElement('img'); el.alt = it.title; }
      el.id = 'lb-media'; el.src = it.src;
      fig.insertBefore(el, cap);
      cap.innerHTML = '<b>' + esc(it.title) + '</b><span>' + esc([it.event, meta(it)].filter(Boolean).join(' · ')) + '</span>' + (it.caption ? '<span class="lb-note">' + esc(it.caption) + '</span>' : '');
      count.textContent = (cur + 1) + ' of ' + shown.length;
      $$('.lb-nav', lb).forEach(function (b) { b.hidden = shown.length < 2; });
      history.replaceState(null, '', '#item-' + it.id);
    }
    function open(i, from) { opener = from || null; show(i); if (!lb.open) lb.showModal(); $('[data-lb="close"]', lb).focus(); }
    groupsEl.addEventListener('click', function (e) { var b = e.target.closest('.gp-tile[data-i]'); if (b) open(+b.getAttribute('data-i'), b); });
    lb.addEventListener('close', function () {
      var m = $('#lb-media'); if (m) m.remove();          /* stops a playing video */
      history.replaceState(null, '', location.pathname);
      if (opener) opener.focus();
    });
    lb.addEventListener('click', function (e) {
      var b = e.target.closest('[data-lb]');
      if (b) { var k = b.getAttribute('data-lb'); if (k === 'close') lb.close(); else show(cur + (k === 'next' ? 1 : -1)); }
      else if (e.target === lb || e.target === fig) lb.close();
    });
    lb.addEventListener('keydown', function (e) {
      if (e.target.tagName === 'VIDEO') return;
      if (e.key === 'ArrowRight') show(cur + 1); else if (e.key === 'ArrowLeft') show(cur - 1);
      else if (e.key === 'Tab') {
        var f = $$('button:not([hidden])', lb), first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    var sx = null;
    fig.addEventListener('pointerdown', function (e) { sx = e.clientX; });
    fig.addEventListener('pointerup', function (e) {
      if (sx === null) return; var dx = e.clientX - sx; sx = null;
      if (Math.abs(dx) > 50 && shown.length > 1) show(cur + (dx < 0 ? 1 : -1));
    });
  })();
