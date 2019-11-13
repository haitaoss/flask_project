function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function getFormData(formId) {
    var data = {};
    $(formId).find('input,select').each(function () {
        data[this.name] = this.value
    });
    return JSON.stringify(data);
}


$(function () {
// $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    // 获取数据
    $.get("/api/v1.0/areas", function (data) {
        if (data.errno == 0) {
            var areas = data.data;

            // for(var i =0 ;i < areas.length;i++){
            //     $("#area-id").append('<option value="'+areas[i].aid+'">'+areas[i].aname+'</option>')
            // }

            // 使用js模板
            var html = template("areas-templ", {areas: areas});
            $("#area-id").html(html);
            return;
        }
        alert(data.errmsg);
    })

    // 保存房屋的基本信息
    $("#form-house-info").submit(function (e) {
        // 阻止默认提交行为
        e.preventDefault();

        //获取表单数据的json字符
        var data = {};
        $("#form-house-info").serializeArray().map(function (x) {
            data[x.name] = x.value;
        });

        // 收集设置，id信息
        var facility = [];
        $(":checked[name='facility']").each(function (index, x) {
            facility[index] = $(x).val();
        });

        // 把设备列表设置到data中
        data.facility = facility;
        //发起ajax请求
        $.ajax({
            url: "/api/v1.0/houses/info",
            type: "post",
            data: JSON.stringify(data),
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrf_token")
            },
            dataType: "json",
            success: function (resp) {
                if (resp.errno == "4101") {
                    //用户未登录
                    location.href = "/login.html";
                    return;
                } else if (resp.errno == 0) {
                    // 保存成功

                    // 隐藏基本信息表单
                    $("#form-house-info").hide();
                    // 显示图片表单
                    $("#form-house-image").show();

                    // 设置图片表单的id字段
                    $("#house-id").val(resp.data.house_id);
                    return;
                }
                alert(resp.errmsg);
            }

        })
    });

    // 保存房屋图片

    $("#form-house-image").submit(function (e) {
        // 阻止表单的默认提交行为
        e.preventDefault();

        //发起使用插件提交多文本表单数据，他会帮我们传递参数
        $("#form-house-image").ajaxSubmit(
            {
                url: "/api/v1.0/houses/image",
                type: "post",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                dataType: "json",
                success: function (resp) {
                    if (resp.errno == "4101") {
                        //用户未登录
                        location.href = "/login.html";
                        return;
                    } else if (resp.errno == 0) {
                        // 保存成功
                        //设置图片
                        $("#image_url").attr("arc", resp.data.image_url);
                        $(".house-image-cons").append("<img src='"+resp.data.image_url+"' ></img>");
                        return;
                    }
                    alert(resp.errmsg);
                }

            }
        )

    });
});
