function updateMoney(user_id) {
    $.ajax({
        type: 'POST',
        url: '/dealers',
        data: {'user_id': user_id},
        success: function(data) {
            if (data.success) {
                $("#dialog-message").dialog({
                    modal: true,
                    buttons: {
                        Ok: function() {
                            $(this).dialog("close");
                        }
                    }
                });
                $("#dialog-message").text("You have successfully tipped");
                setTimeout(function() {
                    $("#dialog-message").dialog("close");
                }, 3000); // close dialog after 5 seconds
            } else {
                $("#dialog-message").dialog({
                    modal: true,
                    buttons: {
                        Ok: function() {
                            $(this).dialog("close");
                        }
                    }
                });
                $("#dialog-message").text("You don't have enough HP!");
                setTimeout(function() {
                    $("#dialog-message").dialog("close");
                }, 3000); // close dialog after 5 seconds
            }
        },
        error: function() {
            $("#dialog-message").dialog({
                modal: true,
                buttons: {
                    Ok: function() {
                        $(this).dialog("close");
                    }
                }
            });
            $("#dialog-message").text("Failed to make AJAX request");
            setTimeout(function() {
                $("#dialog-message").dialog("close");
            }, 3000); // close dialog after 5 seconds
        }
    });
}