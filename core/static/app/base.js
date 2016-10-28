$(function () {
  $('[data-toggle="tooltip"]').tooltip()
  $(document).on("click", ".js-skip-to-content", function() {
    return $("#start-of-content")
      .next()
      .attr("tabindex","-1")
      .focus()
  });
})
