# 《Python数据收集与分析》期末考查报告

## 一、项目概述

本次期末考查围绕一份药品销售数据集，使用 Python 完成从数据加载、清洗、异常处理到统计分析和可视化的完整流程。数据文件为 `exam-materials/data/药品销售数据.xlsx`，共 6578 条记录、8 个字段，涵盖销售时间、社保卡号、商品信息、销售数量、应收/实收金额等。分析时间范围为 2022 年 1 月至 7 月。

项目采用模块化设计，将数据加载、概览、清洗、统计和可视化分别封装在独立 Python 文件中，由统一的流水线模块调度执行。整体技术栈为 Pandas + NumPy + Matplotlib + Seaborn。

## 二、数据加载与概览

### 2.1 数据加载

数据加载模块使用 Pandas 的 `read_excel()` 函数读取本地 Excel 文件，并在加载后校验必要字段是否齐全，避免后续分析因缺列而产生隐蔽错误：

```python
def load_sales_data(data_path: Path) -> pd.DataFrame:
    """读取 Excel 原始数据并校验必要字段。"""
    if not data_path.exists():
        raise FileNotFoundError(f"找不到数据文件：{data_path}")

    data = pd.read_excel(data_path)
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in data.columns]
    if missing_columns:
        raise ValueError(f"数据缺少必要列：{', '.join(missing_columns)}")
    return data
```

成功读取后获得 6578 行 × 8 列的原始数据，字段包括购药时间、社保卡号、商品编码、商品名称、销售数量、应收金额、实收金额和星期。

### 2.2 数据概览

通过 `inspect_raw_data()` 函数对原始数据进行概览检查，输出行列数、字段类型、缺失值统计和重复行数量：

```python
def inspect_raw_data(data: pd.DataFrame) -> dict[str, Any]:
    """返回行列数、字段元数据、缺失值数量和重复行数量。"""
    return {
        "row_count": int(len(data)),
        "column_count": int(len(data.columns)),
        "columns": list(data.columns),
        "dtypes": {column: str(dtype) for column, dtype in data.dtypes.items()},
        "missing_counts": {
            column: int(count) for column, count in data.isna().sum().items()
        },
        "duplicate_rows": int(data.duplicated().sum()),
    }
```

检查结果表明：原始数据中"购药时间"和"社保卡号"各缺失 2 条，"商品编码""商品名称""销售数量""应收金额""实收金额"各缺失 1 条，"星期"缺失 2 条；原始重复行数量为 0。

### 2.3 列名修正

按照考查要求，将原始列名"购药时间"统一修正为"销售时间"。同时保留原始 Excel 行号作为辅助字段，便于在异常记录表中追溯数据来源：

```python
def rename_sales_time(data: pd.DataFrame) -> pd.DataFrame:
    """按照考查要求将"购药时间"改名为"销售时间"。"""
    renamed = data.rename(columns={ORIGINAL_DATE_COLUMN: SALES_TIME_COLUMN}).copy()
    renamed.insert(0, "源数据行号", renamed.index + 2)
    return renamed
```

## 三、数据清洗与异常处理

数据清洗是本次分析的核心环节，包含重复值处理、缺失值处理、类型统一、异常值检测与处理四个步骤。

### 3.1 重复值处理

按业务字段（销售时间、社保卡号、商品编码、商品名称、销售数量、应收金额、实收金额、星期）检测重复记录。本次数据中重复行数量为 0，无需删除。

### 3.2 类型统一

在进行异常值检测之前，需要先将字段转换为正确的数据类型。`normalize_types()` 函数将销售时间转为 DateTime 类型，将销售数量和金额字段转为数值类型：

```python
def normalize_types(data: pd.DataFrame) -> pd.DataFrame:
    """将销售日期和数值字段转换为便于分析的数据类型。"""
    normalized = data.copy()
    normalized[SALES_TIME_COLUMN] = pd.to_datetime(
        normalized[SALES_TIME_COLUMN], errors="coerce"
    )
    for column in NUMERIC_COLUMNS:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    return normalized
```

其中 `errors="coerce"` 参数确保无法转换的值被设为 NaN 而非抛出异常，为后续缺失值检测提供统一入口。原始数据中的"星期"列存在 `2022-02-29` 这样的错误值，因此不直接采用原始星期列，而是根据标准化后的销售时间重新计算星期信息：

```python
cleaned["星期"] = cleaned[SALES_TIME_COLUMN].dt.dayofweek.map(WEEKDAY_NAMES)
```

### 3.3 异常值检测

异常值检测分为两类：

**确定错误**——无法参与销售分析的记录，通过 `_detect_required_field_errors()` 函数识别：

```python
def _detect_required_field_errors(data: pd.DataFrame) -> pd.Series:
    """返回无法参与销售分析的记录掩码。"""
    invalid_date = data[SALES_TIME_COLUMN].isna()
    invalid_product = data["商品名称"].isna()
    invalid_numeric = data[NUMERIC_COLUMNS].isna().any(axis=1)
    non_positive_numeric = (data[NUMERIC_COLUMNS] <= 0).any(axis=1)
    return invalid_date | invalid_product | invalid_numeric | non_positive_numeric
```

这类记录包括：销售时间缺失或无效、商品名称缺失、销售数量或金额字段缺失、销售数量或金额小于等于 0。

**统计异常**——使用 IQR（四分位距）方法检测数值偏高的记录。对于每 个数值字段，计算 Q1 和 Q3，超出 [Q1 - 1.5×IQR, Q3 + 1.5×IQR] 范围的记录被标记为统计异常：

```python
def _detect_statistical_outliers(data: pd.DataFrame) -> pd.DataFrame:
    """在剔除确定错误后检测 IQR 统计异常值。"""
    outlier_parts: list[pd.DataFrame] = []
    for column in NUMERIC_COLUMNS:
        q1 = data[column].quantile(0.25)
        q3 = data[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        mask = (data[column] < lower_bound) | (data[column] > upper_bound)
        part = data.loc[mask].copy()
        if part.empty:
            continue
        part["异常原因"] = (
            f"{column}超出IQR范围[{lower_bound:.2f}, {upper_bound:.2f}]"
        )
        outlier_parts.append(part)
    if not outlier_parts:
        return pd.DataFrame()
    return pd.concat(outlier_parts, ignore_index=True)
```

### 3.4 异常值处理

对两类异常采用不同策略：确定错误（无效日期、负数销售、关键字段缺失）直接剔除，因为这些记录无法代表正常销售行为；IQR 统计异常的大额或大数量记录保留并输出到 `anomaly_rows.csv` 供复核，因为医药销售中可能存在真实的批量购买，不能仅因数值偏大就删除。

最终剔除确定错误记录 68 行，清洗后保留 6510 行有效数据，IQR 统计异常标记 2012 条。

### 3.5 清洗流程总控

上述清洗步骤在 `clean_sales_data()` 函数中按顺序执行，最终返回一个 `CleanedData` 数据对象，包含原始数据、清洗后数据、被剔除行、统计异常行和质量摘要：

```python
def clean_sales_data(raw_data: pd.DataFrame) -> CleanedData:
    """应用评分标准要求的全部清洗规则。"""
    overview = inspect_raw_data(raw_data)
    renamed = rename_sales_time(raw_data)

    # 重复值处理
    duplicate_count = int(renamed.duplicated(subset=RENAMED_DATA_COLUMNS).sum())
    deduplicated = renamed.drop_duplicates(subset=RENAMED_DATA_COLUMNS).copy()

    # 类型统一
    normalized = normalize_types(deduplicated)

    # 缺失和确定错误处理
    invalid_mask = _detect_required_field_errors(normalized)
    removed_rows = normalized.loc[invalid_mask].copy()
    cleaned = normalized.loc[~invalid_mask].copy()
    cleaned["销售数量"] = cleaned["销售数量"].round().astype("int64")

    # 重算星期、排序并重置索引
    cleaned["星期"] = cleaned[SALES_TIME_COLUMN].dt.dayofweek.map(WEEKDAY_NAMES)
    cleaned = cleaned.sort_values(SALES_TIME_COLUMN).reset_index(drop=True)

    statistical_outliers = _detect_statistical_outliers(cleaned)
    return CleanedData(
        raw=raw_data, renamed=renamed, cleaned=cleaned,
        removed_rows=removed_rows, statistical_outliers=statistical_outliers,
        quality_summary={...},
    )
```

## 四、数据分析

清洗完成后，对数据进行多维度的统计分析和可视化。

### 4.1 按销售时间排序

评分要求将清洗后的数据按销售时间升序排列并重置行索引。这一步在 `clean_sales_data()` 末尾通过 `sort_values()` 和 `reset_index()` 完成，排序后数据的时间范围为 2022-01-01 至 2022-07-19。

### 4.2 月度销售统计

`compute_monthly_summary()` 函数按月份对实收金额进行分组聚合，计算每月的订单数、销售数量和实收金额，并求出月均值：

```python
def compute_monthly_summary(cleaned: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """计算月度销售汇总和月均实收金额。"""
    working = cleaned.copy()
    working["销售月份"] = working[SALES_TIME_COLUMN].dt.to_period("M").astype(str)
    monthly = (
        working.groupby("销售月份", as_index=False)
        .agg(
            订单数=("商品名称", "count"),
            销售数量合计=("销售数量", "sum"),
            应收金额合计=("应收金额", "sum"),
            实收金额合计=("实收金额", "sum"),
            单笔平均实收金额=("实收金额", "mean"),
        )
        .sort_values("销售月份")
    )
    monthly_average_actual = float(monthly["实收金额合计"].mean())
    return monthly, monthly_average_actual
```

计算结果：月均实收金额为 43434.98 元。其中 2022 年 1 月实收金额最高（49461.19 元），7 月最低（30120.22 元，但该月数据仅覆盖 19 天）。

### 4.3 销售时间与实收金额关系

`compute_daily_actual()` 按日期汇总每日实收金额，再由 `plot_time_vs_actual()` 绘制时间序列折线图：

```python
def compute_daily_actual(cleaned: pd.DataFrame) -> pd.DataFrame:
    """按日期汇总实收金额，用于时间序列图。"""
    working = cleaned.copy()
    working["日期"] = working[SALES_TIME_COLUMN].dt.date
    return (
        working.groupby("日期", as_index=False)
        .agg(订单数=("商品名称", "count"), 实收金额合计=("实收金额", "sum"))
        .sort_values("日期")
    )
```

从图表可以看出，不同日期之间的销售波动明显，部分日期存在高峰值。这类高峰通常与大额或批量购药记录有关，这正是清洗阶段选择保留 IQR 统计异常而非直接删除的原因。

### 4.4 星期分组统计

`compute_weekday_summary()` 按星期分组统计销售情况，并使用 `pd.Categorical` 确保星期按正确顺序排列：

```python
def compute_weekday_summary(cleaned: pd.DataFrame) -> pd.DataFrame:
    """按星期分组统计销售数量和金额。"""
    working = cleaned.copy()
    working["星期"] = pd.Categorical(
        working["星期"], categories=WEEKDAY_ORDER, ordered=True
    )
    return (
        working.groupby("星期", observed=False)
        .agg(
            订单数=("商品名称", "count"),
            销售数量合计=("销售数量", "sum"),
            应收金额合计=("应收金额", "sum"),
            实收金额合计=("实收金额", "sum"),
        )
        .reset_index()
    )
```

统计结果表明，星期五的订单数（1160）、销售数量（2831）和实收金额（51284.66 元）均为一周最高，是一周中销售表现最突出的日期。星期四的各项指标则相对较低。

### 4.5 销售数量前十位药品

`compute_top_products()` 按商品名称分组统计销售数量，取前 10 位并绘制横向柱状图：

```python
def compute_top_products(cleaned: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """返回按销售数量合计排序的药品排行。"""
    return (
        cleaned.groupby("商品名称", as_index=False)
        .agg(
            订单数=("商品名称", "count"),
            销售数量合计=("销售数量", "sum"),
            应收金额合计=("应收金额", "sum"),
            实收金额合计=("实收金额", "sum"),
        )
        .sort_values(["销售数量合计", "实收金额合计"], ascending=[False, False])
        .head(limit)
        .reset_index(drop=True)
    )
```

销售数量最高的是苯磺酸氨氯地平片（安内真），共售出 1781 件；开博通销售数量排第二（1440 件），但实收金额较高（37080.36 元），说明不同药品的价格差异会影响金额排名与数量排名的对应关系。

## 五、可视化配置

为确保图表中的中文标签正常显示，项目在绘图前统一配置 Matplotlib 和 Seaborn 的字体和样式：

```python
def configure_plot_style() -> None:
    """配置 Matplotlib/Seaborn，使其支持中文标签和 PNG 输出。"""
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = [
        "WenQuanYi Zen Hei", "Noto Sans CJK SC", "SimHei", "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False
```

所有图表统一保存为 180 DPI 的 PNG 文件，存储在 `generated/figures/` 目录下。

## 六、项目结构与运行方式

项目采用模块化设计，各分析步骤独立封装：

```
src/medicine_sales_analysis/
├── constants.py          # 共享常量（列名、星期映射等）
├── data_loading.py       # 数据加载
├── data_overview.py      # 数据概览与列名修正
├── data_cleaning.py      # 数据清洗与异常处理
├── monthly_sales.py      # 月度销售统计
├── weekday_sales.py      # 星期分组统计
├── top_products.py       # 前十位药品统计
├── time_actual_relationship.py  # 销售时间与实收金额关系
├── visualization.py      # 绘图配置
├── models.py             # 数据模型定义
├── outputs.py            # 输出保存
└── pipeline.py           # 流水线调度
```

运行入口为 `main.py`，通过命令行 `python main.py` 即可执行完整分析流程。流水线模块 `pipeline.py` 按顺序调用各模块：

```python
def run_analysis(data_path: Path, output_dir: Path) -> AnalysisResult:
    """运行完整期末考查分析流程。"""
    raw_data = load_sales_data(data_path)
    cleaned_data = clean_sales_data(raw_data)
    monthly_summary, monthly_average_actual = compute_monthly_summary(
        cleaned_data.cleaned
    )
    weekday_summary = compute_weekday_summary(cleaned_data.cleaned)
    top_products = compute_top_products(cleaned_data.cleaned)
    daily_actual = compute_daily_actual(cleaned_data.cleaned)

    write_outputs(
        output_dir=output_dir,
        cleaned_data=cleaned_data,
        monthly_summary=monthly_summary,
        monthly_average_actual=monthly_average_actual,
        weekday_summary=weekday_summary,
        top_products=top_products,
        daily_actual=daily_actual,
    )
    return AnalysisResult(...)
```

## 七、总结

通过本次项目，我完整实践了使用 Python 进行数据分析的全流程，从数据读取、概览检查、清洗处理到统计分析和可视化输出。项目中最关键的设计决策在于异常值处理策略：对于无效日期、负数销售和关键字段缺失这类确定错误，直接剔除以保证后续分析的准确性；但对于 IQR 方法检测出的统计异常，考虑到医药销售中存在真实批量购买的可能性，选择保留并导出供复核，而非简单删除。

整个项目通过模块化设计将分析流程拆分为独立的评分点对应模块，既便于代码维护，也方便答辩时逐项讲解每个评分点的实现思路。
