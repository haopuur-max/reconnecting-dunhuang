/* Reconnecting Dunhuang - shared page behaviour: mobile menu and figure enlargement. */
(function () {
  'use strict';

  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Figure enlargement: clones the figure's SVG or image into a dialog at natural size
  var box = document.createElement('div');
  box.className = 'lightbox';
  box.setAttribute('role', 'dialog');
  box.setAttribute('aria-modal', 'true');
  box.setAttribute('aria-label', 'Enlarged figure');
  box.innerHTML =
    '<div class="lightbox__panel">' +
    '<div class="lightbox__bar"><span class="lightbox__title"></span>' +
    '<button type="button" class="lightbox__close">Close</button></div>' +
    '<div class="lightbox__body"></div></div>';
  document.body.appendChild(box);
  var body = box.querySelector('.lightbox__body');
  var title = box.querySelector('.lightbox__title');
  var closeBtn = box.querySelector('.lightbox__close');
  var lastTrigger = null;

  function naturalWidth(el) {
    if (el.tagName.toLowerCase() === 'img') return el.naturalWidth || 1600;
    var vb = el.viewBox && el.viewBox.baseVal;
    return vb && vb.width ? vb.width * 1.33 : 1400; // Graphviz points to CSS pixels
  }

  function open(figure, trigger) {
    var source = figure.querySelector('.figure__panel svg, .figure__panel img');
    if (!source) return;
    var clone = source.cloneNode(true);
    var width = Math.max(naturalWidth(source), body.clientWidth || 0);
    clone.style.width = Math.round(Math.min(width, 2600)) + 'px';
    body.innerHTML = '';
    body.appendChild(clone);
    var cap = figure.querySelector('figcaption b');
    title.textContent = cap ? cap.textContent : 'Figure';
    box.classList.add('is-open');
    lastTrigger = trigger;
    closeBtn.focus();
  }

  function close() {
    box.classList.remove('is-open');
    body.innerHTML = '';
    if (lastTrigger) lastTrigger.focus();
  }

  // (every zoomable figure opens the full-screen viewer defined below)
  // Model diagrams: kept at reading size; where the screen is too narrow the panel scrolls sideways, and a
  // "Fit to width" button switches to the overview (and back)
  document.querySelectorAll('.figure[data-model]').forEach(function (fig) {
    var scroller = fig.querySelector('.figure__scroll');
    var fit = fig.querySelector('[data-fit]');
    var hint = fig.querySelector('.figure__hint');
    function update() {
      var narrow = fig.classList.contains('is-fit') || scroller.scrollWidth > scroller.clientWidth + 2;
      fit.hidden = !narrow;
      hint.hidden = !narrow;
    }
    fit.addEventListener('click', function (e) {
      e.stopPropagation();
      var on = fig.classList.toggle('is-fit');
      fit.textContent = on ? 'Reading size' : 'Fit to width';
      fit.setAttribute('aria-pressed', on ? 'true' : 'false');
      update();
    });
    window.addEventListener('resize', update);
    var img = scroller.querySelector('img');
    if (img && !img.complete) img.addEventListener('load', update);
    update();
  });

  // Model viewer: the diagram full screen, with drag, pinch and wheel zoom. Opens from "Explore the model",
  // from a click on the diagram, or (on phones) from the thumbnail. Esc, Close or the browser's Back closes it.
  var mv = document.createElement('div');
  mv.className = 'mv';
  mv.setAttribute('role', 'dialog');
  mv.setAttribute('aria-modal', 'true');
  mv.setAttribute('aria-label', 'Model viewer');
  mv.innerHTML =
    '<div class="mv__bar"><span class="mv__title"></span>' +
    '<button type="button" class="mv__btn" data-z="-" aria-label="Zoom out">−</button>' +
    '<span class="mv__zoom" aria-live="polite"></span>' +
    '<button type="button" class="mv__btn" data-z="+" aria-label="Zoom in">+</button>' +
    '<button type="button" class="mv__btn" data-z="fit">Fit</button>' +
    '<button type="button" class="mv__btn" data-z="1">100%</button>' +
    '<button type="button" class="mv__btn mv__btn--close">Close</button></div>' +
    '<div class="mv__stage"></div>' +
    '<div class="mv__foot"><span class="mv__help">Drag to move · wheel or pinch to zoom · double-click to zoom in</span><span class="mv__links"></span></div>';
  document.body.appendChild(mv);
  var stage = mv.querySelector('.mv__stage');
  var mvTitle = mv.querySelector('.mv__title');
  var mvZoom = mv.querySelector('.mv__zoom');
  var mvLinks = mv.querySelector('.mv__links');
  var mvClose = mv.querySelector('.mv__btn--close');
  var pic = null, s = 1, tx = 0, ty = 0, fitS = 1, natW = 0, natH = 0, mvTrigger = null, pushed = false;
  var pointers = {}, pinch = null, drag = null;

  function apply() {
    pic.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + s + ')';
    mvZoom.textContent = Math.round(s * 100) + '%';
  }
  function clampPos() {
    var W = stage.clientWidth, H = stage.clientHeight, w = natW * s, h = natH * s, m = 60;
    tx = w <= W ? (W - w) / 2 : Math.min(m, Math.max(W - w - m, tx));
    ty = h <= H ? (H - h) / 2 : Math.min(m, Math.max(H - h - m, ty));
  }
  function zoomAt(f, cx, cy) {
    var ns = Math.min(Math.max(4, fitS * 6), Math.max(fitS * 0.8, s * f));   // up to 6x the fitted size
    tx = cx - (cx - tx) * (ns / s); ty = cy - (cy - ty) * (ns / s); s = ns;
    clampPos(); apply();
  }
  function fit() {
    fitS = Math.min(stage.clientWidth / natW, stage.clientHeight / natH);
    s = fitS; tx = 0; ty = 0; clampPos(); apply();
  }
  var blobUrl = null;
  function openMv(figure, trigger) {
    var img = figure.querySelector('.figure__panel img');
    var svg = img ? null : figure.querySelector('.figure__panel svg');
    if (!img && !svg) return;
    pic = document.createElement('img');
    pic.draggable = false;
    if (img) {
      pic.src = img.currentSrc || img.src; pic.alt = img.alt;
      natW = img.naturalWidth || parseFloat(img.getAttribute('width')) || 1600;
      natH = img.naturalHeight || natW * (img.clientHeight / Math.max(1, img.clientWidth));
    } else {   // inline SVG: shown as an image of the same markup
      var vb = svg.viewBox && svg.viewBox.baseVal;
      natW = vb && vb.width ? vb.width * 1.33 : 1400;
      natH = vb && vb.height ? vb.height * 1.33 : 800;
      var copy = svg.cloneNode(true);
      copy.setAttribute('width', natW); copy.setAttribute('height', natH); copy.removeAttribute('style');
      if (!copy.getAttribute('xmlns')) copy.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      blobUrl = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(copy)], { type: 'image/svg+xml' }));
      pic.src = blobUrl; pic.alt = svg.getAttribute('aria-label') || '';
    }
    pic.style.width = natW + 'px'; pic.style.height = natH + 'px';
    stage.innerHTML = ''; stage.appendChild(pic);
    var cap = figure.querySelector('figcaption b');
    mvTitle.textContent = cap ? cap.textContent.replace(/\.$/, '') : (figure.closest('.formalize__layer') ? 'From theory to formalization' : 'Figure');
    mvLinks.innerHTML = '';
    figure.querySelectorAll('.figure__links a').forEach(function (a) { mvLinks.appendChild(a.cloneNode(true)); mvLinks.appendChild(document.createTextNode(' · ')); });
    if (mvLinks.lastChild) mvLinks.removeChild(mvLinks.lastChild);
    mv.classList.add('is-open');
    document.documentElement.style.overflow = 'hidden';
    mvTrigger = trigger || null;
    fit();
    try { history.pushState({ mv: 1 }, ''); pushed = true; } catch (e) { pushed = false; }
    mvClose.focus();
  }
  function closeMv(fromHistory) {
    if (!mv.classList.contains('is-open')) return;
    mv.classList.remove('is-open');
    document.documentElement.style.overflow = '';
    stage.innerHTML = ''; pic = null;
    if (blobUrl) { URL.revokeObjectURL(blobUrl); blobUrl = null; }
    if (pushed && !fromHistory) { pushed = false; history.back(); }
    pushed = false;
    if (mvTrigger) mvTrigger.focus();
  }
  window.addEventListener('popstate', function () { closeMv(true); });
  mvClose.addEventListener('click', function () { closeMv(false); });
  mv.querySelectorAll('[data-z]').forEach(function (b) {
    b.addEventListener('click', function () {
      var z = b.getAttribute('data-z'), cx = stage.clientWidth / 2, cy = stage.clientHeight / 2;
      if (z === '+') zoomAt(1.4, cx, cy);
      else if (z === '-') zoomAt(1 / 1.4, cx, cy);
      else if (z === 'fit') fit();
      else zoomAt(1 / s, cx, cy);
    });
  });
  function local(e) { var r = stage.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
  stage.addEventListener('wheel', function (e) {
    if (!pic) return; e.preventDefault();
    var p = local(e); zoomAt(Math.exp(-e.deltaY * 0.0015), p.x, p.y);
  }, { passive: false });
  var gestureBase = 1;
  ['gesturestart', 'gesturechange', 'gestureend'].forEach(function (type) {
    document.addEventListener(type, function (e) {
      if (!mv.classList.contains('is-open')) return;
      e.preventDefault();   // no page zoom while the viewer is open
      if (!pic || Object.keys(pointers).length >= 2) return;   // touch screens: the pointer pinch below does the zooming
      if (type === 'gesturestart') { gestureBase = s; return; }
      if (type === 'gesturechange') {
        var r = stage.getBoundingClientRect();
        var cx = (e.clientX || r.left + r.width / 2) - r.left, cy = (e.clientY || r.top + r.height / 2) - r.top;
        zoomAt((gestureBase * e.scale) / s, cx, cy);
      }
    }, { passive: false });
  });
  mv.addEventListener('wheel', function (e) { if (e.target.closest('.mv__stage') === null) e.preventDefault(); }, { passive: false });
  stage.addEventListener('dblclick', function (e) { var p = local(e); zoomAt(1.8, p.x, p.y); });
  stage.addEventListener('pointerdown', function (e) {
    if (!pic) return;
    stage.setPointerCapture(e.pointerId);
    pointers[e.pointerId] = local(e);
    var ids = Object.keys(pointers);
    if (ids.length === 1) { drag = { x: pointers[ids[0]].x - tx, y: pointers[ids[0]].y - ty }; stage.classList.add('is-drag'); }
    if (ids.length === 2) {
      var a = pointers[ids[0]], b = pointers[ids[1]];
      pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), s: s }; drag = null;
    }
  });
  stage.addEventListener('pointermove', function (e) {
    if (!pointers[e.pointerId]) return;
    pointers[e.pointerId] = local(e);
    var ids = Object.keys(pointers);
    if (pinch && ids.length === 2) {
      var a = pointers[ids[0]], b = pointers[ids[1]], d = Math.hypot(a.x - b.x, a.y - b.y);
      zoomAt((pinch.s * d / pinch.d) / s, (a.x + b.x) / 2, (a.y + b.y) / 2);
    } else if (drag) {
      tx = pointers[e.pointerId].x - drag.x; ty = pointers[e.pointerId].y - drag.y; clampPos(); apply();
    }
  });
  function up(e) {
    delete pointers[e.pointerId];
    if (Object.keys(pointers).length < 2) pinch = null;
    if (!Object.keys(pointers).length) { drag = null; stage.classList.remove('is-drag'); }
  }
  stage.addEventListener('pointerup', up);
  stage.addEventListener('pointercancel', up);
  document.addEventListener('keydown', function (e) {
    if (!mv.classList.contains('is-open')) return;
    var cx = stage.clientWidth / 2, cy = stage.clientHeight / 2;
    if (e.key === 'Escape') closeMv(false);
    else if (e.key === '+' || e.key === '=') zoomAt(1.4, cx, cy);
    else if (e.key === '-') zoomAt(1 / 1.4, cx, cy);
    else if (e.key === '0') fit();
    else if (e.key.indexOf('Arrow') === 0) {
      var st = 80; if (e.key === 'ArrowLeft') tx += st; if (e.key === 'ArrowRight') tx -= st;
      if (e.key === 'ArrowUp') ty += st; if (e.key === 'ArrowDown') ty -= st; clampPos(); apply(); e.preventDefault();
    }
  });
  window.addEventListener('resize', function () { if (pic) fit(); });

  document.querySelectorAll('.figure[data-zoomable]:not([data-model])').forEach(function (fig) {
    var btn = fig.querySelector('[data-enlarge]');
    if (btn) btn.addEventListener('click', function (e) { e.stopPropagation(); openMv(fig, btn); });
    var panel = fig.querySelector('.figure__panel');
    panel.style.cursor = 'zoom-in';
    panel.addEventListener('click', function (e) {
      if (e.target.closest('button, a')) return;
      openMv(fig, btn);
    });
  });
  var phone = window.matchMedia('(max-width: 767px)');
  document.querySelectorAll('.figure[data-model]').forEach(function (fig) {
    var enlarge = fig.querySelector('[data-enlarge]');
    if (enlarge) {
      enlarge.textContent = 'Explore the model';
      enlarge.className = 'btn-explore';
      enlarge.addEventListener('click', function (e) { e.stopPropagation(); openMv(fig, enlarge); });
    }
    var panel = fig.querySelector('.figure__panel');
    var tap = document.createElement('button');
    tap.type = 'button'; tap.className = 'figure__tap';
    tap.innerHTML = '<span>Tap to explore</span>';
    tap.addEventListener('click', function () { openMv(fig, tap); });
    panel.appendChild(tap);
    panel.style.cursor = 'zoom-in';
    panel.addEventListener('click', function (e) {
      if (e.target.closest('button, a')) return;
      if (fig.querySelector('.figure__scroll').scrollWidth > fig.querySelector('.figure__scroll').clientWidth + 2 && !phone.matches) return; // sideways scrolling panel: let the user scroll
      openMv(fig, enlarge);
    });
    function thumb() { fig.classList.toggle('is-thumb', phone.matches); }
    thumb();
    if (phone.addEventListener) phone.addEventListener('change', thumb);
  });
  closeBtn.addEventListener('click', close);
  box.addEventListener('click', function (e) { if (e.target === box) close(); });
  // Tabs (Domain page entity tables); without JavaScript every panel stays visible
  document.querySelectorAll('[data-tabs]').forEach(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(tab, false); });
      tab.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') select(tabs[(i + 1) % tabs.length], true);
        if (e.key === 'ArrowLeft') select(tabs[(i - 1 + tabs.length) % tabs.length], true);
      });
    });
    box.classList.add('is-ready');
  });

  // Print: open every folded panel so nothing is hidden on paper
  window.addEventListener('beforeprint', function () {
    document.querySelectorAll('details:not([open])').forEach(function (d) {
      d.setAttribute('open', ''); d.dataset.printOpened = '1';
    });
  });
  window.addEventListener('afterprint', function () {
    document.querySelectorAll('details[data-print-opened]').forEach(function (d) {
      d.removeAttribute('open'); delete d.dataset.printOpened;
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && box.classList.contains('is-open')) close();
  });
})();
