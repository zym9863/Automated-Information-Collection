"""
数据解析模块 - 负责解析、分类和评分资源
"""
import re
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ResourceParser:
    """资源解析器类"""

    def __init__(self):
        """初始化解析器"""
        # 资源类型关键词映射
        self.type_keywords = {
            'book': ['book', 'pdf', '书', '教材', 'guide', 'handbook', 'manual'],
            'course': ['course', 'tutorial', 'lesson', '课程', '教程', 'class', 'lecture'],
            'blog': ['blog', 'article', 'post', '博客', '文章', 'medium.com'],
            'code': ['github', 'gitlab', 'code', 'repository', 'repo', '代码', 'example', 'demo'],
            'documentation': ['docs', 'documentation', 'api', 'reference', '文档', 'nvidia.com/docs']
        }

        # 语言检测模式
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')

    def detect_resource_type(self, resource: Dict[str, Any]) -> str:
        """
        检测资源类型

        Args:
            resource: 资源字典

        Returns:
            资源类型字符串
        """
        title = (resource.get('title') or '').lower()
        url = (resource.get('url') or '').lower()
        description = (resource.get('description') or '').lower()

        # 合并所有文本进行检测
        combined_text = f"{title} {url} {description}"

        # 检测每种类型的关键词
        type_scores = {}
        for resource_type, keywords in self.type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            type_scores[resource_type] = score

        # 特殊规则
        if 'github.com' in url or 'gitlab.com' in url:
            type_scores['code'] += 3
        if '.pdf' in url:
            type_scores['book'] += 2

        # 返回得分最高的类型
        if max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)
        return 'other'

    def detect_language(self, resource: Dict[str, Any]) -> str:
        """
        检测资源语言

        Args:
            resource: 资源字典

        Returns:
            语言标识 (zh/en/mixed)
        """
        title = resource.get('title', '')
        description = resource.get('description', '')
        combined_text = f"{title} {description}"

        # 检测中文字符
        chinese_chars = self.chinese_pattern.findall(combined_text)
        has_chinese = len(chinese_chars) > 0

        # 检测英文（简单判断）
        english_words = re.findall(r'[a-zA-Z]+', combined_text)
        has_english = len(english_words) > 3

        if has_chinese and has_english:
            return 'mixed'
        elif has_chinese:
            return 'zh'
        elif has_english:
            return 'en'
        else:
            return 'unknown'

    def calculate_quality_score(self, resource: Dict[str, Any]) -> float:
        """
        计算资源质量评分

        Args:
            resource: 资源字典

        Returns:
            质量评分 (1.0-5.0)
        """
        score = 3.0  # 基础分

        # GitHub仓库特殊评分
        if resource.get('source') == 'GitHub':
            stars = resource.get('stars', 0)
            if stars >= 1000:
                score += 2.0
            elif stars >= 100:
                score += 1.5
            elif stars >= 10:
                score += 0.5

            # 最近更新加分
            updated_at = resource.get('updated_at', '')
            if updated_at:
                try:
                    update_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    days_ago = (datetime.now(update_date.tzinfo) - update_date).days
                    if days_ago < 30:
                        score += 0.5
                    elif days_ago < 180:
                        score += 0.3
                except:
                    pass

        # 官方网站加分
        url = resource.get('url', '').lower()
        official_sites = ['nvidia.com', 'cuda.com', 'github.com/nvidia',
                          'docs.nvidia.com', 'developer.nvidia.com']
        if any(site in url for site in official_sites):
            score += 1.0

        # 描述完整度加分
        description = resource.get('description', '')
        if len(description) > 100:
            score += 0.3
        if len(description) > 200:
            score += 0.2

        # 确保分数在1-5范围内
        return min(max(score, 1.0), 5.0)

    def generate_recommendation(self, resource: Dict[str, Any]) -> str:
        """
        生成推荐理由

        Args:
            resource: 资源字典

        Returns:
            推荐理由字符串
        """
        reasons = []

        # 基于类型的推荐
        resource_type = resource.get('type', '')
        if resource_type == 'book':
            reasons.append("系统学习的好材料")
        elif resource_type == 'course':
            reasons.append("结构化的学习路径")
        elif resource_type == 'code':
            reasons.append("包含实践代码示例")
        elif resource_type == 'documentation':
            reasons.append("官方权威参考")
        elif resource_type == 'blog':
            reasons.append("实战经验分享")

        # 基于评分的推荐
        score = resource.get('quality_score', 0)
        if score >= 4.5:
            reasons.append("高质量资源")
        elif score >= 4.0:
            reasons.append("优质资源")

        # 基于GitHub星标的推荐
        stars = resource.get('stars', 0)
        if stars >= 1000:
            reasons.append(f"社区广泛认可({stars}★)")
        elif stars >= 100:
            reasons.append(f"受欢迎项目({stars}★)")

        # 基于更新时间的推荐
        if resource.get('updated_recently'):
            reasons.append("持续更新维护")

        # 基于语言的推荐
        language = resource.get('language_detected', '')
        if language == 'zh':
            reasons.append("中文友好")
        elif language == 'mixed':
            reasons.append("中英双语")

        return "；".join(reasons) if reasons else "值得关注的资源"

    def parse_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        解析资源列表，添加类型、语言、评分等信息

        Args:
            resources: 原始资源列表

        Returns:
            解析后的资源列表
        """
        parsed_resources = []

        for resource in resources:
            # 添加解析信息
            resource['type'] = self.detect_resource_type(resource)
            resource['language_detected'] = self.detect_language(resource)
            resource['quality_score'] = self.calculate_quality_score(resource)

            # 检查是否最近更新
            updated_at = resource.get('updated_at', '')
            if updated_at:
                try:
                    update_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    days_ago = (datetime.now(update_date.tzinfo) - update_date).days
                    resource['updated_recently'] = days_ago < 90
                except:
                    resource['updated_recently'] = False
            else:
                resource['updated_recently'] = False

            # 生成推荐理由
            resource['recommendation'] = self.generate_recommendation(resource)

            # 添加收集时间
            resource['collected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            parsed_resources.append(resource)

        logger.info(f"成功解析 {len(parsed_resources)} 个资源")
        return parsed_resources

    def categorize_resources(self, resources: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        将资源按类型分类

        Args:
            resources: 资源列表

        Returns:
            分类后的资源字典
        """
        categorized = {
            'book': [],
            'course': [],
            'blog': [],
            'code': [],
            'documentation': [],
            'other': []
        }

        for resource in resources:
            resource_type = resource.get('type', 'other')
            if resource_type in categorized:
                categorized[resource_type].append(resource)
            else:
                categorized['other'].append(resource)

        # 打印分类统计
        for category, items in categorized.items():
            if items:
                logger.info(f"{category}: {len(items)} 个资源")

        return categorized

    def get_top_resources(self, resources: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        获取评分最高的资源

        Args:
            resources: 资源列表
            top_n: 返回数量

        Returns:
            Top N 资源列表
        """
        # 按质量评分排序
        sorted_resources = sorted(
            resources,
            key=lambda x: x.get('quality_score', 0),
            reverse=True
        )

        return sorted_resources[:top_n]


# 测试代码
if __name__ == "__main__":
    parser = ResourceParser()

    # 测试资源
    test_resource = {
        'title': 'CUDA Programming Guide',
        'url': 'https://docs.nvidia.com/cuda/',
        'description': 'Official CUDA programming documentation from NVIDIA',
        'source': 'DuckDuckGo'
    }

    # 解析单个资源
    test_resource['type'] = parser.detect_resource_type(test_resource)
    test_resource['language_detected'] = parser.detect_language(test_resource)
    test_resource['quality_score'] = parser.calculate_quality_score(test_resource)

    print(f"Type: {test_resource['type']}")
    print(f"Language: {test_resource['language_detected']}")
    print(f"Quality Score: {test_resource['quality_score']}")