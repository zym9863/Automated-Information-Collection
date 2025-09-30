"""
信息收集模块 - 负责从多个源搜索CUDA和HPC相关资源
"""
import time
import requests
from typing import List, Dict, Any
from ddgs import DDGS
from tqdm import tqdm
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceCollector:
    """资源收集器类"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化收集器

        Args:
            config: 配置字典
        """
        self.config = config or {}
        try:
            self.ddgs = DDGS()
            logger.info("DuckDuckGo 搜索引擎初始化成功")
        except Exception as e:
            logger.error(f"DuckDuckGo 搜索引擎初始化失败: {e}")
            self.ddgs = None
        self.collected_resources = []

    def search_duckduckgo(self, keywords: List[str], max_results: int = 50) -> List[Dict[str, Any]]:
        """
        使用DuckDuckGo搜索资源

        Args:
            keywords: 搜索关键词列表
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        results = []
        
        # 检查 DuckDuckGo 是否初始化成功
        if self.ddgs is None:
            logger.warning("DuckDuckGo 搜索引擎未初始化,跳过搜索")
            return results

        logger.info(f"开始 DuckDuckGo 搜索,关键词数量: {len(keywords)}, 每个关键词最多 {max_results} 条结果")
        
        for keyword in tqdm(keywords, desc="DuckDuckGo搜索"):
            try:
                logger.debug(f"搜索关键词: {keyword}")
                # 执行搜索
                search_results = list(self.ddgs.text(
                    query=keyword,
                    max_results=max_results
                ))
                
                logger.info(f"关键词 '{keyword}' 返回 {len(search_results)} 条结果")

                for result in search_results:
                    # ddgs 可能返回 'href' 或 'link' 作为 URL 字段
                    url = result.get('href') or result.get('link') or result.get('url', '')
                    
                    # 跳过没有 URL 的结果
                    if not url:
                        logger.warning(f"跳过无 URL 的结果: {result.get('title', 'Unknown')}")
                        logger.debug(f"结果详情: {result}")
                        continue
                    
                    resource = {
                        'title': result.get('title', ''),
                        'url': url,
                        'description': result.get('body', ''),
                        'source': 'DuckDuckGo',
                        'keyword': keyword
                    }
                    results.append(resource)

                # 避免请求过快
                time.sleep(1)

            except Exception as e:
                logger.error(f"DuckDuckGo搜索错误 ({keyword}): {e}", exc_info=True)
                continue

        logger.info(f"DuckDuckGo 搜索完成,共获得 {len(results)} 条结果")
        return results

    def search_github(self, keywords: List[str], min_stars: int = 10) -> List[Dict[str, Any]]:
        """
        使用GitHub API搜索代码仓库

        Args:
            keywords: 搜索关键词列表
            min_stars: 最小星标数

        Returns:
            搜索结果列表
        """
        results = []
        base_url = "https://api.github.com/search/repositories"

        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }

        for keyword in tqdm(keywords, desc="GitHub搜索"):
            try:
                # 构建查询
                query = f"{keyword} stars:>={min_stars}"
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 30
                }

                response = requests.get(base_url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()

                    for repo in data.get('items', []):
                        resource = {
                            'title': repo.get('full_name', ''),
                            'url': repo.get('html_url', ''),
                            'description': repo.get('description', ''),
                            'source': 'GitHub',
                            'stars': repo.get('stargazers_count', 0),
                            'language': repo.get('language', ''),
                            'updated_at': repo.get('updated_at', ''),
                            'keyword': keyword
                        }
                        results.append(resource)

                # 遵守GitHub API速率限制
                time.sleep(2)

            except Exception as e:
                logger.error(f"GitHub搜索错误 ({keyword}): {e}")
                continue

        return results

    def collect_all(self, keywords_zh: List[str] = None,
                    keywords_en: List[str] = None) -> List[Dict[str, Any]]:
        """
        从所有源收集资源

        Args:
            keywords_zh: 中文关键词列表
            keywords_en: 英文关键词列表

        Returns:
            所有收集到的资源
        """
        all_resources = []

        # 默认关键词
        if not keywords_zh:
            keywords_zh = [
                "CUDA编程教程",
                "GPU并行计算",
                "高性能计算HPC",
                "CUDA优化技巧"
            ]

        if not keywords_en:
            keywords_en = [
                "CUDA programming tutorial",
                "GPU parallel computing",
                "HPC high performance computing",
                "CUDA optimization guide"
            ]

        # 从配置读取源设置
        sources_config = self.config.get('sources', {})
        
        # DuckDuckGo搜索
        ddg_config = sources_config.get('duckduckgo', {})
        if ddg_config.get('enabled', True):
            logger.info("=" * 50)
            logger.info("开始 DuckDuckGo 搜索...")
            logger.info("=" * 50)
            ddg_max_results = ddg_config.get('max_results', 30)
            ddg_results = self.search_duckduckgo(
                keywords_zh + keywords_en,
                max_results=ddg_max_results
            )
            all_resources.extend(ddg_results)
            logger.info(f"DuckDuckGo 搜索完成: 获得 {len(ddg_results)} 个资源")
        else:
            logger.info("DuckDuckGo 搜索已禁用")

        # GitHub搜索
        github_config = sources_config.get('github', {})
        if github_config.get('enabled', True):
            logger.info("=" * 50)
            logger.info("开始 GitHub 搜索...")
            logger.info("=" * 50)
            github_min_stars = github_config.get('min_stars', 10)
            github_results = self.search_github(
                keywords_en,  # GitHub主要使用英文
                min_stars=github_min_stars
            )
            all_resources.extend(github_results)
            logger.info(f"GitHub 搜索完成: 获得 {len(github_results)} 个资源")
        else:
            logger.info("GitHub 搜索已禁用")

        # 保存结果
        self.collected_resources = all_resources
        logger.info("=" * 50)
        logger.info(f"总共收集到 {len(all_resources)} 个资源 (DuckDuckGo: {len(ddg_results) if ddg_config.get('enabled', True) else 0}, GitHub: {len(github_results) if github_config.get('enabled', True) else 0})")
        logger.info("=" * 50)

        return all_resources

    def get_unique_resources(self) -> List[Dict[str, Any]]:
        """
        去重并返回唯一资源

        Returns:
            去重后的资源列表
        """
        seen_urls = set()
        unique_resources = []

        for resource in self.collected_resources:
            url = resource.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(resource)

        logger.info(f"去重后剩余 {len(unique_resources)} 个资源")
        return unique_resources


# 测试代码
if __name__ == "__main__":
    collector = ResourceCollector()
    resources = collector.collect_all()
    unique = collector.get_unique_resources()

    # 打印前5个资源
    for i, resource in enumerate(unique[:5], 1):
        print(f"\n{i}. {resource['title']}")
        print(f"   URL: {resource['url']}")
        print(f"   Source: {resource['source']}")