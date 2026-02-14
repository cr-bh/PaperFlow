"""
Arxiv PDF 下载服务
从 Arxiv 下载论文 PDF 文件
"""
import requests
from pathlib import Path
from typing import Optional
import time


class ArxivDownloader:
    """Arxiv PDF 下载器"""

    def __init__(self):
        self.base_url = "https://arxiv.org/pdf"
        self.max_retries = 3
        self.retry_delay = 2.0

    def download_pdf(self, arxiv_id: str, save_dir: str) -> Optional[str]:
        """
        下载 Arxiv 论文 PDF

        Args:
            arxiv_id: Arxiv ID（如 2401.12345 或 2401.12345v1）
            save_dir: 保存目录

        Returns:
            下载的 PDF 文件路径，失败返回 None
        """
        # 清理 arxiv_id（移除版本号）
        clean_id = arxiv_id.split('v')[0] if 'v' in arxiv_id else arxiv_id

        # 构建下载 URL
        pdf_url = f"{self.base_url}/{clean_id}.pdf"

        # 创建保存目录
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        # 生成文件路径
        file_path = save_path / f"{clean_id}.pdf"

        # 如果文件已存在，直接返回
        if file_path.exists():
            print(f"✓ PDF 文件已存在: {file_path}")
            return str(file_path)

        # 下载 PDF（带重试）
        for attempt in range(self.max_retries):
            try:
                print(f"📡 正在下载 PDF: {pdf_url} (尝试 {attempt + 1}/{self.max_retries})")

                # 发送请求
                response = requests.get(pdf_url, timeout=30, stream=True)
                response.raise_for_status()

                # 保存文件
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                print(f"✓ PDF 下载成功: {file_path}")
                return str(file_path)

            except requests.exceptions.RequestException as e:
                print(f"❌ 下载失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")

                if attempt < self.max_retries - 1:
                    print(f"⏳ 等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"❌ 下载失败，已达到最大重试次数")
                    return None

        return None

    def get_pdf_url(self, arxiv_id: str) -> str:
        """
        获取 Arxiv PDF 下载链接

        Args:
            arxiv_id: Arxiv ID

        Returns:
            PDF 下载链接
        """
        clean_id = arxiv_id.split('v')[0] if 'v' in arxiv_id else arxiv_id
        return f"{self.base_url}/{clean_id}.pdf"


# 创建全局实例
arxiv_downloader = ArxivDownloader()
