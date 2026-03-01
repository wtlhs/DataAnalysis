#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据分析工具 - 对接国内大模型API
支持：百度文心一言、阿里通义千问、智谱GLM
"""

import os
import json
import glob
from typing import Optional
import pandas as pd
from dataclasses import dataclass

# ================== 配置区域 ==================

# 选择使用的模型: "wenxin", "tongyi", "zhipu"
MODEL_PROVIDER = "zhipu"

# API密钥 (请替换为你的真实密钥)
API_KEYS = {
    "wenxin": "your-baidu-api-key-here",      # 百度文心一言
    "tongyi": "your-alibaba-api-key-here",    # 阿里通义千问
    "zhipu": "your-zhipu-api-key-here",        # 智谱GLM
}

# 数据目录
DATA_DIR = r"D:\GitHubProjects\dataAnalysis\data"

# 分析报告输出目录
OUTPUT_DIR = r"D:\GitHubProjects\dataAnalysis\reports"

# ================== 核心逻辑 ==================

@dataclass
class ModelConfig:
    """模型配置"""
    api_key: str
    base_url: str
    model_name: str
    system_prompt: str


def get_model_config(provider: str) -> ModelConfig:
    """获取模型配置"""
    
    configs = {
        "zhipu": ModelConfig(
            api_key=API_KEYS["zhipu"],
            base_url="https://open.bigmodel.cn/api/paas/v4",
            model_name="glm-4",
            system_prompt="你是一个专业的数据分析师，擅长从数据中发现趋势、统计规律和潜在风险。你的分析报告结构清晰、数据详实、建议可行。"
        ),
        "wenxin": ModelConfig(
            api_key=API_KEYS["wenxin"],
            base_url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-8k",
            model_name="ernie-4.0-8k",
            system_prompt="你是一个专业的数据分析师，擅长从数据中发现趋势、统计规律和潜在风险。"
        ),
        "tongyi": ModelConfig(
            api_key=API_KEYS["tongyi"],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_name="qwen-plus",
            system_prompt="你是一个专业的数据分析师，擅长从数据中发现趋势、统计规律和潜在风险。"
        ),
    }
    return configs[provider]


def load_excel_files(data_dir: str) -> dict:
    """加载所有Excel文件"""
    excel_files = glob.glob(os.path.join(data_dir, "*.xlsx")) + \
                  glob.glob(os.path.join(data_dir, "*.xls"))
    
    data_dict = {}
    for file_path in excel_files:
        filename = os.path.basename(file_path)
        try:
            # 读取所有sheet
            sheets = pd.read_excel(file_path, sheet_name=None)
            for sheet_name, df in sheets.items():
                key = f"{filename}_{sheet_name}" if len(sheets) > 1 else filename
                data_dict[key] = df
                print(f"✓ 加载: {key} ({len(df)} 行)")
        except Exception as e:
            print(f"✗ 加载失败 {filename}: {e}")
    
    return data_dict


def generate_data_summary(data_dict: dict) -> str:
    """生成数据摘要"""
    summary_parts = []
    
    for name, df in data_dict.items():
        summary_parts.append(f"\n## {name}")
        
        # 基本信息
        summary_parts.append(f"- 行数: {len(df)}")
        summary_parts.append(f"- 列数: {len(df.columns)}")
        summary_parts.append(f"- 列名: {list(df.columns)}")
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats = df[numeric_cols].describe().round(2)
            summary_parts.append(f"\n### 数值列统计")
            summary_parts.append(stats.to_string())
        
        # 缺失值
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) > 0:
            summary_parts.append(f"\n### 缺失值")
            summary_parts.append(missing.to_string())
    
    return "\n".join(summary_parts)


def call_model(prompt: str, config: ModelConfig) -> str:
    """调用大模型API"""
    import requests
    
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }
    
    if config.model_name.startswith("glm"):
        # 智谱API
        payload = {
            "model": config.model_name,
            "messages": [
                {"role": "system", "content": config.system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
    elif "ernie" in config.model_name:
        # 百度API (需要access token)
        # 这里简化处理，实际需要获取access token
        print("⚠ 百度API需要额外获取access token，请使用智谱或通义")
        return ""
    elif "qwen" in config.model_name:
        # 阿里API
        payload = {
            "model": config.model_name,
            "messages": [
                {"role": "system", "content": config.system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
    
    try:
        response = requests.post(
            f"{config.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        result = response.json()
        
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        elif "content" in result:
            return result["content"]
        else:
            print(f"API返回: {result}")
            return ""
    except Exception as e:
        print(f"API调用失败: {e}")
        return ""


def generate_analysis_prompt(data_summary: str, analysis_type: str) -> str:
    """生成分析提示词"""
    
    prompts = {
        "trend": """请分析以下数据的时间趋势：
1. 识别数据中的时间列
2. 分析关键指标的变化趋势
3. 找出趋势的拐点或异常变化
4. 预测未来可能的走势

数据摘要：
{data}

请给出详细的趋势分析报告。""",
        
        "statistics": """请对以下数据进行全面的统计汇总：
1. 各关键指标的均值、中位数、标准差
2. 数据的分布特征
3. 相关性分析
4. 排名分析（Top/Bottom）

数据摘要：
{data}

请给出详细的统计报告。""",
        
        "risk": """请进行风险监测分析：
1. 识别数据中的异常值
2. 检测潜在的风险指标
3. 评估风险等级
4. 给出风险预警

数据摘要：
{data}

请给出详细的风险分析报告。""",
        
        "comprehensive": """请对以下数据进行全面的综合分析，包括：
1. 趋势分析 - 数据随时间的变化趋势
2. 统计汇总 - 关键指标的统计特征
3. 风险监测 - 识别异常和风险点
4. 外部因素分析 - 基于数据特点，分析可能受影响的外部因素

数据摘要：
{data}

请给出详细的分析报告，包含数据洞察、问题发现、建议措施。"""
    }
    
    return prompts[analysis_type].format(data=data_summary)


def run_analysis(data_dir: str, output_dir: str, analysis_type: str = "comprehensive"):
    """运行分析"""
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 加载数据
    print("\n" + "="*50)
    print("步骤1: 加载Excel数据")
    print("="*50)
    data_dict = load_excel_files(data_dir)
    
    if not data_dict:
        print("❌ 未找到Excel文件")
        return
    
    print(f"\n✓ 共加载 {len(data_dict)} 个数据表")
    
    # 2. 生成数据摘要
    print("\n" + "="*50)
    print("步骤2: 生成数据摘要")
    print("="*50)
    data_summary = generate_data_summary(data_dict)
    
    # 保存摘要
    summary_file = os.path.join(output_dir, "data_summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(data_summary)
    print(f"✓ 摘要已保存: {summary_file}")
    
    # 3. 调用大模型分析
    print("\n" + "="*50)
    print("步骤3: 调用大模型分析")
    print("="*50)
    
    config = get_model_config(MODEL_PROVIDER)
    
    if not config.api_key or config.api_key == "your-api-key-here":
        print("❌ 请先配置API密钥！")
        print(f"请修改 {__file__} 中的 API_KEYS 配置")
        return
    
    prompt = generate_analysis_prompt(data_summary, analysis_type)
    print("正在调用大模型，请稍候...")
    
    report = call_model(prompt, config)
    
    if report:
        # 保存报告
        report_file = os.path.join(output_dir, f"analysis_report_{analysis_type}.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✓ 分析报告已保存: {report_file}")
        print("\n" + "="*50)
        print("分析报告内容:")
        print("="*50)
        print(report)
    else:
        print("❌ 分析失败")


# ================== 主程序 ==================

if __name__ == "__main__":
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════╗
║          Excel数据分析工具 - 国内大模型API版              ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 检查数据目录
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"⚠ 请将Excel文件放入: {DATA_DIR}")
        print("然后重新运行脚本")
        sys.exit(1)
    
    # 运行分析
    run_analysis(DATA_DIR, OUTPUT_DIR, analysis_type="comprehensive")
