window.cache = {
  'user_suggest': {},
};

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
  $(document).on("click", ".js-skip-to-content", function() {
    return $("#start-of-content")
      .next()
      .attr("tabindex","-1")
      .focus()
  });

  $('.user_suggest input').on('keyup', function(evt) {
    var prefix = $(this).val();
    if (prefix.length < 3) {
      return;
    }
    if (window.cache.user_suggest[prefix]) {
      updateUserSuggest.call(this, prefix, window.cache.user_suggest[prefix]);
    } else {
      $.get(window.apiURL + 'user_suggest', {
        'prefix': prefix
      }, updateUserSuggest.bind(this, prefix));
    }
  });
})

function updateUserSuggest(prefix, data) {
  window.cache.user_suggest[prefix] = data;
  var ul = $(this).parent().find('.suggestions');
  ul.html('');
  if (data.length == 0) {
    ul.addClass('empty');
  } else {
    ul.removeClass('empty');
  }
  data.forEach(function(item) {
    ul.append('<li class="suggestion">' + item + '</li>');
  })

  ul.find('.suggestion').on('click', function(evt) {
    evt.preventDefault();
    var ul = $(this).parent(),
        input = ul.parent().find('input');
    ul.html('');
    ul.addClass('empty');
    input.val($(this).text());
  })
}
