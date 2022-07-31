//各页面的输入输出参数项
page_param_json = {
    "ocr.v1": {
        "title": "OCR.V1.0测试结果",
        "url": "ocr",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr.png"
            },
            {
                "name": "do_correct",
                "name_zh": "是否NLP纠错",
                "type": "bool",
                "default": false
            }
        ],
        "output_type": "show",
        "output": {}
    },
    "crnn.v1": {
        "title": "CRNN v1.0 测试结果",
        "url": "/crnn",
        // "input_is_array": true,
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image"
            }
        ],
        "output_type": "show"
    },
    "crnn.v2": {
        "title": "CRNN v2.0测试结果",
        "url": "/v2/crnn.ajax",
        // "input_is_array": true,
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image"
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/crnn.png"
            },
        ],
        "output_type": "show"
    },
    "captcha": {
        "title": "验证码识别",
        "url": "/business/captcha/tax.ajax",
        "input_is_array": false,
        "input": [
            {
                "name": "img",
                "name_zh": "图片",
                "type": "image"
            },
            {
                "name": "type",
                "name_zh": "类型",
                "type": "select",
                "value": {
                    "common": "通用",
                    "tax": "国税"
                },
            },
            {
                "name": "color",
                "name_zh": "颜色",
                "type": "select",
                "value": {
                    "black": "黑",
                    "blue": "蓝",
                    "yellow": "黄",
                    "red": "红"
                },

            }
        ],
        "output_type": "show"
    },
    "ocr.v2": {
        "title": "OCR v2.0 测试结果",
        "url": "/v2/ocr.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr.png"
            },
            {
                "name": "biz_type",
                "name_zh": "业务类型",
                "type": "select",
                "value": {
                    "00": "默认",
                    "01": "银行流水",
                    "02": "征信报告",
                },
                "default": "00"
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "ocr.v3": {
        "title": "OCR v2.0 测试结果",
        "url": "v2/ocr_debug.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "do_preprocess",
                "name_zh": "是否预处理",
                "type": "bool",
                "default": false
            },
            {
                "name": "detect_model",
                "name_zh": "检测模型",
                "type": "select",
                "value": {
                    "ctpn": "ctpn",
                    "psenet": "psenet",
                    "psenet1": "psenet1",
                    "doc": "合同文档",
                    "gjj": "公积金",
                },
                "default": "psenet"
            },
            {
                "name": "do_correct",
                "name_zh": "是否NLP纠错",
                "type": "bool",
                "default": false
            },
            {
                "name": "correct_model",
                "name_zh": "纠错模型",
                "type": "select",
                "value": {
                    "bert": "bert",
                    "report_keywords": "征信报告"
                }
            },
            {
                "name": "do_table_detect",
                "name_zh": "是否检测表格",
                "type": "bool",
                "default": false
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "plate": {
        "title": "车牌检测结果",
        "url": "/plate.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/plate.jpg"
            },
            {
                "name": "imgSign",
                "name_zh": "图片标识",
                "type": "select",
                "value": {
                    "T1": "T1",
                    "T2": "T2"
                },
                "default": "T1"
            },
            {
                "name": "merchantPrimaryKeyId",
                "name_zh": "商户主键id",
                "type": "input"
            },
            {
                "name": "merchantPlate",
                "name_zh": "商户车牌号码",
                "type": "input"
            },
        ],
        "output": {},
        "output_type": "plate"
    },
    "plate_ocr": {
        "title": "车牌小图检测",
        "url": "/plate_ocr.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            }
        ],
        "output": {},
        "output_type": "plate"
    },
    "plate_barcode": {
        "title": "车牌和二维码检测",
        "url": "/business/plate_barcode.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/plate_barcode.jpg"
            },
            {
                "name": "plate",
                "name_zh": "商户车牌号码",
                "type": "input"
            },
            {
                "name": "extra_json",
                "name_zh": "附加字段",
                "type": "extra_json",
                "default": {
                    "sn": [""]
                }
            }
        ],
        "output": {},
        "output_type": "show"
    },
    "preprocess": {
        "title": "图片预处理测试结果",
        "url": "/preprocess.ajax",
        "input": [
            {
                "name": "data",
                "name_zh": "识别图片",
                "type": "image",
            }, {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/rotate.jpg"
            },
        ],
        "output": {},
        "output_type": "show",

    },
    "rotate.single": {
        "title": "图片预处理测试结果",
        "url": "/rotate/single.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            }, {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/rotate.jpg"
            },
        ],
        "output": {},
        "output_type": "show",

    },
    "detect": {
        "title": "图像检测测试",
        "url": "/detect/detect.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr.png"
            },
            {
                "name": "detect_model",
                "name_zh": "检测模型",
                "type": "select",
                "value": {
                    "ctpn": "ctpn",
                    "psenet": "psenet",
                    "psenet1": "psenet1",
                    "plate_detect": "车牌",
                    "table_detect": "表格",
                    "table.v2": "绿本",
                    "card": "卡证类",
                    "doc": "图像",
                    "psenet.jsz": "psenet.驾驶证",
                    "invoice_segment": "发票混贴",
                    "car_contract": "车辆融资/抵押合同"
                },
                "default": "psenet"
            }, {
                "name": "output_type",
                "name_zh": "输出类型",
                "type": "select",
                "value": {
                    "rect": "外接矩形",
                    "para": "平行四边形",
                    "poly": "多边形",
                    "ori": "原始坐标",
                },
                "default": "rect"
            },
            {
                "name": "channel",
                "name_zh": "渠道类型",
                "type": "select",
                "value": {
                    "single": "single",
                    "tfserving": "tfserving",
                    "rest": "rest",
                },
                "default": "tfserving"
            },
            {
                "name": "do_lsd",
                "name_zh": "是否做直线矫正",
                "type": "bool",
                "default": false
            },
        ],
        "output": {},
        "output_type": "show",
    },
    "document": {
        "title": "合同识别",
        "url": "/document.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr.png"
            },
            {
                "name": "do_correct",
                "name_zh": "是否NLP纠错",
                "type": "bool",
                "default": false
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "credit.report.split": {
        "title": "征信报告预处理V1",
        "url": "/business/credit_report/split.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/rotate.jpg"
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "gjj.v1": {
        "title": "公积金识别",
        "url": "/gjj",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr.png"
            },
        ],
        "output_type": "show",
        "output": {}
    }, "gjj": {
        "title": "公积金识别V1",
        "url": "/gjj.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr.png"
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "correct": {
        "title": "文本纠错V1",
        "url": "/correct",
        "input": [
            {
                "name": "sentences",
                "name_zh": "要纠错的文本",
                "type": "input",
                "is_array": true
            },
            {
                "name": "merchantPrimaryKeyId",
                "name_zh": "商户主键id",
                "type": "input",
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "binary": {
        "title": "图像二值化",
        "url": "/tools/binary.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr.png"
            },
            {
                "name": "threshold",
                "name_zh": "二值化阈值",
                "type": "input",
                "default": -1
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "table_doc": {
        "title": "带表格文档类识别",
        "url": "/table_doc.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/lv.jpg"
            },
            {
                "name": "biz_type",
                "name_zh": "业务类型",
                "type": "select",
                "value": {
                    "00": "其他",
                    "07": "绿本",
                },
                "default": "07"
            },
            {
                "name": "do_rotate",
                "name_zh": "是否旋转摆正",
                "type": "bool",
                "default": true
            },
            {
                "name": "do_table",
                "name_zh": "是否做表格识别",
                "type": "bool",
                "default": true
            },
            {
                "name": "do_correct",
                "name_zh": "是否做文字矫正",
                "type": "bool",
                "default": false

            }
        ],
        "output_type": "show",
        "output": {}
    },
    "card": {
        "title": "卡证类识别\n",
        "url": "/card.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/jsz.jpg"
            },
            {
                "name": "biz_type",
                "name_zh": "卡证类型",
                "type": "select",
                "value": {
                    "03": "行驶证",
                    "04": "驾驶证",
                    "05": "银行卡",
                    "06": "身份证",
                    "00": "其他",
                },
                "default": "04"
            },
            {
                "name": "do_preprocess",
                "name_zh": "是否区域切出",
                "type": "bool",
                "default": true

            },
            {
                "name": "do_correct",
                "name_zh": "是否做文字矫正",
                "type": "bool",
                "default": false

            }
        ],
        "output_type": "show",
        "output": {}
    },
    "invoice": {
        "title": "发票识别",
        "url": "/business/invoice/ocr.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/invoice.jpg"
            }, {
                "name": "do_multi",
                "name_zh": "是否发票混贴",
                "type": "bool",
                "default": false
            },
            {
                "name": "do_correct",
                "name_zh": "是否做文字矫正",
                "type": "bool",
                "default": false
            }
        ],
        "output_type": "show",
        "output": {}
    },
    "biz_card": {
        "title": "卡证识别",
        "url": "/business/card/ocr.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
            },
            {
                "name": "biz_type",
                "name_zh": "业务类型",
                "type": "select",
                "value": {
                    "03": "行驶证",
                    "04": "驾驶证",
                    "05": "银行卡",
                    "06": "身份证",
                    "00": "其他",
                },
                "default": "04"
            }
        ],
        "output_type": "biz_card",
        "output": {}
    },
    "invoice_segment": {
        "title": "混贴发票分割",
        "url": "/business/invoice/segment.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/multi_invoice.jpg"
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "sali": {
        "title": "交强险",
        "url": "/business/sali/ocr.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/sali.png"
            },
        ],
        "output_type": "show",
        "output": {}
    },
    "v_contract": {
        "title": "车贷合同印章签名校验",
        "url": "/business/vehicle/contract/verify.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr/diya.jpg"
            },
            {
                "name": "contract_type",
                "name_zh": "合同类型",
                "type": "select",
                "value": {
                    "01": "融资租赁合同",
                    "02": "抵押合同",
                },
                "default": "01"
            },

        ],
        "output_type": "show",
        "output": {}
    },
    "table.line": {
        "title": "表格线检测",
        "url": "/table/table_line.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/ocr/diya.jpg"
            }

        ],
        "output_type": "show",
        "output": {}
    },
    "vrc.ocr": {
        "title": "绿本识别",
        "url": "/business/vehicle/vehicle_register_certificate.ajax",
        "input": [
            {
                "name": "img",
                "name_zh": "识别图片",
                "type": "image",
            },
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": "test/lv.jpg"
            },
            {
                "name": "page",
                "name_zh": "12页/34页",
                "type": "select",
                "value": {
                    "12": "1-2页",
                    "34": "3-4页",
                },
                "default": "12"
            }
        ],
        "output_type": "show",
        "output": {}
    },
    "img.preview": {
        "title": "图片预览（传绝对路径或者相对路径）",
        "url": "/tools/preview.ajax",
        "input": [
            {
                "name": "url",
                "name_zh": "图片地址",
                "type": "input",
                "default": ""
            }
        ],
        "output_type": "show",
        "output": {}
    }
}

var g_page_type = "ocr"
var g_origin_image = ""
var g_result_image = ""

/**
 * 获取元素html
 * @param element_node
 * @param image_arr
 * @returns {string}
 */
function get_element_str(element_node, image_arr) {
    var temp_str = ""
    let defaultValue = element_node.default;
    if (defaultValue == undefined) {
        defaultValue = ""
    }
    if (element_node.type == 'bool') {
        let true_class = "btn ";
        let false_class = "btn ";
        if (defaultValue === true)
            true_class += "btn-primary ";
        else if (defaultValue === false)
            false_class += "btn-primary ";

        temp_str += "<input type='hidden' class='form-control' name='" + element_node.name + "' value='" + defaultValue + "'>"

        temp_str +=
            "    <a href=\"javascript:;\" class='" + true_class + element_node.name + "' onclick=\"query_bool(true,this,'" + element_node.name + "');\">是</a>\n" +
            "    <a href=\"javascript:;\" class='" + false_class + element_node.name + "' onclick=\"query_bool(false,this,'" + element_node.name + "');\">否</a>"

    } else if (element_node.type == 'select') {

        temp_str += "<input  class='form-control select biz_type'  type='hidden' name='" + element_node.name + "' value='" + defaultValue + "'/>"

        $.each(element_node.value, function (key, item) {
            let sel_class = "biz_type btn btn_primary "
            if (key === defaultValue)
                sel_class += "btn-primary "
            temp_str += "<a href=\"javascript:;\" class='" + sel_class + element_node.name + "'" +
                " onclick=\"query_select('" + key + "',this,'" + element_node.name + "');\">" + item + "</a>"
        })
    } else if (element_node.type == 'image') {
        temp_str += "<input  class='form-control'  type='hidden' name='" + element_node.name + "' value=''/>"
        var img_id = element_node.name + "_file"
        temp_str += '<input  class="form-control"  type="file" id="' + img_id + '" multiple="multiple" />'
        image_arr.push(element_node.name)
    } else if (element_node.type == 'input') {
        temp_str += "<input  class='form-control'  type='text' name='" + element_node.name + "' value='" + defaultValue + "'/>"
    } else if (element_node.type == 'extra_json') {
        temp_str += '<textarea rows="3" cols="100" name="' + element_node.name + '">' + JSON.stringify(defaultValue) + '</textarea>'
    }
    return temp_str;
}

/**
 * 输出类型
 * 1. 一张大图多张小图
 * 2. 检测的一张大图，
 */


function init_page(page_type) {
    var input_str = ""
    var page_param = page_param_json[page_type]
    var image_arr = []
    $.each(page_param.input, function (index, value) {
        var temp_str =
            "<div class=\"form-group\">" +
            " <dl>" +
            "  <label>" + value.name_zh + "：</label>" +
            "  <dd>"
        temp_str += get_element_str(value, image_arr);
        temp_str +=
            "  </dd>" +
            "</dl>" +
            "</div>"
        input_str += temp_str
    })
    $("#toolbar").prepend(input_str)
    $.each(image_arr, function (i, img_name) {
        init_image(img_name + "_file", img_name)
    })
    if (page_param.title) {
        $("#result_title").html(page_param.title)
    }
    $("#request_url").html("请求url：" + page_param.url)
}

function init_image(image_id, image_name) {
    $("#" + image_id).change(function () {
        var v = $(this).val();
        var reader = new FileReader();
        reader.readAsDataURL(this.files[0]);
        reader.onload = function (e) {
            var result = reader.result.split(",")[1]
            $("input[name='" + image_name + "']").val(result)
            load_origin_image(result)
        };
    });
}

$(function () {

    g_page_type = getUrlParam("name")
    init_page(g_page_type)
    $('#submit_ocr').click(function () {
        return submit_ocr();
    });
});

function query_bool(bool_flg, e, cls) {
    $("." + cls).removeClass("btn-primary");
    $(e).addClass("btn-primary");
    $("input[name='" + cls + "']").val(bool_flg)
}

function query_select(select_type, e, cls) {
    $("." + cls).removeClass("btn-primary");
    $(e).addClass("btn-primary");
    $("input[name='" + cls + "']").val(select_type)
}


function submit_ocr() {
    //清空
    $("#small_table  tr:not(:first)").empty("");
    $("#big_image").attr("src", "")

    var param = {}
    param['do_verbose'] = true
    param['sid'] = 'page_sid'
    var page_param = page_param_json[g_page_type]
    $.each(page_param.input, function (index, item) {
        //extra_json, json转list
        if (item.type == 'extra_json') {
            temp_val = $("textarea[name='" + item.name + "']").val()
            temp_json = JSON.parse(temp_val)
            param = $.extend(param, temp_json)
        } else {
            let temp_val = $("input[name='" + item.name + "']").val()
            if (item.type == 'bool') {
                temp_val = JSON.parse(temp_val)
            }
            //数组元素则多拼
            if (item.is_array) {
                param[item.name] = [temp_val]
            } else {
                param[item.name] = temp_val
            }
            param[item.name] = temp_val
        }
    })
    //最外侧是数组
    if (page_param.input_is_array) {
        param = [param]
    }

    $.ajax({
        url: page_param.url,
        type: 'post',
        dataType: 'json',
        contentType: "application/json",
        data: JSON.stringify(param),
        success: function (res) {
            if (res.code != '0') {
                alert(res.message)
                $('#result_json').html(syntaxHighlight(res));
                return
            }
            // 成功处理逻辑
            load_result(res)
        },
        error: function (res) {
            // 错误时处理逻辑
            debugger
        }
    });
}


function load_result(result) {
    var output_type = page_param_json[g_page_type].output_type
    load_show(result)
    //展示json
    delete result['debug_info']
    delete result['show_info']
    $('#result_json').html(syntaxHighlight(result));
}


function load_show(data_list) {
    $("#show_table").empty("");
    var $table = $("#show_table");
    detail_list.forEach(function (row, i, array) {
        var $tr = '<tr>';
        title_list.forEach(function (e, i, array) {
            var cell_value = cell[e['name']]
            if (e['content_type'] == 'img') {
                $tr += '<td width="' + e['percent'] + '%" align="left"><img style="min-height:20px;max-width:95%" src="data:image/jpg;base64,' + cell_value + '"></td>'
            } else {
                $tr += '<td width="' + e['percent'] + '%" style="WORD-WARP:break-word">' + cell_value + '</td>'
            }
        });
        $tr += '</tr>'
        $table.append($tr)
    });
}


function __load_text(result) {
    $("#text_output").show()
    $("#text_table  tr:not(:first)").empty("");
    var $table = $("#text_table");

    let value;
    for (let key in result) {
        value = result[key]
        if (typeof (key) == "undefined") key = ""
        if (typeof (value) == "undefined") value = ""
        var $tr =
            '<tr>' +
            '   <td width="90%" align="left">' +
            '       <div class="text">' + key + '</div>' +
            '   </td>' +
            '   <td width="90%" align="left">' +
            '       <div class="text">' + value + '</div>' +
            '   </td>' +
            '</tr>'
        $table.append($tr)
    }
}


function load_origin_image(base64_img) {
    $("#orgin_image").attr("src", "data:image/jpg;base64," + base64_img)
}


function load_ocr(result) {
    $("#ocr_output").show()
    var debug_info = result.debug_info
    load_origin_image(debug_info.image)
    var $table = $("#small_table");
    var small_images = debug_info['small_images']
    var probs = debug_info['probs']

    small_images.forEach(function (e, i, array) {
        var $tr =
            '<tr>' +
            '   <td align="left"><img style="min-height:20px;max-width:95%" src="data:image/jpg;base64,' + e + '"></td>' +
            '   <td>' + debug_info['text'][i] + '</td>' +
            // + '<td>' + debug_info['text_corrected'][i] + '</td>'
            +'</tr>'
        $table.append($tr)
    });
}

function load_plate(result) {
    $("#plate_output").show()
    if (result.debug_info != null) {
        var debug_info = result.debug_info
        $("#plate_no").html(result.plate.plate)
        load_origin_image(debug_info.image)
        $("#plate_small").attr("src", "data:image/jpg;base64," + debug_info.plate_image)
    }
}

//// 2020.9 piginzoo
//function load_biz_card(result) {
//    var texts = result.debug_info['text']
//    var small_images = result.debug_info['small_images']
//    var biz_card_result = result.result
//    __load_text(biz_card_result) //显示文本
//    load_ocr(result) //显示图和小图
//}

function syntaxHighlight(json) {
    if (typeof json != 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
        function (match) {
            var cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        }
    );
}

//获取url中的参数
function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg); //匹配目标参数
    if (r != null) return unescape(r[2]);
    return null; //返回参数值
}
