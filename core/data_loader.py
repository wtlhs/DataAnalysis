"""
数据加载与预处理模块

支持大文件分块读取、数据验证、缺失值处理、多表管理
"""
import os
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from config.settings import settings


class FileExtension(Enum):
    """支持的文件扩展名"""
    XLSX = ".xlsx"
    XLS = ".xls"
    CSV = ".csv"


@dataclass
class ValidationResult:
    """数据验证结果"""
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    file_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.file_info is None:
            self.file_info = {}


class DataLoader:
    """Excel/CSV数据加载器"""

    def __init__(self, config=None):
        self.config = config or settings.data
        self._cached_df: Optional[pd.DataFrame] = None
        self._file_path: Optional[str] = None

    def load_file(
        self,
        file_path: str,
        sheet_name: str = 0,
        chunk_size: Optional[int] = None
    ) -> Tuple[pd.DataFrame, ValidationResult]:
        """
        加载Excel/CSV文件

        Args:
            file_path: 文件路径
            sheet_name: Excel工作表名称或索引
            chunk_size: 分块读取大小（仅CSV文件支持，None表示不分块）

        Returns:
            (DataFrame, 验证结果)
        """
        # 验证文件
        validation = self._validate_file(file_path)
        if not validation.is_valid:
            return pd.DataFrame(), validation

        # 确定读取方式
        chunk_size = chunk_size or self.config.chunk_size

        try:
            # 读取文件
            if file_path.lower().endswith('.csv'):
                df = self._read_csv(file_path, chunk_size)
            else:
                # Excel文件不支持分块读取，直接读取
                df = self._read_excel(file_path, sheet_name)

            # 基本信息统计
            validation.file_info = {
                'rows': len(df),
                'columns': len(df.columns),
                'size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'columns_list': df.columns.tolist()
            }

            # 缓存数据
            self._cached_df = df
            self._file_path = file_path

            return df, validation

        except Exception as e:
            validation.is_valid = False
            validation.errors.append(f"文件读取失败: {str(e)}")
            return pd.DataFrame(), validation

    def _validate_file(self, file_path: str) -> ValidationResult:
        """验证文件"""
        result = ValidationResult(is_valid=True)

        # 检查文件是否存在
        if not Path(file_path).exists():
            result.is_valid = False
            result.errors.append("文件不存在")
            return result

        # 检查文件扩展名
        ext = Path(file_path).suffix.lower()
        if ext not in [e.value for e in FileExtension]:
            result.is_valid = False
            result.errors.append(f"不支持的文件格式: {ext}，仅支持 {', '.join([e.value for e in FileExtension])}")
            return result

        # 检查文件大小
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > self.config.max_file_size_mb:
            result.is_valid = False
            result.errors.append(f"文件过大: {size_mb:.2f}MB (最大 {self.config.max_file_size_mb}MB)")
            return result

        return result

    def _read_excel(self, file_path: str, sheet_name: str = 0) -> pd.DataFrame:
        """读取Excel文件"""
        # pd.read_excel 不支持 chunksize 参数，直接读取整个文件
        # 对于非常大的文件，可以考虑使用 openpyxl 分页读取
        return pd.read_excel(file_path, sheet_name=sheet_name)

    def _read_csv(self, file_path: str, chunk_size: Optional[int] = None) -> pd.DataFrame:
        """读取CSV文件"""
        encoding = self._detect_encoding(file_path)

        if chunk_size is None:
            return pd.read_csv(file_path, encoding=encoding)
        else:
            dfs = []
            for chunk in pd.read_csv(file_path, encoding=encoding, chunksize=chunk_size):
                dfs.append(chunk)
            return pd.concat(dfs, ignore_index=True)

    def _detect_encoding(self, file_path: str) -> str:
        """检测CSV文件编码"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'big5']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)
                return encoding
            except UnicodeDecodeError:
                continue
        return 'utf-8'

    def preprocess(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        数据预处理

        Args:
            df: 原始DataFrame

        Returns:
            (处理后的DataFrame, 预处理信息)
        """
        info = {
            'original_shape': df.shape,
            'missing_before': df.isnull().sum().sum(),
            'duplicates_removed': 0
        }

        # 移除完全为空的行
        df = df.dropna(how='all')

        # 移除完全为空的列
        df = df.dropna(axis=1, how='all')

        # 尝试转换日期列
        df = self._convert_date_columns(df)

        # 移除重复行（保留第一次出现）
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            df = df.drop_duplicates(keep='first')
            info['duplicates_removed'] = duplicates

        info['processed_shape'] = df.shape
        info['missing_after'] = df.isnull().sum().sum()
        info['missing_ratio'] = info['missing_after'] / (df.shape[0] * df.shape[1]) if df.shape[0] > 0 else 0

        # 警告：缺失值比例过高
        if info['missing_ratio'] > self.config.max_missing_ratio:
            info['warning'] = f"数据缺失值比例过高: {info['missing_ratio']:.2%}"

        # 更新缓存
        self._cached_df = df

        return df, info

    def _convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """尝试转换日期列"""
        df = df.copy()

        # 尝试检测日期列
        date_keywords = self.config.date_columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in date_keywords):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception:
                    continue

        return df

    def validate_data_schema(
        self,
        df: pd.DataFrame,
        required_columns: Optional[List[str]] = None,
        min_rows: Optional[int] = None
    ) -> ValidationResult:
        """
        验证数据模式

        Args:
            df: 数据框
            required_columns: 必需的列名
            min_rows: 最小行数

        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)

        # 检查最小行数
        min_rows = min_rows or self.config.min_data_points
        if len(df) < min_rows:
            result.warnings.append(f"数据行数较少: {len(df)} (建议至少 {min_rows} 行)")

        # 检查必需列
        if required_columns:
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                result.is_valid = False
                result.errors.append(f"缺少必需列: {', '.join(missing_cols)}")

        # 检查缺失值
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if missing_ratio > 0.5:
            result.warnings.append(f"数据缺失值比例过高: {missing_ratio:.2%}")

        return result

    def get_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """获取数值型列"""
        numeric_types = ['int64', 'float64', 'int32', 'float32']
        return [col for col in df.columns if df[col].dtype in numeric_types]

    def get_date_columns(self, df: pd.DataFrame) -> List[str]:
        """获取日期型列"""
        return [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]

    def get_categorical_columns(self, df: pd.DataFrame) -> List[str]:
        """获取分类型列"""
        excluded_types = ['int64', 'float64', 'int32', 'float32', 'datetime64[ns]']
        return [col for col in df.columns if df[col].dtype not in excluded_types]

    def sample_for_ai(self, df: pd.DataFrame, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        采样用于AI分析的数据

        对于大数据集，进行智能采样以减少token消耗
        """
        sample_size = sample_size or self.config.sample_size

        if len(df) <= sample_size:
            return df

        # 按时间列排序后采样（如果有时间列）
        date_cols = self.get_date_columns(df)
        if date_cols:
            df_sorted = df.sort_values(date_cols[0])
            # 均匀采样
            step = len(df_sorted) // sample_size
            return df_sorted.iloc[::step][:sample_size]

        # 否则随机采样
        return df.sample(n=sample_size, random_state=42)

    @property
    def cached_data(self) -> Optional[pd.DataFrame]:
        """获取缓存的数据"""
        return self._cached_df

    def clear_cache(self):
        """清除缓存"""
        self._cached_df = None
        self._file_path = None

    # ============ 多表支持方法 ============

    def load_multiple_files(
        self,
        file_list: List[Tuple[str, bytes]],
        upload_dir: str,
        session_manager=None
    ) -> Dict[str, pd.DataFrame]:
        """加载多个Excel/CSV文件

        Args:
            file_list: 文件列表，每个元素为 (filename, file_content)
            upload_dir: 上传目录
            session_manager: 会话管理器（可选）

        Returns:
            字典 {dataset_id: DataFrame}
        """
        datasets = {}

        for filename, file_content in file_list:
            # 保存文件
            file_path = Path(upload_dir) / filename
            with open(file_path, 'wb') as f:
                f.write(file_content)

            # 加载数据
            df, validation = self.load_file(str(file_path))

            if validation.is_valid:
                # 预处理
                df, _ = self.preprocess(df)

                # 保存到数据库
                if session_manager:
                    dataset_id = session_manager.save_dataset(
                        file_path=str(file_path),
                        name=filename,
                        df=df,
                        metadata={'file_info': validation.file_info}
                    )
                    datasets[dataset_id] = df
                else:
                    # 如果没有session_manager，使用文件名作为key
                    datasets[filename] = df

        return datasets

    def get_dataset_from_db(
        self,
        dataset_id: str,
        session_manager
    ) -> Optional[pd.DataFrame]:
        """从数据库获取数据集

        Args:
            dataset_id: 数据集ID
            session_manager: 会话管理器

        Returns:
            DataFrame，如果不存在则返回None
        """
        metadata = session_manager.get_dataset(dataset_id)
        if metadata:
            file_path = metadata['file_path']
            if Path(file_path).exists():
                df, _ = self.load_file(file_path)
                self._cached_df = df
                self._file_path = file_path
                return df
        return None

    def merge_datasets(
        self,
        datasets: Dict[str, pd.DataFrame],
        merge_config: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """合并多个数据集

        Args:
            datasets: 数据集字典 {name: DataFrame}
            merge_config: 合并配置
                - on: 合并键
                - how: 合并方式 ('inner', 'outer', 'left', 'right')
                - join_cols: 用于join的列名列表

        Returns:
            合并后的DataFrame
        """
        if not datasets:
            return pd.DataFrame()

        if len(datasets) == 1:
            return list(datasets.values())[0]

        # 如果没有配置，尝试自动合并
        if merge_config is None:
            merge_config = self._detect_merge_config(datasets)

        merge_config = merge_config or {}

        # 获取合并键
        merge_keys = merge_config.get('on') or merge_config.get('join_cols', [])
        merge_how = merge_config.get('how', 'inner')

        # 如果有指定的合并键
        if merge_keys:
            # 将第一个数据集作为基础
            dataset_list = list(datasets.values())
            result = dataset_list[0]

            # 逐个合并其他数据集
            for df in dataset_list[1:]:
                # 尝试找到共同的列
                common_cols = list(set(result.columns) & set(df.columns))

                if common_cols and not merge_keys:
                    # 使用共同列作为合并键
                    result = pd.merge(result, df, on=common_cols[0], how=merge_how)
                elif merge_keys:
                    # 使用指定的合并键
                    available_keys = [k for k in merge_keys if k in df.columns]
                    if available_keys:
                        result = pd.merge(result, df, on=available_keys[0], how=merge_how)
                    else:
                        # 如果合并键不存在，使用索引
                        result = pd.merge(result, df, left_index=True, right_index=True, how=merge_how)
                else:
                    # 没有合并键，使用索引
                    result = pd.merge(result, df, left_index=True, right_index=True, how=merge_how)

            return result
        else:
            # 简单的行堆叠
            return pd.concat(datasets.values(), ignore_index=True)

    def _detect_merge_config(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """自动检测合并配置

        Args:
            datasets: 数据集字典

        Returns:
            合并配置字典
        """
        # 获取所有列名
        all_columns = {}
        for name, df in datasets.items():
            all_columns[name] = set(df.columns)

        # 查找共同列
        common_columns = set.intersection(*all_columns.values())

        # 如果有共同列，建议使用第一个共同列作为合并键
        if common_columns:
            return {
                'on': list(common_columns)[0],
                'how': 'inner'
            }

        # 没有共同列，使用简单的concat
        return {
            'how': 'concat'
        }

    def compare_datasets(
        self,
        datasets: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """比较多个数据集

        Args:
            datasets: 数据集字典

        Returns:
            比较结果
        """
        comparison = {
            'datasets': {},
            'common_columns': set(),
            'unique_columns': {},
            'shape_comparison': {}
        }

        # 收集列信息
        all_columns = {}
        for name, df in datasets.items():
            all_columns[name] = set(df.columns)
            comparison['datasets'][name] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'numeric_cols': len(self.get_numeric_columns(df)),
                'date_cols': len(self.get_date_columns(df)),
                'missing_values': df.isnull().sum().sum(),
                'dtypes': df.dtypes.astype(str).to_dict()
            }

        # 查找共同列
        all_column_sets = list(all_columns.values())
        if all_column_sets:
            comparison['common_columns'] = set.intersection(*all_column_sets)

        # 查找唯一列
        for name, cols in all_columns.items():
            unique = cols - set.union(*[c for n, c in all_columns.items() if n != name])
            comparison['unique_columns'][name] = list(unique)

        return comparison

