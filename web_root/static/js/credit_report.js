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
        url: '/credit_report/split.ajax',
        type: 'post',
        dataType: 'json',
        contentType: "application/json",
        data:JSON.stringify({
            'img':img_base64,
            'sid':"page_sid",
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
    $("#split_width").text(result.split_width)
    $("#rotate_angle").text(result.rotate_angle)

    var small_images =result['split_images']

    var $table = $("#small_table");
    small_images.forEach(function (e,i,array) {
        var $tr ='<tr>'
              +'<td width="90%" align="left"><img style="min-height:20px;max-width:95%" src="data:image/jpg;base64,'+e+'"></td>'
            +'</tr>'
        $table.append($tr)
    });

}

