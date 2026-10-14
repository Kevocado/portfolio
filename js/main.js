/* Portfolio interactions: experience tabs, mobile menu, nav scroll state. */
(function () {
  'use strict';

  // Experience tabs
  var tabBtns = document.querySelectorAll('.tab-btn');
  var panels = document.querySelectorAll('.tab-panel');
  tabBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      tabBtns.forEach(function (b) {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      panels.forEach(function (p) { p.classList.remove('active'); });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      var panel = document.getElementById(btn.getAttribute('data-tab'));
      if (panel) { panel.classList.add('active'); }
    });
  });

  // Mobile menu
  var menuBtn = document.getElementById('menuBtn');
  var mobileMenu = document.getElementById('mobileMenu');
  function closeMenu() {
    menuBtn.classList.remove('open');
    menuBtn.setAttribute('aria-expanded', 'false');
    mobileMenu.classList.remove('open');
    mobileMenu.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }
  menuBtn.addEventListener('click', function () {
    var open = mobileMenu.classList.toggle('open');
    menuBtn.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    mobileMenu.setAttribute('aria-hidden', open ? 'false' : 'true');
    document.body.style.overflow = open ? 'hidden' : '';
  });
  mobileMenu.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', closeMenu);
  });

  // Nav shadow on scroll
  var header = document.getElementById('siteHeader');
  function onScroll() {
    header.classList.toggle('scrolled', window.scrollY > 50);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Dot Foods tradeoff toy (Decisions section). Simplified illustration
  // of the capstone model's structure: quantities are fixed from the
  // model (7,229 loads; 309,761 traditional pallets; 416,159 optimized
  // pallets) and only the four placeholder unit costs move.
  // CASES and LABOR_HOURS are calibration constants backed out from the
  // notebook's own totals at the default unit costs, so the defaults
  // reproduce Traditional $8,457,877 and Optimized $11,507,953 exactly.
  var toy = document.getElementById('dotFoodsToy');
  if (toy) {
    var P_TRAD = 309761;
    var P_OPT = 416159;
    var LOADS = 7229;
    var CASES = 18962980;
    var LABOR_HOURS = 259116;
    var DEFAULTS = { palletCost: 12, laborRate: 25, sortFee: 0.25, dropFee: 5 };

    function fmt(n) {
      return '$' + Math.round(n).toLocaleString('en-US');
    }
    function fmtMoney(v, decimals) {
      return v.toFixed(decimals);
    }
    function compute() {
      var pallet = parseFloat(document.getElementById('palletCost').value);
      var labor = parseFloat(document.getElementById('laborRate').value);
      var sort = parseFloat(document.getElementById('sortFee').value);
      var drop = parseFloat(document.getElementById('dropFee').value);
      document.getElementById('palletCostVal').textContent = fmtMoney(pallet, 0);
      document.getElementById('laborVal').textContent = fmtMoney(labor, 0);
      document.getElementById('sortFeeVal').textContent = fmtMoney(sort, 2);
      document.getElementById('dropFeeVal').textContent = fmtMoney(drop, 2);
      var trad = pallet * P_TRAD + sort * CASES;
      var opt = pallet * P_OPT + labor * LABOR_HOURS + drop * LOADS;
      document.getElementById('toyTraditional').textContent = fmt(trad);
      document.getElementById('toyOptimized').textContent = fmt(opt);
      var diff = opt - trad;
      var verdict = document.getElementById('toyVerdict');
      if (diff > 0) {
        verdict.textContent = 'At these assumptions, optimized costs ' +
          fmt(diff) + ' more than traditional.';
      } else if (diff < 0) {
        verdict.textContent = 'At these assumptions, optimized costs ' +
          fmt(-diff) + ' less than traditional.';
      } else {
        verdict.textContent = 'At these assumptions, the two scenarios cost the same.';
      }
    }
    ['palletCost', 'laborRate', 'sortFee', 'dropFee'].forEach(function (id) {
      document.getElementById(id).addEventListener('input', compute);
    });
    document.getElementById('toyReset').addEventListener('click', function () {
      Object.keys(DEFAULTS).forEach(function (id) {
        document.getElementById(id).value = String(DEFAULTS[id]);
      });
      compute();
    });
    compute();
  }
})();
