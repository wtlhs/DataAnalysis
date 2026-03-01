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

### 2. 启动应用

应用支持前后台分离访问：

```bash
# 启动前台（数据分析工作台）
streamlit run app.py --server.port 8530

# 启动后台（管理配置页面）
streamlit run admin.py --server.port 8532
```

- 前台地址：`http://localhost:8530`
- 后台地址：`http://localhost:8532`

### 3. 配置API密钥

首次使用需在后台配置API密钥：

1. 访问后台管理页面 `http://localhost:8532`
2. 登录管理员账号
3. 在「API配置」页面添加API密钥

支持的模型供应商：
- OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo)
- Anthropic (Claude Sonnet 4)
- 智谱AI (GLM-4, GLM-4-Flash)

## 📁 项目结构

```
dataAnalysis/
├── app.py                    # 前台主应用（数据分析工作台）
├── admin.py                  # 后台管理应用（独立入口）
├── requirements.txt          # Python依赖
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
│       ├── zhipu.py        # 智谱AI适配器
│       └── factory.py      # 模型工厂
├── ui/                      # 界面模块
│   ├── frontend.py         # 前台页面
│   ├── backend.py          # 后台页面
│   └── components.py       # UI组件
├── db/                     # 数据库模块
│   ├── models.py           # 数据模型
│   ├── session_manager.py  # 数据集管理
│   └── task_manager.py    # 任务管理
└── utils/                   # 工具函数
    ├── validators.py       # 数据验证
    └── visualizations.py   # 图表生成
```

## 🎯 使用指南

### 前台操作

#### 1. 数据上传
- 点击「上传」页面
- 上传Excel或CSV文件（最大500MB）
- 可选择多个数据集，并切换当前分析对象

#### 2. 数据预览
- 点击「预览」页面
- 查看数据结构、列信息、数据样例

#### 3. 统计分析
- 选择要分析的数值列
- 查看描述性统计（均值、标准差、偏度、峰度等）
- 查看数据分布图
- 如有时间列，进行趋势分析
- 查看相关性热力图

#### 4. 趋势预测
- 选择日期列和数值列
- 设置预测周期和时间频率
- 选择季节性模式（加法/乘法）
- 查看预测图表和置信区间

#### 5. 风险预警
- 选择要监控的列
- 选择异常检测方法（Z-Score/IQR）
- 查看风险评分和风险细分
- 获取详细告警和应对建议

#### 6. AI智能分析
- **生成洞察**：AI自动分析数据，生成关键洞察
- **生成完整报告**：自动生成结构化Markdown报告
- **交互式问答**：用自然语言提问，AI基于数据回答

#### 7. 报告中心
- 查看已生成的历史报告
- 下载或删除报告

### 后台管理

访问 `http://localhost:8532` 进行管理：

- **API配置**：管理AI模型API密钥
- **数据集管理**：查看和删除已上传的数据集
- **报告管理**：查看和删除已生成的报告

## 🔧 技术栈

- **Web框架**: Streamlit 1.40+
- **数据处理**: Pandas 2.0+, NumPy
- **AI模型**: OpenAI / Anthropic / 智谱AI
- **预测模型**: Facebook Prophet
- **可视化**: Plotly 5.17+
- **数据库**: SQLite (本地存储)

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
- 智谱AI (GLM-4, GLM-4-Flash)
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

### 简洁UI设计
- 横向导航菜单
- 分页展示各功能模块
- 响应式布局

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
- API密钥加密存储在数据库中

## 📚 开发计划

- [x] Phase 1: 基础框架搭建
- [x] Phase 2: 核心分析模块
- [x] Phase 3: AI智能体
- [x] Phase 4: 预测与预警
- [x] Phase 5: 报告生成
- [x] Phase 6: 前后台分离
- [ ] 报告导出为PDF/Word
- [ ] 多文件对比分析
- [ ] 自定义报告模板
- [ ] 更多预测模型（ARIMA、机器学习）

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系

如有问题或建议，请提交Issue。