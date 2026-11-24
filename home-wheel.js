document.addEventListener('DOMContentLoaded', function () {
  var wheel = document.querySelector('.article-wheel');
  if (!wheel) return;

  wheel.querySelectorAll('.wheel-item').forEach(function (item) {
    item.addEventListener('focus', function () {
      wheel.style.animationPlayState = 'paused';
    });
    item.addEventListener('blur', function () {
      wheel.style.animationPlayState = '';
    });
  });

  wheel.addEventListener('mouseenter', function () {
    wheel.style.animationPlayState = 'paused';
  });
  wheel.addEventListener('mouseleave', function () {
    wheel.style.animationPlayState = '';
  });
});
