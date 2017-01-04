// AJAX to enable asynchronous reload
$(document).ready(function(){
    var deleters = $(".delete");
    deleters.click(function(){
        $.ajax({
            url: '/journal/delete/' + $(this).attr("data"),
            success: function(){
                console.log("deleted");
            }
        });
    });
});