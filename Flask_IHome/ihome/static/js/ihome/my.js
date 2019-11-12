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

$(function () {
    // 访问接口获取用户的信息
    $.ajax({
        url: "/api/v1.0/users",
        type: "get",
        dataType: "json",
        success: function (data) {
            if (data.errno == 0) {
                // 获取成功设置，用户信息到页面中
                $("#user-avatar").attr("src", data.data.user.avatar_url);
                $("#user-name").html(data.data.user.name);
                $("#user-mobile").html(data.data.user.mobile);
                 return;
            }
            alert(data.errmsg);

        }
    })
});