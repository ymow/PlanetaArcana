"""AI 解讀 Prompt 模板"""

# System Prompt - 定義 AI 角色與行為
SYSTEM_PROMPT = """你是一位專業的偉特塔羅解讀師,擁有深厚的塔羅知識與豐富的諮詢經驗。

你的解讀風格:
- 溫暖而不失專業
- 基於傳統牌義,但能結合現代生活情境
- 避免絕對化預言,強調自由意志與行動力
- 語言清晰易懂,不使用過度神秘化的詞彙

解讀原則:
1. 先理解問題的核心關切
2. 分析每張牌在牌陣位置中的意義
3. 綜合解讀牌與牌之間的關係
4. 提供具體可行的建議
5. 保持中立與尊重,避免價值判斷

正逆位處理:
- 正位:正面能量、流暢展現、積極面向
- 逆位:能量阻塞、內在化、需要調整

你使用繁體中文(台灣)回覆。"""


# 結構化輸出 Schema — 透過 output_config.format 保證 API 回傳合法 JSON
INTERPRETATION_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_summary": {
            "type": "string",
            "description": "整體解讀（200-500字）",
        },
        "card_interpretations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "position": {"type": "string"},
                    "card_name": {"type": "string"},
                    "interpretation": {"type": "string"},
                },
                "required": ["position", "card_name", "interpretation"],
                "additionalProperties": False,
            },
        },
        "advice": {"type": "string", "description": "行動建議"},
        "key_insights": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-5 條關鍵洞察",
        },
    },
    "required": ["overall_summary", "card_interpretations", "advice", "key_insights"],
    "additionalProperties": False,
}


# 牌陣位置說明
SPREAD_DESCRIPTIONS = {
    "past_present_future": {
        "name": "過去-現在-未來",
        "description": "三牌陣,揭示事件的時間脈絡",
        "positions": {
            "past": "影響問題的過去因素或背景",
            "present": "當前的狀態、挑戰或機會",
            "future": "可能的發展方向或結果趨勢",
        },
    }
}


# User Prompt Template
def build_interpretation_prompt(
    question: str, spread_type: str, cards_data: list
) -> str:
    """
    組裝 User Prompt

    Args:
        question: 用戶問題
        spread_type: 牌陣類型
        cards_data: 卡片資料列表
            [
                {
                    "position": "past",
                    "card_name": "權杖六",
                    "orientation": "正位",
                    "meaning": "...",
                    "keywords": ["勝利", "認可"]
                }
            ]

    Returns:
        完整的 User Prompt
    """
    spread_info = SPREAD_DESCRIPTIONS.get(spread_type, {})
    spread_name = spread_info.get("name", spread_type)
    positions = spread_info.get("positions", {})

    # 組裝卡片資訊
    cards_text = ""
    for card in cards_data:
        pos = card["position"]
        pos_desc = positions.get(pos, pos)
        keywords_str = "、".join(card.get("keywords", []))

        cards_text += f"""
{pos_desc}:{card['card_name']}({card['orientation']})
- 傳統牌義:{card['meaning']}
- 關鍵字:{keywords_str}
"""

    prompt = f"""請為以下塔羅占卜提供解讀:

【問題】
{question}

【牌陣】
{spread_name}

【抽到的牌】
{cards_text}

請提供:
1. 每張牌在其位置上的具體解讀
2. 三張牌之間的關聯與故事線
3. 針對問題的整體建議
4. 3-5 條關鍵洞察

請以 JSON 格式輸出,結構如下:
{{
  "overall_summary": "整體解讀(200-500字)",
  "card_interpretations": [
    {{
      "position": "past",
      "card_name": "權杖六(正位)",
      "interpretation": "具體解讀內容..."
    }},
    {{
      "position": "present",
      "card_name": "吊人(逆位)",
      "interpretation": "具體解讀內容..."
    }},
    {{
      "position": "future",
      "card_name": "錢幣皇后(正位)",
      "interpretation": "具體解讀內容..."
    }}
  ],
  "advice": "行動建議",
  "key_insights": [
    "洞察1",
    "洞察2",
    "洞察3"
  ]
}}

請確保輸出是有效的 JSON 格式。"""

    return prompt


# 追問對話的 System Prompt
FOLLOW_UP_SYSTEM_PROMPT = """你是一位專業的偉特塔羅解讀師,正在與提問者進行深入對話。

你已經為對方完成了一次塔羅占卜解讀,現在對方想要針對某些部分進一步了解。

請根據之前的解讀內容和對方的問題,提供更詳細、更具體的說明。

注意:
- 保持與先前解讀一致的觀點
- 避免自相矛盾
- 提供實際可行的建議
- 如果對方問到超出塔羅解讀範圍的問題,請委婉地引導回到牌面本身

使用繁體中文(台灣)回覆。"""
