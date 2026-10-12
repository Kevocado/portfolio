/* Photography page interactions: featured reel (auto-scroll + manual
   arrows/drag), shoot accordion drawers, and the on-site lightbox. Photos
   never navigate away; the only Instagram exits are explicit
   "View full post on Instagram" links. */
(function () {
  'use strict';

  var dataEl = document.getElementById('galleryData');
  if (!dataEl) { return; }
  var data = JSON.parse(dataEl.textContent);

  /* Flat lightbox list: featured photos first, then every shoot's frames. */
  var ITEMS = [];
  data.featured.forEach(function (ph) {
    ITEMS.push({ src: ph.src, title: ph.title, post: ph.post,
                 alt: 'Photograph from ' + ph.title + ' by Kevin Sigey.' });
  });
  var shootIndex = {}; /* slug -> {title, post, start} */
  data.shoots.forEach(function (s) {
    shootIndex[s.slug] = { title: s.title, post: s.post, start: ITEMS.length };
    s.files.forEach(function (f) {
      ITEMS.push({ src: f.src, title: s.title, post: f.post,
                   alt: 'Photograph from ' + s.title + ' by Kevin Sigey.' });
    });
  });

  /* ---------- Featured reel: auto-scroll + arrows + drag ---------- */
  var reel = document.getElementById('reel');
  var track = document.getElementById('reelTrack');
  var caption = document.getElementById('reelCaption');
  var reelPrev = document.getElementById('reelPrev');
  var reelNext = document.getElementById('reelNext');
  if (reel && track) {
    var rItems = Array.prototype.slice.call(
      track.querySelectorAll('.reel-item'));
    var reduceMotion = window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var autoOn = !reduceMotion;
    var hoverPause = false;
    var interactPauseUntil = 0;
    var dragging = false;
    var dragMoved = 0;
    var dragStartX = 0;
    var dragStartScroll = 0;
    var dragSuppressClick = false;
    var SPEED = 0.55; /* px per frame */

    function halfWidth() {
      return track.scrollWidth / 2;
    }

    function highlight() {
      var r = reel.getBoundingClientRect();
      var cx = r.left + r.width / 2;
      var best = null, bestD = Infinity;
      rItems.forEach(function (el) {
        var er = el.getBoundingClientRect();
        var d = Math.abs((er.left + er.width / 2) - cx);
        if (d < bestD) { bestD = d; best = el; }
      });
      rItems.forEach(function (el) {
        el.classList.toggle('is-center', el === best);
      });
      if (best && caption) {
        caption.textContent = best.getAttribute('data-title');
      }
    }

    function tick() {
      var now = Date.now();
      if (autoOn && !hoverPause && !dragging && now > interactPauseUntil &&
          !document.hidden) {
        reel.scrollLeft += SPEED;
        var hw = halfWidth();
        if (hw > 0 && reel.scrollLeft >= hw) {
          reel.scrollLeft -= hw;
        }
      }
      highlight();
      requestAnimationFrame(tick);
    }

    function pauseForInteraction() {
      interactPauseUntil = Date.now() + 3500;
    }

    reel.addEventListener('mouseenter', function () { hoverPause = true; });
    reel.addEventListener('mouseleave', function () {
      hoverPause = false;
      dragging = false;
      reel.classList.remove('dragging');
    });
    reel.addEventListener('wheel', pauseForInteraction, { passive: true });
    reel.addEventListener('touchstart', pauseForInteraction, { passive: true });

    /* Mouse drag-to-scroll (touch uses native scrolling). */
    reel.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) { return; }
      dragging = true;
      dragMoved = 0;
      dragSuppressClick = false;
      dragStartX = e.clientX;
      dragStartScroll = reel.scrollLeft;
      reel.classList.add('dragging');
      pauseForInteraction();
    });
    window.addEventListener('pointermove', function (e) {
      if (!dragging) { return; }
      var dx = e.clientX - dragStartX;
      dragMoved = Math.max(dragMoved, Math.abs(dx));
      reel.scrollLeft = dragStartScroll - dx;
    });
    window.addEventListener('pointerup', function () {
      if (!dragging) { return; }
      dragging = false;
      reel.classList.remove('dragging');
      if (dragMoved > 8) { dragSuppressClick = true; }
    });

    function nudge(dir) {
      pauseForInteraction();
      reel.scrollBy({ left: dir * 360, behavior: 'smooth' });
    }
    if (reelPrev) {
      reelPrev.addEventListener('click', function () { nudge(-1); });
    }
    if (reelNext) {
      reelNext.addEventListener('click', function () { nudge(1); });
    }

    /* Suppress the lightbox click when a drag just ended. */
    document.addEventListener('click', function (e) {
      if (dragSuppressClick) {
        dragSuppressClick = false;
        e.stopPropagation();
        e.preventDefault();
      }
    }, true);

    requestAnimationFrame(tick);
    highlight();
  }

  /* ---------- Shoot accordion drawers ---------- */
  var bySlug = {};
  data.shoots.forEach(function (s) { bySlug[s.slug] = s; });

  function closeDrawers() {
    document.querySelectorAll('.shoot-drawer').forEach(function (d) {
      d.hidden = true;
      d.removeAttribute('data-slug');
    });
    document.querySelectorAll('.shoot-card').forEach(function (c) {
      c.setAttribute('aria-expanded', 'false');
    });
  }

  function openDrawer(card) {
    var slug = card.getAttribute('data-shoot');
    var s = bySlug[slug];
    if (!s) { return; }
    var drawer = document.getElementById(card.getAttribute('aria-controls'));
    var wasOpen = !drawer.hidden && drawer.getAttribute('data-slug') === slug;
    closeDrawers();
    if (wasOpen) { return; }
    drawer.querySelector('.drawer-title').textContent = s.title;
    var ig = drawer.querySelector('.drawer-ig');
    ig.href = s.post;
    ig.setAttribute('aria-label', 'View ' + s.title + ' on Instagram');
    var frames = drawer.querySelector('.drawer-frames');
    frames.innerHTML = '';
    var start = shootIndex[slug].start;
    s.files.forEach(function (f, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'dframe';
      b.setAttribute('data-idx', String(start + i));
      b.setAttribute('aria-label',
        'Open photo ' + (i + 1) + ' from ' + s.title);
      var img = document.createElement('img');
      img.src = f.src;
      img.alt = 'Photograph from ' + s.title + ' by Kevin Sigey.';
      img.loading = 'lazy';
      b.appendChild(img);
      frames.appendChild(b);
    });
    drawer.setAttribute('data-slug', slug);
    drawer.hidden = false;
    card.setAttribute('aria-expanded', 'true');
    drawer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  document.querySelectorAll('.shoot-card').forEach(function (card) {
    card.addEventListener('click', function () { openDrawer(card); });
  });
  document.querySelectorAll('.drawer-close').forEach(function (btn) {
    btn.addEventListener('click', closeDrawers);
  });

  /* ---------- Lightbox ---------- */
  var lb = document.getElementById('lightbox');
  var lbImg = document.getElementById('lbImg');
  var lbTitle = document.getElementById('lbTitle');
  var lbIg = document.getElementById('lbIg');
  var lbClose = document.getElementById('lbClose');
  var lbPrev = document.getElementById('lbPrev');
  var lbNext = document.getElementById('lbNext');
  var cur = 0;
  var lastFocus = null;

  function render() {
    var it = ITEMS[cur];
    lbImg.src = it.src;
    lbImg.alt = it.alt;
    lbTitle.textContent = it.title;
    lbIg.href = it.post;
    lbIg.setAttribute('aria-label', 'View ' + it.title + ' on Instagram');
  }
  function openLb(i) {
    cur = ((i % ITEMS.length) + ITEMS.length) % ITEMS.length;
    render();
    lb.hidden = false;
    document.body.style.overflow = 'hidden';
    lastFocus = document.activeElement;
    lbClose.focus();
  }
  function closeLb() {
    lb.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) { lastFocus.focus(); }
  }
  function step(d) {
    cur = ((cur + d) % ITEMS.length + ITEMS.length) % ITEMS.length;
    render();
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-idx]');
    if (t && !lb.hidden) { return; }
    if (t) { openLb(parseInt(t.getAttribute('data-idx'), 10)); }
  });
  lbClose.addEventListener('click', closeLb);
  lbPrev.addEventListener('click', function () { step(-1); });
  lbNext.addEventListener('click', function () { step(1); });
  lb.addEventListener('click', function (e) {
    if (e.target === lb) { closeLb(); }
  });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) { return; }
    if (e.key === 'Escape') { closeLb(); }
    else if (e.key === 'ArrowLeft') { step(-1); }
    else if (e.key === 'ArrowRight') { step(1); }
  });
})();
