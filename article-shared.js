(function () {
  'use strict';

  var root = document.documentElement;

  function syncThemeIcon() {
    var icon = document.getElementById('toggle-icon') || document.getElementById('theme-icon');
    if (icon) icon.textContent = root.getAttribute('data-theme') === 'dark' ? '☀️' : '🌙';
  }

  function changeTheme() {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (_error) {}
    syncThemeIcon();
  }

  window.toggleTheme = changeTheme;
  window.theme = changeTheme;

  window.copyLink = function () {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(window.location.href).then(function () {
      var confirmation = document.getElementById('copy-confirm');
      if (!confirmation) return;
      confirmation.style.display = 'inline';
      window.setTimeout(function () { confirmation.style.display = 'none'; }, 2000);
    });
  };

  window.toggleMenu = function () {
    var menu = document.getElementById('mobile-nav') || document.getElementById('mobileNav');
    if (menu) menu.classList.toggle('open');
  };

  function initializeArticle() {
    syncThemeIcon();
    var backToTop = document.getElementById('back-top');
    if (backToTop) {
      window.addEventListener('scroll', function () {
        backToTop.classList.toggle('visible', window.scrollY > 350);
      });
      backToTop.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    var page = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(function (link) {
      if (link.getAttribute('href') === page) link.classList.add('active');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeArticle);
  } else {
    initializeArticle();
  }
})();
