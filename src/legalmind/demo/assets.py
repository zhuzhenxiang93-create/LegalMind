"""Manually authored synthetic fixtures. Scores are illustrative, not model predictions."""

CASES = [
    {
        "id": "clear-theft",
        "title": "01 · 盗窃与退赔",
        "subtitle": "Clear facts · evidence walkthrough",
        "fact": "某成年人趁商店店员离开柜台，秘密拿走一部价值约5000元的手机并离开。事后返还手机、赔偿损失，并取得被害人谅解。未使用暴力或威胁。",
        "scores": [("盗窃", 0.91), ("抢夺", 0.18)],
        "uncertain": False,
        "missing": ["核实价格认定、行为人年龄及当地数额标准", "核实退赔和谅解材料"],
    },
    {
        "id": "ambiguous-taking",
        "title": "02 · 取财方式存疑",
        "subtitle": "Competing charges · manual review",
        "fact": "某成年人在街边拿走他人手中的手机后离开。双方发生拉扯，但现有记录没有说明拉扯针对手机还是被害人，也不清楚是否存在威胁、伤情及先后顺序。",
        "scores": [("抢夺", 0.48), ("抢劫", 0.44), ("盗窃", 0.31)],
        "uncertain": True,
        "missing": ["补充拉扯对象、暴力程度及取财先后顺序", "补充监控、证人及伤情信息"],
    },
    {
        "id": "insufficient-facts",
        "title": "03 · 信息不足",
        "subtitle": "Abstention · request more information",
        "fact": "有人说自己的东西不见了，希望了解该如何分析。物品价值、保管关系、行为人和具体经过均不清楚。",
        "scores": [("盗窃", 0.22), ("抢夺", 0.11)],
        "uncertain": True,
        "missing": ["补充物品、价值、占有关系和具体行为经过", "确认是否存在取财行为及可核实证据"],
    },
]

# These invented historical outcomes are for interface demonstration only.
RECORDS = [
    {
        "id": "SYN-001",
        "charge": "盗窃",
        "text": "商店柜台秘密拿走手机，价值5000元，事后返还并退赔，取得谅解。",
        "months": 6,
        "fine": 2000,
    },
    {
        "id": "SYN-002",
        "charge": "盗窃",
        "text": "趁店员离开取走电子产品，价值6000元，主动退赔损失。",
        "months": 8,
        "fine": 3000,
    },
    {
        "id": "SYN-003",
        "charge": "盗窃",
        "text": "秘密拿走他人手机，未使用暴力，返还手机，取得被害人谅解。",
        "months": 5,
        "fine": 1000,
    },
    {
        "id": "SYN-004",
        "charge": "抢夺",
        "text": "街边突然拿走他人手中的手机后离开，未发现针对人的暴力。",
        "months": 10,
        "fine": 2000,
    },
    {
        "id": "SYN-005",
        "charge": "抢劫",
        "text": "街边使用暴力威胁被害人，强行拿走手机，被害人出现伤情。",
        "months": 36,
        "fine": 3000,
    },
    {
        "id": "SYN-006",
        "charge": "抢夺",
        "text": "突然夺走手中的物品，双方拉扯手机，事后退赔。",
        "months": 9,
        "fine": 2000,
    },
]

STATUTES = [
    {
        "article": 264,
        "charge": "盗窃",
        "summary": "演示摘要：盗窃公私财物的相关规定；具体构成、情节与数额标准需核实。",
    },
    {
        "article": 267,
        "charge": "抢夺",
        "summary": "演示摘要：抢夺公私财物的相关规定；携带凶器抢夺的法律评价需单独核实。",
    },
    {
        "article": 263,
        "charge": "抢劫",
        "summary": "演示摘要：以暴力、胁迫或其他方法抢劫公私财物的相关规定。",
    },
]
SOURCE_URL = "https://www.stats.gov.cn/gk/tjfg/xgfxfg/202503/t20250311_1958931.html"
