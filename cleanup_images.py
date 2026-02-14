"""
清理无用图片脚本
删除已导入论文中的无用图片（小图标、符号等）
"""
import os
from pathlib import Path
from PIL import Image
from database.db_manager import db_manager


def cleanup_small_images(min_width=200, min_height=150, min_size_kb=10, dry_run=True):
    """
    清理太小的图片

    Args:
        min_width: 最小宽度（像素）
        min_height: 最小高度（像素）
        min_size_kb: 最小文件大小（KB）
        dry_run: 是否为试运行（不实际删除）
    """
    print("开始扫描图片...")
    print(f"过滤条件: 宽度 >= {min_width}px, 高度 >= {min_height}px, 大小 >= {min_size_kb}KB")
    print(f"模式: {'试运行（不会实际删除）' if dry_run else '实际删除'}")
    print("-" * 60)

    # 获取所有论文
    papers = db_manager.get_all_papers()
    total_deleted = 0
    total_size_saved = 0

    for paper in papers:
        print(f"\n检查论文: {paper.title} (ID: {paper.id})")

        # 获取论文的所有图片
        images = db_manager.get_paper_images(paper.id)

        for img in images:
            image_path = img.image_path

            if not os.path.exists(image_path):
                print(f"  ⚠️  图片不存在: {image_path}")
                continue

            try:
                # 获取文件大小
                file_size_kb = os.path.getsize(image_path) / 1024

                # 获取图片尺寸
                with Image.open(image_path) as pil_img:
                    width, height = pil_img.size

                # 计算宽高比
                aspect_ratio = width / height if height > 0 else 0

                # 判断是否需要删除
                should_delete = (
                    width < min_width or
                    height < min_height or
                    file_size_kb < min_size_kb or
                    aspect_ratio < 0.3 or  # 过窄
                    aspect_ratio > 5.0     # 过宽
                )

                if should_delete:
                    print(f"  ❌ 删除: {os.path.basename(image_path)}")
                    print(f"     尺寸: {width}x{height}px, 大小: {file_size_kb:.1f}KB, 宽高比: {aspect_ratio:.2f}")
                    print(f"     Caption: {img.caption or '(无)'}")

                    if not dry_run:
                        # 从数据库删除记录
                        db_manager.delete_image(img.id)
                        # 删除文件
                        os.remove(image_path)

                    total_deleted += 1
                    total_size_saved += file_size_kb

            except Exception as e:
                print(f"  ⚠️  处理失败: {image_path}, 错误: {str(e)}")

    print("\n" + "=" * 60)
    print(f"扫描完成！")
    print(f"发现 {total_deleted} 张无用图片")
    print(f"可节省空间: {total_size_saved:.1f} KB ({total_size_saved/1024:.2f} MB)")

    if dry_run:
        print("\n这是试运行，没有实际删除任何文件。")
        print("如需实际删除，请运行: python cleanup_images.py --delete")


def cleanup_images_without_caption(dry_run=True):
    """
    清理没有 caption 的图片（可能是无用图片）

    Args:
        dry_run: 是否为试运行
    """
    print("\n开始扫描没有 caption 的图片...")
    print(f"模式: {'试运行（不会实际删除）' if dry_run else '实际删除'}")
    print("-" * 60)

    papers = db_manager.get_all_papers()
    total_deleted = 0

    for paper in papers:
        images = db_manager.get_paper_images(paper.id)

        for img in images:
            if not img.caption or img.caption.strip() == "":
                print(f"  ❌ 删除: {os.path.basename(img.image_path)}")
                print(f"     论文: {paper.title}")

                if not dry_run:
                    # 从数据库删除记录
                    db_manager.delete_image(img.id)
                    # 删除文件
                    if os.path.exists(img.image_path):
                        os.remove(img.image_path)

                total_deleted += 1

    print("\n" + "=" * 60)
    print(f"发现 {total_deleted} 张没有 caption 的图片")

    if dry_run:
        print("\n这是试运行，没有实际删除任何文件。")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="清理无用图片")
    parser.add_argument("--delete", action="store_true", help="实际删除（默认为试运行）")
    parser.add_argument("--min-width", type=int, default=200, help="最小宽度（像素）")
    parser.add_argument("--min-height", type=int, default=150, help="最小高度（像素）")
    parser.add_argument("--min-size", type=float, default=10.0, help="最小文件大小（KB）")
    parser.add_argument("--no-caption", action="store_true", help="删除没有 caption 的图片")

    args = parser.parse_args()

    dry_run = not args.delete

    if args.no_caption:
        cleanup_images_without_caption(dry_run=dry_run)
    else:
        cleanup_small_images(
            min_width=args.min_width,
            min_height=args.min_height,
            min_size_kb=args.min_size,
            dry_run=dry_run
        )


if __name__ == "__main__":
    main()
