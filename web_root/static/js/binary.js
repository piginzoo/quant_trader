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
    $("#big_image").attr("src","")
    var threshold = $("#threshold").val()

    $.ajax({
        url: 'tools/binary.ajax',
        type: 'post',
        dataType: 'json',
        contentType: "application/json",
        data:JSON.stringify({
            "sid":"page",
            'img':img_base64,
            'threshold': threshold
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
}

