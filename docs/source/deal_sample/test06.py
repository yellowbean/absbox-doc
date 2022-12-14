JY_RMBS_2017_5 = 信贷ABS(
    "建元2017年第五期个人住房抵押贷款资产支持证券"
    ,("2022-07-26","2022-07-26","2022-08-26")
    ,"每月"
    ,{'清单':[["按揭贷款"
        ,{"放款金额":120,"放款利率":["浮动",0.085,{"基准":"LPR5Y","利差":0.01,"重置频率":"每月"}],"初始期限":30
          ,"频率":"每月","类型":"等额本金","放款日":"2020-06-01"}
          ,{"当前余额":2_261_042_196.13
          ,"当前利率":0.0444
          ,"剩余期限":106
          ,"状态":"正常"}]
      ,["按揭贷款"
        ,{"放款金额":0,"放款利率":["浮动",0.085,{"基准":"LPR5Y","利差":0.01,"重置频率":"每月"}],"初始期限":30
          ,"频率":"每月","类型":"等额本金","放款日":"2020-06-01"}
          ,{"当前余额": 81_403_764.08
          ,"当前利率":0.0444
          ,"剩余期限":106
          ,"状态":"违约"}]]
     }
    ,(("本金分账户",{"余额":0 })
      ,("收入分账户",{"余额":0,"记录":[("2019-12-01",0,-81_403_764.08,"To:本金分账户|ABCD")]})
      )
    ,(("A1",{"当前余额":0.00
             ,"当前利率":0.051
             ,"初始余额":2_903_000_000.00
             ,"初始利率":0.051
             ,"起息日":"2020-01-03"
             ,"利率":{"浮动":["LPR5Y",0.012,{"重置月份":3}]}
             ,"债券类型":{"过手摊还":None}
             })
       ,("A2",{"当前余额":0.00
             ,"当前利率":0.051
             ,"初始余额":2_903_000_000.00
             ,"初始利率":0.051
             ,"起息日":"2020-01-03"
             ,"利率":{"浮动":["LPR5Y",0.012,{"重置月份":3}]}
             ,"债券类型":{"过手摊还":None}
             })
       ,("A3",{"当前余额":1_456_725_400.00
             ,"当前利率":0.051
             ,"初始余额":2_903_000_000.00
             ,"初始利率":0.051
             ,"起息日":"2020-01-03"
             ,"利率":{"浮动":["LPR5Y",0.002,{"重置月份":3}]}
             ,"债券类型":{"过手摊还":None}
             })
      ,("次级",{"当前余额":795_626_718.16
             ,"当前利率":0.0
             ,"初始余额":795_626_718.16
             ,"初始利率":0.0
             ,"起息日":"2020-01-03"
             ,"利率":{"固定":0.00}
             ,"债券类型":{"权益":None}
             }))
    ,(("增值税",{"类型":{"百分比费率":["资产池当期利息",0.0326]}})
      ,("服务商费用",{"类型":{"年化费率":["资产池余额",0.0012]}})
      ,("报销",{"类型":{"周期费用":["每月",60000]}})
     )
    ,{"未违约":[
        ["支付费用限额",["收入分账户"],["服务商费用"],{"应计费用百分比":0.5}]
         ,["支付费用限额",["收入分账户"],["报销"],{"应计费用上限":50000}]
         ,["支付利息","收入分账户",["A1","A2","A3"]]
         ,["支付费用",["收入分账户"],["服务商费用"]]
         ,["按公式账户转移","收入分账户","本金分账户","A+B+C-D"]
         ,["支付费用",["收入分账户"],["报销"]]
         ,["账户转移","收入分账户","本金分账户"]
         ,["支付本金","本金分账户",["A1"]]
         ,["支付本金","本金分账户",["A2"]]
         ,["支付本金","本金分账户",["A3"]]
         ,["支付本金","本金分账户",["次级"]]
         ,["支付收益","本金分账户","次级"]
      ]
     ,"回款后":[["支付费用",["收入分账户"],["增值税"]]]
     ,"清仓回购":[["出售资产",["正常|违约",1.0,0.0],"收入分账户"]]}
    ,(["利息回款","收入分账户"]
      ,["本金回款","本金分账户"]
      ,["早偿回款","本金分账户"]
      ,["回收回款","本金分账户"])
    ,None
   )