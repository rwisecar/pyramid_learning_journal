// AJAX to enable asynchronous reload for delete view
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

// AJAX to enable asynchronous reload for create form
$(document).ready(function(){
    $('form[name=home_form]').submit(function(){
        $.post({
            url: '/journal/new-entry',
            data: $('form[name=home_form]').serialize(),
            success: function(){
                console.log("new entry created");
            }
        });
    });
});  

// AJAX to enable asynchronous reload for edit view-- NOT SETUP TO RUN
$(document).ready(function(){
    $('form[name=edit_form]').submit(function(){
        $.post({
            url: '/journal/' + $(this).attr("data") + '/edit-entry',
            data: $('form[name=edit_form]').serialize(),
            success: function(){
                console.log("entry edited");
            }
        });
    });
});
