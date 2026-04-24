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

  /* ── Enterprise icon preload ── */
  var _entImg = null;
  (function () {
    if (!window.OC_ENTERPRISE_ICON) return;
    var img = new Image();
    img.onload = function () { _entImg = img; };
    img.src = window.OC_ENTERPRISE_ICON;
  })();

  /* Draw enterprise PNG as white icon on a colored rounded-square background.
     Strategy: invert the black-on-white PNG to white-on-black via a temp canvas,
     then screen-blend onto the colored square so icon = white, bg = color. */
  function drawEnterpriseIcon(mainCtx, s, color) {
    mainCtx.clearRect(0, 0, s, s);
    var r = s * 0.18;
    mainCtx.fillStyle = color;
    mainCtx.beginPath();
    mainCtx.moveTo(r, 0); mainCtx.lineTo(s - r, 0); mainCtx.quadraticCurveTo(s, 0, s, r);
    mainCtx.lineTo(s, s - r); mainCtx.quadraticCurveTo(s, s, s - r, s);
    mainCtx.lineTo(r, s); mainCtx.quadraticCurveTo(0, s, 0, s - r);
    mainCtx.lineTo(0, r); mainCtx.quadraticCurveTo(0, 0, r, 0);
    mainCtx.closePath(); mainCtx.fill();

    if (_entImg) {
      var pad = Math.round(s * 0.16);
      var tmp = document.createElement('canvas');
      tmp.width = tmp.height = s;
      var tc = tmp.getContext('2d');
      tc.fillStyle = '#000'; tc.fillRect(0, 0, s, s);
      try { tc.filter = 'invert(1)'; } catch (e) {}
      tc.drawImage(_entImg, pad, pad, s - pad * 2, s - pad * 2);
      try { tc.filter = 'none'; } catch (e) {}
      mainCtx.globalCompositeOperation = 'screen';
      mainCtx.drawImage(tmp, 0, 0);
      mainCtx.globalCompositeOperation = 'source-over';
    } else {
      mainCtx.fillStyle = 'rgba(255,255,255,0.9)';
      mainCtx.font = 'bold ' + Math.round(s * 0.52) + 'px Arial,sans-serif';
      mainCtx.textAlign = 'center'; mainCtx.textBaseline = 'middle';
      mainCtx.fillText('C', s / 2, s / 2 + s * 0.02);
    }
  }

  function drawEnterpriseGradient(mainCtx, s, from, to) {
    mainCtx.clearRect(0, 0, s, s);
    var r = s * 0.18;
    var g = mainCtx.createLinearGradient(0, 0, s, s);
    g.addColorStop(0, from); g.addColorStop(1, to);
    mainCtx.fillStyle = g;
    mainCtx.beginPath();
    mainCtx.moveTo(r, 0); mainCtx.lineTo(s - r, 0); mainCtx.quadraticCurveTo(s, 0, s, r);
    mainCtx.lineTo(s, s - r); mainCtx.quadraticCurveTo(s, s, s - r, s);
    mainCtx.lineTo(r, s); mainCtx.quadraticCurveTo(0, s, 0, s - r);
    mainCtx.lineTo(0, r); mainCtx.quadraticCurveTo(0, 0, r, 0);
    mainCtx.closePath(); mainCtx.fill();

    if (_entImg) {
      var pad = Math.round(s * 0.16);
      var tmp = document.createElement('canvas');
      tmp.width = tmp.height = s;
      var tc = tmp.getContext('2d');
      tc.fillStyle = '#000'; tc.fillRect(0, 0, s, s);
      try { tc.filter = 'invert(1)'; } catch (e) {}
      tc.drawImage(_entImg, pad, pad, s - pad * 2, s - pad * 2);
      try { tc.filter = 'none'; } catch (e) {}
      mainCtx.globalCompositeOperation = 'screen';
      mainCtx.drawImage(tmp, 0, 0);
      mainCtx.globalCompositeOperation = 'source-over';
    } else {
      mainCtx.fillStyle = 'rgba(255,255,255,0.9)';
      mainCtx.font = 'bold ' + Math.round(s * 0.45) + 'px Arial,sans-serif';
      mainCtx.textAlign = 'center'; mainCtx.textBaseline = 'middle';
      mainCtx.fillText('C', s / 2, s / 2 + s * 0.02);
    }
  }

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

  /* ── Patterns (avatar – with silhouette) ── */
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

  /* ── Cover patterns (rectangular, no silhouette) ── */
  function coverDots(bg, fg) {
    return function(ctx, w, h) {
      ctx.clearRect(0,0,w,h);
      ctx.fillStyle = bg; ctx.fillRect(0,0,w,h);
      ctx.fillStyle = fg;
      var r = h*0.07, sp = h*0.28;
      for (var x = sp/2; x < w + sp; x += sp)
        for (var y = sp/2; y < h + sp; y += sp) {
          ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.fill();
        }
    };
  }
  function coverStripes(bg, fg) {
    return function(ctx, w, h) {
      ctx.clearRect(0,0,w,h);
      ctx.fillStyle = bg; ctx.fillRect(0,0,w,h);
      ctx.fillStyle = fg; ctx.globalAlpha = 0.28;
      var sw = h*0.10, gap = h*0.26;
      for (var x = -h; x < w + h; x += gap) {
        ctx.save();
        ctx.translate(x, 0);
        ctx.rotate(Math.PI / 4);
        ctx.fillRect(0, -h, sw, h*4);
        ctx.restore();
      }
      ctx.globalAlpha = 1;
    };
  }
  function coverGrid(bg, line) {
    return function(ctx, w, h) {
      ctx.clearRect(0,0,w,h);
      ctx.fillStyle = bg; ctx.fillRect(0,0,w,h);
      ctx.strokeStyle = line; ctx.lineWidth = 1; ctx.globalAlpha = 0.55;
      var sp = h * 0.22;
      for (var x = 0; x <= w; x += sp) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,h); ctx.stroke(); }
      for (var y = 0; y <= h; y += sp) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); }
      ctx.globalAlpha = 1;
    };
  }
  function coverWave(c1, c2) {
    return function(ctx, w, h) {
      ctx.clearRect(0,0,w,h);
      var g = ctx.createLinearGradient(0,0,w,h);
      g.addColorStop(0,c1); g.addColorStop(1,c2);
      ctx.fillStyle = g; ctx.fillRect(0,0,w,h);
      ctx.strokeStyle = 'rgba(255,255,255,0.28)'; ctx.lineWidth = h*0.07;
      for (var i = 0; i < 4; i++) {
        ctx.beginPath();
        ctx.moveTo(0, h*(0.25 + i*0.2));
        ctx.bezierCurveTo(w*0.25, h*(0.1+i*0.2), w*0.75, h*(0.4+i*0.2), w, h*(0.25+i*0.2));
        ctx.stroke();
      }
    };
  }
  function coverMesh(c1, c2) {
    return function(ctx, w, h) {
      ctx.clearRect(0,0,w,h);
      var g = ctx.createLinearGradient(0,0,w,h);
      g.addColorStop(0,c1); g.addColorStop(1,c2);
      ctx.fillStyle = g; ctx.fillRect(0,0,w,h);
      ctx.strokeStyle = 'rgba(255,255,255,0.15)'; ctx.lineWidth = 1;
      var sp = h * 0.3;
      for (var x = 0; x <= w + h; x += sp) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x - h, h); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + h, h); ctx.stroke();
      }
    };
  }

  var COVER_PATTERNS = [
    { name:'dots-blue',   colors:['#EFF6FF','#1B5EC7'], fn: coverDots('#EFF6FF','#1B5EC7') },
    { name:'dots-teal',   colors:['#F0FDF4','#10B981'], fn: coverDots('#F0FDF4','#10B981') },
    { name:'dots-purple', colors:['#F5F3FF','#8B5CF6'], fn: coverDots('#F5F3FF','#8B5CF6') },
    { name:'dots-rose',   colors:['#FFF1F2','#F43F5E'], fn: coverDots('#FFF1F2','#F43F5E') },
    { name:'dots-amber',  colors:['#FFFBEB','#F59E0B'], fn: coverDots('#FFFBEB','#F59E0B') },
    { name:'stripe-blue',  colors:['#EFF6FF','#1B5EC7'], fn: coverStripes('#EFF6FF','#1B5EC7') },
    { name:'stripe-ink',   colors:['#F8FAFC','#0A1628'], fn: coverStripes('#F8FAFC','#0A1628') },
    { name:'stripe-green', colors:['#F0FDF4','#059669'], fn: coverStripes('#F0FDF4','#059669') },
    { name:'stripe-amber', colors:['#FFFBEB','#F59E0B'], fn: coverStripes('#FFFBEB','#F59E0B') },
    { name:'stripe-purple',colors:['#F5F3FF','#8B5CF6'], fn: coverStripes('#F5F3FF','#8B5CF6') },
    { name:'grid-blue',   colors:['#EFF6FF','#BFDBFE'], fn: coverGrid('#EFF6FF','#BFDBFE') },
    { name:'grid-slate',  colors:['#F8FAFC','#CBD5E1'], fn: coverGrid('#F8FAFC','#CBD5E1') },
    { name:'grid-purple', colors:['#F5F3FF','#DDD6FE'], fn: coverGrid('#F5F3FF','#DDD6FE') },
    { name:'grid-rose',   colors:['#FFF1F2','#FECDD3'], fn: coverGrid('#FFF1F2','#FECDD3') },
    { name:'grid-amber',  colors:['#FFFBEB','#FDE68A'], fn: coverGrid('#FFFBEB','#FDE68A') },
    { name:'wave-ocean',  colors:['#0EA5E9','#1B5EC7'], fn: coverWave('#0EA5E9','#1B5EC7') },
    { name:'wave-sunset', colors:['#F59E0B','#EF4444'], fn: coverWave('#F59E0B','#EF4444') },
    { name:'wave-forest', colors:['#10B981','#059669'], fn: coverWave('#10B981','#059669') },
    { name:'wave-galaxy', colors:['#6366F1','#8B5CF6'], fn: coverWave('#6366F1','#8B5CF6') },
    { name:'mesh-ocean',  colors:['#0EA5E9','#1B5EC7'], fn: coverMesh('#0EA5E9','#1B5EC7') },
    { name:'mesh-ink',    colors:['#0A1628','#1B5EC7'], fn: coverMesh('#0A1628','#1B5EC7') },
    { name:'mesh-sunset', colors:['#F59E0B','#EF4444'], fn: coverMesh('#F59E0B','#EF4444') },
    { name:'mesh-forest', colors:['#10B981','#059669'], fn: coverMesh('#10B981','#059669') },
    { name:'mesh-galaxy', colors:['#6366F1','#EC4899'], fn: coverMesh('#6366F1','#EC4899') },
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
      ? [{ id:'gradients', label:'Gradients' }, { id:'patterns', label:'Patterns' }]
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
        buildAvatarPane(pane, opts, type);
      } else if (t.id === 'gradients') {
        buildGradientPane(pane, opts, type, letter);
      } else if (t.id === 'patterns') {
        buildPatternPane(pane, opts, type);
      }

      container.appendChild(pane);
    });
  }

  function buildAvatarPane(pane, opts, type) {
    var fileInput = document.getElementById(opts.inputId);
    var previewEl = opts.previewId ? document.getElementById(opts.previewId) : null;
    var isLogo = type === 'logo';

    var grid = document.createElement('div');
    grid.className = 'oc-picker-grid';

    PALETTE.forEach(function (color) {
      var cc = crispCanvas(64);
      if (isLogo) drawEnterpriseIcon(cc.ctx, 64, color);
      else        drawPerson(cc.ctx, 64, color);
      if (isLogo) { cc.cvs.style.borderRadius = '10px'; }
      var item = document.createElement('div');
      item.className = 'oc-picker-item';
      if (isLogo) item.style.borderRadius = '10px';
      item.appendChild(cc.cvs);
      item.addEventListener('click', function () {
        var big = document.createElement('canvas');
        big.width = big.height = 300;
        if (isLogo) drawEnterpriseIcon(big.getContext('2d'), 300, color);
        else        drawPerson(big.getContext('2d'), 300, color);
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

    var isLogo = type === 'logo';

    GRADIENTS.forEach(function (pair) {
      var cc = isCover ? crispCanvas(88, 40) : crispCanvas(64);
      if (isCover)        drawCoverGradient(cc.ctx, 88, 40, pair[0], pair[1]);
      else if (isLogo)    drawEnterpriseGradient(cc.ctx, 64, pair[0], pair[1]);
      else                drawGradientCircle(cc.ctx, 64, pair[0], pair[1]);
      var item = document.createElement('div');
      item.className = 'oc-picker-item';
      if (isCover || isLogo) item.style.borderRadius = '10px';
      item.appendChild(cc.cvs);
      item.addEventListener('click', function () {
        var big = document.createElement('canvas');
        if (isCover) {
          big.width = 1200; big.height = 300;
          drawCoverGradient(big.getContext('2d'), 1200, 300, pair[0], pair[1]);
        } else if (isLogo) {
          big.width = big.height = 300;
          drawEnterpriseGradient(big.getContext('2d'), 300, pair[0], pair[1]);
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

  function overlayEnterpriseOnCanvas(ctx, s) {
    if (!_entImg) return;
    var pad = Math.round(s * 0.16);
    var tmp = document.createElement('canvas');
    tmp.width = tmp.height = s;
    var tc = tmp.getContext('2d');
    tc.fillStyle = '#000'; tc.fillRect(0, 0, s, s);
    try { tc.filter = 'invert(1)'; } catch (e) {}
    tc.drawImage(_entImg, pad, pad, s - pad * 2, s - pad * 2);
    try { tc.filter = 'none'; } catch (e) {}
    ctx.globalCompositeOperation = 'screen';
    ctx.drawImage(tmp, 0, 0);
    ctx.globalCompositeOperation = 'source-over';
  }

  function buildPatternPane(pane, opts, type) {
    var fileInput = document.getElementById(opts.inputId);
    var previewEl = opts.previewId ? document.getElementById(opts.previewId) : null;
    var isCover = type === 'cover';
    var isLogo  = type === 'logo';
    var list = isCover ? COVER_PATTERNS : PATTERNS;

    var grid = document.createElement('div');
    grid.className = isCover ? 'oc-picker-grid oc-picker-grid--cover' : 'oc-picker-grid';

    list.forEach(function (pat) {
      var cc = isCover ? crispCanvas(88, 40) : crispCanvas(64);
      if (isCover) pat.fn(cc.ctx, 88, 40); else pat.fn(cc.ctx, 64);
      if (isLogo) overlayEnterpriseOnCanvas(cc.ctx, 64);
      var item = document.createElement('div');
      item.className = 'oc-picker-item';
      if (isCover || isLogo) item.style.borderRadius = '10px';
      item.appendChild(cc.cvs);
      item.addEventListener('click', function () {
        var big = document.createElement('canvas');
        if (isCover) {
          big.width = 1200; big.height = 300;
          pat.fn(big.getContext('2d'), 1200, 300);
        } else {
          big.width = big.height = 300;
          pat.fn(big.getContext('2d'), 300);
          if (isLogo) overlayEnterpriseOnCanvas(big.getContext('2d'), 300);
        }
        applyToInput(big, fileInput, previewEl, 'pattern_logo.png');
        if (!isCover) setHeroBg(pane.closest('.oc-picker-panel'),
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
