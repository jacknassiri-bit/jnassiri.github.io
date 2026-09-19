(function () {
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem('theme'); } catch (_error) {}
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  if (saved === 'dark' || saved === 'light') root.dataset.theme = saved;
  else root.dataset.theme = media && media.matches ? 'dark' : 'light';

  function syncIcon() {
    var icon = document.getElementById('toggle-icon') || document.getElementById('theme-icon');
    if (icon) icon.textContent = root.dataset.theme === 'dark' ? '☀️' : '🌙';
  }
  document.addEventListener('DOMContentLoaded', syncIcon);
  if (media && media.addEventListener) media.addEventListener('change', function (event) {
    var current = null;
    try { current = localStorage.getItem('theme'); } catch (_error) {}
    if (!current) {
      root.dataset.theme = event.matches ? 'dark' : 'light';
      syncIcon();
    }
  });
})();
