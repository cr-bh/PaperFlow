"""
测试论文导入功能
"""
from services.arxiv_downloader import arxiv_downloader
from services.paper_processor import paper_processor
from services.paper_importer import paper_importer
from database.db_manager import db_manager


def test_arxiv_downloader():
    """测试 Arxiv 下载器"""
    print("\n=== 测试 Arxiv 下载器 ===")

    # 测试 URL 生成
    test_id = "2401.12345"
    url = arxiv_downloader.get_pdf_url(test_id)
    print(f"✓ PDF URL: {url}")
    assert url == "https://arxiv.org/pdf/2401.12345.pdf"

    print("✓ Arxiv 下载器测试通过")


def test_paper_processor():
    """测试论文处理器"""
    print("\n=== 测试论文处理器 ===")

    # 检查方法是否存在
    assert hasattr(paper_processor, 'process_paper_from_file')
    print("✓ process_paper_from_file 方法存在")

    print("✓ 论文处理器测试通过")


def test_paper_importer():
    """测试论文导入器"""
    print("\n=== 测试论文导入器 ===")

    # 检查方法是否存在
    assert hasattr(paper_importer, 'import_arxiv_paper')
    print("✓ import_arxiv_paper 方法存在")

    print("✓ 论文导入器测试通过")


def test_db_methods():
    """测试数据库方法"""
    print("\n=== 测试数据库方法 ===")

    # 检查必要的方法是否存在
    assert hasattr(db_manager, 'get_arxiv_paper_by_id')
    print("✓ get_arxiv_paper_by_id 方法存在")

    assert hasattr(db_manager, 'get_arxiv_paper_by_arxiv_id')
    print("✓ get_arxiv_paper_by_arxiv_id 方法存在")

    assert hasattr(db_manager, 'update_arxiv_paper_import_status')
    print("✓ update_arxiv_paper_import_status 方法存在")

    print("✓ 数据库方法测试通过")


def main():
    """运行所有测试"""
    print("开始测试论文导入功能...")

    try:
        test_arxiv_downloader()
        test_paper_processor()
        test_paper_importer()
        test_db_methods()

        print("\n" + "="*50)
        print("✅ 所有测试通过！")
        print("="*50)
        print("\n下一步：")
        print("1. 运行 Streamlit 应用: streamlit run app.py")
        print("2. 进入 Auto-Scholar → 收藏列表")
        print("3. 点击任意论文的「📥 导入论文库」按钮")
        print("4. 观察导入进度和结果")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
