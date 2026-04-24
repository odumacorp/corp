/* ============================================================
   OC Avatar / Photo Picker  —  Oduma Corp
   Usage: ocPicker.open({ inputId, previewId, type, letterSrc, containerId })
   type: 'person' | 'logo' | 'cover'
   ============================================================ */
(function (window) {
  'use strict';

  var GRADIENTS = [
    ['#1B5EC7','#0EA5E9'], ['#0A1628','#1B5EC7'],
    ['#10B981','#059669'], ['#F59E0B','#EF4444'],
    ['#8B5CF6','#EC4899'], ['#06B6D4','#6366F1'],
    ['#0A1628','#374151'], ['#1B5EC7','#6366F1'],
    ['#059669','#06B6D4'], ['#DC2626','#F97316'],
    ['#4B0082','#7C3AED'], ['#0EA5E9','#10B981'],
    ['#F97316','#F59E0B'], ['#EC4899','#F43F5E'],
    ['#14B8A6','#0EA5E9'], ['#7C3AED','#EC4899'],
    ['#1B5EC7','#14B8A6'], ['#F43F5E','#8B5CF6'],
    ['#0A1628','#6366F1'], ['#059669','#10B981'],
  ];

  /* solid colors for avatar circles */
  var PALETTE = [
    /* blues */
    '#1B5EC7','#2563EB','#0EA5E9','#0284C7','#075985',
    /* greens */
    '#10B981','#059669','#16A34A','#15803D','#166534',
    /* purples */
    '#8B5CF6','#7C3AED','#6D28D9','#A855F7','#9333EA',
    /* pinks / reds */
    '#EC4899','#DB2777','#EF4444','#DC2626','#F43F5E',
    /* teals / cyans */
    '#06B6D4','#0891B2','#14B8A6','#0D9488','#0F766E',
    /* oranges / ambers */
    '#F97316','#EA580C','#F59E0B','#D97706','#B45309',
    /* slate / ink */
    '#334155','#475569','#0A1628','#1E293B','#374151',
    /* rose / warm */
    '#FB7185','#F472B6','#C084FC','#818CF8','#60A5FA',
  ];

  /* ── Canvas drawers ── */

  var DPR = Math.min(window.devicePixelRatio || 1, 3);

  /* Create a crisp canvas at logical size `px`, drawn at physical DPR size */
  function crispCanvas(px, py) {
    py = py || px;
    var c = document.createElement('canvas');
    c.width  = Math.round(px * DPR);
    c.height = Math.round(py * DPR);
    c.style.width  = px + 'px';
    c.style.height = py + 'px';
    var ctx = c.getContext('2d');
    ctx.scale(DPR, DPR);
    return { cvs: c, ctx: ctx };
  }

  /* Parse hex color → {r,g,b} */
  function hexToRgb(hex) {
    var r = parseInt(hex.slice(1,3),16);
    var g = parseInt(hex.slice(3,5),16);
    var b = parseInt(hex.slice(5,7),16);
    return {r:r, g:g, b:b};
  }

  /*
   * Replicates the user.png silhouette design:
   *   – light-tinted circular background
   *   – subtle border ring
   *   – head: filled circle (top-center)
   *   – body: dome / arch (top half of a large circle), rounded corners via arc
   */
  function drawPerson(ctx, s, color) {
    var c = hexToRgb(color);
    ctx.clearRect(0, 0, s, s);

    /* ── background circle ── */
    ctx.fillStyle = 'rgba(' + c.r + ',' + c.g + ',' + c.b + ',0.13)';
    ctx.beginPath(); ctx.arc(s/2, s/2, s/2, 0, Math.PI*2); ctx.fill();

    /* ── silhouette, clipped to circle ── */
    ctx.save();
    ctx.beginPath(); ctx.arc(s/2, s/2, s/2, 0, Math.PI*2); ctx.clip();
    ctx.fillStyle = color;

    /* head */
    ctx.beginPath();
    ctx.arc(s/2, s*0.32, s*0.20, 0, Math.PI*2);
    ctx.fill();

    /* body dome */
    var bcy = s * 0.90;
    var br  = s * 0.40;
    ctx.beginPath();
    ctx.arc(s/2, bcy, br, Math.PI, 0);
    ctx.lineTo(s/2 + br, s + 4);
    ctx.lineTo(s/2 - br, s + 4);
    ctx.closePath();
    ctx.fill();

    ctx.restore();
  }

  function drawLogo(ctx, s, color, letter) {
    ctx.clearRect(0, 0, s, s);
    var r = s * 0.18;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(r, 0); ctx.lineTo(s-r, 0); ctx.quadraticCurveTo(s, 0, s, r);
    ctx.lineTo(s, s-r); ctx.quadraticCurveTo(s, s, s-r, s);
    ctx.lineTo(r, s); ctx.quadraticCurveTo(0, s, 0, s-r);
    ctx.lineTo(0, r); ctx.quadraticCurveTo(0, 0, r, 0);
    ctx.closePath(); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.95)';
    ctx.font = 'bold ' + Math.round(s * 0.52) + 'px Arial,sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(((letter || 'O').charAt(0)).toUpperCase(), s/2, s/2 + s*0.02);
  }

  function drawGradientCircle(ctx, s, from, to) {
    ctx.clearRect(0, 0, s, s);
    var cf = hexToRgb(from);
    ctx.fillStyle = 'rgba(' + cf.r + ',' + cf.g + ',' + cf.b + ',0.13)';
    ctx.beginPath(); ctx.arc(s/2, s/2, s/2, 0, Math.PI*2); ctx.fill();
    ctx.save();
    ctx.beginPath(); ctx.arc(s/2, s/2, s/2, 0, Math.PI*2); ctx.clip();
    var g = ctx.createLinearGradient(0, 0, s, s);
    g.addColorStop(0, from); g.addColorStop(1, to);
    ctx.fillStyle = g;
    /* head */
    ctx.beginPath(); ctx.arc(s/2, s*0.32, s*0.20, 0, Math.PI*2); ctx.fill();
    /* body dome */
    ctx.beginPath();
    ctx.arc(s/2, s*0.90, s*0.40, Math.PI, 0);
    ctx.lineTo(s/2 + s*0.40, s + 4);
    ctx.lineTo(s/2 - s*0.40, s + 4);
    ctx.closePath(); ctx.fill();
    ctx.restore();
  }

  function drawCoverGradient(ctx, w, h, from, to) {
    ctx.clearRect(0, 0, w, h);
    var g = ctx.createLinearGradient(0, 0, w, h);
    g.addColorStop(0, from); g.addColorStop(1, to);
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  }

  /* ── Patterns ── */
  var PATTERNS = [
    { name:'dots-blue',   colors:['#EFF6FF','#1B5EC7'], fn: drawDots('#EFF6FF','#1B5EC7') },
    { name:'dots-teal',   colors:['#F0FDF4','#10B981'], fn: drawDots('#F0FDF4','#10B981') },
    { name:'dots-purple', colors:['#F5F3FF','#8B5CF6'], fn: drawDots('#F5F3FF','#8B5CF6') },
    { name:'dots-rose',   colors:['#FFF1F2','#F43F5E'], fn: drawDots('#FFF1F2','#F43F5E') },
    { name:'stripe-blue',   colors:['#EFF6FF','#1B5EC7'], fn: drawStripes('#EFF6FF','#1B5EC7') },
    { name:'stripe-ink',    colors:['#F8FAFC','#0A1628'], fn: drawStripes('#F8FAFC','#0A1628') },
    { name:'stripe-green',  colors:['#F0FDF4','#059669'], fn: drawStripes('#F0FDF4','#059669') },
    { name:'stripe-amber',  colors:['#FFFBEB','#F59E0B'], fn: drawStripes('#FFFBEB','#F59E0B') },
    { name:'grid-blue',   colors:['#EFF6FF','#BFDBFE'], fn: drawGrid('#EFF6FF','#BFDBFE') },
    { name:'grid-slate',  colors:['#F8FAFC','#CBD5E1'], fn: drawGrid('#F8FAFC','#CBD5E1') },
    { name:'grid-purple', colors:['#F5F3FF','#DDD6FE'], fn: drawGrid('#F5F3FF','#DDD6FE') },
    { name:'grid-rose',   colors:['#FFF1F2','#FECDD3'], fn: drawGrid('#FFF1F2','#FECDD3') },
    { name:'wave-ocean',  colors:['#0EA5E9','#1B5EC7'], fn: drawWave('#0EA5E9','#1B5EC7') },
    { name:'wave-sunset', colors:['#F59E0B','#EF4444'], fn: drawWave('#F59E0B','#EF4444') },
    { name:'wave-forest', colors:['#10B981','#059669'], fn: drawWave('#10B981','#059669') },
    { name:'wave-galaxy', colors:['#6366F1','#8B5CF6'], fn: drawWave('#6366F1','#8B5CF6') },
  ];

  function drawDots(bg, fg) {
    return function(ctx, s) {
      ctx.clearRect(0,0,s,s);
      ctx.beginPath(); ctx.arc(s/2,s/2,s/2,0,Math.PI*2); ctx.clip();
      ctx.fillStyle = bg; ctx.fillRect(0,0,s,s);
      ctx.fillStyle = fg;
      var r = s*0.04, sp = s*0.18;
      for (var x = sp/2; x < s; x += sp) {
        for (var y = sp/2; y < s; y += sp) {
          ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.fill();
        }
      }
      ctx.fillStyle = 'rgba(0,0,0,0.18)';
      ctx.beginPath(); ctx.arc(s/2, s*0.32, s*0.20, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(s/2, s*0.90, s*0.40, Math.PI, 0);
      ctx.lineTo(s/2+s*0.40,s+4); ctx.lineTo(s/2-s*0.40,s+4); ctx.closePath(); ctx.fill();
    };
  }

  function drawStripes(bg, fg) {
    return function(ctx, s) {
      ctx.clearRect(0,0,s,s);
      ctx.beginPath(); ctx.arc(s/2,s/2,s/2,0,Math.PI*2); ctx.clip();
      ctx.fillStyle = bg; ctx.fillRect(0,0,s,s);
      ctx.fillStyle = fg; ctx.globalAlpha = 0.25;
      var w = s*0.06, gap = s*0.14;
      for (var x = -s; x < s*2; x += gap) {
        ctx.fillRect(x, 0, w, s);
      }
      ctx.globalAlpha = 1;
      ctx.fillStyle = 'rgba(0,0,0,0.18)';
      ctx.beginPath(); ctx.arc(s/2, s*0.32, s*0.20, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(s/2, s*0.90, s*0.40, Math.PI, 0);
      ctx.lineTo(s/2+s*0.40,s+4); ctx.lineTo(s/2-s*0.40,s+4); ctx.closePath(); ctx.fill();
    };
  }

  function drawGrid(bg, line) {
    return function(ctx, s) {
      ctx.clearRect(0,0,s,s);
      ctx.beginPath(); ctx.arc(s/2,s/2,s/2,0,Math.PI*2); ctx.clip();
      ctx.fillStyle = bg; ctx.fillRect(0,0,s,s);
      ctx.strokeStyle = line; ctx.lineWidth = 1; ctx.globalAlpha = 0.7;
      var sp = s * 0.14;
      for (var x = 0; x < s; x += sp) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,s); ctx.stroke(); }
      for (var y = 0; y < s; y += sp) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(s,y); ctx.stroke(); }
      ctx.globalAlpha = 1;
      ctx.fillStyle = 'rgba(0,0,0,0.18)';
      ctx.beginPath(); ctx.arc(s/2, s*0.32, s*0.20, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(s/2, s*0.90, s*0.40, Math.PI, 0);
      ctx.lineTo(s/2+s*0.40,s+4); ctx.lineTo(s/2-s*0.40,s+4); ctx.closePath(); ctx.fill();
    };
  }

  function drawWave(c1, c2) {
    return function(ctx, s) {
      ctx.clearRect(0,0,s,s);
      ctx.beginPath(); ctx.arc(s/2,s/2,s/2,0,Math.PI*2); ctx.clip();
      var g = ctx.createLinearGradient(0,0,s,s);
      g.addColorStop(0,c1); g.addColorStop(1,c2);
      ctx.fillStyle = g; ctx.fillRect(0,0,s,s);
      ctx.strokeStyle = 'rgba(255,255,255,0.25)'; ctx.lineWidth = s*0.04;
      for (var i = 0; i < 3; i++) {
        ctx.beginPath();
        ctx.moveTo(0, s*0.3 + i*s*0.15);
        ctx.bezierCurveTo(s*0.25, s*0.2+i*s*0.15, s*0.75, s*0.4+i*s*0.15, s, s*0.3+i*s*0.15);
        ctx.stroke();
      }
      ctx.fillStyle = 'rgba(255,255,255,0.85)';
      ctx.beginPath(); ctx.arc(s/2, s*0.32, s*0.20, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(s/2, s*0.90, s*0.40, Math.PI, 0);
      ctx.lineTo(s/2+s*0.40,s+4); ctx.lineTo(s/2-s*0.40,s+4); ctx.closePath(); ctx.fill();
    };
  }

  /* ── Apply blob/file to input ── */
  function applyToInput(bigCvs, fileInput, previewEl, fname) {
    bigCvs.toBlob(function (blob) {
      if (previewEl) {
        previewEl.src = URL.createObjectURL(blob);
        previewEl.style.display = 'block';
        var ph = previewEl.parentElement && previewEl.parentElement.querySelector('.oc-upload-placeholder');
        if (ph) ph.style.display = 'none';
      }
      try {
        var file = new File([blob], fname, { type: 'image/png' });
        var dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
      } catch (e) {}
    }, 'image/png');
  }

  /* ── Update hero/sidebar background to match chosen avatar ── */
  function setHeroBg(panel, bg) {
    var hero = panel.closest('.ep-sidebar-hero') || document.getElementById('ep-sidebar-hero');
    if (hero) hero.style.background = bg;
    var inp = document.getElementById('ep-cover-style');
    if (inp) inp.value = bg;
  }

  /* ── Build tabs UI ── */
  function buildPickerTabs(container, opts, type, letter) {
    container.innerHTML = '';

    var tabs = type === 'cover'
      ? [{ id:'gradients', label:'Gradients' }]
      : [{ id:'avatars', label:'Avatars' }, { id:'gradients', label:'Gradients' }, { id:'patterns', label:'Patterns' }];

    /* tab bar */
    var bar = document.createElement('div');
    bar.className = 'oc-ptabs';
    tabs.forEach(function (t, i) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'oc-ptab' + (i === 0 ? ' oc-ptab--active' : '');
      btn.textContent = t.label;
      btn.dataset.tab = t.id;
      btn.addEventListener('click', function () {
        bar.querySelectorAll('.oc-ptab').forEach(function(b){ b.classList.remove('oc-ptab--active'); });
        btn.classList.add('oc-ptab--active');
        container.querySelectorAll('.oc-pane').forEach(function(p){ p.style.display = 'none'; });
        container.querySelector('.oc-pane[data-pane="' + t.id + '"]').style.display = 'block';
      });
      bar.appendChild(btn);
    });
    container.appendChild(bar);

    /* panes */
    tabs.forEach(function (t, i) {
      var pane = document.createElement('div');
      pane.className = 'oc-pane';
      pane.dataset.pane = t.id;
      pane.style.display = i === 0 ? 'block' : 'none';

      if (t.id === 'avatars') {
        buildAvatarPane(pane, opts);
      } else if (t.id === 'gradients') {
        buildGradientPane(pane, opts, type, letter);
      } else if (t.id === 'patterns') {
        buildPatternPane(pane, opts);
      }

      container.appendChild(pane);
    });
  }

  function buildAvatarPane(pane, opts) {
    var fileInput = document.getElementById(opts.inputId);
    var previewEl = opts.previewId ? document.getElementById(opts.previewId) : null;

    var grid = document.createElement('div');
    grid.className = 'oc-picker-grid';

    PALETTE.forEach(function (color) {
      var cc = crispCanvas(64);
      drawPerson(cc.ctx, 64, color);
      var item = document.createElement('div');
      item.className = 'oc-picker-item';
      item.appendChild(cc.cvs);
      item.addEventListener('click', function () {
        var big = document.createElement('canvas');
        big.width = big.height = 300;
        drawPerson(big.getContext('2d'), 300, color);
        applyToInput(big, fileInput, previewEl, 'avatar.png');
        var c = hexToRgb(color);
        setHeroBg(pane.closest('.oc-picker-panel'),
          'linear-gradient(135deg,rgba('+c.r+','+c.g+','+c.b+',0.18) 0%,rgba('+c.r+','+c.g+','+c.b+',0.38) 100%)');
        pane.querySelectorAll('.oc-picker-item').forEach(function(el){ el.classList.remove('oc-picker-item--selected'); });
        item.classList.add('oc-picker-item--selected');
        setTimeout(function () { pane.closest('.oc-picker-panel').style.display = 'none'; }, 340);
      });
      grid.appendChild(item);
    });

    pane.appendChild(grid);
  }

  function buildGradientPane(pane, opts, type, letter) {
    var fileInput = document.getElementById(opts.inputId);
    var previewEl = opts.previewId ? document.getElementById(opts.previewId) : null;
    var isCover = type === 'cover';

    var grid = document.createElement('div');
    grid.className = isCover ? 'oc-picker-grid oc-picker-grid--cover' : 'oc-picker-grid';

    GRADIENTS.forEach(function (pair) {
      var cc = isCover ? crispCanvas(88, 40) : crispCanvas(64);
      if (isCover) drawCoverGradient(cc.ctx, 88, 40, pair[0], pair[1]);
      else         drawGradientCircle(cc.ctx, 64, pair[0], pair[1]);
      var item = document.createElement('div');
      item.className = 'oc-picker-item';
      item.appendChild(cc.cvs);
      item.addEventListener('click', function () {
        var big = document.createElement('canvas');
        if (isCover) {
          big.width = 1200; big.height = 300;
          drawCoverGradient(big.getContext('2d'), 1200, 300, pair[0], pair[1]);
        } else {
          big.width = big.height = 300;
          drawGradientCircle(big.getContext('2d'), 300, pair[0], pair[1]);
        }
        applyToInput(big, fileInput, previewEl, 'gradient_avatar.png');
        if (!isCover) setHeroBg(pane.closest('.oc-picker-panel'),
          'linear-gradient(135deg,'+pair[0]+' 0%,'+pair[1]+' 100%)');
        pane.querySelectorAll('.oc-picker-item').forEach(function(el){ el.classList.remove('oc-picker-item--selected'); });
        item.classList.add('oc-picker-item--selected');
        setTimeout(function () { pane.closest('.oc-picker-panel').style.display = 'none'; }, 340);
      });
      grid.appendChild(item);
    });

    pane.appendChild(grid);
  }

  function buildPatternPane(pane, opts) {
    var fileInput = document.getElementById(opts.inputId);
    var previewEl = opts.previewId ? document.getElementById(opts.previewId) : null;

    var grid = document.createElement('div');
    grid.className = 'oc-picker-grid';

    PATTERNS.forEach(function (pat) {
      var cc = crispCanvas(64);
      pat.fn(cc.ctx, 64);
      var item = document.createElement('div');
      item.className = 'oc-picker-item';
      item.appendChild(cc.cvs);
      item.addEventListener('click', function () {
        var big = document.createElement('canvas');
        big.width = big.height = 300;
        pat.fn(big.getContext('2d'), 300);
        applyToInput(big, fileInput, previewEl, 'pattern_avatar.png');
        setHeroBg(pane.closest('.oc-picker-panel'),
          'linear-gradient(135deg,'+pat.colors[0]+' 0%,'+pat.colors[1]+' 100%)');
        pane.querySelectorAll('.oc-picker-item').forEach(function(el){ el.classList.remove('oc-picker-item--selected'); });
        item.classList.add('oc-picker-item--selected');
        setTimeout(function () { pane.closest('.oc-picker-panel').style.display = 'none'; }, 340);
      });
      grid.appendChild(item);
    });

    pane.appendChild(grid);
  }

  /* ── Main open ── */
  function openPicker(opts) {
    var fileInput = document.getElementById(opts.inputId);
    var container = document.getElementById(opts.containerId);
    if (!fileInput || !container) return;

    if (container.style.display !== 'none' && container.innerHTML !== '') {
      container.style.display = 'none'; return;
    }

    var letter = 'O';
    if (opts.letterSrc) {
      var lel = document.getElementById(opts.letterSrc);
      if (lel && lel.value.trim()) letter = lel.value.trim().charAt(0).toUpperCase();
    }

    var type = opts.type || 'person';
    buildPickerTabs(container, opts, type, letter);
    container.style.display = 'block';
  }

  /* close on outside click */
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.oc-picker-panel').forEach(function (panel) {
      var wrap = panel.closest('[data-picker-wrap]') || panel.parentElement;
      if (wrap && !wrap.contains(e.target)) panel.style.display = 'none';
    });
  });

  window.ocPicker = { open: openPicker };
})(window);
