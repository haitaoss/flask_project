$(function () {
    $("#form1").submit(function (e) {
        // 阻止浏览器的表单提交行为
        e.preventDefault();

        // 获取表单数据
        var data = {};

        $("#form1").serializeArray().map(function (x) {
            data[x.name] = x.value;
        });

        //发起ajax post 请求,数据是json数据
        $.ajax({
                url: "/api/v1.0/pay",
                type: "post",
                data: JSON.stringify(data),
                dataType: "json",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFTOKEN": getCookie("csrf_token")

                },
                success: function (resp) {
                    if (resp == "0") {
                        alert(resp.errmsg);
                        // 支付成功
                        return;
                    }
                    alert(resp.errmsg);
                }
            }
        )
    });
});
