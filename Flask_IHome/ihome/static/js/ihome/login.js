function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
    });
    $(".form-login").submit(function (e) {
        // 阻止表单的默认提交行为
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        // 发送ajax请求

        // 封装参数
        var req_data = {
            mobile: mobile,
            password: passwd
        };
        var req_json = JSON.stringify(req_data);
        // 发送请求
        $.ajax({
            url: "/api/v1.0/sessions",
            type: "POST",
            data: req_json,
            dataType: "json",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (data) {
                if (data.errno == "0") {
                    location.href = "/index.html";
                } else {
                    alert(data.errmsg);
                }
            }
        })


    });
});