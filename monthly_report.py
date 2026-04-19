"""
月次レポート生成スクリプト
==========================
スプレッドシートのデータから月次の科目別集計レポートを生成する。

実行方法:
    python monthly_report.py              # 当月のレポート
    python monthly_report.py 2025-01      # 指定月のレポート
"""

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from config import Config


def generate_report(year_month: str = None):
    """指定月の科目別集計レポートを生成する"""
    
    config = Config()
    
    # 対象月
    target = year_month or datetime.now().strftime('%Y-%m')
    
    # スプレッドシート接続
    credentials = Credentials.from_service_account_file(
        config.GOOGLE_CREDENTIALS_PATH,
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
        ]
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(config.SPREADSHEET_ID).worksheet(config.SHEET_NAME)
    
    records = sheet.get_all_records()
    
    # 対象月のデータを抽出
    filtered = [r for r in records if str(r.get('日付', '')).startswith(target)]
    
    if not filtered:
        print(f'[{target}] 該当するデータがありません')
        return
    
    # 科目別集計
    category_totals = defaultdict(lambda: {'count': 0, 'amount': 0})
    for r in filtered:
        cat = r.get('科目', '雑費')
        try:
            amt = int(str(r.get('金額', 0)).replace(',', ''))
        except (ValueError, TypeError):
            amt = 0
        category_totals[cat]['count'] += 1
        category_totals[cat]['amount'] += amt
    
    # レポート出力
    total_count = len(filtered)
    total_amount = sum(c['amount'] for c in category_totals.values())
    
    print('=' * 60)
    print(f'  {target} 月次経費レポート')
    print('=' * 60)
    print(f'  件数: {total_count}件')
    print(f'  合計: ¥{total_amount:,}')
    print('-' * 60)
    print(f'  {"科目":<12} {"件数":>6} {"金額":>14} {"割合":>8}')
    print('-' * 60)
    
    for cat, data in sorted(category_totals.items(), key=lambda x: -x[1]['amount']):
        ratio = data['amount'] / total_amount * 100 if total_amount else 0
        print(f'  {cat:<12} {data["count"]:>6}件 ¥{data["amount"]:>12,} {ratio:>6.1f}%')
    
    print('=' * 60)
    
    # CSV出力
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f'report_{target}.csv'
    
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write('科目,件数,金額,割合\n')
        for cat, data in sorted(category_totals.items(), key=lambda x: -x[1]['amount']):
            ratio = data['amount'] / total_amount * 100 if total_amount else 0
            f.write(f'{cat},{data["count"]},{data["amount"]},{ratio:.1f}%\n')
        f.write(f'合計,{total_count},{total_amount},100.0%\n')
    
    print(f'CSVレポート出力: {output_path}')


if __name__ == '__main__':
    target_month = sys.argv[1] if len(sys.argv) > 1 else None
    generate_report(target_month)
