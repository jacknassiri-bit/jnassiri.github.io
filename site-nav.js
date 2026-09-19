document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('nav').forEach(function (nav) {
    var button = nav.querySelector('.menu-toggle');
    var links = nav.querySelector('.nav-links');
    if (!button || !links) return;

    function closeMenu() {
      nav.classList.remove('menu-open');
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', 'Open navigation menu');
    }

    button.addEventListener('click', function () {
      var opening = button.getAttribute('aria-expanded') !== 'true';
      nav.classList.toggle('menu-open', opening);
      button.setAttribute('aria-expanded', String(opening));
      button.setAttribute('aria-label', opening ? 'Close navigation menu' : 'Open navigation menu');
    });

    links.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', closeMenu);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        closeMenu();
        button.focus();
      }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 768) closeMenu();
    });
  });
});
