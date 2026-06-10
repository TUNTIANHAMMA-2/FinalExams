"""Shared constants for the medicine sales analysis assignment."""

ORIGINAL_DATE_COLUMN = "购药时间"
SALES_TIME_COLUMN = "销售时间"
NUMERIC_COLUMNS = ["销售数量", "应收金额", "实收金额"]

EXPECTED_COLUMNS = [
    ORIGINAL_DATE_COLUMN,
    "社保卡号",
    "商品编码",
    "商品名称",
    "销售数量",
    "应收金额",
    "实收金额",
    "星期",
]

RENAMED_DATA_COLUMNS = [
    SALES_TIME_COLUMN,
    "社保卡号",
    "商品编码",
    "商品名称",
    "销售数量",
    "应收金额",
    "实收金额",
    "星期",
]

WEEKDAY_NAMES = {
    0: "星期一",
    1: "星期二",
    2: "星期三",
    3: "星期四",
    4: "星期五",
    5: "星期六",
    6: "星期日",
}
WEEKDAY_ORDER = [WEEKDAY_NAMES[index] for index in range(7)]

