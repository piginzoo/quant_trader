let g_do_correct;
let g_do_rotate;
$(function(){
    $( "#upload_file" ).change( function () {
        var v = $( this ).val();
        var reader = new FileReader();
        reader.readAsDataURL( this.files[ 0 ] );
        reader.onload = function ( e ) {
            var result = reader.result.split( "," )[ 1 ]
            $( '#file_base64' ).val( result );
        };
    } );

    $('#submit_ocr').click(function() {
        return submit_ocr();
    });
});


function submit_ocr() {
    var img_base64 = $("#file_base64").val()
    var detect_model  =$("#detect_model").val()
    var output_type  =$("#output_type").val()
    var do_correct  =$("#do_correct").val()
    console.log(do_correct)
    //清空
    $("#small_table  tr:not(:first)").empty("");
    $("#big_image").attr("src","")

    $.ajax({
        url: '/detect/detect.ajax',
        type: 'post',
        dataType: 'json',
        contentType: "application/json",
        data:JSON.stringify({
            'img':img_base64,
            'detect_model':detect_model,
            'output_type':output_type,
            'do_verbose':true
        }),
        success: function(res){
            if (res.code != '0'){
                alert(res.message)
                return
            }
            // 成功处理逻辑
            load_result(res)
         },
        error: function(res){
            // 错误时处理逻辑
            debugger
            }
        });
}


function load_result(result) {
    $("#big_image").attr("src","data:image/jpg;base64," + result.image)
    var small_images =result['small_images']
    var $table = $("#small_table");
    small_images.forEach(function (e,i,array) {
        var $tr ='<tr>'
              +'<td width="70%" align="left"><img style="min-height:20px;max-width:95%" src="data:image/jpg;base64,'+e+'"></td>'
              +'<td width="30%" style="WORD-WARP:break-word">'+result['boxes'][i]+'</td>'
            +'</tr>'
        $table.append($tr)
    });

}



function queryCorrect(is_correct, id) {
    // $("#do_correct").val(is_correct);
    g_do_correct = is_correct
    $("#correct_true").removeClass("btn-primary");
    $("#correct_false").removeClass("btn-primary");
    $("#" + id).addClass("btn-primary");
}

function queryRotate(is_rotate, id) {
    g_do_rotate = is_rotate
    $("#rotate_true").removeClass("btn-primary");
    $("#rotate_false").removeClass("btn-primary");
    $("#" + id).addClass("btn-primary");
}


function queryModel(detect_model, id) {
    $("#detect_model").val(detect_model);
    $(".detect_model").removeClass("btn-primary");
    $("#" + id).addClass("btn-primary");
}


function queryOutput(output_type, obj) {
    $("#output_type").val(output_type);
    $(".output_type").removeClass("btn-primary");
    $(obj).addClass("btn-primary");
}

