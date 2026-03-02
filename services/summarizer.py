"""
论文总结服务
生成结构化的论文总结，支持缺失字段自动补全
"""
import logging
from services.llm_service import llm_service
from utils.prompts import SUMMARIZE_PAPER_PROMPT, format_prompt
from typing import Dict, List

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    'one_sentence_summary', 'problem_definition', 'existing_solutions',
    'limitations', 'contribution', 'methodology', 'results',
    'future_work_paper', 'future_work_insights',
]

COMPLETION_PROMPT = """你是一位专业的学术研究专家。以下是一篇论文的部分结构化总结，但缺少了一些部分。
请根据论文原文，**仅**补全下列缺失的部分。

**已有的总结（供参考上下文）：**
{existing_summary}

**需要补全的字段**：{missing_fields}

**字段要求说明**：
- methodology: **极其详细且清晰地**描述本文提出的方法和技术路线，包括整体框架、核心算法、技术细节、创新机制、实现要点
- results: 全面总结实验结果和性能表现，包括实验设置、数据集、对比baseline、消融实验、量化数据
- future_work_paper: 总结论文本身明确提出的未来研究方向
- future_work_insights: 基于论文内容提出个人见解和改进建议
- one_sentence_summary: 用1-2句话精炼概括论文核心工作
- problem_definition: 清晰描述本文要解决的具体问题
- existing_solutions: 全面总结相关工作和现有解决方案
- limitations: 深入分析现有方案的不足之处
- contribution: 阐述本文的主要贡献和创新点

**格式要求**：
- 使用中文描述，关键术语保留英文
- 使用 Markdown 格式增强可读性（粗体、列表等）
- 子标题使用 ##### (五级标题)

**输出格式（仅输出有效的 JSON，不要有其他文本）：**
仅包含缺失字段的 JSON 对象，例如：
{{
  "{example_field}": "该字段的详细内容..."
}}

论文全文：
{paper_text}

记住：仅输出有效的 JSON，只包含需要补全的字段。"""


class Summarizer:
    """论文总结器，支持缺失字段自动补全"""

    def __init__(self):
        self.llm = llm_service

    def summarize_paper(self, paper_text: str) -> Dict:
        """
        生成论文的结构化总结

        Args:
            paper_text: 论文全文文本

        Returns:
            结构化总结的 JSON 对象
        """
        if len(paper_text) > 30000:
            paper_text = paper_text[:30000] + "\n\n[文本已截断...]"

        prompt = format_prompt(SUMMARIZE_PAPER_PROMPT, paper_text=paper_text)
        summary = self.llm.generate_json(prompt, temperature=0.3, max_tokens=16384)

        summary_struct = summary.get('summary_struct', {})
        missing = self._find_missing_fields(summary_struct)

        if missing:
            logger.warning(f"首次总结缺少 {len(missing)} 个字段: {missing}，正在补全...")
            completed = self._complete_missing_fields(
                paper_text, summary_struct, missing
            )
            if completed:
                summary_struct.update(completed)
                summary['summary_struct'] = summary_struct
                still_missing = self._find_missing_fields(summary_struct)
                if still_missing:
                    logger.warning(f"补全后仍缺少: {still_missing}")
                else:
                    logger.info("所有字段补全成功")

        return summary

    def _find_missing_fields(self, summary_struct: Dict) -> List[str]:
        return [f for f in REQUIRED_FIELDS
                if not summary_struct.get(f)]

    def _complete_missing_fields(
        self, paper_text: str, existing: Dict, missing: List[str]
    ) -> Dict:
        existing_text = "\n".join(
            f"- {k}: {str(v)[:200]}..." if len(str(v)) > 200 else f"- {k}: {v}"
            for k, v in existing.items() if v
        )
        prompt = COMPLETION_PROMPT.format(
            existing_summary=existing_text,
            missing_fields=", ".join(missing),
            example_field=missing[0],
            paper_text=paper_text,
        )
        try:
            return self.llm.generate_json(prompt, temperature=0.3, max_tokens=16384)
        except Exception as e:
            logger.error(f"补全缺失字段失败: {e}")
            return {}


summarizer = Summarizer()
