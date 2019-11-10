function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url: '/api/v1.0/session',
        type: "delete",
        dataType: "json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (data) {
            if ("0" == data.errno) {
                location.href = '/index.html';
            }
        }
    })
}

$(document).ready(function () {
});