$('.login-modal').fadeOut();
$('.login-modal').empty();

$(document).ready(function() {

  $('.submit').click(function () {
    event.preventDefault();
    submit();
  });

  $('.cancel').click(function() {
    event.preventDefault();
    $('.form-modal').slideUp();
    $('.form-modal').empty();
  });

  $('input[name="username"]').blur(function() {
    username = $('input[name="username"]').val();
    if(username.length < 6) {
      $('.user-error').html('Username must be at least 6 characters');
    } else {
      $.post('/usernamecheck', {'username': username}, function(data) {
        if(data.taken) {
          $('.user-error').html('This username is taken');
        } else {
          $('.user-error').empty();
        }
      });
    }
  });

  $('input[name="password"]').change(function() {
    password = $('input[name="password"]').val();
    if(password.length < 6) {
      $('.password-error').html('Password must be at least 6 characters');
    } else {
      $('.password-error').empty();
    }
  });

  $('input[name="passcheck"]').change(function() {
    password = $('input[name="password"]').val();
    passcheck = $('input[name="passcheck"]').val();
    if(password !== passcheck) {
      $('.passcheck-error').html('Passwords do not match');
    } else {
      $('.passcheck-error').empty();
    }
  });

  $('.form-modal').find('.login').click(function() {
    $.get('/login', function(data) {
      $('.form-modal').slideUp();
      $('.login-modal').html(data);
      $('.login-modal').slideDown();
      $('.form-modal').empty();
    });
  });
  
});

function submit() {
  username = $('input[name="username"]').val();
  password = $('input[name="password"]').val();
  passcheck = $('input[name="passcheck"]').val();
  email = $('input[name="email"]').val();
  if(username.length > 5 && password.length > 5 && password === passcheck) {
    $.post('/signup', {
      'username': username,
      'password': password,
      'passcheck': passcheck,
      'email': email
    }, function() {
      location.reload(true);
    });
  }
}
