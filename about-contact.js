document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('about-contact-form');
  if (!form) return;

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var address = atob('amFjay5uYXNzaXJpQGxoc2xhLm9yZw==');
    var name = document.getElementById('contact-name').value.trim();
    var reply = document.getElementById('contact-reply').value.trim();
    var topic = document.getElementById('contact-topic').value;
    var message = document.getElementById('contact-message').value.trim();
    var subject = 'The Med Frontier: ' + topic;
    var body = 'Name: ' + name + '\nReply email: ' + reply + '\nTopic: ' + topic + '\n\nMessage:\n' + message;
    window.location.href = 'mailto:' + address + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });
});
