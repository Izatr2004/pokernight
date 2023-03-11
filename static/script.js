function tip(user_id) {
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
                }, 4000); // close dialog after 5 seconds
                $('#value-container').html("HP: " + data.hp);
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
                }, 4000); // close dialog after 5 seconds
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
            $("#dialog-message").text("No Internet Connection!");
            setTimeout(function() {
                $("#dialog-message").dialog("close");
            }, 4000); // close dialog after 5 seconds
        }
    });
}

function updateHP(amount) {
    $.ajax({
        url: "/update-hp",
        type: "POST",
        data: {amount: amount},
        success: function(response) {
            $('#value-container').html("HP: " + response.new_hp);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function placeBounty(user_id) {
    $.ajax({
        type: 'POST',
        url: '/players',
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
                $("#dialog-message").text("You have successfully placed a bounty!");
                setTimeout(function() {
                    $("#dialog-message").dialog("close");
                }, 4000); // close dialog after 5 seconds
                $('#value-container').html("HP: " + data.hp);
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
                }, 4000); // close dialog after 5 seconds
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
            $("#dialog-message").text("No Internet Connection!");
            setTimeout(function() {
                $("#dialog-message").dialog("close");
            }, 4000); // close dialog after 5 seconds
        }
    });
}