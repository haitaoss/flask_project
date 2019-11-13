// 将表单数据变成json对象，返回
function getFormData(obj) {
    var data = {};
    //$("#form-house-info").serializeArray().map(function (x) {
    // map函数,里面的参数当前遍历的对象
    // each函数，有两个参数，当前下表和当前页面的元素。需要$()才能变成对象
    obj.serializeArray().map(function (x) {
        data[x.name] = x.value;
    });
    return data;
}

// 获取当前浏览器保存的cookie的值
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}