function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
// $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
        // 获取数据
$.get("/api/v1.0/areas",function(data){
    if(data.errno==0){
        var areas = data.data;

        // 清空城区信息
//         $("#area-id").empty();
        for(var i =0 ;i < areas.length;i++){
            $("#area-id").append('<option value="'+areas[i].aid+'">'+areas[i].aname+'</option>')
        }
        return;
    }
    alert(data.errmsg);
})

});

$(function(){




})
