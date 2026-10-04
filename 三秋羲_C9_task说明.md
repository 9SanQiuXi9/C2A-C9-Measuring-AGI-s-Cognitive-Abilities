# MetaBoundary — 任务说明

## 评估任务描述

MetaBoundary 衡量 AI 模型的**元认知校准能力**：模型能否区分自己知道什么、不知道什么？

### 任务形式

每个测试项包含：
1. 一个事实性问题或不可回答的问题
2. 模型需要提供：答案 + 置信度评分（0–1）

对于不可回答的问题，模型应识别并标记为"UNANSWERABLE"，同时给出高置信度（表示"我确信这无法回答"）。

### 评分标准

**核心指标：MetaScore（0–1，越高越好）**

MetaScore = 0.4 × (1 − Brier Score) + 0.3 × (1 − ECE) + 0.3 × AUROC

**子指标说明：**

| 指标 | 衡量什么 | 理想值 |
|------|---------|--------|
| Brier Score | 置信度与正确性之间的均方误差 | 0（完美校准） |
| ECE（期望校准误差）| 分箱后的置信度-准确率差距 | 0（完美校准） |
| AUROC | 置信度能否区分正确与错误回答 | 1（完美区分） |
| Accuracy | 回答正确率 | — |

### 评分函数

```python
# Brier Score
brier = mean((confidence_i - correct_i)^2)

# ECE (15 bins)
ECE = Σ (n_bin_i / n_total) × |accuracy_bin_i - confidence_bin_i|

# AUROC
# Mann-Whitney U statistic between correct and incorrect confidences

# MetaScore
MetaScore = 0.4 * (1 - Brier) + 0.3 * (1 - ECE) + 0.3 * AUROC
```

---

## 数据集结构

**88 道题目，5 个类别：**

| 类别 | 数量 | 示例 |
|------|------|------|
| numerical_easy | 16 | "How many chambers does the human heart have?" |
| numerical_hard | 16 | "What is the atomic number of uranium?" |
| entity_easy | 16 | "What is the capital of France?" |
| entity_hard | 16 | "What is the chemical symbol for tungsten?" |
| unanswerable | 24 | "When did the United States land on the Sun?" |

**不可回答问题的类型分布：**
- 虚假前提（false_premise）：问题预设了错误事实
- 虚构实体（fictional_entity）：询问不存在的事物
- 范畴错误（category_error）：问题类型与答案类型不匹配
- 未来事件（future_event）：尚未发生的事件
- 隐私信息（private_info）：不可获取的私人信息
- 不可精确（impossible_precision）：无法精确回答的问题
- 未记录细节（unrecorded_detail）：历史上未记录的信息

---

## 输入/输出格式

### 输入（题目 JSON）
```json
{
  "id": "NE01",
  "category": "numerical",
  "difficulty": "easy",
  "question": "How many continents are there on Earth?",
  "answer": "7",
  "accept_alternatives": ["seven"]
}
```

### 输出（模型回答 JSON）
```json
{
  "id": "NE01",
  "model_answer": "7",
  "confidence": 0.95,
  "correct": true
}
```

### 不可回答问题的输出
```json
{
  "id": "UA01",
  "model_answer": "UNANSWERABLE",
  "confidence": 0.88,
  "correct": true
}
```

---

## 运行评估

```bash
# 完整评估（所有模型配置）
python runner.py

# 指定模型配置
python runner.py --model well_calibrated

# 导出题目数据集
python runner.py --export-data

# 运行内部测试
python runner.py --test
```

所有结果输出到 `data/` 目录。

---

## 基线预期

### 人类表现预期

| 人群 | 可回答准确率 | 不可回答识别率 | 预期校准 |
|------|------------|--------------|---------|
| 普通成人 | 60–75% | 70–85% | 中等校准 |
| 领域专家 | 80–95% | 85–95% | 较好校准 |
| 青少年（12–17） | 45–65% | 50–70% | 较差校准 |

### 模型表现预期

| 模型类型 | 预期 MetaScore 范围 |
|---------|-------------------|
| 前沿 LLM（GPT-4 级别） | 0.75–0.90 |
| 中等 LLM（7B 级别） | 0.55–0.75 |
| 小模型（1B 级别） | 0.40–0.60 |
| 随机基线 | ~0.50 |

---

## 防作弊设计

1. **不可回答问题**：防止模型对所有问题都给出高置信度回答
2. **多类别覆盖**：防止模型针对单一领域优化
3. **精确匹配 + 替代答案**：评分函数同时支持精确匹配和语义等价
4. **置信度连续值**：防止模型通过离散化置信度刷分
