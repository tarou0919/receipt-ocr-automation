"""
ReceiptParser のユニットテスト
==============================
OCRを呼ばずにパース処理だけ動作確認する用。

実行方法:
    python test_parser.py
"""

from receipt_parser import ReceiptParser


def test_parser():
    parser = ReceiptParser()
    
    # テストケース: 典型的なコンビニレシート
    sample_1 = """
セブンイレブン 渋谷店
東京都渋谷区1-2-3
TEL: 03-1234-5678

2025年11月08日 14:23

おにぎり鮭           ¥150
お茶 500ml          ¥130
ボールペン          ¥176

小計                ¥456
合計                ¥456
現金                ¥500
お釣り              ¥44
"""
    
    # テストケース: カフェのレシート
    sample_2 = """
STARBUCKS COFFEE
新宿南口店

2025/11/09

カフェラテ Tall     ¥455
スコーン           ¥220

合計             ¥675
"""
    
    # テストケース: タクシー領収書
    sample_3 = """
領収書

東京無線タクシー
2025-11-10

料金    ¥2,340
合計    ¥2,340
"""
    
    test_cases = [
        ('コンビニ', sample_1, {'date': '2025-11-08', 'category': '消耗品費'}),
        ('カフェ', sample_2, {'date': '2025-11-09', 'category': '会議費'}),
        ('タクシー', sample_3, {'date': '2025-11-10', 'category': '交通費'}),
    ]
    
    print('=' * 60)
    print('  ReceiptParser テスト')
    print('=' * 60)
    
    for name, text, expected in test_cases:
        result = parser.parse(text)
        print(f'\n【{name}】')
        print(f'  日付: {result["date"]}')
        print(f'  店名: {result["store"]}')
        print(f'  金額: ¥{result["amount"]:,}')
        print(f'  科目: {result["category"]}')
        
        # 簡易アサーション
        for key, expected_val in expected.items():
            actual = result[key]
            status = '✓' if actual == expected_val else '✗'
            print(f'  [{status}] {key}: expected={expected_val}, actual={actual}')
    
    print('\n' + '=' * 60)


if __name__ == '__main__':
    test_parser()
