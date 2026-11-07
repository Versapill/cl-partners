/* CL Partners — site behaviour (no dependencies) */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     CONFIG — connect form endpoints here when ready.
     Each endpoint receives a JSON POST. Leave empty to run in demo mode
     (form validates and completes, data is logged to console only).
     Works with Formspree, Make/Zapier webhooks, Netlify functions, etc.
     ------------------------------------------------------------------ */
  var CONFIG = {
    leadEndpoint: '',     // Executive Field Notes downloads
    contactEndpoint: '',  // Contact page
    careersEndpoint: ''   // Join our team page
  };

  var doc = document.documentElement;
  doc.classList.remove('no-js');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Header scroll state ---------- */
  var header = document.querySelector('.site-header');
  var onScroll = function () { if (header) header.classList.toggle('is-scrolled', window.scrollY > 24); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Dropdown ---------- */
  document.querySelectorAll('[data-dropdown]').forEach(function (btn) {
    var menu = document.getElementById(btn.getAttribute('aria-controls'));
    var li = btn.parentElement;
    var open = function (v) { btn.setAttribute('aria-expanded', String(v)); menu.classList.toggle('is-open', v); };
    btn.addEventListener('click', function (e) { e.stopPropagation(); open(btn.getAttribute('aria-expanded') !== 'true'); });
    li.addEventListener('mouseenter', function () { if (window.matchMedia('(hover: hover)').matches) open(true); });
    li.addEventListener('mouseleave', function () { if (window.matchMedia('(hover: hover)').matches) open(false); });
    li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) open(false); });
    document.addEventListener('click', function () { open(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') { open(false); btn.focus(); } });
  });

  /* ---------- Mobile menu ---------- */
  var mm = document.getElementById('mobile-menu');
  var mmToggle = document.querySelector('.menu-toggle');
  if (mm && mmToggle) {
    var mmClose = mm.querySelector('.menu-close');
    var setMenu = function (v) {
      mm.classList.toggle('is-open', v);
      mm.setAttribute('aria-hidden', String(!v));
      mmToggle.setAttribute('aria-expanded', String(v));
      document.body.classList.toggle('no-scroll', v);
      if (v) { mmClose.focus(); } else { mmToggle.focus(); }
    };
    mmToggle.addEventListener('click', function () { setMenu(true); });
    mmClose.addEventListener('click', function () { setMenu(false); });
    mm.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); trapFocus(e, mm); });
    mm.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { document.body.classList.remove('no-scroll'); }); });
  }

  /* ---------- Reveal on scroll ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- Sub-nav active state (resources) ---------- */
  var subLinks = document.querySelectorAll('.subnav a');
  if (subLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    subLinks.forEach(function (a) { var t = document.querySelector(a.getAttribute('href')); if (t) map[t.id] = a; });
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { subLinks.forEach(function (l) { l.classList.remove('is-active'); l.removeAttribute('aria-current'); }); var l = map[en.target.id]; if (l) { l.classList.add('is-active'); l.setAttribute('aria-current', 'true'); } }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(map).forEach(function (id) { so.observe(document.getElementById(id)); });
  }

  /* ---------- Focus trap helper ---------- */
  function trapFocus(e, container) {
    if (e.key !== 'Tab') return;
    var f = container.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select, textarea, video[controls], [tabindex]:not([tabindex="-1"])');
    f = Array.prototype.filter.call(f, function (el) { return el.offsetParent !== null; });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  /* ---------- Modals ---------- */
  var lastTrigger = null;
  function openModal(modal, trigger) {
    lastTrigger = trigger || document.activeElement;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('no-scroll');
    var focusEl = modal.querySelector('[data-autofocus]') || modal.querySelector('.modal-close');
    setTimeout(function () { focusEl && focusEl.focus(); }, 60);
  }
  function closeModal(modal) {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('no-scroll');
    var v = modal.querySelector('video'); if (v) v.pause();
    if (lastTrigger) lastTrigger.focus();
  }
  document.querySelectorAll('.modal').forEach(function (m) {
    m.querySelectorAll('[data-close]').forEach(function (c) { c.addEventListener('click', function () { closeModal(m); }); });
    m.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeModal(m); trapFocus(e, m); });
  });

  /* Video modal */
  var vModal = document.getElementById('video-modal');
  document.querySelectorAll('[data-video-open]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (!vModal) return;
      openModal(vModal, b);
      var v = vModal.querySelector('video');
      if (v) { v.currentTime = 0; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
    });
  });

  /* Inline video */
  document.querySelectorAll('[data-inline-video]').forEach(function (frame) {
    var v = frame.querySelector('video');
    var btn = frame.querySelector('.video-overlay');
    btn.addEventListener('click', function () {
      frame.classList.add('is-playing');
      v.setAttribute('controls', '');
      v.muted = false;
      var p = v.play(); if (p && p.catch) p.catch(function () {});
      v.focus();
    });
    v.addEventListener('ended', function () { frame.classList.remove('is-playing'); v.removeAttribute('controls'); });
  });

  /* ---------- Lead magnet (gated downloads) ---------- */
  var RESOURCES = {
    efn01: { no: 'Executive Field Note 01', title: 'Before You Change Anything', sub: '7 questions worth asking when stepping into a new leadership role', file: 'assets/docs/CL-Partners-EFN01-Before-You-Change-Anything.pdf' },
    efn02: { no: 'Executive Field Note 02', title: 'After Everyone Agrees', sub: '7 questions to turn agreement into action', file: 'assets/docs/CL-Partners-EFN02-After-Everyone-Agrees.pdf' },
    efn03: { no: 'Executive Field Note 03', title: 'When Everything Is a Priority', sub: '7 questions to make choices when your team is overloaded', file: 'assets/docs/CL-Partners-EFN03-When-Everything-Is-a-Priority.pdf' }
  };
  var STORE_KEY = 'clp_lead';
  function getLead() { try { return JSON.parse(localStorage.getItem(STORE_KEY) || 'null'); } catch (e) { return null; } }
  function setLead(v) { try { localStorage.setItem(STORE_KEY, JSON.stringify(v)); } catch (e) {} }

  function triggerDownload(res) {
    var a = document.createElement('a');
    a.href = res.file; a.download = res.file.split('/').pop(); a.rel = 'noopener';
    document.body.appendChild(a); a.click(); a.remove();
  }

  var leadModal = document.getElementById('lead-modal');
  if (leadModal) {
    var leadForm = leadModal.querySelector('form');
    var leadSuccess = leadModal.querySelector('.form-success');
    var current = null;

    document.querySelectorAll('[data-resource]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        current = RESOURCES[btn.getAttribute('data-resource')];
        if (!current) return;
        leadModal.querySelector('[data-res-no]').textContent = current.no;
        leadModal.querySelector('[data-res-title]').textContent = current.title;
        leadModal.querySelector('[data-res-sub]').textContent = current.sub;
        leadModal.querySelector('[data-res-link]').href = current.file;
        var known = getLead();
        leadForm.hidden = false; leadSuccess.classList.remove('is-visible');
        resetErrors(leadForm);
        if (known) {
          // Returning visitor: prefill so they can confirm in one click
          ['name', 'company', 'email'].forEach(function (k) { var i = leadForm.elements[k]; if (i && known[k]) i.value = known[k]; });
        }
        openModal(leadModal, btn);
      });
    });

    leadForm.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validate(leadForm)) return;
      var data = formData(leadForm);
      data.resource = current ? current.title : '';
      submit(leadForm, CONFIG.leadEndpoint, data, function () {
        setLead({ name: data.name, company: data.company, email: data.email });
        leadForm.hidden = true;
        leadSuccess.classList.add('is-visible');
        leadSuccess.querySelector('[data-success-name]').textContent = (data.name || '').split(' ')[0];
        if (current) triggerDownload(current);
        var dl = leadSuccess.querySelector('[data-res-link]'); if (dl) dl.focus();
      });
    });
  }

  /* ---------- Generic forms (contact, careers) ---------- */
  document.querySelectorAll('form[data-form]').forEach(function (form) {
    var type = form.getAttribute('data-form');
    var endpoint = type === 'contact' ? CONFIG.contactEndpoint : CONFIG.careersEndpoint;
    var success = form.parentElement.querySelector('.form-success');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validate(form)) return;
      submit(form, endpoint, formData(form), function () {
        form.hidden = true;
        if (success) { success.classList.add('is-visible'); success.setAttribute('tabindex', '-1'); success.focus(); }
      });
    });
  });

  /* ---------- Validation ---------- */
  var MESSAGES = {
    name: 'Please enter your full name.',
    company: 'Please enter your company name.',
    email: 'Please enter a valid email address, e.g. name@company.com.',
    role: 'Please enter your role.',
    message: 'Please describe your situation in a few words.',
    consent: 'Please confirm you agree to the privacy notice.',
    interest: 'Please choose the role you are interested in.',
    linkedin: 'Please enter a valid URL starting with https://',
    default: 'Please complete this field.'
  };
  function fieldOf(input) { return input.closest('.field') || input.closest('.check-field'); }
  function checkInput(input) {
    var valid = input.checkValidity();
    var f = fieldOf(input); if (!f) return valid;
    f.classList.toggle('has-error', !valid);
    input.setAttribute('aria-invalid', String(!valid));
    var err = f.querySelector('.field-error');
    if (err && !valid) err.textContent = MESSAGES[input.name] || MESSAGES.default;
    return valid;
  }
  function resetErrors(form) {
    form.querySelectorAll('.has-error').forEach(function (f) { f.classList.remove('has-error'); });
    form.querySelectorAll('[aria-invalid]').forEach(function (i) { i.removeAttribute('aria-invalid'); });
    var s = form.querySelector('.error-summary'); if (s) s.classList.remove('is-visible');
  }
  function validate(form) {
    var inputs = form.querySelectorAll('input, textarea, select');
    var bad = [];
    inputs.forEach(function (i) { if (i.type !== 'hidden' && !checkInput(i)) bad.push(i); });
    var summary = form.querySelector('.error-summary');
    if (bad.length) {
      if (summary && bad.length > 1) {
        summary.innerHTML = '<strong>Please correct ' + bad.length + ' fields:</strong><ul>' + bad.map(function (i) {
          return '<li><a href="#' + i.id + '">' + (MESSAGES[i.name] || MESSAGES.default) + '</a></li>';
        }).join('') + '</ul>';
        summary.classList.add('is-visible');
        summary.focus();
      } else { bad[0].focus(); }
      return false;
    }
    if (summary) summary.classList.remove('is-visible');
    return true;
  }
  document.addEventListener('blur', function (e) {
    var t = e.target;
    if (t.matches && t.matches('form input, form textarea, form select') && (t.value || fieldOf(t) && fieldOf(t).classList.contains('has-error'))) checkInput(t);
  }, true);
  document.addEventListener('input', function (e) {
    var t = e.target; var f = t.closest && fieldOf(t);
    if (f && f.classList.contains('has-error')) checkInput(t);
  });

  function formData(form) {
    var o = {};
    new FormData(form).forEach(function (v, k) { o[k] = v; });
    o.page = location.pathname; o.submittedAt = new Date().toISOString();
    return o;
  }
  function submit(form, endpoint, data, done) {
    if (form.elements['website'] && form.elements['website'].value) return; // honeypot
    var btn = form.querySelector('[type="submit"]');
    btn.setAttribute('aria-busy', 'true'); btn.disabled = true;
    var finish = function () { btn.removeAttribute('aria-busy'); btn.disabled = false; };
    if (!endpoint) {
      // Demo mode — no endpoint configured yet
      console.info('[CL Partners] Form submission (demo mode, not sent):', data);
      setTimeout(function () { finish(); done(); }, 700);
      return;
    }
    fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); finish(); done(); })
      .catch(function () {
        finish();
        var s = form.querySelector('.error-summary');
        if (s) { s.innerHTML = 'Sorry, something went wrong sending your details. Please try again, or email <a href="mailto:welcome@cl-partners.ch">welcome@cl-partners.ch</a>.'; s.classList.add('is-visible'); s.focus(); }
      });
  }

  /* ---------- Team check-in (Team Effectiveness toolkit) ---------- */
  document.querySelectorAll('[data-checkin]').forEach(function (form) {
    var opts = ['1', '2', '3', '4', '5', 'N/O'];
    var rows = form.querySelectorAll('.ci-row');
    rows.forEach(function (row, i) {
      var text = row.querySelector('.ci-text').textContent;
      var group = document.createElement('div');
      group.className = 'ci-scale'; group.setAttribute('role', 'radiogroup'); group.setAttribute('aria-label', text);
      opts.forEach(function (o) {
        var id = 'ci' + i + '-' + o.replace('/', '');
        var lab = document.createElement('label'); lab.className = 'ci-opt' + (o === 'N/O' ? ' na' : ''); lab.htmlFor = id;
        lab.innerHTML = '<input type="radio" id="' + id + '" name="ci' + i + '" value="' + o + '"><span>' + o + '</span>';
        group.appendChild(lab);
      });
      row.appendChild(group);
    });
    var empty = form.querySelector('.ci-empty'), box = form.querySelector('.ci-priorities'), list = form.querySelector('.ci-list');
    function update() {
      var rated = [];
      rows.forEach(function (row, i) {
        var c = form.querySelector('input[name="ci' + i + '"]:checked');
        if (c && c.value !== 'N/O') rated.push({ i: i, v: +c.value, cards: row.getAttribute('data-cards'), text: row.querySelector('.ci-text').textContent, p: row.closest('fieldset').querySelector('legend').textContent.trim() });
      });
      if (rated.length < 3) { empty.hidden = false; box.hidden = true; return; }
      rated.sort(function (a, b) { return a.v - b.v || a.i - b.i; });
      list.innerHTML = rated.slice(0, 3).map(function (r, n) {
        return '<li><span class="pr-n">Priority ' + (n + 1) + '</span><span class="pr-t"><strong>' + r.text + '</strong><small>' + r.p + ' · rated ' + r.v + '/5</small></span><span class="pr-c">Cards ' + r.cards + '</span></li>';
      }).join('');
      empty.hidden = true; box.hidden = false;
    }
    form.addEventListener('change', update);
    form.addEventListener('reset', function () { setTimeout(update, 0); });
  });

  /* ---------- Year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
