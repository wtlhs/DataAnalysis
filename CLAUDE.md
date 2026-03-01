# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**数据分析智能体** is an intelligent data analysis system built with Streamlit that processes Excel/CSV files and generates comprehensive reports including data analysis, trend prediction, and risk warning using large language models.

**Core Capabilities:**
- 📤 Large file processing (10MB-500MB Excel/CSV files with chunked reading)
- 📈 Statistical analysis (descriptive statistics, trend analysis, anomaly detection, correlation analysis)
- 🔮 Trend prediction (time series forecasting with confidence intervals)
- ⚠️ Risk warning (intelligent anomaly detection, risk scoring, alerts)
- 🤖 AI agent (generates intelligent insights and interactive Q&A using LLMs)
- 📊 Rich visualization (Plotly interactive charts)
- 📝 Auto-generated Markdown reports

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Web Interface                   │
│  ┌────────┬────────┬────────┬────────┬────────┐   │
│  │Upload   │Analysis │Predict │  Risk  │Report │   │
│  └────────┴────────┴────────┴────────┴────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Core Services Layer                    │
│  ┌──────────┬──────────┬──────────┬──────────┐    │
│  │DataLoad  │ Analyzer │Predictor │RiskMonitor│    │
│  └──────────┴──────────┴──────────┴──────────┘    │
│  ┌──────────┬──────────┬──────────┐                    │
│  │Reporter  │AIAgent  │          │                    │
│  └──────────┴──────────┴──────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                       │
│  LLM APIs: OpenAI GPT-4 / Anthropic Claude / 智谱AI    │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
dataAnalysis/
├── app.py                      # Streamlit main application
├── requirements.txt              # Python dependencies
├── .env                        # Environment variables (API keys, model settings)
├── .env.example                 # Environment variables template
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── config/
│   └── settings.py             # Configuration management (ModelConfig, DataConfig, RiskThresholds)
├── core/
│   ├── data_loader.py          # Excel/CSV data loading & preprocessing
│   ├── analyzer.py             # Statistical analysis engine (descriptive stats, trends, anomalies)
│   ├── predictor.py            # Time series forecasting (Prophet/ARIMA)
│   ├── risk_monitor.py         # Risk warning system (anomaly detection, risk scoring)
│   └── reporter.py             # Report generator (Markdown format)
├── ai/
│   ├── agent.py                # AI agent core class
│   ├── prompts.py              # Prompt templates for LLM interactions
│   └── models/                 # Model adapters for different LLM providers
│       ├── base.py               # BaseModel abstract interface
│       ├── openai.py             # OpenAI API adapter
│       ├── anthropic.py          # Anthropic Claude API adapter
│       └── factory.py            # Model factory pattern for creating model instances
└── utils/
    ├── validators.py            # Data validation utilities
    └── visualizations.py        # Plotly chart generation
```

## Key Components

### Core Services Layer

#### 1. Data Loader (`core/data_loader.py`)

**Purpose**: Efficient loading and preprocessing of Excel/CSV files

**Key Classes**:
- `FileExtension`: Enum for supported file types (.xlsx, .xls, .csv)
- `ValidationResult`: Dataclass for validation results
- `DataLoader`: Main class for loading files

**Key Methods**:
- `load_file(file_path, sheet_name, chunk_size)`: Load Excel/CSV files with chunked reading (CSV only)
- `validate_file(file_path)`: Validate file size, type, existence
- `preprocess(df)`: Handle missing values, convert date columns, remove duplicates
- `get_numeric_columns(df)`: Return numeric column names
- `get_date_columns(df)`: Return date column names
- `sample_for_ai(df, sample_size)`: Sample data for AI analysis (reduces token usage)

**Design Decisions**:
- Excel files are loaded entirely (no chunking) because `pd.read_excel()` doesn't support `chunksize`
- CSV files support chunked reading for large files
- Auto-detects encoding (UTF-8, GBK, GB2312, Big5)
- Date columns are automatically detected and converted

#### 2. Analyzer (`core/analyzer.py`)

**Purpose**: Statistical analysis and trend detection

**Key Classes**:
- `DescriptiveStats`: Dataclass for descriptive statistics results
- `TrendAnalysis`: Dataclass for trend analysis results
- `AnomalyDetection`: Dataclass for anomaly detection results
- `Analyzer`: Main statistical analysis engine

**Key Methods**:
- `descriptive_statistics(df, column)`: Calculate mean, std, min, max, quantiles, skewness, kurtosis
- `batch_descriptive_statistics(df)`: Calculate stats for all numeric columns
- `trend_analysis(df, date_col, value_col)`: Analyze trends, calculate YoY, MoM
- `detect_anomalies(df, column, method)`: Detect anomalies using IQR or Z-Score
- `correlation_analysis(df)`: Generate correlation matrix
- `get_highly_correlated_pairs(df, threshold)`: Find highly correlated feature pairs
- `year_over_year(df, date_col, value_col)`: Calculate year-over-year growth
- `month_over_month(df, date_col, value_col)`: Calculate month-over-month growth
- `compare_categories(df, category_col, value_col)`: Category-based statistics
- `detect_seasonality(df, date_col, value_col)`: Detect seasonal patterns

#### 3. Predictor (`core/predictor.py`)

**Purpose**: Time series forecasting with Prophet or ARIMA

**Key Classes**:
- `ForecastResult`: Dataclass for forecast results
- `ModelEvaluation`: Dataclass for model evaluation metrics (MAE, RMSE, MAPE, coverage)

**Key Methods**:
- `prepare_data(df, date_col, value_col)`: Prepare Prophet-format data
- `train_prophet(prophet_df, seasonality_mode)`: Train Prophet model
- `predict_forecast(model, periods, freq)`: Generate forecast
- `evaluate_forecast(prophet_df, forecast)`: Evaluate prediction accuracy
- `run_forecast(df, date_col, value_col, ...)`: Complete forecasting pipeline
- `_run_prophet_forecast(...)`: Prophet-based forecasting (preferred)
- `_run_arima_forecast(...)`: ARIMA-based forecasting (fallback)
- `_simple_forecast(...)`: Simple moving average forecast (final fallback)

**Design Decisions**:
- Prophet is preferred when available (automatic seasonality detection)
- ARIMA is used as fallback when Prophet not installed
- Simple moving average is final fallback
- Forecast returns standard Prophet columns: `ds`, `yhat`, `yhat_lower`, `yhat_upper`

#### 4. Risk Monitor (`core/risk_monitor.py`)

**Purpose**: Risk detection and warning system

**Key Classes**:
- `RiskLevel`: Enum for risk levels (LOW, MEDIUM, HIGH, CRITICAL)
- `RiskAlert`: Dataclass for individual risk alerts
- `RiskScore`: Dataclass for overall risk score
- `RiskMonitor`: Risk monitoring engine

**Key Methods**:
- `check_value_thresholds(df, column, min_threshold, max_threshold)`: Check for threshold violations
- `detect_statistical_anomalies(df, column, method)`: Z-Score or IQR-based anomaly detection
- `detect_trend_reversal(df, date_col, value_col, window)`: Detect trend reversals
- `detect_data_quality_issues(df)`: Check for missing values, duplicates, empty columns
- `calculate_risk_score(df, alerts)`: Calculate overall risk score (0-100)
- `generate_comprehensive_report(df, columns_to_monitor, date_column)`: Full risk assessment

**Design Decisions**:
- Risk levels: LOW (<30), MEDIUM (30-50), HIGH (50-70), CRITICAL (≥70)
- Threshold defaults: HIGH (3σ), MEDIUM (2σ), LOW (1.5σ)
- Alerts are categorized by risk type (data quality, statistical anomaly, threshold violation, trend reversal)

#### 5. Reporter (`core/reporter.py`)

**Purpose**: Generate comprehensive Markdown analysis reports

**Key Methods**:
- `generate_markdown_report(...)`: Generate full report with all sections
- `_generate_data_overview(df, data_summary)`: Data overview section
- `_generate_stats_section(stats_result)`: Statistics section
- `_generate_trend_section(trend_result)`: Trend analysis section
- `_generate_anomaly_section(anomaly_result)`: Anomaly detection section
- `_generate_forecast_section(forecast_result)`: Forecast section
- `_generate_risk_section(risk_result)`: Risk assessment section
- `_generate_insights_section(insights)`: AI insights section
- `_generate_conclusion(...)`: Summary and recommendations
- `save_report(report, output_path)`: Save to file
- `export_to_html(report, output_path)`: Export as HTML

**Report Structure**:
1. Executive Summary
2. Data Overview
3. Statistical Analysis
4. Trend Analysis
5. Anomaly Detection
6. Forecast Results
7. Risk Assessment
8. AI Insights
9. Conclusion & Recommendations

### AI Agent Layer

#### 1. Agent Core (`ai/agent.py`)

**Purpose**: Coordinate LLM calls for intelligent data analysis

**Key Methods**:
- `analyze_context(df, data_summary)`: Analyze data context using LLM
- `generate_insights(data_summary, analysis_result)`: Generate 3-5 key insights
- `generate_comprehensive_insights(df, stats, trend, anomalies, forecast)`: Generate multi-dimensional insights
- `write_report(all_results, include_charts)`: Generate full report using LLM
- `chat(question, df, context)`: Interactive Q&A with context
- `summarize_data(df)`: Generate data summary for AI consumption

#### 2. Model Adapters (`ai/models/`)

**Base Interface** (`base.py`):
```python
class BaseModel(ABC):
    def chat(messages: List[Dict[str, str]]) -> str
    def analyze(data: Dict[str, Any], prompt: str) -> str
    def generate_insights(data_summary, analysis_result) -> List[str]
    def write_report(all_results, report_format) -> str
```

**OpenAI Adapter** (`openai.py`):
- Uses OpenAI Python SDK
- Supports GPT-4o, GPT-4o-mini, GPT-4-turbo
- Compatible with OpenAI-compatible APIs (like 智谱AI)

**Anthropic Adapter** (`anthropic.py`):
- Uses Anthropic Python SDK
- Supports Claude Sonnet 4, Claude 3.5 Sonnet

**Model Factory** (`factory.py`):
- Creates model instances based on provider
- Supports dynamic model switching

**Supported Providers**:
- `openai`: OpenAI GPT-4 models
- `智谱AI(GLM)`: 智谱AI GLM models (uses OpenAI-compatible API)
- `anthropic`: Anthropic Claude models

**智谱AI Configuration**:
- API Base: `https://open.bigmodel.cn/api/coding/paas/v4`
- Models: glm-5, glm-4, glm-4-flash, glm-3-turbo, glm-4-air, glm-4-long

#### 3. Prompt Templates (`ai/prompts.py`)

**Purpose**: Pre-built prompt templates for consistent LLM interactions

**Key Templates**:
- `SYSTEM_ANALYST`: System prompt for data analysis tasks
- `SYSTEM_REPORTER`: System prompt for report generation
- `ANALYZE_TREND`: Trend analysis prompt
- `ANALYZE_ANOMALY`: Anomaly analysis prompt
- `ANALYZE_CORRELATION`: Correlation analysis prompt
- `GENERATE_INSIGHTS`: Insight generation prompt
- `REPORT_STRUCTURE`: Complete report structure template
- `ANALYZE_FORECAST`: Forecast analysis prompt
- `ANALYZE_RISK`: Risk analysis prompt

**PromptBuilder Class**:
- `build_analyze_prompt(data_description, key_metrics, analysis_type)`: Build analysis prompt
- `build_insight_prompt(data_summary, analysis_results)`: Build insight generation prompt
- `build_report_prompt(all_results)`: Build report generation prompt
- `build_qa_prompt(question, background, analysis_results)`: Build Q&A prompt

### Utility Layer

#### 1. Validators (`utils/validators.py`)

**Purpose**: Data validation with detailed error reporting

**Key Classes**:
- `ValidationLevel`: Enum (ERROR, WARNING, INFO)
- `ValidationIssue`: Dataclass for individual validation issues
- `ValidationResult`: Dataclass for validation results
- `DataValidator`: Data validation engine

**Key Methods**:
- `validate_dataframe(df, schema)`: Validate entire DataFrame
- `_validate_schema(df, schema)`: Validate against schema definition
- `validate_numeric_column(df, column, ...)`: Validate numeric columns
- `validate_text_column(df, column, ...)`: Validate text columns
- `validate_date_column(df, column, ...)`: Validate date columns
- `check_missing_values(df, threshold)`: Check missing value ratios
- `check_duplicates(df, subset)`: Check duplicate rows
- `generate_validation_report(result)`: Generate text report

#### 2. Visualizations (`utils/visualizations.py`)

**Purpose**: Generate interactive Plotly charts

**Key Functions**:
- `plot_distribution(df, column)`: Histogram with mean line
- `plot_trend(df, date_col, value_col)`: Time series with moving average
- `plot_correlation(corr_df)`: Correlation heatmap
- `plot_forecast(df, forecast, date_col, value_col, title)`: Forecast chart with confidence intervals
- `plot_boxplot(df, columns, title)`: Boxplot for anomaly visualization
- `plot_pie_chart(df, column, title)`: Pie chart for category distribution

## Configuration System

### Settings Hierarchy (`config/settings.py`)

```
Settings (Singleton)
├── AppConfig
│   ├── app_name: str
│   ├── version: str
│   ├── debug: bool
│   ├── base_dir: Path
│   ├── data_dir: Path
│   ├── upload_dir: Path
│   └── output_dir: Path
│
├── ModelConfig
│   ├── provider: str  # 'openai', 'anthropic'
│   ├── model_name: str
│   ├── temperature: float
│   ├── max_tokens: int
│   ├── api_key: str
│   └── api_base: Optional[str]
│
├── RiskThresholds
│   ├── high_risk_sigma: float
│   ├── medium_risk_sigma: float
│   ├── low_risk_sigma: float
│   ├── min_data_points: int
│   ├── max_missing_ratio: float
│   └── trend_change_threshold: float
│
└── DataConfig
    ├── max_file_size_mb: int
    ├── allowed_extensions: list
    ├── chunk_size: int
    ├── sample_size: int
    ├── date_columns: list
    ├── max_missing_ratio: float
    ├── min_data_points: int
    ├── forecast_periods: int
    └── prediction_confidence: float
```

### Environment Variables (.env)

Required:
- `MODEL_PROVIDER`: Default model provider (openai/anthropic)
- `OPENAI_API_KEY`: OpenAI API key (or compatible API key)
- `OPENAI_API_BASE`: API base URL
- `MODEL_NAME`: Default model name
- `MODEL_TEMPERATURE`: Temperature parameter (0.0-2.0)
- `MODEL_MAX_TOKENS`: Max tokens for responses

Optional:
- `ANTHROPIC_API_KEY`: Anthropic API key
- `ANTHROPIC_MODEL`: Anthropic model name
- `MAX_FILE_SIZE_MB`: Max file size (default: 500)
- `CHUNK_SIZE`: Chunk size for CSV reading (default: 10000)

### 智谱AI Configuration Example

```env
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_zhipu_api_key_here
OPENAI_API_BASE=https://open.bigmodel.cn/api/coding/paas/v4
MODEL_NAME=glm-5
MODEL_TEMPERATURE=0.7
MODEL_MAX_TOKENS=4000
```

## Common Development Tasks

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys (edit .env file)
# Configure at least one of: OPENAI_API_KEY or ANTHROPIC_API_KEY

# Start the application
python -m streamlit run app.py

# The app will be available at http://localhost:8501
```

### Testing

**Testing Data Loading**:
1. Upload sample Excel/CSV file
2. Verify data preview displays correctly
3. Check column types are detected properly
4. Verify date columns are converted

**Testing Analysis**:
1. Select numeric column
2. Verify descriptive statistics calculate
3. Verify charts render correctly
4. If date column exists, verify trend analysis works

**Testing Prediction**:
1. Select date and numeric columns
2. Set forecast parameters (periods, frequency)
3. Click "开始预测"
4. Verify forecast chart and accuracy metrics display

**Testing Risk Monitoring**:
1. Select columns to monitor
2. Choose anomaly detection method (Z-Score/IQR)
3. Click "开始风险评估"
4. Verify risk score and alerts display

**Testing AI Agent**:
1. Verify API key is configured
2. Test "生成分析洞察"
3. Test "生成完整报告"
4. Test "交互式问答" with sample questions

### Common Issues and Solutions

**Issue: File upload fails**
- Solution: Check file size (<500MB), check file type (.xlsx, .xls, .csv)

**Issue: No data in statistics page**
- Solution: Ensure file is uploaded first, verify data preview shows data
- Solution: Ensure numeric columns exist in the data

**Issue: Prediction fails**
- Solution: Ensure date column and numeric column are selected
- Solution: Ensure enough data points (at least 30 for Prophet)
- Solution: If Prophet not installed, it will fall back to ARIMA

**Issue: AI analysis hangs**
- Solution: Check API key is configured in .env
- Solution: Check API base URL is correct
- Solution: Try disabling "使用AI增强" to use standard report template

**Issue: 智谱AI API errors**
- Solution: Ensure API base is `https://open.bigmodel.cn/api/coding/paas/v4`
- Solution: Verify API key is correct format
- Solution: Select model from available options (glm-5, glm-4, etc.)

## Code Style and Patterns

### Immutability
- Create new objects, never mutate existing ones in place
- Example: Use `df = df.copy()` before modifications
- Example: Use `new_df = df.assign(new_col=value)` instead of `df['new_col'] = value`

### Error Handling
- Always handle exceptions at each level
- Provide user-friendly error messages in UI
- Log detailed error context for debugging
- Never silently swallow errors

### Function Design
- Keep functions small (<50 lines preferred)
- Single responsibility per function
- Descriptive function names
- Type hints on all function signatures

### File Organization
- Target 200-400 lines per file
- Maximum 800 lines per file
- Organize by feature/domain, not by type
- Extract utilities from large modules

### Data Validation
- Always validate at system boundaries
- Use schema-based validation where appropriate
- Fail fast with clear error messages
- Never trust external data

## Session State Management

The application uses Streamlit's `st.session_state` to persist data across page re-runs:

```python
# Initialized in app.py
st.session_state.df = None                 # Uploaded data
st.session_state.loader = DataLoader()   # Data loader instance
st.session_state.analyzer = Analyzer() # Analyzer instance
st.session_state.predictor = Predictor() # Predictor instance
st.session_state.risk_monitor = RiskMonitor() # Risk monitor instance
st.session_state.reporter = ReportGenerator() # Reporter instance
st.session_state.ai_agent = None       # AI agent (lazy init)
st.session_state.analysis_results = {}  # Analysis results cache
st.session_state.generated_report = None  # Generated report
```

**Key Point**: Streamlit re-runs the entire script on every interaction, so `st.session_state` is essential for persisting loaded data and analysis results.

## Data Flow

1. **Upload Phase**:
   - User uploads Excel/CSV file
   - `DataLoader.load_file()` reads and validates
   - `DataLoader.preprocess()` cleans data
   - Data stored in `st.session_state.df`

2. **Analysis Phase**:
   - User selects columns in UI
   - `Analyzer.descriptive_statistics()` calculates stats
   - `Analyzer.trend_analysis()` detects trends
   - `Analyzer.detect_anomalies()` finds outliers
   - Results displayed with charts

3. **Prediction Phase**:
   - User selects date/numeric columns
   - `Predictor.run_forecast()` trains model
   - Generates forecast with confidence intervals
   - Evaluates model accuracy
   - Results displayed

4. **Risk Assessment Phase**:
   - User selects columns to monitor
   - `RiskMonitor.generate_comprehensive_report()` runs checks
   - Calculates risk score (0-100)
   - Generates alerts
   - Results displayed

5. **AI Analysis Phase**:
   - `DataAnalysisAgent` initialized on first use
   - `summarize_data()` creates compact data summary
   - `generate_insights()` or `write_report()` calls LLM
   - Results displayed or report downloaded

## AI Integration

### LLM API Integration

**OpenAI-Compatible APIs** (OpenAI, 智谱AI):
- Use `openai` Python SDK
- Set `base_url` in client initialization
- Standard chat completions API

**Anthropic API**:
- Use `anthropic` Python SDK
- Messages API
- System message for instructions, user messages for input

### Prompt Strategy

**Two-Stage Prompting**:
1. First stage: Analyze data context and statistics
2. Second stage: Generate insights and write report

**Context Injection**:
- Data summary: row count, column list, data types
- Statistical results: descriptive stats, trends, anomalies
- Reduces token usage by sending summaries, not raw data

**Few-Shot Examples**:
- Included in prompts to improve report quality
- Provide examples of good analysis and insights

### Token Optimization

**Sampling Strategy**:
- Use `DataLoader.sample_for_ai()` to reduce data size
- Default sample size: 500 rows
- Only sample when data size > 500

**Summarization**:
- Convert analysis results to concise summaries
- Avoid sending entire DataFrames to LLM
- Use key statistics and trends instead

## Future Enhancements

**Planned Features** (marked in README):
- More prediction models (ARIMA, machine learning)
- Report export to PDF/Word
- Multi-file comparison analysis
- Custom report templates

**Potential Improvements**:
- Add unit tests (currently missing)
- Add integration tests for API interactions
- Add E2E tests for critical user flows
- Performance profiling for large datasets
- Caching mechanism for repeated analyses
