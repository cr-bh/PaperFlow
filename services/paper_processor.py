"""
通用论文处理器
提取论文处理的核心逻辑，供上传和导入功能复用
"""
from pathlib import Path
from typing import Optional, Callable
from database.db_manager import db_manager
from services.pdf_parser import pdf_parser
from services.summarizer import summarizer
from services.mindmap_generator import mindmap_generator
from services.tagger import tagger
from services.image_extractor import image_extractor
from services.rag_service import rag_service


class PaperProcessor:
    """论文处理器（通用）"""

    def process_paper_from_file(
        self,
        pdf_path: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> dict:
        """
        处理论文文件（通用函数）

        Args:
            pdf_path: PDF 文件路径
            progress_callback: 进度回调函数 callback(progress: int, message: str)

        Returns:
            {
                'success': bool,
                'paper': Paper 对象（成功时）,
                'error': str（失败时）
            }
        """
        try:
            # 步骤 1: 解析 PDF
            self._update_progress(progress_callback, 20, "🔍 正在解析 PDF 内容...")

            parsed_data = pdf_parser.parse_pdf(pdf_path)
            paper_text = parsed_data['text']

            # 步骤 2: 生成总结
            self._update_progress(progress_callback, 40, "🧠 正在生成结构化总结...")

            summary = summarizer.summarize_paper(paper_text)

            # 检查是否存在同名论文
            title = summary.get('title', Path(pdf_path).stem)
            existing_paper = db_manager.get_paper_by_title(title)

            if existing_paper:
                # 已存在同名论文，更新
                paper_id = existing_paper.id
                is_update = True
            else:
                paper_id = None
                is_update = False

            # 步骤 3: 生成思维导图
            self._update_progress(progress_callback, 55, "🗺️ 正在生成思维导图...")

            mindmap_code = mindmap_generator.generate_mindmap(summary)

            # 步骤 4: 生成标签
            self._update_progress(progress_callback, 70, "🏷️ 正在生成标签...")

            tags = tagger.generate_tags(summary)

            # 步骤 5: 保存到数据库
            self._update_progress(progress_callback, 80, "💾 正在保存到数据库...")

            if is_update:
                # 更新现有论文
                paper = db_manager.update_paper(
                    paper_id,
                    title=title,
                    authors=summary.get('authors', []),
                    file_path=pdf_path,
                    content_summary=summary,
                    mindmap_code=mindmap_code
                )
                # 删除旧的向量数据
                rag_service.delete_paper_vectors(paper_id)
            else:
                # 创建新论文
                paper = db_manager.create_paper(
                    title=title,
                    authors=summary.get('authors', []),
                    file_path=pdf_path,
                    content_summary=summary,
                    mindmap_code=mindmap_code
                )

            # 保存标签
            tagger.save_tags_to_db(paper.id, tags)

            # 步骤 6: 提取图片
            self._update_progress(progress_callback, 85, "🖼️ 正在提取关键图片...")

            image_extractor.extract_key_images(pdf_path, paper.id)

            # 步骤 7: 向量化（用于 RAG）
            self._update_progress(progress_callback, 95, "💬 正在向量化文本（用于对话问答）...")

            rag_service.add_paper_to_vector_db(paper.id, paper_text)

            # 更新向量化状态
            db_manager.update_paper(paper.id, embedding_status=True)

            # 完成
            self._update_progress(progress_callback, 100, "✅ 处理完成！")

            return {
                'success': True,
                'paper': paper,
                'is_update': is_update
            }

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
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
paper_processor = PaperProcessor()
