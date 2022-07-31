let g_do_correct;
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

    $('#submit_doc').click(function() {
        return submit_doc();
    });
});


function submit_doc() {
    var img_base64 = $("#file_base64").val()
    var do_correct  =$("#do_correct").val()
    console.log(do_correct)
    //清空
    $("#small_table  tr:not(:first)").empty("");
    $("#big_image").attr("src","")

    $.ajax({
        url: '../document',
        type: 'post',
        dataType: 'json',
        contentType: "application/json",
        data:JSON.stringify({
            'img':img_base64,
            'do_correct': g_do_correct,
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
    var $table = $("#small_table");
    var small_images =result['small_images']
    small_images.forEach(function (e,i,array) {
        // console.log(i)
        var $tr ='<tr>'
              +'<td width="60%" align="left"><img style="min-height:20px;max-width:95%" src="data:image/jpg;base64,'+e+'"></td>'
              +'<td width="20%">'+result['text'][i]+'</td>'
              +'<td>'+result['text_corrected'][i]+'</td>'
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
