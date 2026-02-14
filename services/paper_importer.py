"""
论文导入服务
从 Auto-Scholar 导入论文到主论文库
"""
from pathlib import Path
from typing import Optional, Callable
from database.db_manager import db_manager
from services.arxiv_downloader import arxiv_downloader
from services.paper_processor import paper_processor
from config import PAPERS_DIR


class PaperImporter:
    """论文导入服务（从 Auto-Scholar 到主论文库）"""

    def import_arxiv_paper(
        self,
        arxiv_paper_id: int,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> dict:
        """
        导入 Arxiv 论文到主论文库

        Args:
            arxiv_paper_id: ArxivPaper 表的 ID
            progress_callback: 进度回调函数 callback(progress: int, message: str)

        Returns:
            {
                'success': bool,
                'paper': Paper 对象（成功时）,
                'message': str,
                'error': str（失败时）
            }
        """
        try:
            # 步骤 1: 获取 ArxivPaper 记录
            self._update_progress(progress_callback, 5, "📋 正在获取论文信息...")

            arxiv_paper = db_manager.get_arxiv_paper_by_id(arxiv_paper_id)
            if not arxiv_paper:
                return {
                    'success': False,
                    'error': f"未找到 ID 为 {arxiv_paper_id} 的 Arxiv 论文"
                }

            # 步骤 2: 检查是否已导入
            if arxiv_paper.is_imported:
                # 已导入，返回已导入的论文
                imported_paper = db_manager.get_paper_by_id(arxiv_paper.imported_paper_id)
                return {
                    'success': True,
                    'paper': imported_paper,
                    'message': '该论文已导入，无需重复导入',
                    'is_duplicate': True
                }

            # 步骤 3: 下载 PDF
            self._update_progress(progress_callback, 10, "📡 正在下载 PDF...")

            pdf_path = arxiv_downloader.download_pdf(
                arxiv_id=arxiv_paper.arxiv_id,
                save_dir=PAPERS_DIR
            )

            if not pdf_path:
                return {
                    'success': False,
                    'error': f"PDF 下载失败: {arxiv_paper.arxiv_id}"
                }

            # 步骤 4: 处理论文（调用通用处理器）
            # 创建进度转发函数（将 20-95% 的进度映射到处理器的 0-100%）
            def forward_progress(processor_progress: int, message: str):
                # 处理器进度 0-100 映射到总进度 20-95
                total_progress = 20 + int(processor_progress * 0.75)
                self._update_progress(progress_callback, total_progress, message)

            result = paper_processor.process_paper_from_file(
                pdf_path=pdf_path,
                progress_callback=forward_progress
            )

            if not result['success']:
                return {
                    'success': False,
                    'error': result.get('error', '论文处理失败')
                }

            paper = result['paper']

            # 步骤 5: 更新 ArxivPaper 状态
            self._update_progress(progress_callback, 98, "💾 正在更新导入状态...")

            db_manager.update_arxiv_paper_import_status(
                arxiv_paper_id=arxiv_paper_id,
                imported_paper_id=paper.id
            )

            # 完成
            self._update_progress(progress_callback, 100, "✅ 导入完成！")

            return {
                'success': True,
                'paper': paper,
                'message': '论文导入成功',
                'is_duplicate': False
            }

        except Exception as e:
            error_msg = f"导入失败: {str(e)}"
            self._update_progress(progress_callback, 0, f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

    def _update_progress(
        self,
        callback: Optional[Callable[[int, str], None]],
        progress: int,
        message: str
    ):
        """更新进度"""
        if callback:
            callback(progress, message)
        else:
            print(f"[{progress}%] {message}")


# 创建全局实例
paper_importer = PaperImporter()
