/* Photography page interactions: featured reel (auto-scroll + manual
   arrows/drag), album popup overview, and the on-site lightbox. Shoot cards
   open a popup with the whole shoot; picking a frame opens the individual
   lightbox view. Photos never navigate away; the only Instagram exits are
   explicit "View full post on Instagram" links. */
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
  var shootIndex = {}; /* slug -> {title, post, start, count} */
  data.shoots.forEach(function (s) {
    shootIndex[s.slug] = { title: s.title, post: s.post,
                            start: ITEMS.length, count: s.files.length };
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

  /* ---------- Album popup: whole-shoot overview first ----------
     A card opens a popup with every frame of the shoot in place; picking
     one frame opens the individual lightbox view. */
  var pop = document.getElementById('albumPop');
  var popTitle = document.getElementById('albumPopTitle');
  var popIg = document.getElementById('albumPopIg');
  var popFrames = document.getElementById('albumPopFrames');
  var popClose = document.getElementById('albumPopClose');
  var popReturnFocus = null;

  function openAlbum(slug) {
    var info = shootIndex[slug];
    if (!info) { return; }
    LIST = ITEMS.slice(info.start, info.start + info.count);
    popTitle.textContent = info.title;
    popIg.href = info.post;
    popIg.setAttribute('aria-label', 'View ' + info.title + ' on Instagram');
    popFrames.innerHTML = '';
    LIST.forEach(function (it, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'pop-frame';
      b.setAttribute('data-pidx', String(i));
      b.setAttribute('aria-label',
        'View photo ' + (i + 1) + ' of ' + LIST.length +
        ' from ' + info.title);
      var img = document.createElement('img');
      img.src = it.src;
      img.alt = it.alt;
      img.loading = 'lazy';
      b.appendChild(img);
      popFrames.appendChild(b);
    });
    pop.hidden = false;
    document.body.style.overflow = 'hidden';
    popReturnFocus = document.activeElement;
    popClose.focus();
  }
  function closeAlbum() {
    pop.hidden = true;
    if (lb.hidden) { document.body.style.overflow = ''; }
    if (popReturnFocus && popReturnFocus.focus) { popReturnFocus.focus(); }
  }
  popClose.addEventListener('click', closeAlbum);
  pop.addEventListener('click', function (e) {
    if (e.target === pop) { closeAlbum(); }
  });

  /* ---------- Lightbox ----------
     Reel items browse every photo; popup frames browse just their shoot. */
  var lb = document.getElementById('lightbox');
  var lbImg = document.getElementById('lbImg');
  var lbTitle = document.getElementById('lbTitle');
  var lbCount = document.getElementById('lbCount');
  var lbIg = document.getElementById('lbIg');
  var lbClose = document.getElementById('lbClose');
  var lbPrev = document.getElementById('lbPrev');
  var lbNext = document.getElementById('lbNext');
  var LIST = ITEMS;
  var cur = 0;
  var lastFocus = null;

  function render() {
    var it = LIST[cur];
    lbImg.src = it.src;
    lbImg.alt = it.alt;
    lbTitle.textContent = it.title;
    if (lbCount) { lbCount.textContent = (cur + 1) + ' / ' + LIST.length; }
    lbIg.href = it.post;
    lbIg.setAttribute('aria-label', 'View ' + it.title + ' on Instagram');
  }
  function openLb(list, i) {
    LIST = list;
    cur = ((i % LIST.length) + LIST.length) % LIST.length;
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
    cur = ((cur + d) % LIST.length + LIST.length) % LIST.length;
    render();
  }

  document.addEventListener('click', function (e) {
    if (!lb.hidden) { return; }
    if (!pop.hidden) {
      var f = e.target.closest('[data-pidx]');
      if (f) { openLb(LIST, parseInt(f.getAttribute('data-pidx'), 10)); }
      return;
    }
    /* Reel items and shoot cards both carry data-shoot: open the album. */
    var t = e.target.closest('[data-shoot]');
    if (t) { openAlbum(t.getAttribute('data-shoot')); }
  });
  lbClose.addEventListener('click', closeLb);
  lbPrev.addEventListener('click', function () { step(-1); });
  lbNext.addEventListener('click', function () { step(1); });
  lb.addEventListener('click', function (e) {
    if (e.target === lb) { closeLb(); }
  });
  document.addEventListener('keydown', function (e) {
    if (!lb.hidden) {
      if (e.key === 'Escape') { closeLb(); }
      else if (e.key === 'ArrowLeft') { step(-1); }
      else if (e.key === 'ArrowRight') { step(1); }
      return;
    }
    if (!pop.hidden && e.key === 'Escape') { closeAlbum(); }
  });
})();
