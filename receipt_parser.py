"""
レシートパーサー
================
OCR結果のテキストから、日付・店名・金額・科目を抽出する。
"""

import re
from datetime import datetime
from typing import Dict, Optional


class ReceiptParser:
    """レシートテキストから構造化データを抽出するクラス"""
    
    # 科目分類のキーワード辞書
    # 用途: 店名や項目からカテゴリを自動判定
    CATEGORY_KEYWORDS = {
        '交通費': [
            'JR', '私鉄', '地下鉄', 'メトロ', '駅', 'タクシー', 'バス',
            'ETC', 'NEXCO', '高速', 'パーキング', '駐車', 'ガソリン',
            'ENEOS', '出光', 'SHELL', 'コスモ', 'スイカ', 'ICOCA', 'PASMO'
        ],
        '会議費': [
            'スターバックス', 'STARBUCKS', 'ドトール', 'タリーズ',
            'コメダ', 'エクセルシオール', '珈琲', 'カフェ', 'CAFE',
            'レストラン', '食堂', '居酒屋'
        ],
        '消耗品費': [
            'ヨドバシ', 'ビック', 'ビッグ', 'ヤマダ', 'ケーズ',
            'アスクル', 'カウネット', 'LOHACO', 'Amazon', 'アマゾン',
            '文具', 'オフィス', 'ダイソー', 'セリア', 'キャンドゥ',
            'ホームセンター', 'カインズ', 'コーナン',
            'セブンイレブン', 'ローソン', 'ファミリーマート', 'ファミマ',
            'ミニストップ', 'デイリーヤマザキ', 'セイコーマート'
        ],
        '新聞図書費': [
            '書店', 'ブックス', 'BOOKS', '蔦屋', 'TSUTAYA',
            '紀伊國屋', '丸善', 'ジュンク堂', '本屋'
        ],
        '通信費': [
            'NTT', 'ドコモ', 'au', 'KDDI', 'ソフトバンク', 'SoftBank',
            '楽天モバイル', '通信', 'Wi-Fi', '郵便', 'ヤマト', '佐川'
        ],
        '接待交際費': [
            'ホテル', 'HOTEL', '料亭', '寿司', '鮨', '焼肉', 'バー',
            'ラウンジ', 'クラブ'
        ],
    }
    
    DEFAULT_CATEGORY = '雑費'
    
    def parse(self, text: str) -> Dict:
        """
        OCRテキストから構造化データを抽出する。
        
        Args:
            text: OCRで抽出されたテキスト全文
        
        Returns:
            {
                'date': str,       # YYYY-MM-DD
                'store': str,      # 店名
                'amount': int,     # 金額(円)
                'category': str,   # 勘定科目
                'raw_text': str,   # 元テキスト(デバッグ用)
            }
        """
        return {
            'date': self._extract_date(text) or datetime.now().strftime('%Y-%m-%d'),
            'store': self._extract_store(text) or '不明',
            'amount': self._extract_amount(text) or 0,
            'category': self._classify_category(text),
            'raw_text': text,
        }
    
    def _extract_date(self, text: str) -> Optional[str]:
        """日付を抽出する。複数フォーマットに対応。"""
        patterns = [
            # 2025年01月15日, 2025/01/15, 2025-01-15
            (r'(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})', lambda m: (m.group(1), m.group(2), m.group(3))),
            # 25/01/15 (西暦下2桁)
            (r'(\d{2})/(\d{1,2})/(\d{1,2})', lambda m: (f'20{m.group(1)}', m.group(2), m.group(3))),
            # 令和7年1月15日
            (r'令和(\d{1,2})[年/](\d{1,2})[月/](\d{1,2})', 
             lambda m: (str(2018 + int(m.group(1))), m.group(2), m.group(3))),
        ]
        
        for pattern, converter in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    year, month, day = converter(match)
                    return f'{int(year):04d}-{int(month):02d}-{int(day):02d}'
                except (ValueError, AttributeError):
                    continue
        return None
    
    def _extract_store(self, text: str) -> Optional[str]:
        """店名を抽出する。通常は最初の行に入っている。"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 電話番号や日付の行はスキップして最初の意味のある行を店名と判定
        skip_patterns = [
            r'^\d',  # 数字で始まる
            r'^[\-\=]',  # 記号で始まる
            r'領収',
            r'レシート',
        ]
        
        for line in lines[:5]:  # 最初の5行から探す
            if any(re.match(p, line) for p in skip_patterns):
                continue
            if len(line) < 2:
                continue
            # 店名っぽい文字数の行を返す
            if 2 <= len(line) <= 30:
                return line
        
        return lines[0] if lines else None
    
    def _extract_amount(self, text: str) -> Optional[int]:
        """合計金額を抽出する。「合計」「計」などのキーワード近傍から優先的に。"""
        
        # 優先パターン: 「合計」「小計」「計」などの後の金額
        priority_patterns = [
            r'合\s*計\s*[¥\\]?\s*([\d,]+)',
            r'お支払[い]?\s*[合計]*\s*[¥\\]?\s*([\d,]+)',
            r'総\s*計\s*[¥\\]?\s*([\d,]+)',
            r'TOTAL\s*[¥\\]?\s*([\d,]+)',
            r'計\s*[¥\\]?\s*([\d,]+)',
        ]
        
        for pattern in priority_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = int(match.group(1).replace(',', ''))
                    if 10 <= amount <= 10_000_000:  # 妥当性チェック
                        return amount
                except ValueError:
                    continue
        
        # フォールバック: ¥マーク付きの金額のうち最大値を採用
        amounts = re.findall(r'[¥\\]\s*([\d,]+)', text)
        valid_amounts = []
        for a in amounts:
            try:
                num = int(a.replace(',', ''))
                if 10 <= num <= 10_000_000:
                    valid_amounts.append(num)
            except ValueError:
                continue
        
        return max(valid_amounts) if valid_amounts else None
    
    def _classify_category(self, text: str) -> str:
        """科目を自動分類する。キーワードマッチング方式。"""
        text_upper = text.upper()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    return category
        
        return self.DEFAULT_CATEGORY
