function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function getFormData(formId) {
            var form = document.getElementById(formId);
            var data = {};
            var tagElements = form.getElementsByTagName('input');
            for (var j = 0; j < tagElements.length; j++) {
                var input = tagElements[j];
                var n = input.name;
                var v = input.value;
                data[n] = v;
            }
            return data;
        }
function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

$(function () {
    // 获取用户的认证信息
    $.ajax({
        url: "/api/v1.0/users",
        type: "get",
        dataType: "json",
        success: function (data) {
            if (data.errno == 0) {
                // 获取成功设置，用户信息到页面中
                $("#real-name").val(data.data.user.real_name);
                $("#id-card").val(data.data.user.id_card);
                $("#name").val(data.data.user.name);
                return;
            }
            alert(data.errmsg);

        }
    });

    // 修改认证信息
    $("#form-auth").submit(function (e) {
        // 阻止默认提交行为
        e.preventDefault();

        var data_json = getFormData("form-auth");
        // alert(data_json);
        var data_str = JSON.stringify(data_json);
        $.ajax({
            url: "/api/v1.0/users?auth=1",
            type:"put",
            data: data_str,
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrf_token")
            },
            dataType: "json",
            success: function (data) {
                if (data.errno == 0) {
                    $("#real-name").val(data.data.real_name);
                    $("#id-card").val(data.data.id_card);
                    return;
                }
                alert(data.errmsg);
            }
        })
    });
});
