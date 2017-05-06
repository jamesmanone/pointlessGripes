$(document).ready(function() {

  $('.cancel').click(function() {
    id = $(this).parents('article').attr('id');
    $.get('/onepost/' + id, function(data) {
      $('#' + id).html(data);
    });
  });

  $('.submit').click(function() {
    subject = $('input[name="subject"]').val();
    content = $('textarea[name="content"]').val();
    id = $(this).parents('article').attr('id');
    if(subject && content) {
      $.post('/editpost/' + id, {
        'subject': subject,
        'content': content
      }, function(data) {
        if(data.success) {
          $('#' + id).html(data.response);
        } else {
          $('.error').html(data.message);
        }
      });
    } else {
      $('.error').html('We need a subject and some content');
    }
  });

});
