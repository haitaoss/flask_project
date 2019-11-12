function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
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
                $("#user-name").val(data.data.user.name);
                return;
            }
            alert(data.errmsg);

        }
    });
    // 图片表单提交触发的事件
    $("#form-avatar").submit(function (e) {
        // 阻止表单的默认行为(阻止浏览器，让js来上传)
        e.preventDefault();

        // 利用jquery.form.min.js提供的ajaxSubmit对表单进行异步提交
        $(this).ajaxSubmit(
            {
                url: "/api/v1.0/users/avatar",
                type: "post",
                // 不需要data，headers，这个ajaxSubmit已经封装好了
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                dataType: "json",
                success: function (data) {
                    if (data.errno == 0) {
                        // 上传成功
                        $("#user-avatar").attr("src", data.data.avatar_url);
                        return;
                    }
                    alert(data.errmsg);
                }
            }
        )
    });
    // 保存用户名
    $("#form-name").submit(function (e) {
        // 阻止浏览器的提价行为
        e.preventDefault();

        var name = $("#user-name").val();
        var data_json = {name: name};
        var data_str = JSON.stringify(data_json);
        $.ajax({
            url: "/api/v1.0/users",
            type: "put",
            data: data_str,

            headers: {
                "Content-Type":"application/json",
                "X-CSRFToken": getCookie("csrf_token")
            },
            dataType: "json",
            success: function (data) {
                if (data.errno == 0) {
                    // 获取成功设置，用户信息到页面中
                    $("#user-name").val(data.data.name);
                    return;
                }
                alert(data.errmsg);

            }
        });
    });

});
