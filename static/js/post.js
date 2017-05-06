$(document).ready(function() {

  $('.cancel').click(function() {
    $('.newpost-slide').slideUp();
    $('.newpost-slide').empty();
  });

  $('.submit').click(function() {
    subject = $('input[name="subject"]').val();
    content = $('textarea[name="content"]').val();
    if(subject && content) {
      $.post('/newpost', {
        'subject': subject,
        'content': content
      }, function(data) {
        if(data.success) {
          location.assign('/permalink/' + data.post_id);
        } else {
          $('.error').html(data.message);
        }
      });
    } else {
      $('.error').html('We need a subject and some content');
    }
  });

});
