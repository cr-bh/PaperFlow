"""
质量分析器 - 基于已评分论文（ArxivPaper表）
用于质量维度分析，依赖评分系统
"""
from typing import List, Dict, Optional
from collections import defaultdict
from database.db_manager import db_manager


class QualityAnalyzer:
    """质量分析器 - 基于已评分论文（ArxivPaper表）"""

    def __init__(self):
        pass

    def get_score_distribution(self, papers: List) -> Dict[str, int]:
        """
        获取分数分布（S/A/B/C级）

        Args:
            papers: ArxivPaper对象列表

        Returns:
            {'S级 (9-10分)': int, 'A级 (7-8分)': int, ...}
        """
        distribution = {
            "S级 (9-10分)": 0,
            "A级 (7-8分)": 0,
            "B级 (5-6分)": 0,
            "C级 (<5分)": 0
        }

        for paper in papers:
            if paper.score >= 9:
                distribution["S级 (9-10分)"] += 1
            elif paper.score >= 7:
                distribution["A级 (7-8分)"] += 1
            elif paper.score >= 5:
                distribution["B级 (5-6分)"] += 1
            else:
                distribution["C级 (<5分)"] += 1

        return distribution

    def get_score_statistics(self, papers: List) -> Dict[str, float]:
        """
        获取分数统计（平均分、中位数等）

        Args:
            papers: ArxivPaper对象列表

        Returns:
            {'avg': float, 'median': float, 'max': float, 'min': float}
        """
        if not papers:
            return {'avg': 0.0, 'median': 0.0, 'max': 0.0, 'min': 0.0}

        scores = [p.score for p in papers]
        scores_sorted = sorted(scores)

        return {
            'avg': sum(scores) / len(scores),
            'median': scores_sorted[len(scores) // 2],
            'max': max(scores),
            'min': min(scores)
        }

    def get_venue_distribution(self, papers: List, min_score: float = 0.0, top_n: int = 20) -> List[Dict]:
        """
        获取顶会顶刊分布和平均分

        Args:
            papers: ArxivPaper对象列表
            min_score: 最低分数筛选
            top_n: 返回前N个

        Returns:
            [{'venue': str, 'count': int, 'avg_score': float}, ...]
        """
        venue_stats = defaultdict(lambda: {'count': 0, 'scores': []})

        for paper in papers:
            if paper.score < min_score:
                continue

            if hasattr(paper, 'venue') and paper.venue:
                venue = paper.venue
                if hasattr(paper, 'venue_year') and paper.venue_year:
                    venue = f"{paper.venue} {paper.venue_year}"

                venue_stats[venue]['count'] += 1
                venue_stats[venue]['scores'].append(paper.score)

        # 计算平均分并排序
        result = []
        for venue, data in venue_stats.items():
            avg_score = sum(data['scores']) / len(data['scores'])
            result.append({
                'venue': venue,
                'count': data['count'],
                'avg_score': avg_score
            })

        # 按论文数量排序
        result.sort(key=lambda x: x['count'], reverse=True)
        return result[:top_n]

    def get_institution_distribution(self, papers: List, min_score: float = 0.0, top_n: int = 20) -> List[Dict]:
        """
        获取知名机构分布和平均分

        Args:
            papers: ArxivPaper对象列表
            min_score: 最低分数筛选
            top_n: 返回前N个

        Returns:
            [{'institution': str, 'count': int, 'avg_score': float}, ...]
        """
        institution_stats = defaultdict(lambda: {'count': 0, 'scores': []})

        for paper in papers:
            if paper.score < min_score:
                continue

            if hasattr(paper, 'institutions') and paper.institutions:
                for inst in paper.institutions:
                    institution_stats[inst]['count'] += 1
                    institution_stats[inst]['scores'].append(paper.score)

        # 计算平均分并排序
        result = []
        for inst, data in institution_stats.items():
            avg_score = sum(data['scores']) / len(data['scores'])
            result.append({
                'institution': inst,
                'count': data['count'],
                'avg_score': avg_score
            })

        # 按论文数量排序
        result.sort(key=lambda x: x['count'], reverse=True)
        return result[:top_n]

    def get_author_productivity(self, papers: List, top_n: int = 20) -> List[Dict]:
        """
        获取高产作者排行

        Args:
            papers: ArxivPaper对象列表
            top_n: 返回前N个

        Returns:
            [{'author': str, 'count': int, 'avg_score': float}, ...]
        """
        author_stats = defaultdict(lambda: {'count': 0, 'scores': []})

        for paper in papers:
            if paper.authors:
                for author in paper.authors:
                    # 处理不同的作者格式
                    if isinstance(author, dict):
                        author_name = author.get('name', '')
                    else:
                        author_name = str(author)

                    if author_name:
                        author_stats[author_name]['count'] += 1
                        author_stats[author_name]['scores'].append(paper.score)

        # 计算平均分并排序
        result = []
        for author, data in author_stats.items():
            avg_score = sum(data['scores']) / len(data['scores'])
            result.append({
                'author': author,
                'count': data['count'],
                'avg_score': avg_score
            })

        # 按论文数量排序
        result.sort(key=lambda x: x['count'], reverse=True)
        return result[:top_n]

    def get_venue_score_matrix(self, papers: List, top_venues: int = 10) -> Dict:
        """
        获取会议×分数交叉分析

        Args:
            papers: ArxivPaper对象列表
            top_venues: 分析前N个会议

        Returns:
            {
                'venues': [str],
                'score_levels': ['S级', 'A级', 'B级', 'C级'],
                'matrix': [[int]]  # matrix[i][j] = venue i 在 score_level j 的论文数
            }
        """
        # 获取前N个会议
        venue_dist = self.get_venue_distribution(papers, top_n=top_venues)
        venues = [v['venue'] for v in venue_dist]

        # 初始化矩阵
        score_levels = ['S级', 'A级', 'B级', 'C级']
        matrix = [[0] * len(score_levels) for _ in range(len(venues))]

        # 统计
        for paper in papers:
            if hasattr(paper, 'venue') and paper.venue:
                venue = paper.venue
                if hasattr(paper, 'venue_year') and paper.venue_year:
                    venue = f"{paper.venue} {paper.venue_year}"

                if venue in venues:
                    venue_idx = venues.index(venue)

                    # 确定分数等级
                    if paper.score >= 9:
                        level_idx = 0  # S级
                    elif paper.score >= 7:
                        level_idx = 1  # A级
                    elif paper.score >= 5:
                        level_idx = 2  # B级
                    else:
                        level_idx = 3  # C级

                    matrix[venue_idx][level_idx] += 1

        return {
            'venues': venues,
            'score_levels': score_levels,
            'matrix': matrix
        }

    def get_institution_score_matrix(self, papers: List, top_institutions: int = 10) -> Dict:
        """
        获取机构×分数交叉分析

        Args:
            papers: ArxivPaper对象列表
            top_institutions: 分析前N个机构

        Returns:
            {
                'institutions': [str],
                'score_levels': ['S级', 'A级', 'B级', 'C级'],
                'matrix': [[int]]
            }
        """
        # 获取前N个机构
        inst_dist = self.get_institution_distribution(papers, top_n=top_institutions)
        institutions = [i['institution'] for i in inst_dist]

        # 初始化矩阵
        score_levels = ['S级', 'A级', 'B级', 'C级']
        matrix = [[0] * len(score_levels) for _ in range(len(institutions))]

        # 统计
        for paper in papers:
            if hasattr(paper, 'institutions') and paper.institutions:
                for inst in paper.institutions:
                    if inst in institutions:
                        inst_idx = institutions.index(inst)

                        # 确定分数等级
                        if paper.score >= 9:
                            level_idx = 0  # S级
                        elif paper.score >= 7:
                            level_idx = 1  # A级
                        elif paper.score >= 5:
                            level_idx = 2  # B级
                        else:
                            level_idx = 3  # C级

                        matrix[inst_idx][level_idx] += 1

        return {
            'institutions': institutions,
            'score_levels': score_levels,
            'matrix': matrix
        }


# 创建全局实例
quality_analyzer = QualityAnalyzer()
