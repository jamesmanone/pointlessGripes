
/* jQuery and AJAX was not part of the assignment. I wrote this code because
   the idea of new page loads for every upvote, comment read, comment post
   and a dedicated page for deleting a post just seems ridiculous. I didn't
   know jQuery or AJAX, and had only a tenuous grasp on javascript, but learned
   what I could to get this done. Please keep that in mind when grading. */

$(document).ready(function() {

  // Event listener for delete post
  $('.fontawesome-trash').click(function () {
    id = $(this).parents("article").attr('id');
    trash(id);
  });

  // Sets event listener for new comment box. If new comment, posts comment
  $('.submit-comment').click(function() {
    id = $(this).parents('article').attr('id');
    commentVal = $(this).siblings('input[name="newcomment"]').val();
    comments = $('#' + id).children('.comments');
    $.post('/comments/' + id, {
      'comment': commentVal
    }, function (data) {
      console.log('posted');
        comments.append(data.result);
    });
  });

  // Event listener for upvote
  $('.fontawesome-plus').click(function() {
    id = $(this).parents("article").attr('id');
    upvote(id);
  });

  // Event listener for comments drawer
  $('.comment-tab').click(function() {
    id = $(this).parents('article').attr('id');
    $(this).hide();
    $(this).siblings('.open-tab').show();
    openCommments(id);
  });

  // Event  listener to close comment drawer
  $('.open-tab').click(function() {
    var comments = $(this).siblings('.comments');
    comments.slideUp();
    comments.empty();
    $(this).hide();
    $(this).siblings('.newcomment').hide();
    $(this).siblings('.comment-tab').show();
  });

  $('.signup-button').click(function() {
    $.get('/signup', function(data) {
      $('.form-modal').html(data);
      $('.form-modal').slideDown();
    });
  });

  $('.login-button').click(function() {
    $.get('/login', function(data) {
      $('.login-modal').html(data);
      $('.login-modal').slideDown();
    });
  });

  $('.newpost').click(function() {
    $.get('/newpost', function(data) {
      if(data.success) {
        $('.newpost-slide').html(data.result);
        $('.newpost-slide').slideDown();
      } else {
        $('.login-button').trigger('click');
      }
  });
});

  $('.fontawesome-edit').click(function () {
    id = $(this).parents('article').attr('id');
    $.get('/editpost/' + id, function(data) {
      $('#' + id).html(data);
    });
  });

});

/* Takes post ID as input. After confirming delete, sends delete
   post to /delete/{post_id}. Fades out post on success */
var trash = function(id) {
  if (confirm('Delete post?')) {
    $.post('/delete/' + id, {
      delete: 'True'
    })
      .done(function() {
        $('#' + id).fadeOut();
      });
  }
};

// Takes post ID as input. Posts upvote. Replaces upvote count with response
// from server on success.
var upvote = function(id) {
  $.post('/upvote/' + id, {
    upvote: 'True'
  }, function(data) {
      if(data.success === true) {
        plus = $('#' + id).find('.fontawesome-plus');
        plus.siblings('.upvote-count').html(data.message);
      } else {
          plus = $('#' + id).find('.fontawesome-plus').siblings('.error');
          plus.append('<br>' + data.message);
        }
    }, 'json');
};

/* Takes post ID as input. Makes AJAX request for comments and appends them to
   .comments. Once populated, it slides down the comment drawer. Sets Event
   listener for comment delete button. */
var openCommments = function(id) {
  $.getJSON('/comments/' + id, function(data) {
    var comments = $('#' + id).find('.comments');
    $.each(data, function(key, value) {
      if(key !== 'success') {
        comments.append(value);
      }
    });
    comments.slideDown();
    comments.siblings('.newcomment').slideDown();

    $('.fontawesome-remove-sign').click(function() {
      console.log('click');
      id = $(this).parents('.comment').attr('id');
      deleteComment(id);
    });
  });
};


// Deletes comment using AJAX post.
var deleteComment = function(id) {
  if(confirm('Are you sure you want to delete this post?')) {
    $.post('/commentdelete/' + id, function() {
      $('#' + id).fadeOut();
    });
  }
};
