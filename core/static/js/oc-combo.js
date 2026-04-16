/**
 * oc-combo.js — Searchable + creatable combobox for industry (and other) fields.
 *
 * Two usage patterns:
 *
 * 1. Static HTML (existing pattern in create_project, create_company, groups, pages):
 *    <div class="oc-combo" data-hidden="my-hidden-id">
 *      <input type="hidden" id="my-hidden-id" name="industry" value="tech">
 *      <input type="text" class="oc-combo__input" placeholder="Search…">
 *      <ul class="oc-combo__list">
 *        <li class="oc-combo__item" data-value="tech">Technology</li>
 *        ...
 *      </ul>
 *    </div>
 *    Add data-creatable="false" to disable the "Add X" option.
 *
 * 2. Auto-upgrade an existing <select>:
 *    <select name="industry" data-combo>          ← creatable (form fields)
 *    <select name="industry" data-combo-filter>   ← search-only (filter bars)
 */
(function () {
  'use strict';

  /* ── Core combo behaviour ─────────────────────────────────── */
  function initComboEl(wrap, hiddenInput, textInput, list, creatable, autoSubmit) {
    var items  = Array.from(list.querySelectorAll('.oc-combo__item'));
    var addRow = null;

    function openList() {
      filterList();
      list.style.display = 'block';
      textInput.setAttribute('aria-expanded', 'true');
    }

    function closeList() {
      list.style.display = 'none';
      textInput.setAttribute('aria-expanded', 'false');
    }

    function filterList() {
      var q = textInput.value.trim().toLowerCase();
      var anyVisible = false;

      items.forEach(function (li) {
        var show = !q || li.textContent.toLowerCase().indexOf(q) !== -1;
        li.style.display = show ? '' : 'none';
        if (show) anyVisible = true;
      });

      var typed = textInput.value.trim();

      // "Add X" row (creatable mode only)
      if (creatable && typed && !anyVisible) {
        if (!addRow) {
          addRow = document.createElement('li');
          addRow.className = 'oc-combo__add';
          list.appendChild(addRow);
        }
        addRow.textContent = '+ Add "' + typed + '"';
        addRow.style.display = '';
        addRow.onmousedown = function (e) {
          e.preventDefault();
          hiddenInput.value = typed;
          textInput.value   = typed;
          closeList();
        };
      } else if (addRow) {
        addRow.style.display = 'none';
      }

      // Keep hidden in sync as user types (allows free-text if nothing selected)
      hiddenInput.value = typed;
    }

    textInput.addEventListener('focus',  openList);
    textInput.addEventListener('input',  filterList);
    textInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeList();
    });

    items.forEach(function (li) {
      li.addEventListener('mousedown', function (e) {
        e.preventDefault(); // prevent blur firing before click
        hiddenInput.value = li.dataset.value;
        textInput.value   = li.textContent.trim();
        closeList();
        if (autoSubmit) {
          var form = hiddenInput.closest('form');
          if (form) form.submit();
        }
      });
    });

    document.addEventListener('mousedown', function (e) {
      if (!wrap.contains(e.target)) closeList();
    });
  }

  /* ── Resolve stored key → display label ──────────────────── */
  function resolveLabel(list, storedValue) {
    if (!storedValue) return '';
    var item = list.querySelector('.oc-combo__item[data-value="' + storedValue.replace(/"/g, '\\"') + '"]');
    return item ? item.textContent.trim() : storedValue;
  }

  /* ── Pattern 1: static .oc-combo[data-hidden] elements ───── */
  function initStaticCombos(root) {
    (root || document).querySelectorAll('.oc-combo[data-hidden]').forEach(function (combo) {
      if (combo._ocComboInit) return; // already done
      combo._ocComboInit = true;

      var hiddenInput = document.getElementById(combo.dataset.hidden);
      if (!hiddenInput) return;
      var textInput = combo.querySelector('.oc-combo__input');
      var list      = combo.querySelector('.oc-combo__list');
      if (!textInput || !list) return;

      var creatable   = combo.dataset.creatable !== 'false';
      var autoSubmit  = combo.hasAttribute('data-auto-submit');

      // Show label (not raw key) for pre-populated edit forms
      if (hiddenInput.value && textInput.value === hiddenInput.value) {
        var label = resolveLabel(list, hiddenInput.value);
        if (label) textInput.value = label;
      }

      initComboEl(combo, hiddenInput, textInput, list, creatable, autoSubmit);
    });
  }

  /* ── Pattern 2: auto-upgrade <select data-combo[*]> ─────── */
  function upgradeSelects(root) {
    (root || document).querySelectorAll('select[data-combo], select[data-combo-filter]').forEach(function (select) {
      if (select._ocComboInit) return;
      select._ocComboInit = true;

      var creatable   = select.hasAttribute('data-combo');
      var name        = select.name;
      var id          = select.id;
      var currentVal  = select.value;
      var placeholder = select.dataset.placeholder ||
                        (creatable ? 'Search or type a custom industry…' : 'Search industries…');

      // Collect options (skip blank placeholder)
      var options = [];
      Array.from(select.options).forEach(function (opt) {
        if (opt.value) options.push({ value: opt.value, label: opt.text });
      });

      // Build wrapper
      var wrap = document.createElement('div');
      wrap.className = 'oc-combo';

      // Hidden input for form submission
      var hidden  = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = name;
      hidden.value = currentVal;
      if (id) { hidden.id = id; }
      if (select.required) hidden.required = true;
      wrap.appendChild(hidden);

      // Visible search input
      var textInput         = document.createElement('input');
      textInput.type        = 'text';
      textInput.className   = 'oc-input oc-combo__input';
      textInput.autocomplete = 'off';
      textInput.placeholder  = placeholder;
      // Show label for pre-selected value
      var matched = options.find(function (o) { return o.value === currentVal; });
      textInput.value = matched ? matched.label : (currentVal || '');
      wrap.appendChild(textInput);

      // Dropdown list
      var list      = document.createElement('ul');
      list.className = 'oc-combo__list';
      list.style.display = 'none';
      options.forEach(function (opt) {
        var li         = document.createElement('li');
        li.className   = 'oc-combo__item';
        li.dataset.value = opt.value;
        li.textContent = opt.label;
        list.appendChild(li);
      });
      wrap.appendChild(list);

      // Copy any width/style class from the original select (except oc-select itself)
      if (select.className) {
        var extra = select.className.replace(/\boc-select\b/g, '').trim();
        if (extra) wrap.className += ' ' + extra;
      }

      var autoSubmit = select.hasAttribute('data-auto-submit');
      select.parentNode.replaceChild(wrap, select);
      initComboEl(wrap, hidden, textInput, list, creatable, autoSubmit);
    });
  }

  /* ── Public API ────────────────────────────────────────────── */
  function init(root) {
    initStaticCombos(root);
    upgradeSelects(root);
  }

  window.ocComboInit = init;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
