"""
PDF 解析服务
使用 PyMuPDF 提取 PDF 内容
"""
import fitz  # PyMuPDF
import re
import logging
from typing import Dict, List, Set
from pathlib import Path
import config

logger = logging.getLogger(__name__)

FIGURE_PATTERN = re.compile(r'(Figure|Fig\.?)\s*\d+', re.IGNORECASE)


class PDFParser:
    """PDF 解析器"""

    def __init__(self):
        pass

    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        解析 PDF 文件

        Returns:
            包含文本、元数据和图片信息的字典
        """
        doc = fitz.open(pdf_path)

        full_text = self._extract_text(doc)
        metadata = self._extract_metadata(doc)
        images_info = self._extract_images_info(doc)
        page_count = len(doc)

        doc.close()

        return {
            "text": full_text,
            "metadata": metadata,
            "images": images_info,
            "page_count": page_count
        }

    def _extract_text(self, doc: fitz.Document) -> str:
        """提取 PDF 全文文本"""
        text_parts = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            text_parts.append(f"[Page {page_num}]\n{text}")

        return "\n\n".join(text_parts)

    def _extract_metadata(self, doc: fitz.Document) -> Dict:
        """提取 PDF 元数据"""
        metadata = doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", "")
        }

    def _extract_images_info(self, doc: fitz.Document) -> List[Dict]:
        """提取图片信息（不保存图片，只记录位置和 Caption）"""
        images_info = []

        for page_num, page in enumerate(doc, start=1):
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                caption = self._find_image_caption(page, img_index)

                images_info.append({
                    "page": page_num,
                    "index": img_index,
                    "caption": caption,
                    "xref": img[0]
                })

        return images_info

    def _find_image_caption(self, page: fitz.Page, img_index: int) -> str:
        """查找页面中的 Figure/Fig. 文本作为 Caption"""
        text = page.get_text()
        lines = text.split('\n')

        for line in lines:
            if FIGURE_PATTERN.search(line):
                return line.strip()

        return ""

    def _find_figure_pages(self, doc: fitz.Document) -> Dict[int, List[str]]:
        """扫描所有页面，返回包含 Figure 引用的页码及其 Caption 列表"""
        figure_pages = {}
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            captions = []
            for line in text.split('\n'):
                if FIGURE_PATTERN.search(line):
                    captions.append(line.strip())
            if captions:
                figure_pages[page_num] = captions
        return figure_pages

    def extract_images_to_disk(self, pdf_path: str, paper_id: int) -> List[Dict]:
        """
        提取图片并保存到磁盘
        主方法：光栅图提取 + 矢量图页面渲染补全
        """
        doc = fitz.open(pdf_path)
        saved_images = []

        image_dir = Path(config.IMAGES_DIR) / str(paper_id)
        image_dir.mkdir(parents=True, exist_ok=True)

        MIN_WIDTH = 200
        MIN_HEIGHT = 150
        MIN_SIZE_KB = 10
        MIN_ASPECT_RATIO = 0.3
        MAX_ASPECT_RATIO = 5.0

        pages_with_raster = set()

        # ===== 阶段 1：提取嵌入式光栅图（原有逻辑） =====
        for page_num, page in enumerate(doc, start=1):
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                size_kb = len(image_bytes) / 1024

                aspect_ratio = width / height if height > 0 else 0

                if (width < MIN_WIDTH or
                    height < MIN_HEIGHT or
                    size_kb < MIN_SIZE_KB or
                    aspect_ratio < MIN_ASPECT_RATIO or
                    aspect_ratio > MAX_ASPECT_RATIO):
                    continue

                image_filename = f"page{page_num}_img{img_index}.{image_ext}"
                image_path = image_dir / image_filename

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                caption = self._find_image_caption(page, img_index)

                saved_images.append({
                    "page": page_num,
                    "path": str(image_path),
                    "caption": caption,
                    "width": width,
                    "height": height,
                    "size_kb": size_kb
                })
                pages_with_raster.add(page_num)

        # ===== 阶段 2：对有 Figure 引用但无光栅图的页面进行渲染 =====
        figure_pages = self._find_figure_pages(doc)
        pages_needing_render = set(figure_pages.keys()) - pages_with_raster

        if pages_needing_render:
            logger.info(
                f"发现 {len(pages_needing_render)} 个页面有 Figure 引用但无光栅图，"
                f"启用页面渲染: {sorted(pages_needing_render)}"
            )
            rendered = self._render_figure_pages(
                doc, pages_needing_render, figure_pages, image_dir
            )
            saved_images.extend(rendered)

        doc.close()
        return saved_images

    def _render_figure_pages(
        self,
        doc: fitz.Document,
        page_numbers: Set[int],
        figure_pages: Dict[int, List[str]],
        image_dir: Path,
    ) -> List[Dict]:
        """将指定页面渲染为高分辨率图片"""
        rendered_images = []
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)

        for page_num in sorted(page_numbers):
            page = doc[page_num - 1]
            pix = page.get_pixmap(matrix=mat, alpha=False)

            image_filename = f"page{page_num}_rendered.png"
            image_path = image_dir / image_filename
            pix.save(str(image_path))

            captions = figure_pages.get(page_num, [])
            caption = captions[0] if captions else ""

            rendered_images.append({
                "page": page_num,
                "path": str(image_path),
                "caption": caption,
                "width": pix.width,
                "height": pix.height,
                "size_kb": image_path.stat().st_size / 1024,
                "rendered": True,
            })
            logger.info(f"  渲染页面 {page_num}: {caption[:60]}")

        return rendered_images


pdf_parser = PDFParser()
