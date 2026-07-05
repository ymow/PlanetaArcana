"""塔羅牌種子資料"""

import json
from sqlalchemy.orm import Session
from app.models.card import Card
from app.services.card_slug import build_card_slug_from_mapping


def seed_tarot_cards(db: Session):
    """填入 78 張偉特塔羅牌資料"""

    # 檢查是否已有資料
    existing_count = db.query(Card).count()
    if existing_count > 0:
        print(f"資料庫已有 {existing_count} 張卡片，跳過初始化")
        return

    cards_data = get_tarot_cards_data()

    for card_data in cards_data:
        card = Card(**card_data)
        db.add(card)

    db.commit()
    print(f"已建立 {len(cards_data)} 張塔羅牌")


def get_tarot_cards_data():
    """取得塔羅牌資料"""

    cards = []

    # === 大阿爾克那（Major Arcana）22 張 ===

    major_arcana = [
        {
            "name": "愚者",
            "name_en": "The Fool",
            "type": "major",
            "number": 0,
            "upright_meaning": "新開始、純真、自發性、自由精神",
            "upright_keywords": json.dumps(
                ["新開始", "冒險", "純真", "自由", "潛力"], ensure_ascii=False
            ),
            "reversed_meaning": "魯莽、冒險過度、不負責任、愚蠢決定",
            "reversed_keywords": json.dumps(
                ["魯莽", "風險", "不成熟", "逃避"], ensure_ascii=False
            ),
            "symbolism": "站在懸崖邊的旅人，象徵勇敢踏入未知",
        },
        {
            "name": "魔術師",
            "name_en": "The Magician",
            "type": "major",
            "number": 1,
            "upright_meaning": "顯化、資源、力量、啟發的行動",
            "upright_keywords": json.dumps(
                ["顯化", "創造", "技能", "意志力", "掌控"], ensure_ascii=False
            ),
            "reversed_meaning": "操控、幻覺、未開發的天賦",
            "reversed_keywords": json.dumps(
                ["操控", "欺騙", "浪費天賦", "缺乏能量"], ensure_ascii=False
            ),
            "symbolism": "手持權杖的魔術師，桌上擺放四元素，象徵創造力",
        },
        {
            "name": "女祭司",
            "name_en": "The High Priestess",
            "type": "major",
            "number": 2,
            "upright_meaning": "直覺、神聖知識、潛意識、內在智慧",
            "upright_keywords": json.dumps(
                ["直覺", "神秘", "內在", "智慧", "靈性"], ensure_ascii=False
            ),
            "reversed_meaning": "隱藏的議題、忽視直覺、缺乏洞察力",
            "reversed_keywords": json.dumps(
                ["忽視直覺", "秘密", "混亂", "表面"], ensure_ascii=False
            ),
            "symbolism": "坐在黑白柱子之間的女祭司，象徵神秘與智慧",
        },
        {
            "name": "皇后",
            "name_en": "The Empress",
            "type": "major",
            "number": 3,
            "upright_meaning": "豐饒、女性力量、美麗、自然、富足",
            "upright_keywords": json.dumps(
                ["豐盛", "母性", "創造", "美麗", "自然"], ensure_ascii=False
            ),
            "reversed_meaning": "依賴、窒息、缺乏增長",
            "reversed_keywords": json.dumps(
                ["依賴", "空虛", "過度保護", "停滯"], ensure_ascii=False
            ),
            "symbolism": "坐在豐饒大地上的皇后，象徵生命力與創造",
        },
        {
            "name": "皇帝",
            "name_en": "The Emperor",
            "type": "major",
            "number": 4,
            "upright_meaning": "權威、建立、結構、父親形象",
            "upright_keywords": json.dumps(
                ["權威", "結構", "控制", "穩定", "父親"], ensure_ascii=False
            ),
            "reversed_meaning": "專制、過度控制、僵化、缺乏紀律",
            "reversed_keywords": json.dumps(
                ["專制", "僵化", "失控", "無力"], ensure_ascii=False
            ),
            "symbolism": "坐在寶座上的皇帝，象徵權威與秩序",
        },
        {
            "name": "教皇",
            "name_en": "The Hierophant",
            "type": "major",
            "number": 5,
            "upright_meaning": "精神智慧、宗教信仰、符合傳統、制度",
            "upright_keywords": json.dumps(
                ["傳統", "教導", "信仰", "道德", "規範"], ensure_ascii=False
            ),
            "reversed_meaning": "個人信念、自由、挑戰現狀",
            "reversed_keywords": json.dumps(
                ["反叛", "非傳統", "自由", "質疑"], ensure_ascii=False
            ),
            "symbolism": "宗教導師傳授知識，象徵傳統與教導",
        },
        {
            "name": "戀人",
            "name_en": "The Lovers",
            "type": "major",
            "number": 6,
            "upright_meaning": "愛、和諧、關係、價值觀一致、選擇",
            "upright_keywords": json.dumps(
                ["愛情", "和諧", "選擇", "結合", "吸引"], ensure_ascii=False
            ),
            "reversed_meaning": "自愛、不和諧、價值觀失衡、不忠",
            "reversed_keywords": json.dumps(
                ["失衡", "衝突", "錯誤選擇", "分離"], ensure_ascii=False
            ),
            "symbolism": "亞當夏娃在天使祝福下，象徵愛與結合",
        },
        {
            "name": "戰車",
            "name_en": "The Chariot",
            "type": "major",
            "number": 7,
            "upright_meaning": "控制、意志力、決心、行動、野心",
            "upright_keywords": json.dumps(
                ["勝利", "決心", "前進", "控制", "意志"], ensure_ascii=False
            ),
            "reversed_meaning": "自我紀律欠缺、方向不明、攻擊性",
            "reversed_keywords": json.dumps(
                ["失控", "缺乏方向", "侵略", "阻礙"], ensure_ascii=False
            ),
            "symbolism": "駕駛戰車的勝利者，象徵意志與前進",
        },
        {
            "name": "力量",
            "name_en": "Strength",
            "type": "major",
            "number": 8,
            "upright_meaning": "力量、勇氣、耐心、控制、同情心",
            "upright_keywords": json.dumps(
                ["勇氣", "耐心", "溫柔", "自信", "內在力量"], ensure_ascii=False
            ),
            "reversed_meaning": "內在力量、自我懷疑、低自尊、缺乏信心",
            "reversed_keywords": json.dumps(
                ["軟弱", "自我懷疑", "缺乏勇氣", "失控"], ensure_ascii=False
            ),
            "symbolism": "女子溫柔馴服獅子，象徵內在力量與勇氣",
        },
        {
            "name": "隱士",
            "name_en": "The Hermit",
            "type": "major",
            "number": 9,
            "upright_meaning": "靈魂探索、內省、獨處、內在指引",
            "upright_keywords": json.dumps(
                ["內省", "智慧", "獨處", "探索", "指引"], ensure_ascii=False
            ),
            "reversed_meaning": "孤立、孤獨、退縮、與世隔絕",
            "reversed_keywords": json.dumps(
                ["孤立", "孤獨", "逃避", "迷失"], ensure_ascii=False
            ),
            "symbolism": "持燈的智者在山頂，象徵智慧與內省",
        },
        {
            "name": "命運之輪",
            "name_en": "Wheel of Fortune",
            "type": "major",
            "number": 10,
            "upright_meaning": "好運、業力、生命週期、命運、轉折點",
            "upright_keywords": json.dumps(
                ["轉變", "命運", "機會", "週期", "進展"], ensure_ascii=False
            ),
            "reversed_meaning": "壞運、抗拒改變、打破週期",
            "reversed_keywords": json.dumps(
                ["壞運", "失控", "抗拒", "挫折"], ensure_ascii=False
            ),
            "symbolism": "旋轉的命運之輪，象徵變化與循環",
        },
        {
            "name": "正義",
            "name_en": "Justice",
            "type": "major",
            "number": 11,
            "upright_meaning": "正義、公平、真理、因果、法律",
            "upright_keywords": json.dumps(
                ["公正", "真理", "因果", "平衡", "法律"], ensure_ascii=False
            ),
            "reversed_meaning": "不公平、缺乏責任感、不誠實",
            "reversed_keywords": json.dumps(
                ["不公", "偏見", "逃避", "失衡"], ensure_ascii=False
            ),
            "symbolism": "手持天秤與寶劍的正義女神，象徵公平與真理",
        },
        {
            "name": "吊人",
            "name_en": "The Hanged Man",
            "type": "major",
            "number": 12,
            "upright_meaning": "暫停、放手、犧牲、新視角",
            "upright_keywords": json.dumps(
                ["暫停", "放下", "犧牲", "新視角", "等待"], ensure_ascii=False
            ),
            "reversed_meaning": "拖延、抗拒、停滯、錯過機會",
            "reversed_keywords": json.dumps(
                ["停滯", "抗拒", "錯失", "浪費"], ensure_ascii=False
            ),
            "symbolism": "倒吊的人帶著平靜，象徵犧牲與新視角",
        },
        {
            "name": "死神",
            "name_en": "Death",
            "type": "major",
            "number": 13,
            "upright_meaning": "結束、轉變、過渡、放手",
            "upright_keywords": json.dumps(
                ["結束", "轉變", "新生", "放手", "蛻變"], ensure_ascii=False
            ),
            "reversed_meaning": "抗拒改變、無法放手、停滯",
            "reversed_keywords": json.dumps(
                ["抗拒", "恐懼", "停滯", "無法前進"], ensure_ascii=False
            ),
            "symbolism": "騎馬的死神，象徵轉變與重生",
        },
        {
            "name": "節制",
            "name_en": "Temperance",
            "type": "major",
            "number": 14,
            "upright_meaning": "平衡、適度、耐心、目的",
            "upright_keywords": json.dumps(
                ["平衡", "和諧", "耐心", "適度", "療癒"], ensure_ascii=False
            ),
            "reversed_meaning": "不平衡、過度、缺乏長遠目標",
            "reversed_keywords": json.dumps(
                ["失衡", "過度", "不耐", "極端"], ensure_ascii=False
            ),
            "symbolism": "天使調和水火，象徵平衡與和諧",
        },
        {
            "name": "惡魔",
            "name_en": "The Devil",
            "type": "major",
            "number": 15,
            "upright_meaning": "束縛、上癮、物質主義、玩樂",
            "upright_keywords": json.dumps(
                ["束縛", "誘惑", "上癮", "物質", "慾望"], ensure_ascii=False
            ),
            "reversed_meaning": "釋放、自由、擺脫束縛",
            "reversed_keywords": json.dumps(
                ["解放", "覺醒", "掙脫", "自由"], ensure_ascii=False
            ),
            "symbolism": "被鎖鏈束縛的人們，象徵誘惑與束縛",
        },
        {
            "name": "高塔",
            "name_en": "The Tower",
            "type": "major",
            "number": 16,
            "upright_meaning": "突然改變、劇變、混亂、啟示、覺醒",
            "upright_keywords": json.dumps(
                ["劇變", "突破", "毀滅", "啟示", "混亂"], ensure_ascii=False
            ),
            "reversed_meaning": "個人轉變、恐懼改變、災難避免",
            "reversed_keywords": json.dumps(
                ["逃避", "延遲", "內在動盪", "恐懼"], ensure_ascii=False
            ),
            "symbolism": "被雷擊中的高塔，象徵突然的劇變",
        },
        {
            "name": "星星",
            "name_en": "The Star",
            "type": "major",
            "number": 17,
            "upright_meaning": "希望、信念、目的、更新、靈性",
            "upright_keywords": json.dumps(
                ["希望", "信念", "靈感", "平靜", "更新"], ensure_ascii=False
            ),
            "reversed_meaning": "缺乏信念、絕望、自我信任缺乏",
            "reversed_keywords": json.dumps(
                ["絕望", "失去信念", "悲觀", "迷失"], ensure_ascii=False
            ),
            "symbolism": "女子在星空下傾倒水瓶，象徵希望與更新",
        },
        {
            "name": "月亮",
            "name_en": "The Moon",
            "type": "major",
            "number": 18,
            "upright_meaning": "幻覺、恐懼、焦慮、潛意識、直覺",
            "upright_keywords": json.dumps(
                ["幻覺", "直覺", "夢境", "恐懼", "不確定"], ensure_ascii=False
            ),
            "reversed_meaning": "釋放恐懼、壓抑情緒、內在混亂",
            "reversed_keywords": json.dumps(
                ["困惑", "恐懼釋放", "澄清", "揭露"], ensure_ascii=False
            ),
            "symbolism": "月光下的小徑與狼犬，象徵潛意識與幻覺",
        },
        {
            "name": "太陽",
            "name_en": "The Sun",
            "type": "major",
            "number": 19,
            "upright_meaning": "快樂、成功、慶祝、正向能量",
            "upright_keywords": json.dumps(
                ["快樂", "成功", "活力", "正向", "光明"], ensure_ascii=False
            ),
            "reversed_meaning": "內在溫暖、過度樂觀、短暫快樂",
            "reversed_keywords": json.dumps(
                ["過度樂觀", "延遲", "悲觀", "缺乏熱情"], ensure_ascii=False
            ),
            "symbolism": "燦爛的太陽與騎馬的孩童，象徵喜悅與成功",
        },
        {
            "name": "審判",
            "name_en": "Judgement",
            "type": "major",
            "number": 20,
            "upright_meaning": "審判、重生、內在呼喚、赦免",
            "upright_keywords": json.dumps(
                ["覺醒", "更新", "呼喚", "赦免", "評估"], ensure_ascii=False
            ),
            "reversed_meaning": "自我懷疑、內在批評、忽視呼喚",
            "reversed_keywords": json.dumps(
                ["自我批評", "懷疑", "拒絕", "錯失"], ensure_ascii=False
            ),
            "symbolism": "天使吹響號角，死者復活，象徵覺醒與更新",
        },
        {
            "name": "世界",
            "name_en": "The World",
            "type": "major",
            "number": 21,
            "upright_meaning": "完成、成就、旅程結束、圓滿",
            "upright_keywords": json.dumps(
                ["完成", "成就", "圓滿", "整合", "成功"], ensure_ascii=False
            ),
            "reversed_meaning": "尋求完整、缺乏完成感、空虛",
            "reversed_keywords": json.dumps(
                ["未完成", "延遲", "缺乏", "停滯"], ensure_ascii=False
            ),
            "symbolism": "在桂冠圈中舞蹈的女子，象徵完成與圓滿",
        },
    ]

    cards.extend(major_arcana)

    # === 小阿爾克那（Minor Arcana）56 張 ===
    # 權杖（Wands）、聖杯（Cups）、寶劍（Swords）、錢幣（Pentacles）
    # 每個花色：Ace, 2-10, Page, Knight, Queen, King

    suits = [
        {
            "suit": "wands",
            "suit_name": "權杖",
            "element": "火",
            "theme": "行動、創造、熱情",
        },
        {
            "suit": "cups",
            "suit_name": "聖杯",
            "element": "水",
            "theme": "情感、關係、直覺",
        },
        {
            "suit": "swords",
            "suit_name": "寶劍",
            "element": "風",
            "theme": "思想、溝通、衝突",
        },
        {
            "suit": "pentacles",
            "suit_name": "錢幣",
            "element": "土",
            "theme": "物質、金錢、實際",
        },
    ]

    # 權杖（Wands）
    wands_cards = [
        {
            "rank": "ace",
            "number": 1,
            "name": "權杖王牌",
            "name_en": "Ace of Wands",
            "upright_meaning": "靈感、新機會、成長、潛力",
            "upright_keywords": json.dumps(
                ["靈感", "新開始", "創造", "潛力"], ensure_ascii=False
            ),
            "reversed_meaning": "缺乏方向、拖延、誤導的能量",
            "reversed_keywords": json.dumps(
                ["延遲", "缺乏方向", "挫折"], ensure_ascii=False
            ),
        },
        {
            "rank": "2",
            "number": 2,
            "name": "權杖二",
            "name_en": "Two of Wands",
            "upright_meaning": "未來規劃、進展、決策、發現",
            "upright_keywords": json.dumps(["計劃", "決策", "探索"], ensure_ascii=False),
            "reversed_meaning": "個人目標、內在一致、恐懼未知",
            "reversed_keywords": json.dumps(["猶豫", "恐懼", "缺乏計劃"], ensure_ascii=False),
        },
        {
            "rank": "3",
            "number": 3,
            "name": "權杖三",
            "name_en": "Three of Wands",
            "upright_meaning": "進展、擴張、遠見、海外機會",
            "upright_keywords": json.dumps(["擴張", "遠見", "進展"], ensure_ascii=False),
            "reversed_meaning": "玩得安全、缺乏遠見、意外延遲",
            "reversed_keywords": json.dumps(["阻礙", "延遲", "保守"], ensure_ascii=False),
        },
        {
            "rank": "4",
            "number": 4,
            "name": "權杖四",
            "name_en": "Four of Wands",
            "upright_meaning": "慶祝、和諧、婚禮、家庭、歸屬感",
            "upright_keywords": json.dumps(["慶祝", "和諧", "穩定"], ensure_ascii=False),
            "reversed_meaning": "個人慶祝、內在和諧、衝突",
            "reversed_keywords": json.dumps(["不和", "不穩定", "延遲"], ensure_ascii=False),
        },
        {
            "rank": "5",
            "number": 5,
            "name": "權杖五",
            "name_en": "Five of Wands",
            "upright_meaning": "衝突、競爭、緊張、多樣性",
            "upright_keywords": json.dumps(["競爭", "衝突", "挑戰"], ensure_ascii=False),
            "reversed_meaning": "內在衝突、避免衝突、緊張釋放",
            "reversed_keywords": json.dumps(["避免", "和解", "內在衝突"], ensure_ascii=False),
        },
        {
            "rank": "6",
            "number": 6,
            "name": "權杖六",
            "name_en": "Six of Wands",
            "upright_meaning": "成功、公眾認可、進展、自尊",
            "upright_keywords": json.dumps(["勝利", "認可", "成就"], ensure_ascii=False),
            "reversed_meaning": "私人成就、自我懷疑、缺乏認可",
            "reversed_keywords": json.dumps(["挫折", "傲慢", "缺乏認可"], ensure_ascii=False),
        },
        {
            "rank": "7",
            "number": 7,
            "name": "權杖七",
            "name_en": "Seven of Wands",
            "upright_meaning": "挑戰、競爭、保護自己、毅力",
            "upright_keywords": json.dumps(["防禦", "挑戰", "堅持"], ensure_ascii=False),
            "reversed_meaning": "疲憊、放棄、壓倒性挑戰",
            "reversed_keywords": json.dumps(["屈服", "疲憊", "放棄"], ensure_ascii=False),
        },
        {
            "rank": "8",
            "number": 8,
            "name": "權杖八",
            "name_en": "Eight of Wands",
            "upright_meaning": "快速行動、速度、進展、運動",
            "upright_keywords": json.dumps(["快速", "行動", "進展"], ensure_ascii=False),
            "reversed_meaning": "延遲、挫折、抗拒改變",
            "reversed_keywords": json.dumps(["延遲", "挫折", "停滯"], ensure_ascii=False),
        },
        {
            "rank": "9",
            "number": 9,
            "name": "權杖九",
            "name_en": "Nine of Wands",
            "upright_meaning": "韌性、勇氣、堅持、考驗信念",
            "upright_keywords": json.dumps(["堅持", "韌性", "防禦"], ensure_ascii=False),
            "reversed_meaning": "內在資源、掙扎、偏執、防禦過度",
            "reversed_keywords": json.dumps(["疲憊", "偏執", "放棄"], ensure_ascii=False),
        },
        {
            "rank": "10",
            "number": 10,
            "name": "權杖十",
            "name_en": "Ten of Wands",
            "upright_meaning": "負擔、額外責任、艱難、壓力",
            "upright_keywords": json.dumps(["負擔", "責任", "壓力"], ensure_ascii=False),
            "reversed_meaning": "放下負擔、授權、尋求幫助",
            "reversed_keywords": json.dumps(["釋放", "授權", "崩潰"], ensure_ascii=False),
        },
        {
            "rank": "page",
            "number": 11,
            "name": "權杖侍者",
            "name_en": "Page of Wands",
            "upright_meaning": "探索、興奮、自由、啟發",
            "upright_keywords": json.dumps(["探索", "熱情", "消息"], ensure_ascii=False),
            "reversed_meaning": "缺乏方向、拖延、延遲消息",
            "reversed_keywords": json.dumps(["不安", "缺乏方向", "壞消息"], ensure_ascii=False),
        },
        {
            "rank": "knight",
            "number": 12,
            "name": "權杖騎士",
            "name_en": "Knight of Wands",
            "upright_meaning": "能量、熱情、衝動、冒險、行動",
            "upright_keywords": json.dumps(["熱情", "行動", "冒險"], ensure_ascii=False),
            "reversed_meaning": "衝動、魯莽、挫折、爭論",
            "reversed_keywords": json.dumps(["魯莽", "衝動", "挫折"], ensure_ascii=False),
        },
        {
            "rank": "queen",
            "number": 13,
            "name": "權杖皇后",
            "name_en": "Queen of Wands",
            "upright_meaning": "勇氣、自信、獨立、社交蝴蝶、決心",
            "upright_keywords": json.dumps(["自信", "獨立", "熱情"], ensure_ascii=False),
            "reversed_meaning": "自我中心、嫉妒、缺乏自信",
            "reversed_keywords": json.dumps(["嫉妒", "不安", "自我"], ensure_ascii=False),
        },
        {
            "rank": "king",
            "number": 14,
            "name": "權杖國王",
            "name_en": "King of Wands",
            "upright_meaning": "自然領導、願景、企業家、榮譽",
            "upright_keywords": json.dumps(["領導", "願景", "企業"], ensure_ascii=False),
            "reversed_meaning": "專橫、無情、過度嚴厲",
            "reversed_keywords": json.dumps(["專橫", "無情", "衝動"], ensure_ascii=False),
        },
    ]

    for card_data in wands_cards:
        card_data.update({"type": "minor", "suit": "wands"})
        cards.append(card_data)

    # 聖杯（Cups）
    cups_cards = [
        {
            "rank": "ace",
            "number": 1,
            "name": "聖杯王牌",
            "name_en": "Ace of Cups",
            "upright_meaning": "愛、新關係、同情心、創造力",
            "upright_keywords": json.dumps(
                ["愛", "新感情", "直覺", "創造"], ensure_ascii=False
            ),
            "reversed_meaning": "自愛、直覺阻塞、情緒壓抑",
            "reversed_keywords": json.dumps(["壓抑", "情緒封閉", "失望"], ensure_ascii=False),
        },
        {
            "rank": "2",
            "number": 2,
            "name": "聖杯二",
            "name_en": "Two of Cups",
            "upright_meaning": "統一愛、夥伴關係、互相吸引",
            "upright_keywords": json.dumps(["愛情", "夥伴", "和諧"], ensure_ascii=False),
            "reversed_meaning": "自愛、分裂、失衡關係",
            "reversed_keywords": json.dumps(["分裂", "失衡", "緊張"], ensure_ascii=False),
        },
        {
            "rank": "3",
            "number": 3,
            "name": "聖杯三",
            "name_en": "Three of Cups",
            "upright_meaning": "慶祝、友誼、創造力、合作",
            "upright_keywords": json.dumps(["慶祝", "友誼", "團體"], ensure_ascii=False),
            "reversed_meaning": "獨立、獨處、過度放縱",
            "reversed_keywords": json.dumps(["過度", "八卦", "孤立"], ensure_ascii=False),
        },
        {
            "rank": "4",
            "number": 4,
            "name": "聖杯四",
            "name_en": "Four of Cups",
            "upright_meaning": "冥想、沉思、冷漠、重新評估",
            "upright_keywords": json.dumps(["冷漠", "沉思", "退縮"], ensure_ascii=False),
            "reversed_meaning": "撤退、重新排列優先順序、動力",
            "reversed_keywords": json.dumps(["覺醒", "動力", "新視角"], ensure_ascii=False),
        },
        {
            "rank": "5",
            "number": 5,
            "name": "聖杯五",
            "name_en": "Five of Cups",
            "upright_meaning": "遺憾、失敗、失望、悲觀",
            "upright_keywords": json.dumps(["失望", "悲傷", "遺憾"], ensure_ascii=False),
            "reversed_meaning": "個人挫折、自我寬恕、前進",
            "reversed_keywords": json.dumps(["接受", "前進", "寬恕"], ensure_ascii=False),
        },
        {
            "rank": "6",
            "number": 6,
            "name": "聖杯六",
            "name_en": "Six of Cups",
            "upright_meaning": "重遊過去、童年記憶、純真、快樂",
            "upright_keywords": json.dumps(["懷舊", "童年", "快樂"], ensure_ascii=False),
            "reversed_meaning": "活在過去、寬恕、缺乏獨立",
            "reversed_keywords": json.dumps(["困在過去", "不成熟", "前進"], ensure_ascii=False),
        },
        {
            "rank": "7",
            "number": 7,
            "name": "聖杯七",
            "name_en": "Seven of Cups",
            "upright_meaning": "機會、選擇、願景清單、幻覺",
            "upright_keywords": json.dumps(["選擇", "幻想", "機會"], ensure_ascii=False),
            "reversed_meaning": "一致、個人價值觀、錯覺散去",
            "reversed_keywords": json.dumps(["混亂", "分心", "現實"], ensure_ascii=False),
        },
        {
            "rank": "8",
            "number": 8,
            "name": "聖杯八",
            "name_en": "Eight of Cups",
            "upright_meaning": "失望、放棄、退縮、逃離",
            "upright_keywords": json.dumps(["放下", "離開", "尋找"], ensure_ascii=False),
            "reversed_meaning": "試圖逃避、恐懼改變、恐懼承諾",
            "reversed_keywords": json.dumps(["逃避", "恐懼", "停滯"], ensure_ascii=False),
        },
        {
            "rank": "9",
            "number": 9,
            "name": "聖杯九",
            "name_en": "Nine of Cups",
            "upright_meaning": "滿足、情緒穩定、奢侈、實現願望",
            "upright_keywords": json.dumps(["滿足", "願望", "快樂"], ensure_ascii=False),
            "reversed_meaning": "內在快樂、物質主義、不滿",
            "reversed_keywords": json.dumps(["貪婪", "不滿", "空虛"], ensure_ascii=False),
        },
        {
            "rank": "10",
            "number": 10,
            "name": "聖杯十",
            "name_en": "Ten of Cups",
            "upright_meaning": "神聖的愛、幸福的關係、和諧、一致",
            "upright_keywords": json.dumps(["幸福", "家庭", "和諧"], ensure_ascii=False),
            "reversed_meaning": "破裂的關係、不一致、需要一致",
            "reversed_keywords": json.dumps(["不和", "分離", "失望"], ensure_ascii=False),
        },
        {
            "rank": "page",
            "number": 11,
            "name": "聖杯侍者",
            "name_en": "Page of Cups",
            "upright_meaning": "創意機會、好奇的探索、可能性",
            "upright_keywords": json.dumps(["創意", "直覺", "消息"], ensure_ascii=False),
            "reversed_meaning": "新想法、情緒不成熟、創意阻塞",
            "reversed_keywords": json.dumps(
                ["不成熟", "情緒化", "壞消息"], ensure_ascii=False
            ),
        },
        {
            "rank": "knight",
            "number": 12,
            "name": "聖杯騎士",
            "name_en": "Knight of Cups",
            "upright_meaning": "浪漫、魅力的信使、想像力、美麗",
            "upright_keywords": json.dumps(["浪漫", "魅力", "理想"], ensure_ascii=False),
            "reversed_meaning": "不切實際、嫉妒、護慕者",
            "reversed_keywords": json.dumps(["情緒化", "幻想", "不實"], ensure_ascii=False),
        },
        {
            "rank": "queen",
            "number": 13,
            "name": "聖杯皇后",
            "name_en": "Queen of Cups",
            "upright_meaning": "同情心、冷靜、情感穩定、直覺",
            "upright_keywords": json.dumps(["同情", "直覺", "關懷"], ensure_ascii=False),
            "reversed_meaning": "情緒不安、過度依賴、烈士情結",
            "reversed_keywords": json.dumps(["情緒化", "依賴", "不安"], ensure_ascii=False),
        },
        {
            "rank": "king",
            "number": 14,
            "name": "聖杯國王",
            "name_en": "King of Cups",
            "upright_meaning": "情緒平衡、外交、同情心、冷靜",
            "upright_keywords": json.dumps(["平衡", "同情", "外交"], ensure_ascii=False),
            "reversed_meaning": "冷酷、情緒操控、不誠實",
            "reversed_keywords": json.dumps(["操控", "冷酷", "不穩"], ensure_ascii=False),
        },
    ]

    for card_data in cups_cards:
        card_data.update({"type": "minor", "suit": "cups"})
        cards.append(card_data)

    # 寶劍（Swords）
    swords_cards = [
        {
            "rank": "ace",
            "number": 1,
            "name": "寶劍王牌",
            "name_en": "Ace of Swords",
            "upright_meaning": "突破、清晰、敏銳心智",
            "upright_keywords": json.dumps(["清晰", "真理", "突破"], ensure_ascii=False),
            "reversed_meaning": "混亂、殘酷、濫用權力",
            "reversed_keywords": json.dumps(["混亂", "殘酷", "誤導"], ensure_ascii=False),
        },
        {
            "rank": "2",
            "number": 2,
            "name": "寶劍二",
            "name_en": "Two of Swords",
            "upright_meaning": "困難決策、權衡、僵局、避免真相",
            "upright_keywords": json.dumps(["僵局", "決策", "平衡"], ensure_ascii=False),
            "reversed_meaning": "混亂、信息過載、謊言揭穿",
            "reversed_keywords": json.dumps(["混亂", "過載", "揭露"], ensure_ascii=False),
        },
        {
            "rank": "3",
            "number": 3,
            "name": "寶劍三",
            "name_en": "Three of Swords",
            "upright_meaning": "心碎、情感痛苦、悲傷、悲痛、痛苦",
            "upright_keywords": json.dumps(["心碎", "悲傷", "痛苦"], ensure_ascii=False),
            "reversed_meaning": "消極自我對話、釋放痛苦、樂觀",
            "reversed_keywords": json.dumps(["療癒", "寬恕", "復原"], ensure_ascii=False),
        },
        {
            "rank": "4",
            "number": 4,
            "name": "寶劍四",
            "name_en": "Four of Swords",
            "upright_meaning": "休息、恢復、冥想、沉思",
            "upright_keywords": json.dumps(["休息", "恢復", "沉思"], ensure_ascii=False),
            "reversed_meaning": "疲憊、精疲力竭、壓力、倦怠",
            "reversed_keywords": json.dumps(["疲憊", "倦怠", "不安"], ensure_ascii=False),
        },
        {
            "rank": "5",
            "number": 5,
            "name": "寶劍五",
            "name_en": "Five of Swords",
            "upright_meaning": "衝突、分歧、競爭、失敗、輸贏",
            "upright_keywords": json.dumps(["衝突", "失敗", "爭執"], ensure_ascii=False),
            "reversed_meaning": "和解、化解敵意、寬恕",
            "reversed_keywords": json.dumps(["和解", "放下", "報復"], ensure_ascii=False),
        },
        {
            "rank": "6",
            "number": 6,
            "name": "寶劍六",
            "name_en": "Six of Swords",
            "upright_meaning": "過渡、改變、釋放負擔、移動",
            "upright_keywords": json.dumps(["過渡", "移動", "釋放"], ensure_ascii=False),
            "reversed_meaning": "個人過渡、抗拒改變、未解決問題",
            "reversed_keywords": json.dumps(["停滯", "抗拒", "困擾"], ensure_ascii=False),
        },
        {
            "rank": "7",
            "number": 7,
            "name": "寶劍七",
            "name_en": "Seven of Swords",
            "upright_meaning": "背叛、欺騙、狡猾、逃避",
            "upright_keywords": json.dumps(["欺騙", "策略", "逃避"], ensure_ascii=False),
            "reversed_meaning": "自欺、良心、坦白",
            "reversed_keywords": json.dumps(["自欺", "坦白", "後悔"], ensure_ascii=False),
        },
        {
            "rank": "8",
            "number": 8,
            "name": "寶劍八",
            "name_en": "Eight of Swords",
            "upright_meaning": "負面思想、自我設限的信念、囚禁、受害者心態",
            "upright_keywords": json.dumps(["束縛", "恐懼", "困境"], ensure_ascii=False),
            "reversed_meaning": "自我限制的信念、內在批評、釋放",
            "reversed_keywords": json.dumps(["解放", "自由", "新視角"], ensure_ascii=False),
        },
        {
            "rank": "9",
            "number": 9,
            "name": "寶劍九",
            "name_en": "Nine of Swords",
            "upright_meaning": "焦慮、擔憂、恐懼、抑鬱、噩夢",
            "upright_keywords": json.dumps(["焦慮", "擔憂", "恐懼"], ensure_ascii=False),
            "reversed_meaning": "內在動盪、深度焦慮、羞恥、自責",
            "reversed_keywords": json.dumps(["希望", "釋放", "療癒"], ensure_ascii=False),
        },
        {
            "rank": "10",
            "number": 10,
            "name": "寶劍十",
            "name_en": "Ten of Swords",
            "upright_meaning": "痛苦結束、觸底、受害者、放棄、屈服",
            "upright_keywords": json.dumps(["結束", "失敗", "背叛"], ensure_ascii=False),
            "reversed_meaning": "復原、重生、抗拒結束、恐懼失敗",
            "reversed_keywords": json.dumps(["復原", "重生", "轉變"], ensure_ascii=False),
        },
        {
            "rank": "page",
            "number": 11,
            "name": "寶劍侍者",
            "name_en": "Page of Swords",
            "upright_meaning": "新想法、好奇心、渴望、警覺",
            "upright_keywords": json.dumps(["好奇", "警覺", "消息"], ensure_ascii=False),
            "reversed_meaning": "散播謠言、缺乏計劃、說話輕率",
            "reversed_keywords": json.dumps(["八卦", "輕率", "謊言"], ensure_ascii=False),
        },
        {
            "rank": "knight",
            "number": 12,
            "name": "寶劍騎士",
            "name_en": "Knight of Swords",
            "upright_meaning": "雄心勃勃、行動導向、驅使行動、快速思維",
            "upright_keywords": json.dumps(["行動", "雄心", "直接"], ensure_ascii=False),
            "reversed_meaning": "不耐煩、魯莽、無方向",
            "reversed_keywords": json.dumps(["魯莽", "衝動", "無方向"], ensure_ascii=False),
        },
        {
            "rank": "queen",
            "number": 13,
            "name": "寶劍皇后",
            "name_en": "Queen of Swords",
            "upright_meaning": "獨立、公正思考、清晰界限、直接溝通",
            "upright_keywords": json.dumps(["獨立", "清晰", "直接"], ensure_ascii=False),
            "reversed_meaning": "冷酷、殘忍、苛刻、不寬容",
            "reversed_keywords": json.dumps(["冷酷", "苛刻", "惡意"], ensure_ascii=False),
        },
        {
            "rank": "king",
            "number": 14,
            "name": "寶劍國王",
            "name_en": "King of Swords",
            "upright_meaning": "心智清晰、智慧力量、真理、權威",
            "upright_keywords": json.dumps(["權威", "真理", "清晰"], ensure_ascii=False),
            "reversed_meaning": "安靜的權力、內在真理、不誠實、操控",
            "reversed_keywords": json.dumps(["操控", "殘酷", "濫用"], ensure_ascii=False),
        },
    ]

    for card_data in swords_cards:
        card_data.update({"type": "minor", "suit": "swords"})
        cards.append(card_data)

    # 錢幣（Pentacles）
    pentacles_cards = [
        {
            "rank": "ace",
            "number": 1,
            "name": "錢幣王牌",
            "name_en": "Ace of Pentacles",
            "upright_meaning": "新財務機會、繁榮、安全",
            "upright_keywords": json.dumps(
                ["機會", "繁榮", "新開始"], ensure_ascii=False
            ),
            "reversed_meaning": "錯失機會、缺乏計劃、投資不佳",
            "reversed_keywords": json.dumps(["錯失", "缺乏", "貪婪"], ensure_ascii=False),
        },
        {
            "rank": "2",
            "number": 2,
            "name": "錢幣二",
            "name_en": "Two of Pentacles",
            "upright_meaning": "多重優先事項、時間管理、優先排序、適應",
            "upright_keywords": json.dumps(["平衡", "靈活", "適應"], ensure_ascii=False),
            "reversed_meaning": "失去平衡、混亂、過度承諾",
            "reversed_keywords": json.dumps(["失衡", "混亂", "壓力"], ensure_ascii=False),
        },
        {
            "rank": "3",
            "number": 3,
            "name": "錢幣三",
            "name_en": "Three of Pentacles",
            "upright_meaning": "團隊合作、合作、學習、實施",
            "upright_keywords": json.dumps(["合作", "技能", "工作"], ensure_ascii=False),
            "reversed_meaning": "缺乏團隊合作、不和諧、工作不協調",
            "reversed_keywords": json.dumps(["不協調", "缺乏技能", "衝突"], ensure_ascii=False),
        },
        {
            "rank": "4",
            "number": 4,
            "name": "錢幣四",
            "name_en": "Four of Pentacles",
            "upright_meaning": "儲蓄金錢、安全、保守、匱乏、貪婪",
            "upright_keywords": json.dumps(["控制", "安全", "保守"], ensure_ascii=False),
            "reversed_meaning": "過度消費、貪婪、自我保護",
            "reversed_keywords": json.dumps(["貪婪", "物質", "揮霍"], ensure_ascii=False),
        },
        {
            "rank": "5",
            "number": 5,
            "name": "錢幣五",
            "name_en": "Five of Pentacles",
            "upright_meaning": "財務損失、貧窮、缺乏心態、孤立、擔憂",
            "upright_keywords": json.dumps(["困難", "貧窮", "孤立"], ensure_ascii=False),
            "reversed_meaning": "從損失中恢復、精神貧困",
            "reversed_keywords": json.dumps(["復原", "改善", "希望"], ensure_ascii=False),
        },
        {
            "rank": "6",
            "number": 6,
            "name": "錢幣六",
            "name_en": "Six of Pentacles",
            "upright_meaning": "給予和接受、慷慨、慈善",
            "upright_keywords": json.dumps(["慷慨", "給予", "分享"], ensure_ascii=False),
            "reversed_meaning": "自我關懷、無私、債務",
            "reversed_keywords": json.dumps(["利己", "債務", "不平等"], ensure_ascii=False),
        },
        {
            "rank": "7",
            "number": 7,
            "name": "錢幣七",
            "name_en": "Seven of Pentacles",
            "upright_meaning": "長期視野、可持續成果、毅力、投資",
            "upright_keywords": json.dumps(["投資", "努力", "耐心"], ensure_ascii=False),
            "reversed_meaning": "有限的成功、缺乏長期視野、焦慮",
            "reversed_keywords": json.dumps(["焦慮", "失望", "浪費"], ensure_ascii=False),
        },
        {
            "rank": "8",
            "number": 8,
            "name": "錢幣八",
            "name_en": "Eight of Pentacles",
            "upright_meaning": "學徒制、重複任務、精通、技能發展",
            "upright_keywords": json.dumps(["技能", "努力", "專注"], ensure_ascii=False),
            "reversed_meaning": "自我發展、完美主義、錯誤投資",
            "reversed_keywords": json.dumps(["完美主義", "缺乏", "平庸"], ensure_ascii=False),
        },
        {
            "rank": "9",
            "number": 9,
            "name": "錢幣九",
            "name_en": "Nine of Pentacles",
            "upright_meaning": "富足、奢華、自足、財務獨立",
            "upright_keywords": json.dumps(["獨立", "富足", "成功"], ensure_ascii=False),
            "reversed_meaning": "過度工作、利潤損失、財務挫折",
            "reversed_keywords": json.dumps(["過勞", "損失", "依賴"], ensure_ascii=False),
        },
        {
            "rank": "10",
            "number": 10,
            "name": "錢幣十",
            "name_en": "Ten of Pentacles",
            "upright_meaning": "財富、財務安全、家庭、長期成功",
            "upright_keywords": json.dumps(["財富", "家庭", "遺產"], ensure_ascii=False),
            "reversed_meaning": "財務失敗、孤獨、損失",
            "reversed_keywords": json.dumps(["失敗", "損失", "爭執"], ensure_ascii=False),
        },
        {
            "rank": "page",
            "number": 11,
            "name": "錢幣侍者",
            "name_en": "Page of Pentacles",
            "upright_meaning": "顯化、財務機會、技能發展",
            "upright_keywords": json.dumps(["機會", "學習", "顯化"], ensure_ascii=False),
            "reversed_meaning": "缺乏進展、拖延、學習障礙",
            "reversed_keywords": json.dumps(["拖延", "缺乏", "不切實際"], ensure_ascii=False),
        },
        {
            "rank": "knight",
            "number": 12,
            "name": "錢幣騎士",
            "name_en": "Knight of Pentacles",
            "upright_meaning": "努力、承諾、責任、有條不紊",
            "upright_keywords": json.dumps(["責任", "努力", "務實"], ensure_ascii=False),
            "reversed_meaning": "自我紀律、無聊、挫折、自我職業",
            "reversed_keywords": json.dumps(["懶散", "無聊", "停滯"], ensure_ascii=False),
        },
        {
            "rank": "queen",
            "number": 13,
            "name": "錢幣皇后",
            "name_en": "Queen of Pentacles",
            "upright_meaning": "務實、創意、工作與家庭、財務安全",
            "upright_keywords": json.dumps(["務實", "照顧", "富足"], ensure_ascii=False),
            "reversed_meaning": "工作與家庭失衡、疏忽自我、財務依賴",
            "reversed_keywords": json.dumps(["失衡", "自私", "不安"], ensure_ascii=False),
        },
        {
            "rank": "king",
            "number": 14,
            "name": "錢幣國王",
            "name_en": "King of Pentacles",
            "upright_meaning": "財富、商業、領導、安全、紀律、豐饒",
            "upright_keywords": json.dumps(["成功", "財富", "領導"], ensure_ascii=False),
            "reversed_meaning": "貪婪、縱容、虛榮、貧困心態",
            "reversed_keywords": json.dumps(["貪婪", "物質", "失敗"], ensure_ascii=False),
        },
    ]

    for card_data in pentacles_cards:
        card_data.update({"type": "minor", "suit": "pentacles"})
        cards.append(card_data)

    for card_data in cards:
        card_data["slug"] = build_card_slug_from_mapping(card_data)

    return cards
