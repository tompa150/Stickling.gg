$("#like").on("click", function() {
    const id = $(this).attr("data-id");

    if ($(this).attr("data-liked") === "true") {
        // Unlike
        $.ajax({
            url: `/unlike_ad/${id}/`,
            type: "POST",
            dataType: "JSON"
        }).done(function(data) {
            if(data.success === true) {
                $("#like").attr("data-liked", "false");
            }
        })
    } else {
        // Like
        $.ajax({
            url: `/like_ad/${id}/`,
            type: "POST",
            dataType: "JSON"
        }).done(function(data) {
            if(data.success === true) {
                $("#like").attr("data-liked", "true");
            }
        })
    }
    
});