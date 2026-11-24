document.addEventListener('DOMContentLoaded', function () {
  var wheel = document.querySelector('.article-wheel');
  var stage = document.querySelector('.wheel-stage');
  if (!wheel || !stage) return;

  wheel.querySelectorAll('.wheel-item').forEach(function (item) {
    item.addEventListener('focus', function () {
      wheel.style.animationPlayState = 'paused';
    });
    item.addEventListener('blur', function () {
      wheel.style.animationPlayState = '';
    });
  });

  stage.addEventListener('mouseenter', function () {
    wheel.style.animationPlayState = 'paused';
  });
  stage.addEventListener('mouseleave', function () {
    wheel.style.animationPlayState = '';
  });
});
