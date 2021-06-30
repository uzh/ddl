
// When the user scrolls down 50px from the top of the document, resize the header's font size
$(window).on("scroll", function() {
    var s = 110 - Math.min(110, $(document).scrollTop());
    $("#header-brand-full").height(s);

    if (s <= 52) {
        $("#header-brand-full").addClass( "is-hidden" )
        $("#header-brand-small").removeClass( "is-hidden" )
    } else {
        $("#header-brand-full").removeClass( "is-hidden" )
        $("#header-brand-small").addClass( "is-hidden" )
    }
});

$(document).ready(function() {
    $("#navbar-burger").click(function () {
        $(".modal").addClass("is-active")
    });

    $(".modal-close").click(function () {
        $(".modal").removeClass("is-active")
    });
});
