// Takes post ID as input. after confirming delete, sends delete
// post to /delete/{post_id}. Fades out post on success
var trash = function(id) {
  if (confirm('Delete post?')) {
    $.post('/delete/' + id, {
      delete: True
    })
      .done(function() {
        $('#' + id).fadeOut();
      });
  }
};

/* Takes post ID as input. Fetches comments for post using AJAX
   makes space for and displays comments */
var commentOut = function(id) {
  $.get('/comment/' + id, function (data, id) {
    $('#' + id).append(data);
    $('.comments').slideDown();
  });
};

// Takes post ID as input. Posts upvote. Changes upvote icon color on success
var upvote = function(id) {
  $.post('/upvote/' + id, {
    upvote: True
  }, function(id) {
    $('#' + id).find('.fontawesome-plus').css('color', 'green');
  });
};

// Event listener for delete post
$('.fontawesome-trash').on('click', function () {
  id = $(this).parents("article").attr('id');
  trash(id);
});

//Event listener for upvote
$('.fontawesome-plus').on('click', function() {
  id = $(this).parents('article').attr('id');
  console.log('plus called');
  upvote(id);
});

$('button').click(function () {
  console.log('button click');
});
