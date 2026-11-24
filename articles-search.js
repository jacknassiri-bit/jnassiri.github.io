document.addEventListener('DOMContentLoaded', function () {
  var input = document.getElementById('article-search-input');
  var count = document.getElementById('article-search-count');
  var cards = Array.from(document.querySelectorAll('#posts .post-card'));
  var activeCategory = 'All';

  cards.forEach(function (card) {
    var foot = card.querySelector('.post-foot');
    if (!foot) return;
    while (foot.children.length > 1) foot.removeChild(foot.lastElementChild);
  });

  function updateCards() {
    var query = input ? input.value.trim().toLowerCase() : '';
    var shown = 0;

    cards.forEach(function (card) {
      var categoryMatches = activeCategory === 'All' || card.getAttribute('data-category') === activeCategory;
      var title = card.querySelector('h3');
      var excerpt = card.querySelector('p');
      var searchable = ((title ? title.textContent : '') + ' ' + (excerpt ? excerpt.textContent : '')).toLowerCase();
      var searchMatches = !query || searchable.indexOf(query) !== -1;
      var visible = categoryMatches && searchMatches;
      card.style.display = visible ? 'flex' : 'none';
      if (visible) shown += 1;
    });

    if (count) count.textContent = shown + (shown === 1 ? ' article' : ' articles');
  }

  document.querySelectorAll('.filter-btn').forEach(function (button) {
    button.addEventListener('click', function () {
      activeCategory = button.getAttribute('data-filter') || 'All';
      updateCards();
    });
  });

  if (input) input.addEventListener('input', updateCards);
  updateCards();
});
