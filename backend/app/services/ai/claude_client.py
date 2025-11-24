"""Claude API Client"""

import anthropic
import json
from typing import Dict, Any, List
from app.core.config import settings


class ClaudeClient:
    """Claude API 客戶端"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.AI_MODEL
        self.max_tokens = settings.AI_MAX_TOKENS
        self.temperature = settings.AI_TEMPERATURE

    def generate_interpretation(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        """
        生成塔羅解讀

        Args:
            system_prompt: System Prompt
            user_prompt: User Prompt

        Returns:
            {
                "content": "AI 回應內容",
                "tokens": {
                    "input": 123,
                    "output": 456,
                    "total": 579
                }
            }
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            # 提取回應內容
            content = response.content[0].text

            # Token 使用統計
            tokens = {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens,
            }

            return {"content": content, "tokens": tokens}

        except Exception as e:
            raise Exception(f"Claude API 調用失敗: {str(e)}")

    def continue_conversation(
        self, system_prompt: str, messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        繼續對話（追問）

        Args:
            system_prompt: System Prompt
            messages: 對話歷史
                [
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."},
                    {"role": "user", "content": "..."}
                ]

        Returns:
            {
                "content": "AI 回應內容",
                "tokens": {...}
            }
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages,
            )

            content = response.content[0].text

            tokens = {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens,
            }

            return {"content": content, "tokens": tokens}

        except Exception as e:
            raise Exception(f"Claude API 調用失敗: {str(e)}")

    def parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        解析 JSON 回應

        Args:
            content: AI 回應內容

        Returns:
            解析後的 JSON 物件
        """
        try:
            # 嘗試直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 如果失敗，嘗試提取 JSON 部分
            # 尋找第一個 { 和最後一個 }
            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

            raise Exception("無法解析 AI 回應為 JSON 格式")
