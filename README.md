# 📊 数据分析智能体

一个基于大模型的智能数据分析系统，能够处理大量Excel表格，自动生成包含数据分析、趋势预测和风险预警的综合报告。

## ✨ 核心功能

- 📤 **大文件处理**：支持10MB-500MB的Excel/CSV文件，智能分块读取
- 📈 **统计分析**：描述性统计、趋势分析、季节性检测、相关性分析
- 🔮 **趋势预测**：基于Prophet的时间序列预测，带置信区间
- ⚠️ **风险预警**：智能异常检测、风险评分、告警通知
- 🤖 **AI智能体**：利用大模型生成智能洞察和交互式问答
- 📊 **可视化**：丰富的交互式图表（Plotly）
- 📝 **报告生成**：自动生成Markdown格式分析报告

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

项目已包含默认的`.env`文件，请填入你的API密钥：

```env
# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# 或者 Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

### 3. 启动应用

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`

## 📁 项目结构

```
dataAnalysis/
├── app.py                    # Streamlit主应用
├── requirements.txt          # Python依赖
├── .env                     # 环境变量配置
├── .env.example             # 环境变量示例
├── config/
│   └── settings.py          # 配置管理
├── core/                    # 核心业务逻辑
│   ├── data_loader.py       # 数据加载与预处理
│   ├── analyzer.py          # 统计分析引擎
│   ├── predictor.py         # 时间序列预测引擎
│   ├── risk_monitor.py      # 风险预警系统
│   └── reporter.py          # 报告生成器
├── ai/                      # AI智能体模块
│   ├── agent.py            # AI智能体核心
│   ├── prompts.py          # Prompt模板
│   └── models/             # 模型适配器
│       ├── base.py         # 基础接口
│       ├── openai.py       # OpenAI适配器
│       ├── anthropic.py    # Anthropic适配器
│       └── factory.py      # 模型工厂
└── utils/                   # 工具函数
    ├── validators.py       # 数据验证
    └── visualizations.py   # 图表生成
```

## 🎯 使用指南

### 1. 数据上传

1. 点击「数据上传」页面
2. 上传Excel或CSV文件（最大500MB）
3. 查看数据预览和列信息

### 2. 统计分析

1. 选择要分析的数值列
2. 查看描述性统计（均值、标准差、偏度、峰度等）
3. 查看数据分布图
4. 如有时间列，进行趋势分析
5. 查看相关性热力图

### 3. 趋势预测

1. 选择日期列和数值列
2. 设置预测周期和时间频率
3. 选择季节性模式（加法/乘法）
4. 点击「开始预测」
5. 查看预测准确度、预测图表和预测摘要

### 4. 风险预警

1. 选择要监控的列
2. 选择异常检测方法（Z-Score/IQR）
3. 点击「开始风险评估」
4. 查看风险评分和风险细分
5. 查看详细告警列表
6. 获取应对建议

### 5. AI智能分析

#### 生成分析洞察
- AI自动分析数据
- 生成3-5条关键洞察
- 涵盖趋势、异常、机会、风险等维度

#### 生成完整报告
- 选择是否使用AI增强
- 自动生成结构化Markdown报告
- 支持一键下载

#### 交互式问答
- 用自然语言提问
- AI基于数据分析结果回答
- 支持对话历史记录

## 🔧 技术栈

- **Web框架**: Streamlit 1.28+
- **数据处理**: Pandas 2.0+, NumPy
- **AI模型**: OpenAI GPT-4 / Anthropic Claude
- **预测模型**: Facebook Prophet
- **可视化**: Plotly 5.17+

## 📊 支持的数据格式

- **文件格式**: .xlsx, .xls, .csv
- **最大文件**: 500MB
- **数据类型**: 数值型、日期型、文本型
- **编码**: UTF-8, GBK, GB2312, Big5

## 🎨 功能特点

### 智能数据加载
- 自动检测文件编码
- 分块读取大文件
- 智能推断日期列
- 自动处理缺失值

### 多模型支持
- OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo)
- Anthropic (Claude Sonnet 4)
- 可在界面中切换模型

### 风险预警系统
- 统计异常检测（Z-Score, IQR）
- 阈值违规检查
- 趋势反转检测
- 数据质量评估

### 预测引擎
- 基于Prophet的时间序列预测
- 自动检测季节性
- 置信区间估算
- 模型准确度评估

## 📝 示例问题

在AI智能分析中，你可以问：

- "数据的整体趋势如何？"
- "有哪些异常值需要注意？"
- "预测结果可靠吗？"
- "给我一些商业建议"
- "数据质量如何？"
- "有哪些增长机会？"

## 🔒 数据安全

- 数据仅在本地处理
- 不存储原始数据
- 发送给AI的数据经过摘要压缩
- API密钥加密存储

## 📚 开发计划

- [x] Phase 1: 基础框架搭建
- [x] Phase 2: 核心分析模块
- [x] Phase 3: AI智能体
- [x] Phase 4: 预测与预警
- [x] Phase 5: 报告生成
- [ ] Phase 6: 性能优化
- [ ] 更多预测模型（ARIMA、机器学习）
- [ ] 报告导出为PDF/Word
- [ ] 多文件对比分析
- [ ] 自定义报告模板

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系

如有问题或建议，请提交Issue。
