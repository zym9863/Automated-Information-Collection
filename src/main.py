"""
自动化信息收集系统 - 主程序
用于收集CUDA和HPC相关的高质量学习资源
"""
import os
import sys
import argparse
import yaml
import logging
from colorama import Fore, Style, init
from typing import Dict, Any, List

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collector import ResourceCollector
from parsers import ResourceParser
from storage import ResourceStorage

# 初始化colorama（Windows支持）
init(autoreset=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AutomatedInfoCollector:
    """自动化信息收集系统主类"""

    def __init__(self, config_path: str = None):
        """
        初始化收集系统

        Args:
            config_path: 配置文件路径
        """
        self.config = self.load_config(config_path)
        self.collector = ResourceCollector(self.config.get('search', {}))
        self.parser = ResourceParser()
        self.storage = ResourceStorage(self.config.get('output', {}).get('path', 'resources'))

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        if not config_path:
            config_path = os.path.join('config', 'config.yaml')

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    logger.info(f"加载配置文件: {config_path}")
                    return config
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")

        # 返回默认配置
        logger.info("使用默认配置")
        return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置

        Returns:
            默认配置字典
        """
        return {
            'search': {
                'keywords_zh': [
                    'CUDA编程教程',
                    'GPU并行计算',
                    '高性能计算HPC',
                    'CUDA优化技巧',
                    'NVIDIA GPU编程'
                ],
                'keywords_en': [
                    'CUDA programming tutorial',
                    'GPU parallel computing',
                    'HPC high performance computing',
                    'CUDA optimization guide',
                    'NVIDIA GPU development'
                ],
                'max_results': 30,
                'min_stars': 10
            },
            'output': {
                'path': 'resources',
                'excel_file': 'cuda_hpc_resources.xlsx',
                'csv_backup': True
            },
            'filters': {
                'min_quality_score': 3.0,
                'resource_types': ['book', 'course', 'blog', 'code', 'documentation']
            }
        }

    def print_banner(self):
        """打印系统横幅"""
        print(Fore.CYAN + "=" * 60)
        print(Fore.CYAN + "       自动化信息收集系统 - CUDA & HPC资源收集器")
        print(Fore.CYAN + "=" * 60)
        print()

    def print_statistics(self, resources: List[Dict[str, Any]]):
        """
        打印统计信息

        Args:
            resources: 资源列表
        """
        print(Fore.GREEN + "\n[统计] 收集统计:")
        print(Fore.GREEN + "-" * 40)
        print(f"  总资源数: {len(resources)}")

        # 按类型统计
        type_counts = {}
        for r in resources:
            t = r.get('type', 'other')
            type_counts[t] = type_counts.get(t, 0) + 1

        print(Fore.YELLOW + "\n  按类型分类:")
        for t, c in type_counts.items():
            print(f"    {t}: {c}")

        # 按语言统计
        lang_counts = {}
        for r in resources:
            l = r.get('language_detected', 'unknown')
            lang_counts[l] = lang_counts.get(l, 0) + 1

        print(Fore.YELLOW + "\n  按语言分类:")
        for l, c in lang_counts.items():
            print(f"    {l}: {c}")

        # 质量评分统计
        scores = [r.get('quality_score', 0) for r in resources]
        if scores:
            avg_score = sum(scores) / len(scores)
            print(Fore.YELLOW + f"\n  平均质量评分: {avg_score:.2f}")
            print(f"  最高评分: {max(scores):.1f}")
            print(f"  4分以上资源: {sum(1 for s in scores if s >= 4.0)}")

    def collect(self, keywords: List[str] = None):
        """
        执行收集任务

        Args:
            keywords: 额外的搜索关键词
        """
        print(Fore.CYAN + "[搜索] 开始收集资源...")

        # 获取关键词
        keywords_zh = self.config['search']['keywords_zh']
        keywords_en = self.config['search']['keywords_en']

        # 添加用户提供的关键词
        if keywords:
            keywords_en.extend(keywords)

        # 收集资源
        print(Fore.YELLOW + f"  搜索关键词: {len(keywords_zh)} 个中文 + {len(keywords_en)} 个英文")
        resources = self.collector.collect_all(keywords_zh, keywords_en)

        # 去重
        resources = self.collector.get_unique_resources()
        print(Fore.GREEN + f"[完成] 收集完成，共 {len(resources)} 个唯一资源")

        # 解析资源
        print(Fore.CYAN + "\n[解析] 解析资源信息...")
        resources = self.parser.parse_resources(resources)
        print(Fore.GREEN + "[完成] 解析完成")

        # 分类
        categorized = self.parser.categorize_resources(resources)

        # 过滤低质量资源
        min_score = self.config['filters']['min_quality_score']
        filtered = [r for r in resources if r.get('quality_score', 0) >= min_score]
        print(Fore.YELLOW + f"\n[过滤] 质量过滤: {len(filtered)}/{len(resources)} (>={min_score}分)")

        # 打印统计
        self.print_statistics(filtered)

        # 保存结果
        print(Fore.CYAN + "\n[保存] 保存结果...")

        # 保存Excel
        excel_file = self.config['output']['excel_file']
        excel_path = self.storage.save_to_excel(filtered, categorized, excel_file)
        print(Fore.GREEN + f"[Excel] 文件: {excel_path}")

        # 保存CSV备份
        if self.config['output'].get('csv_backup', True):
            csv_path = self.storage.save_to_csv(filtered, excel_file.replace('.xlsx', '.csv'))
            print(Fore.GREEN + f"[CSV] 备份: {csv_path}")

        # 显示Top资源
        print(Fore.CYAN + "\n[推荐] Top 5 高质量资源:")
        print(Fore.CYAN + "-" * 60)
        top_resources = self.parser.get_top_resources(filtered, 5)
        for i, r in enumerate(top_resources, 1):
            print(f"\n{Fore.YELLOW}{i}. {r['title']}")
            print(f"   {Fore.WHITE}URL: {r['url']}")
            print(f"   {Fore.GREEN}评分: {r['quality_score']:.1f} | 类型: {r['type']} | 语言: {r['language_detected']}")
            print(f"   {Fore.CYAN}推荐: {r['recommendation']}")

        print(Fore.GREEN + "\n[成功] 收集任务完成！")

    def update(self, existing_file: str):
        """
        增量更新资源

        Args:
            existing_file: 已存在的资源文件
        """
        print(Fore.CYAN + "[加载] 加载已有资源...")
        existing = self.storage.load_existing_resources(existing_file)
        print(f"  已有 {len(existing)} 个资源")

        # 收集新资源
        self.collect()

        # TODO: 实现增量更新逻辑
        print(Fore.YELLOW + "[警告] 增量更新功能开发中...")

    def show_stats(self):
        """显示当前资源统计"""
        excel_file = self.config['output']['excel_file']
        filepath = os.path.join(self.storage.output_dir, excel_file)

        if not os.path.exists(filepath):
            print(Fore.RED + f"[错误] 文件不存在: {filepath}")
            return

        resources = self.storage.load_existing_resources(excel_file)
        self.print_statistics(resources)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='自动化信息收集系统 - CUDA & HPC资源收集器'
    )

    parser.add_argument(
        'command',
        choices=['search', 'update', 'stats'],
        help='执行的命令: search(搜索新资源), update(增量更新), stats(显示统计)'
    )

    parser.add_argument(
        '--keywords',
        nargs='+',
        help='额外的搜索关键词'
    )

    parser.add_argument(
        '--config',
        help='配置文件路径'
    )

    parser.add_argument(
        '--file',
        help='用于update命令的已存在文件'
    )

    args = parser.parse_args()

    # 创建收集器
    collector = AutomatedInfoCollector(args.config)
    collector.print_banner()

    # 执行命令
    if args.command == 'search':
        collector.collect(args.keywords)
    elif args.command == 'update':
        if not args.file:
            print(Fore.RED + "[错误] update命令需要指定--file参数")
            sys.exit(1)
        collector.update(args.file)
    elif args.command == 'stats':
        collector.show_stats()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[中断] 用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序错误: {e}")
        print(Fore.RED + f"[错误] 程序错误: {e}")
        sys.exit(1)