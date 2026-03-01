"""
数据验证工具

提供数据类型验证、范围验证、格式验证等功能
"""
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


class ValidationLevel(Enum):
    """验证级别"""
    ERROR = "ERROR"      # 严重错误，必须修复
    WARNING = "WARNING"  # 警告，建议修复
    INFO = "INFO"        # 信息，仅供参考


@dataclass
class ValidationIssue:
    """验证问题"""
    level: ValidationLevel
    column: str
    row: Optional[int]  # 行索引，None表示整列问题
    message: str
    value: Any = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue):
        """添加问题"""
        self.issues.append(issue)

    def get_errors(self) -> List[ValidationIssue]:
        """获取所有错误"""
        return [i for i in self.issues if i.level == ValidationLevel.ERROR]

    def get_warnings(self) -> List[ValidationIssue]:
        """获取所有警告"""
        return [i for i in self.issues if i.level == ValidationLevel.WARNING]

    def get_info(self) -> List[ValidationIssue]:
        """获取所有信息"""
        return [i for i in self.issues if i.level == ValidationLevel.INFO]

    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.get_errors()) > 0


class DataValidator:
    """数据验证器"""

    def __init__(self):
        pass

    def validate_dataframe(
        self,
        df: pd.DataFrame,
        schema: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        验证数据框

        Args:
            df: 数据框
            schema: 数据模式定义

        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)

        # 基本验证
        if df.empty:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                column="global",
                row=None,
                message="数据框为空"
            ))
            result.is_valid = False
            return result

        # 检查重复列
        duplicate_columns = df.columns[df.columns.duplicated()].tolist()
        if duplicate_columns:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                column="global",
                row=None,
                message=f"存在重复的列名: {duplicate_columns}"
            ))
            result.is_valid = False

        # 检查列名
        for col in df.columns:
            if pd.isna(col) or col == "":
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    column="global",
                    row=None,
                    message="存在空列名"
                ))
                result.is_valid = False

        # 根据schema验证
        if schema:
            self._validate_schema(df, schema, result)

        return result

    def _validate_schema(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        result: ValidationResult
    ):
        """根据schema验证"""
        # 验证必需列
        if 'required_columns' in schema:
            required = set(schema['required_columns'])
            missing = required - set(df.columns)
            if missing:
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    column="global",
                    row=None,
                    message=f"缺少必需的列: {missing}",
                    suggestion=f"请添加以下列: {missing}"
                ))
                result.is_valid = False

        # 验证列类型
        if 'column_types' in schema:
            for col, expected_type in schema['column_types'].items():
                if col not in df.columns:
                    continue

                actual_type = str(df[col].dtype)
                type_mapping = {
                    'int': ['int64', 'int32', 'int16', 'int8'],
                    'float': ['float64', 'float32'],
                    'string': ['object', 'str'],
                    'datetime': ['datetime64[ns]', 'datetime64[ns, tz]']
                }

                if expected_type in type_mapping:
                    if actual_type not in type_mapping[expected_type]:
                        result.add_issue(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            column=col,
                            row=None,
                            message=f"列类型不匹配: 期望 {expected_type}, 实际 {actual_type}",
                            suggestion=f"尝试: df['{col}'] = df['{col}'].astype('{expected_type}')"
                        ))

        # 验证值范围
        if 'ranges' in schema:
            for col, range_spec in schema['ranges'].items():
                if col not in df.columns:
                    continue

                series = df[col].dropna()

                if 'min' in range_spec:
                    below_min = series < range_spec['min']
                    if below_min.any():
                        count = below_min.sum()
                        result.add_issue(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            column=col,
                            row=None,
                            message=f"{count} 个值低于最小值 {range_spec['min']}"
                        ))

                if 'max' in range_spec:
                    above_max = series > range_spec['max']
                    if above_max.any():
                        count = above_max.sum()
                        result.add_issue(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            column=col,
                            row=None,
                            message=f"{count} 个值高于最大值 {range_spec['max']}"
                        ))

    def validate_numeric_column(
        self,
        df: pd.DataFrame,
        column: str,
        allow_negative: bool = True,
        allow_zero: bool = True
    ) -> ValidationResult:
        """
        验证数值列

        Args:
            df: 数据框
            column: 列名
            allow_negative: 是否允许负数
            allow_zero: 是否允许零

        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)

        if column not in df.columns:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                column=column,
                row=None,
                message=f"列 '{column}' 不存在"
            ))
            result.is_valid = False
            return result

        series = df[column].dropna()

        # 检查是否为数值类型
        if not np.issubdtype(series.dtype, np.number):
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                column=column,
                row=None,
                message=f"列 '{column}' 不是数值类型: {series.dtype}",
                suggestion=f"尝试: df['{column}'] = pd.to_numeric(df['{column}'], errors='coerce')"
            ))

        # 检查负数
        if not allow_negative:
            negative_count = (series < 0).sum()
            if negative_count > 0:
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=column,
                    row=None,
                    message=f"发现 {negative_count} 个负数（不允许负数）"
                ))

        # 检查零值
        if not allow_zero:
            zero_count = (series == 0).sum()
            if zero_count > 0:
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.INFO,
                    column=column,
                    row=None,
                    message=f"发现 {zero_count} 个零值（不允许零值）"
                ))

        # 检查无穷大
        if np.issubdtype(series.dtype, np.number):
            inf_count = np.isinf(series).sum()
            if inf_count > 0:
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    column=column,
                    row=None,
                    message=f"发现 {inf_count} 个无穷大值",
                    suggestion="使用 df['{column}'].replace([np.inf, -np.inf], np.nan) 处理"
                ))
                result.is_valid = False

        return result

    def validate_text_column(
        self,
        df: pd.DataFrame,
        column: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        pattern: Optional[str] = None
    ) -> ValidationResult:
        """
        验证文本列

        Args:
            df: 数据框
            column: 列名
            max_length: 最大长度
            min_length: 最小长度
            pattern: 正则表达式模式

        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)

        if column not in df.columns:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                column=column,
                row=None,
                message=f"列 '{column}' 不存在"
            ))
            result.is_valid = False
            return result

        series = df[column].dropna()

        # 检查长度
        lengths = series.astype(str).str.len()

        if max_length is not None:
            too_long = lengths > max_length
            if too_long.any():
                count = too_long.sum()
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=column,
                    row=None,
                    message=f"{count} 个值超过最大长度 {max_length}"
                ))

        if min_length is not None:
            too_short = lengths < min_length
            if too_short.any():
                count = too_short.sum()
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=column,
                    row=None,
                    message=f"{count} 个值低于最小长度 {min_length}"
                ))

        # 检查正则表达式
        if pattern is not None:
            import re
            invalid = ~series.astype(str).str.match(pattern, na=False)
            if invalid.any():
                count = invalid.sum()
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=column,
                    row=None,
                    message=f"{count} 个值不匹配模式: {pattern}"
                ))

        return result

    def validate_date_column(
        self,
        df: pd.DataFrame,
        column: str,
        min_date: Optional[Any] = None,
        max_date: Optional[Any] = None,
        allow_future: bool = False
    ) -> ValidationResult:
        """
        验证日期列

        Args:
            df: 数据框
            column: 列名
            min_date: 最小日期
            max_date: 最大日期
            allow_future: 是否允许未来日期

        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)

        if column not in df.columns:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                column=column,
                row=None,
                message=f"列 '{column}' 不存在"
            ))
            result.is_valid = False
            return result

        # 尝试转换为日期
        try:
            series = pd.to_datetime(df[column], errors='coerce')
        except Exception as e:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.ERROR,
                column=column,
                row=None,
                message=f"无法转换为日期: {str(e)}"
            ))
            result.is_valid = False
            return result

        # 检查转换失败的数量
        failed_count = series.isna().sum()
        if failed_count > 0:
            result.add_issue(ValidationIssue(
                level=ValidationLevel.WARNING,
                column=column,
                row=None,
                message=f"{failed_count} 个值无法转换为日期"
            ))

        series = series.dropna()

        # 检查日期范围
        if min_date is not None:
            min_date = pd.to_datetime(min_date)
            too_early = series < min_date
            if too_early.any():
                count = too_early.sum()
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=column,
                    row=None,
                    message=f"{count} 个值早于最小日期 {min_date}"
                ))

        if max_date is not None:
            max_date = pd.to_datetime(max_date)
            too_late = series > max_date
            if too_late.any():
                count = too_late.sum()
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=column,
                    row=None,
                    message=f"{count} 个值晚于最大日期 {max_date}"
                ))

        # 检查未来日期
        if not allow_future:
            now = pd.Timestamp.now()
            future_dates = series > now
            if future_dates.any():
                count = future_dates.sum()
                result.add_issue(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=column,
                    row=None,
                    message=f"{count} 个值是未来日期"
                ))

        return result

    def check_missing_values(
        self,
        df: pd.DataFrame,
        threshold: float = 0.5
    ) -> Dict[str, float]:
        """
        检查缺失值

        Args:
            df: 数据框
            threshold: 缺失值比例阈值

        Returns:
            {列名: 缺失值比例}
        """
        missing_ratios = {}

        for col in df.columns:
            ratio = df[col].isna().sum() / len(df)
            missing_ratios[col] = ratio

        return missing_ratios

    def check_duplicates(
        self,
        df: pd.DataFrame,
        subset: Optional[List[str]] = None
    ) -> int:
        """
        检查重复行

        Args:
            df: 数据框
            subset: 检查重复的列子集

        Returns:
            重复行数
        """
        return df.duplicated(subset=subset).sum()

    def generate_validation_report(self, result: ValidationResult) -> str:
        """
        生成验证报告

        Args:
            result: 验证结果

        Returns:
            报告文本
        """
        lines = []

        lines.append("=" * 50)
        lines.append("数据验证报告")
        lines.append("=" * 50)

        lines.append(f"\n总体状态: {'✅ 通过' if result.is_valid else '❌ 失败'}")
        lines.append(f"总问题数: {len(result.issues)}")

        # 按级别分组
        errors = result.get_errors()
        warnings = result.get_warnings()
        infos = result.get_info()

        if errors:
            lines.append(f"\n🔴 错误 ({len(errors)}):")
            for issue in errors:
                lines.append(f"  • [{issue.column}] {issue.message}")
                if issue.suggestion:
                    lines.append(f"    建议: {issue.suggestion}")

        if warnings:
            lines.append(f"\n🟡 警告 ({len(warnings)}):")
            for issue in warnings:
                lines.append(f"  • [{issue.column}] {issue.message}")

        if infos:
            lines.append(f"\n🔵 信息 ({len(infos)}):")
            for issue in infos:
                lines.append(f"  • [{issue.column}] {issue.message}")

        lines.append("\n" + "=" * 50)

        return "\n".join(lines)
