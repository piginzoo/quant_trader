// 菜单导航数链接
window.__navLinks = [
  {
    title: "文档识别服务",
    include: [
      {
        name: "合同识别",
        address: "http://test.fuqianla.net/contractDiff/?token=demo&batchNo=2020061788&merchantId=ZMKM202007136688&type=condiffPc#/",
        target: "_blank",
        status: false
      },
      {
        name: "通用OCR识别",
        address: "/list.html",
        target: "_self",
        status: false
      }
    ]
  },
  {
    title: "卡证识别服务",
    include: [
      {
        name: "身份证识别",
        address: "",
        target: "_self",
        status: false
      },
      {
        name: "银行卡识别",
        address: "",
        target: "_self",
        status: false
      },
      {
        name: "车牌识别",
        address: "/main.html?name=plate",
        target: "_self",
        status: false
      }
    ]
  },
  {
    title: "版面分析服务",
    include: [
      {
        address: "http://pfocr.creditease.corp/pfocr/bankDetail",
        name: "银行流水",
        target: "_blank",
        status: false
      },
      {
        address: "",
        name: "征信报告",
        target: "_self",
        status: false
      },
      {
        name: "公积金",
        address: "http://pfocr.creditease.corp/pfocr/gjjDetail",
        target: "_blank",
        status: false
      }
    ]
  },
  {
    title: "辅助服务",
    include: [
      {
        name: "文本纠错",
        address: "/main.html?name=document",
        target: "_self",
        status: false
      },
      {
        name: "表格检测",
        address: "/main.html?name=detect",
        target: "_self",
        status: false
      }
    ]
  }
];

// 首页链接
window.__homeLinks = [
  {
    name: "合同识别",
    address: "http://test.fuqianla.net/contractDiff/?token=demo&batchNo=2020061788&merchantId=ZMKM202007136688&type=condiffPc#/",
    target: "_blank"
  },
  {
    name: "车牌识别",
    address: "/main.html?name=plate",
    target: "_self"
  },
  {
    name: "银行流水识别",
    address: "http://pfocr.creditease.corp/pfocr/bankDetail",
    target: "_blank"
  },
  {
    name: "通用OCR识别",
    address: "/list.html",
    target: "_self"
  }
]
