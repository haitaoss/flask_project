//js读取cookie的方法
function getCookie(name) {
    // \b是单词边界
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 保存图片验证码编号
var imageCodeId = "";

// uuid 的js源代码
function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 形成图片验证码的后端地址，设置到页面中让浏览器请求生成验证码的接口
    //1.生成图片验证码编号
    imageCodeId = generateUUID();

    //2.设置，img标签的资源路径
    // $('.image-code').next('img').attr('src', '/api/v1.0/image_codes/' + imageCodeId);
    $('.image-code img').attr('src', '/api/v1.0/image_codes/' + imageCodeId);

}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    // 向后端发送请求
    $.get("/api/v1.0/sms_codes/" + mobile + "?id=", {image_code: imageCode, image_code_id: imageCodeId},
        function (data) {
            // data 是后端返回的响应值，因为后端返回的是json字符串
            // 所以ajax帮助我们把这个json字符串转换为js对象，data就是转换后的对象
            if (data.errno == "4002") {
                //验证码失效，所以刷新一下验证码
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
                generateImageCode();
            } else if (data.errno == "4201") {
                // 说明发送短信的请求过于频繁
                alert(data.errmsg);
                var num = 60;
                // 表示发送信息
                var timer = setInterval(function () {
                    $('.phonecode-a').html(num + "秒");
                    if (num === 1) {
                        // 恢复原本本，原事件
                        $('.phonecode-a').html("获取验证码");
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                        //销毁定时器
                        clearInterval(timer);
                    }
                    num -= 1;

                }, 1000, 60);//没1000毫秒执行一次，执行60秒
            } else {
                alert(data.errmsg);
                generateImageCode();
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
            }
        }, 'json');
}

$(document).ready(function () {
    generateImageCode();
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function () {
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function () {
        $("#phone-code-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function () {
        $("#password2-err").hide();
    });

    // 为表单的提交补充自定义的函数行为     （提交事件e）
    $(".form-register").submit(function (e) {

        // 阻止浏览器对于表单的默认自动提交行为
        e.preventDefault();
        mobile = $("#mobile").val();
        phoneCode = $("#phonecode").val();
        passwd = $("#password").val();
        passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        //调用ajax向后端发送注册请求
        var req_data = {
            mobile: mobile,
            sms_code: phoneCode,
            password: passwd,
            password2: passwd2,

        };
        // 将json对象变成json字符串。使用原始ajax发送json数据，必须是json字符串
        // 否则执行ajax代码的时候会出错
        var req_json = JSON.stringify(req_data);
        $.ajax({
            url: '/api/v1.0/users',
            type: 'post',
            data: req_json,
            // contentType: "application/json",
            dataType: 'json',
            headers: {
                "contentType": "application/json",
                "X-CSRFToken": getCookie("csrf_token")
            },//请求头，将csrf_token放到请求头中，方便后端csrf进行校验
            success: function (data) {
                if (data.errno == "0") {
                    // 注册成功，跳转到主页
                    location.href = "/index.html";
                } else {
                    alert(data.errmsg);
                }
            }
        })
    });
});