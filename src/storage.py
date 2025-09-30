"""
数据存储模块 - 负责将收集的资源保存到CSV和Excel文件
"""
import os
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResourceStorage:
    """资源存储类"""

    COLUMN_MAPPING = {
        'title': '资源名称',
        'url': '链接地址',
        'type': '类型',
        'language_detected': '语言',
        'source': '来源平台',
        'quality_score': '质量评分',
        'recommendation': '推荐理由',
        'description': '描述',
        'stars': '星标数',
        'language': '编程语言',
        'updated_at': '更新时间',
        'collected_at': '收集时间',
        'keyword': '搜索关键词'
    }

    REVERSE_COLUMN_MAPPING = {v: k for k, v in COLUMN_MAPPING.items()}

    def __init__(self, output_dir: str = "resources"):
        """
        初始化存储管理器

        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建输出目录: {self.output_dir}")

    def save_to_csv(self, resources: List[Dict[str, Any]], filename: str = None) -> str:
        """
        保存资源到CSV文件

        Args:
            resources: 资源列表
            filename: 文件名（可选）

        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cuda_hpc_resources_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        # 转换为DataFrame
        df = pd.DataFrame(resources)

        # 选择和重排列列
        columns_order = [
            'title', 'url', 'type', 'language_detected', 'source',
            'quality_score', 'recommendation', 'description',
            'stars', 'language', 'updated_at', 'collected_at', 'keyword'
        ]

        # 只保留存在的列
        existing_columns = [col for col in columns_order if col in df.columns]
        df = df[existing_columns]

        # 保存到CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"保存CSV文件: {filepath}")

        return filepath

    def save_to_excel(self, resources: List[Dict[str, Any]],
                      categorized: Dict[str, List[Dict[str, Any]]] = None,
                      filename: str = None) -> str:
        """
        保存资源到Excel文件（支持多个工作表）

        Args:
            resources: 所有资源列表
            categorized: 分类后的资源字典
            filename: 文件名（可选）

        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cuda_hpc_resources_{timestamp}.xlsx"

        filepath = os.path.join(self.output_dir, filename)

        # 使用ExcelWriter创建多个工作表
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 1. 所有资源工作表
            self._write_sheet(writer, resources, '所有资源')

            # 2. 分类工作表
            if categorized:
                for category, items in categorized.items():
                    if items:  # 只创建非空分类的工作表
                        sheet_name = self._translate_category(category)
                        self._write_sheet(writer, items, sheet_name)

            # 3. 统计信息工作表
            stats = self._generate_statistics(resources)
            stats_df = pd.DataFrame([stats])
            stats_df.to_excel(writer, sheet_name='统计信息', index=False)

            # 4. Top资源工作表
            top_resources = sorted(
                resources,
                key=lambda x: x.get('quality_score', 0),
                reverse=True
            )[:20]
            self._write_sheet(writer, top_resources, 'Top20资源')

        logger.info(f"保存Excel文件: {filepath}")
        return filepath

    def _write_sheet(self, writer, resources: List[Dict[str, Any]], sheet_name: str):
        """
        写入单个工作表

        Args:
            writer: ExcelWriter对象
            resources: 资源列表
            sheet_name: 工作表名称
        """
        if not resources:
            return

        # 转换为DataFrame
        df = pd.DataFrame(resources)

        # 列顺序和中文列名映射
        # 选择存在的列并重命名
        existing_columns = [col for col in self.COLUMN_MAPPING.keys() if col in df.columns]
        df = df[existing_columns]
        df = df.rename(columns=self.COLUMN_MAPPING)

        # 写入工作表
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # 获取工作表并调整列宽
        worksheet = writer.sheets[sheet_name]
        for column_cells in worksheet.columns:
            # 获取所有非空单元格的长度
            lengths = [len(str(cell.value)) for cell in column_cells if cell.value is not None]
            # 如果有非空单元格,使用最大长度;否则使用默认值10
            length = max(lengths) if lengths else 10
            length = min(length, 50)  # 限制最大列宽
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

    def _normalize_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """将DataFrame列名转换为内部统一使用的英文键"""
        if df.empty:
            return df

        rename_map = {
            column_name: self.REVERSE_COLUMN_MAPPING[column_name]
            for column_name in df.columns
            if column_name in self.REVERSE_COLUMN_MAPPING
        }

        if rename_map:
            df = df.rename(columns=rename_map)

        return df

    def _translate_category(self, category: str) -> str:
        """
        翻译分类名称为中文

        Args:
            category: 英文分类名

        Returns:
            中文分类名
        """
        translations = {
            'website': '网站',
            'blog': '博客',
            'code': '代码',
            'forum': '论坛',
            'course_notes': '课程笔记讲座',
            'book': '公开书籍',
            'exam': '考试',
            'technical_whitepaper': '技术白皮书',
            'other': '其他'
        }
        return translations.get(category, category)

    def _generate_statistics(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成统计信息

        Args:
            resources: 资源列表

        Returns:
            统计信息字典
        """
        stats = {
            '总资源数': len(resources),
            '收集时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 按类型统计
        type_counts = {}
        for resource in resources:
            resource_type = resource.get('type', 'other')
            type_counts[resource_type] = type_counts.get(resource_type, 0) + 1

        for type_name, count in type_counts.items():
            stats[f'{self._translate_category(type_name)}数量'] = count

        # 按语言统计
        lang_counts = {}
        for resource in resources:
            lang = resource.get('language_detected', 'unknown')
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        stats['中文资源数'] = lang_counts.get('zh', 0)
        stats['英文资源数'] = lang_counts.get('en', 0)
        stats['双语资源数'] = lang_counts.get('mixed', 0)

        # 按来源统计
        source_counts = {}
        for resource in resources:
            source = resource.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1

        for source, count in source_counts.items():
            stats[f'{source}来源数'] = count

        # 质量评分统计
        scores = [r.get('quality_score', 0) for r in resources]
        if scores:
            stats['平均质量评分'] = round(sum(scores) / len(scores), 2)
            stats['最高评分'] = max(scores)
            stats['最低评分'] = min(scores)
            stats['4分以上资源数'] = sum(1 for s in scores if s >= 4.0)

        return stats

    def load_existing_resources(self, filename: str) -> List[Dict[str, Any]]:
        """
        加载已存在的资源文件（用于增量更新）

        Args:
            filename: 文件名

        Returns:
            资源列表
        """
        filepath = os.path.join(self.output_dir, filename)

        if not os.path.exists(filepath):
            logger.warning(f"文件不存在: {filepath}")
            return []

        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(filepath, sheet_name='所有资源')
            else:
                logger.error(f"不支持的文件格式: {filename}")
                return []

            df = self._normalize_dataframe_columns(df)

            # 转换回字典列表
            resources = df.to_dict('records')
            logger.info(f"从 {filepath} 加载了 {len(resources)} 个资源")
            return resources

        except Exception as e:
            logger.error(f"加载文件失败: {e}")
            return []

    def merge_resources(self, existing: List[Dict[str, Any]],
                        new: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并新旧资源，去除重复

        Args:
            existing: 已存在的资源
            new: 新收集的资源

        Returns:
            合并后的资源列表
        """
        # 使用URL作为唯一标识
        existing_urls = {r.get('url', '') for r in existing}

        # 添加新资源
        merged = existing.copy()
        added_count = 0

        for resource in new:
            url = resource.get('url', '')
            if url and url not in existing_urls:
                merged.append(resource)
                existing_urls.add(url)
                added_count += 1

        logger.info(f"合并资源: 已有{len(existing)}个，新增{added_count}个，总计{len(merged)}个")
        return merged


# 测试代码
if __name__ == "__main__":
    storage = ResourceStorage()

    # 测试数据
    test_resources = [
        {
            'title': 'CUDA Programming Guide',
            'url': 'https://docs.nvidia.com/cuda/',
            'type': 'website',
            'language_detected': 'en',
            'source': 'DuckDuckGo',
            'quality_score': 4.5,
            'recommendation': '官方文档，权威参考',
            'description': 'Official CUDA documentation',
            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'title': 'CUDA编程入门',
            'url': 'https://example.com/cuda-tutorial',
            'type': 'course_notes',
            'language_detected': 'zh',
            'source': 'DuckDuckGo',
            'quality_score': 4.0,
            'recommendation': '中文教程，适合入门',
            'description': 'CUDA编程基础教程',
            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    # 测试保存
    csv_path = storage.save_to_csv(test_resources, 'test.csv')
    print(f"CSV saved to: {csv_path}")

    excel_path = storage.save_to_excel(test_resources, filename='test.xlsx')
    print(f"Excel saved to: {excel_path}")