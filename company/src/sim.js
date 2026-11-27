  /* ── USSD simulator: scripted entirely in the browser. Nothing is sent anywhere. ── */
  var out = $('#sim-out'), form = $('#sim-form'), input = $('#sim-input');
  var FOOT = '\n0.Back 00.Home 000.Logout';
  var START = { name: 'Mama', num: '0700 000 101' };
  var contacts, stack, state, draft;
  var EMERG = '999 Police, fire, ambulance\n112 Emergency (any mobile)\n911 Emergency (any mobile)\n1199 Kenya Red Cross\n1195 Gender violence helpline\n116 Childline Kenya';
  function reset() {
    contacts = [START, { name: 'Office', num: '0700 000 102' }, { name: 'Boda guy', num: '0700 000 103' }, { name: 'Shosho', num: '0700 000 104' }];
    stack = []; draft = {};
  }
  function list(arr) { return arr.length ? arr.map(function (c, i) { return (i + 1) + '. ' + c.name + ' ' + c.num; }).join('\n') : '(no contacts)'; }
  var MENU = 'Remote Phone-Book\n1. My contacts\n2. Emergency numbers\n3. My organisations\n4. Add contact\n5. Search contact\n6. Delete contact\n7. SMS me my contacts\n000. Log out';
  var screens = {
    phone: function () { return 'Welcome to Remote Phone-Book\nEnter your phone number:'; },
    pin: function () { return 'Demo: any number works.\nYou entered ' + draft.phone + '\n\nEnter your PIN:'; },
    pinErr: function () { return 'PIN must be 4 digits.\n\nEnter your PIN:'; },
    menu: function () { return MENU; },
    contacts: function () { return 'My contacts\n' + list(contacts) + FOOT; },
    emerg: function () { return 'Emergency numbers\n' + EMERG + FOOT; },
    orgs: function () { return 'My organisations\n1. Demo Academy (school)' + FOOT; },
    school: function () { return 'Demo Academy\n1. Notices (1)\n2. Contacts\n3. Emergency contacts' + FOOT; },
    notices: function () { return 'Notices\nClosing day is Friday. Pick-up at 12:30pm. Fees for next term are due before opening day.' + FOOT; },
    schoolContacts: function () { return 'Demo Academy contacts\n1. Head teacher 0700 000 201\n2. Bursar 0700 000 202\n3. Class teacher 0700 000 203' + FOOT; },
    schoolEmerg: function () { return 'Demo Academy emergency\n1. School nurse 0700 000 211\n2. Gate 0700 000 212\n999 Police, fire, ambulance' + FOOT; },
    addName: function () { return 'Add contact\nEnter the name:' + FOOT; },
    addNum: function () { return 'Add contact\nName: ' + draft.name + '\nEnter the number:' + FOOT; },
    added: function () { return 'Saved ' + draft.name + ' ' + draft.num + '.\n(Demo: kept in this page only.)' + FOOT; },
    search: function () { return 'Search contact\nEnter a name:' + FOOT; },
    found: function () {
      var q = draft.q.toLowerCase(), r = contacts.filter(function (c) { return c.name.toLowerCase().indexOf(q) > -1; });
      return 'Results for "' + draft.q + '"\n' + (r.length ? list(r) : 'No match.') + FOOT;
    },
    del: function () { return 'Delete contact\n' + list(contacts) + '\nReply with a number.' + FOOT; },
    deleted: function () { return 'Deleted ' + draft.gone + '.\n(Demo only.)' + FOOT; },
    sms: function () { return 'Done.\nIn the real service your contacts arrive by SMS.' + FOOT; },
    bad: function () { return 'Invalid choice.\nPlease try again.' + FOOT; },
    bye: function () { return 'Thank you for using Remote Phone-Book.\n\nDemo ended. Press Send to start again.'; }
  };
  function show(name, push) {
    if (push && state) stack.push(state);
    state = name;
    out.textContent = screens[name]();
    out.scrollTop = 0;
    input.value = '';
  }
  function home() { stack = []; state = null; show('menu'); }
  function start() { reset(); state = null; show('phone'); }
  function nav(v) {   /* shared footer keys on inner screens */
    if (v === '000') { show('bye'); return true; }
    if (v === '00') { home(); return true; }
    if (v === '0') { state = stack.pop() || 'menu'; if (state === 'bad') state = stack.pop() || 'menu'; out.textContent = screens[state](); input.value = ''; return true; }
    return false;
  }
  var MAIN = { '1': 'contacts', '2': 'emerg', '3': 'orgs', '4': 'addName', '5': 'search', '6': 'del', '7': 'sms' };
  function send() {
    var v = input.value.trim();
    switch (state) {
      case 'phone': if (!v) return; draft.phone = v; show('pin'); return;
      case 'pin': case 'pinErr':
        if (/^\d{4}$/.test(v)) home(); else show('pinErr'); return;
      case 'bye': start(); return;
      case 'menu':
        if (v === '000') show('bye'); else if (MAIN[v]) show(MAIN[v], true); else show('bad', true); return;
    }
    if (nav(v)) return;
    if (state === 'orgs') { v === '1' ? show('school', true) : show('bad', true); return; }
    if (state === 'school') { var m = { '1': 'notices', '2': 'schoolContacts', '3': 'schoolEmerg' }[v]; show(m || 'bad', true); return; }
    if (state === 'addName') { if (!v) return; draft.name = v.slice(0, 16); show('addNum'); return; }
    if (state === 'addNum') {
      if (!/^\+?\d{3,15}$/.test(v.replace(/\s/g, ''))) { out.textContent = 'Numbers only, please.\nEnter the number:' + FOOT; input.value = ''; return; }
      draft.num = v; contacts.push({ name: draft.name, num: v }); show('added'); return;
    }
    if (state === 'search') { if (!v) return; draft.q = v; show('found'); return; }
    if (state === 'del') {
      var n = parseInt(v, 10);
      if (n >= 1 && n <= contacts.length && String(n) === v) { draft.gone = contacts.splice(n - 1, 1)[0].name; show('deleted'); }
      else show('bad', true);
      return;
    }
    show('bad', true);
  }
  if (out && form) {
    start();
    form.addEventListener('submit', function (e) { e.preventDefault(); send(); });
    $('#sim').addEventListener('click', function (e) {
      var b = e.target.closest('button[data-k]'); if (!b) return;
      var k = b.getAttribute('data-k');
      if (k === 'send') send();
      else if (k === 'del') input.value = input.value.slice(0, -1);
      else if (input.value.length < 20) input.value += k;
    });
    /* Typing while the screen has focus goes to the reply line. */
    out.addEventListener('keydown', function (e) {
      if (/^[0-9*#a-zA-Z+ ]$/.test(e.key) && !e.ctrlKey && !e.metaKey && !e.altKey) { input.focus(); }
      else if (e.key === 'Enter') { e.preventDefault(); send(); }
    });
  }

