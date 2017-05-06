$(document).ready(function() {
  $('.fontawesome-edit').click(function () {
    id = $(this).parents('article').attr('id');
    $.get('/editpost/' + id, function(data) {
      $('#' + id).html(data);
    });
  });
});
