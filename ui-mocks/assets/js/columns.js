$(document).ready(function() {
    // Javascript to resize columns to the size we'd like
    var footer_height = 66;
    var h = $(document).height() - footer_height;
    $('.left-column').height(h);
    $('.right-column').height(h);
});

$(window).resize(function() {
    // Resize the height of each div when the window is resized
    var footer_height = 66;
    var h = $(document).height() - footer_height;
    $('.left-column').height(h);
    $('.right-column').height(h);
});
