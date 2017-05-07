$(document).ready(function() {
  $('button[name="submit-edit"]').click(function() {
    comment = $('input[name="newcomment"]').val();
    id = $(this).parents('.comment').attr('id');

    if(comment) {
      $.post('/editcomment/' + id, {
        'comment': comment
      }, function(data) { 
        $('#' + id).html(data.response);
      });
    } else {
      $('.editcomment-error').html('You must enter some text');
    }
  });

  $('button[name="cancel"]').click(function() {
    var id = $(this).parents('.comment').attr('id');

    $.post('/editcomment/' + id, {
      'cancel': true
    }, function(data) {
      $('#' + id).html(data.response);
    });
  });

});
