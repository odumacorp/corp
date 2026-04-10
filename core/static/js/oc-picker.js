/* ============================================================
   OC Avatar / Photo Picker  —  Oduma Corp
   Usage: ocPicker.open({ inputId, previewId, type, letterSrc, containerId })
   type: 'person' | 'logo' | 'cover'
   ============================================================ */
(function (window) {
  'use strict';

  var PALETTE = [
    '#1B5EC7','#0EA5E9','#10B981','#F59E0B',
    '#EF4444','#8B5CF6','#EC4899','#06B6D4',
    '#F97316','#6366F1','#14B8A6','#F43F5E',
    '#0A1628','#7C3AED','#059669','#DC2626'
  ];

  var COVERS = [
    ['#1B5EC7','#0EA5E9'],['#0A1628','#1B5EC7'],
    ['#10B981','#059669'],['#F59E0B','#EF4444'],
    ['#8B5CF6','#EC4899'],['#06B6D4','#6366F1'],
    ['#0A1628','#374151'],['#1B5EC7','#6366F1'],
    ['#059669','#06B6D4'],['#DC2626','#F97316'],
    ['#4B0082','#7C3AED'],['#0EA5E9','#10B981']
  ];

  /* ── Drawers ── */
  function drawPerson(ctx, s, color) {
    ctx.clearRect(0, 0, s, s);
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(s/2, s/2, s/2, 0, Math.PI*2); ctx.fill();
    ctx.save();
    ctx.beginPath(); ctx.arc(s/2, s/2, s/2, 0, Math.PI*2); ctx.clip();
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.beginPath(); ctx.arc(s/2, s*0.37, s*0.19, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(s/2, s*0.82, s*0.31, s*0.24, 0, 0, Math.PI); ctx.fill();
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

  function drawCover(ctx, w, h, from, to) {
    ctx.clearRect(0, 0, w, h);
    var g = ctx.createLinearGradient(0, 0, w, h);
    g.addColorStop(0, from); g.addColorStop(1, to);
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  }

  /* ── Thumb factory ── */
  function makeThumbs(type, letter) {
    if (type === 'cover') {
      return COVERS.map(function (pair) {
        var cvs = document.createElement('canvas');
        cvs.width = 88; cvs.height = 44;
        drawCover(cvs.getContext('2d'), 88, 44, pair[0], pair[1]);
        return { cvs: cvs, pair: pair };
      });
    }
    return PALETTE.map(function (c) {
      var cvs = document.createElement('canvas');
      cvs.width = cvs.height = 48;
      if (type === 'person') drawPerson(cvs.getContext('2d'), 48, c);
      else drawLogo(cvs.getContext('2d'), 48, c, letter);
      return { cvs: cvs, color: c };
    });
  }

  /* ── Assign blob to file input + update preview ── */
  function applyToInput(bigCvs, fileInput, previewEl, fname) {
    bigCvs.toBlob(function (blob) {
      if (previewEl) {
        previewEl.src = URL.createObjectURL(blob);
        previewEl.style.display = 'block';
        var placeholder = previewEl.parentElement && previewEl.parentElement.querySelector('.oc-upload-placeholder');
        if (placeholder) placeholder.style.display = 'none';
      }
      try {
        var file = new File([blob], fname, { type: 'image/png' });
        var dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
      } catch (e) { /* DataTransfer not supported in this browser */ }
    }, 'image/png');
  }

  /* ── Main open function ── */
  function openPicker(opts) {
    var fileInput = document.getElementById(opts.inputId);
    var container = document.getElementById(opts.containerId);
    if (!fileInput || !container) return;

    // Toggle off
    if (container.style.display !== 'none' && container.innerHTML !== '') {
      container.style.display = 'none'; return;
    }

    // Resolve letter
    var letter = 'O';
    if (opts.letterSrc) {
      var lel = document.getElementById(opts.letterSrc);
      if (lel && lel.value.trim()) letter = lel.value.trim().charAt(0).toUpperCase();
    }

    var type = opts.type || 'person';
    var thumbs = makeThumbs(type, letter);

    // Build panel
    container.innerHTML = '';
    var label = document.createElement('p');
    label.className = 'oc-picker-label';
    label.textContent = type === 'cover' ? 'Pick a cover gradient' : 'Pick an avatar';
    container.appendChild(label);

    var grid = document.createElement('div');
    grid.className = 'oc-picker-grid';

    thumbs.forEach(function (t) {
      var item = document.createElement('div');
      item.className = 'oc-picker-item';
      item.appendChild(t.cvs);
      item.addEventListener('click', function () {
        // Full-size canvas
        var big = document.createElement('canvas');
        if (type === 'cover') {
          big.width = 1200; big.height = 300;
          drawCover(big.getContext('2d'), 1200, 300, t.pair[0], t.pair[1]);
        } else {
          big.width = big.height = 300;
          if (type === 'person') drawPerson(big.getContext('2d'), 300, t.color);
          else drawLogo(big.getContext('2d'), 300, t.color, letter);
        }
        var previewEl = opts.previewId ? document.getElementById(opts.previewId) : null;
        applyToInput(big, fileInput, previewEl, type + '_avatar.png');
        grid.querySelectorAll('.oc-picker-item').forEach(function (el) { el.classList.remove('oc-picker-item--selected'); });
        item.classList.add('oc-picker-item--selected');
        setTimeout(function () { container.style.display = 'none'; }, 300);
      });
      grid.appendChild(item);
    });

    container.appendChild(grid);
    container.style.display = 'block';
  }

  // Close on outside click
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.oc-picker-panel').forEach(function (panel) {
      var wrap = panel.closest('[data-picker-wrap]') || panel.parentElement;
      if (wrap && !wrap.contains(e.target)) panel.style.display = 'none';
    });
  });

  window.ocPicker = { open: openPicker };
})(window);
