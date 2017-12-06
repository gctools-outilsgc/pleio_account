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
});
