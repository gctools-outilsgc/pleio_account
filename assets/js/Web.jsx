import "../less/all.less"

$(document).ready(function() {
   $(".password__toggle").on('click',function(e) {
       $(this).parent().find("input").each(function() {
           if ($(this).attr("type") == "password") {
               $(this).attr("type", "text");
           } else {
               $(this).attr("type", "password");
           }
        });
    });
      
    $("input").keypress(function(e) {
        if ($(this).attr("type") == "password") {
            var s = String.fromCharCode( e.which );
            if ( s.toUpperCase() === s && s.toLowerCase() !== s && !e.shiftKey ) {
                $(this).siblings(".capslock").text(gettext("Attention: CAPS LOCK is ON"));
            } else {
                $(".capslock").text("");
            }
        } else {
            $(".capslock").text("");
    }
    });
      
    $("input").blur(function(e) {
        $(".capslock").text("");
    });
    
    var theme_bg = $('.account-theme').data('bg');
    console.log(theme_bg);
    if(theme_bg){
        $('.account-theme').css('background-image','url(' + theme_bg + ')');
    }

});
