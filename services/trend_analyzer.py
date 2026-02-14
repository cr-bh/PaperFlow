"""
趋势分析器 - 轻量级，从Arxiv API实时抓取
用于发表趋势分析，不依赖评分系统
"""
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict, Counter
from database.db_manager import db_manager


class TrendAnalyzer:
    """趋势分析器 - 轻量级，从Arxiv API实时抓取"""

    def __init__(self):
        self.base_categories = ['cs.AI', 'cs.LG', 'cs.CL', 'math.OC']
        self.excluded_categories = ['physics.', 'biology.', 'chem.', 'q-bio.']

    def fetch_papers_by_date_range(self, start_date: datetime, end_date: datetime,
                                   keywords: List[str], max_results: int = None) -> List[Dict]:
        """
        从Arxiv API抓取指定日期范围和关键词的论文（轻量级）

        Args:
            start_date: 开始日期
            end_date: 结束日期
            keywords: 关键词列表
            max_results: 最大结果数（None表示不限制，默认10000）

        Returns:
            论文列表，格式：
            [
                {
                    'arxiv_id': str,
                    'title': str,
                    'abstract': str,
                    'authors': [str],
                    'published_date': datetime,
                    'categories': [str]
                },
                ...
            ]

        注意：不包含 score, venue, institutions（轻量化）
        """
        # 如果没有指定max_results，使用较大的默认值
        if max_results is None:
            max_results = 10000  # 提高到10000

        # 构建查询
        query = self._build_query(keywords, start_date, end_date)

        print(f"📡 开始抓取 {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')} 的论文...")
        print(f"🔍 查询关键词: {', '.join(keywords[:5])}...")
        print(f"📊 最大结果数: {max_results}")

        papers = []
        try:
            # 使用 arxiv 库搜索
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            for result in search.results():
                # 过滤非相关领域
                if self._should_exclude(result.categories):
                    continue

                # 检查发布日期是否在范围内（因为submittedDate和published可能不一致）
                if result.published.date() < start_date.date() or result.published.date() > end_date.date():
                    continue

                # 提取作者名字（简化版）
                authors = [author.name for author in result.authors]

                paper_data = {
                    'arxiv_id': result.entry_id.split('/')[-1],
                    'title': result.title,
                    'abstract': result.summary,
                    'authors': authors,
                    'published_date': result.published,
                    'categories': result.categories
                }
                papers.append(paper_data)

            print(f"✓ 成功抓取 {len(papers)} 篇论文")
            return papers

        except Exception as e:
            print(f"❌ 抓取失败: {str(e)}")
            return []

    def get_daily_paper_count(self, papers: List[Dict]) -> List[Dict]:
        """
        统计每日论文数量

        Args:
            papers: 论文列表

        Returns:
            [{'date': datetime.date, 'count': int}, ...]
        """
        daily_counts = defaultdict(int)

        for paper in papers:
            date = paper['published_date'].date()
            daily_counts[date] += 1

        # 排序
        result = [{'date': date, 'count': count}
                 for date, count in sorted(daily_counts.items())]

        return result

    def get_weekly_aggregation(self, papers: List[Dict]) -> List[Dict]:
        """
        按周聚合统计

        Args:
            papers: 论文列表

        Returns:
            [{'week': str, 'count': int}, ...]
        """
        weekly_counts = defaultdict(int)

        for paper in papers:
            # 获取周数（ISO格式）
            date = paper['published_date']
            week = date.strftime('%Y-W%W')
            weekly_counts[week] += 1

        # 排序
        result = [{'week': week, 'count': count}
                 for week, count in sorted(weekly_counts.items())]

        return result

    def get_keyword_distribution(self, papers: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        统计各关键词的论文数量

        Args:
            papers: 论文列表
            keywords: 关键词列表

        Returns:
            [{'keyword': str, 'count': int}, ...]
        """
        keyword_counts = defaultdict(int)

        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract']).lower()

            for keyword in keywords:
                if keyword.lower() in text:
                    keyword_counts[keyword] += 1

        # 按数量排序
        result = [{'keyword': kw, 'count': count}
                 for kw, count in sorted(keyword_counts.items(),
                                        key=lambda x: x[1], reverse=True)]

        return result

    def get_keyword_category_ratio(self, papers: List[Dict],
                                   keywords_config: List) -> Dict[str, int]:
        """
        统计关键词类别（core/frontier）占比

        Args:
            papers: 论文列表
            keywords_config: 关键词配置列表（KeywordConfig对象）

        Returns:
            {'core': int, 'frontier': int}
        """
        # 按类别分组关键词
        core_keywords = [kw.keyword for kw in keywords_config if kw.category == 'core']
        frontier_keywords = [kw.keyword for kw in keywords_config if kw.category == 'frontier']

        category_counts = {'core': 0, 'frontier': 0}

        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract']).lower()

            # 检查是否匹配核心关键词
            if any(kw.lower() in text for kw in core_keywords):
                category_counts['core'] += 1

            # 检查是否匹配前沿关键词
            if any(kw.lower() in text for kw in frontier_keywords):
                category_counts['frontier'] += 1

        return category_counts

    def get_keyword_trend(self, papers: List[Dict], keyword: str) -> List[Dict]:
        """
        获取单个关键词的时间趋势

        Args:
            papers: 论文列表
            keyword: 关键词

        Returns:
            [{'date': datetime.date, 'count': int}, ...]
        """
        daily_counts = defaultdict(int)

        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract']).lower()

            if keyword.lower() in text:
                date = paper['published_date'].date()
                daily_counts[date] += 1

        # 排序
        result = [{'date': date, 'count': count}
                 for date, count in sorted(daily_counts.items())]

        return result

    def get_keyword_cooccurrence(self, papers: List[Dict], keywords: List[str]) -> Dict:
        """
        获取关键词共现矩阵

        Args:
            papers: 论文列表
            keywords: 关键词列表

        Returns:
            {
                'keywords': [str],
                'matrix': [[int]]  # matrix[i][j] = keyword i 和 j 共现的论文数
            }
        """
        n = len(keywords)
        matrix = [[0] * n for _ in range(n)]

        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract']).lower()

            # 找出该论文匹配的关键词
            matched_indices = []
            for i, keyword in enumerate(keywords):
                if keyword.lower() in text:
                    matched_indices.append(i)

            # 更新共现矩阵
            for i in matched_indices:
                for j in matched_indices:
                    matrix[i][j] += 1

        return {
            'keywords': keywords,
            'matrix': matrix
        }

    def get_keyword_time_heatmap(self, papers: List[Dict], keywords: List[str]) -> Dict:
        """
        获取关键词×时间热力图数据

        Args:
            papers: 论文列表
            keywords: 关键词列表

        Returns:
            {
                'keywords': [str],
                'dates': [datetime.date],
                'matrix': [[int]]  # matrix[i][j] = keyword i 在 date j 的论文数
            }
        """
        # 获取所有日期
        dates = sorted(set(paper['published_date'].date() for paper in papers))

        # 初始化矩阵
        n_keywords = len(keywords)
        n_dates = len(dates)
        matrix = [[0] * n_dates for _ in range(n_keywords)]

        # 统计
        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract']).lower()
            date = paper['published_date'].date()
            date_idx = dates.index(date)

            for kw_idx, keyword in enumerate(keywords):
                if keyword.lower() in text:
                    matrix[kw_idx][date_idx] += 1

        return {
            'keywords': keywords,
            'dates': dates,
            'matrix': matrix
        }

    def _build_query(self, keywords: List[str], start_date: datetime = None,
                    end_date: datetime = None) -> str:
        """构建 Arxiv 查询字符串"""
        # 类别查询
        cat_query = ' OR '.join([f'cat:{cat}' for cat in self.base_categories])

        # 关键词查询（标题或摘要）
        kw_queries = [f'(ti:"{kw}" OR abs:"{kw}")' for kw in keywords]
        kw_query = ' OR '.join(kw_queries)

        # 组合查询
        query = f'({cat_query}) AND ({kw_query})'

        # 添加日期范围（如果提供）
        if start_date and end_date:
            # Arxiv 使用 submittedDate 格式: YYYYMMDD
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            query += f' AND submittedDate:[{start_str}0000 TO {end_str}2359]'

        return query

    def _should_exclude(self, categories: List[str]) -> bool:
        """判断是否应该排除该论文"""
        for cat in categories:
            for excluded in self.excluded_categories:
                if cat.startswith(excluded):
                    # 检查是否有计算机科学类别
                    has_cs = any(c.startswith('cs.') or c.startswith('math.OC') for c in categories)
                    if not has_cs:
                        return True
        return False


# 创建全局实例
trend_analyzer = TrendAnalyzer()
