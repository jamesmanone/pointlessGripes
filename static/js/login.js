$('.form-modal').fadeOut();
$('.form-modal').empty();

$(document).ready(function() {

  $('.submit').click(function() {
    username = $('input[name="username"]').val();
    password = $('input[name="password"]').val();
    $.post('/login', {
      'username': username,
      'password': password
    }, function(data) {
      if(data.success) {
        location.reload(true);
      } else {
        $('.error').html('Incorrect username or password');
      }
    });
  });

  $('.cancel').click(function() {
    $('.login-modal').slideUp();
    $('.login-modal').empty();
  });

  $('.login-modal').find('.signup').click(function() {
    $.get('/signup', function(data) {
      $('.login-modal').slideUp();
      $('.form-modal').html(data);
      $('.form-modal').slideDown();
      $('.login-modal').empty();
    });
  });
  
});
