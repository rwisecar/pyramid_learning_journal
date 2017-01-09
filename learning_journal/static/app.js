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
// $(document).ready(function(){
//     var csrfToken = "{{ request.session.get_csrf_token() }}";
//     $('.home_form').submit(function(e){
//         e.preventDefault();
//         $.post({
//             headers: { 'X-CSRF-Token': csrfToken },
//             url: 'create',
//             data: {"title": $('#title').val(), "post": $('#post').val()},
//             success: function(){
//                 var creation_date = new Date();
//                 var year = creation_date.getFullYear();
//                 var month = creation_date.getMonth() + 1;
//                 if (month.toString().length == 1) {
//                     month = "0" + month;
//                 };
//                 var day = creation_date.getDate();
//                 if (day.toString().length == 1){
//                     day = "0" + day;
//                 };

//                 $('#entry_title').append($('#title').val());
//                 $('#entry_date').append($('creation_date'));
//                 $('#entry_text').append($('#post').val());
//                 $('#title').val("");
//                 $('#entry').val("");
//             }
//         });
//     });
// });  

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
