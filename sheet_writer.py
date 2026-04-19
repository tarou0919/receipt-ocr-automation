"""
スプレッドシート書き込みモジュール
==================================
gspreadを使ってGoogle スプレッドシートに結果を書き込む。
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import Dict


class SheetWriter:
    """Google スプレッドシートへの書き込みを担当するクラス"""
    
    HEADER = ['処理日時', 'ファイル名', '日付', '店名', '金額', '科目', 'メモ']
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]
    
    def __init__(self, credentials_path: str, spreadsheet_id: str, sheet_name: str = 'Sheet1'):
        """
        Args:
            credentials_path: サービスアカウントJSONのパス
            spreadsheet_id: スプレッドシートのID (URLの /d/ と /edit の間の文字列)
            sheet_name: ワークシート名
        """
        credentials = Credentials.from_service_account_file(
            credentials_path, scopes=self.SCOPES
        )
        client = gspread.authorize(credentials)
        
        self.spreadsheet = client.open_by_key(spreadsheet_id)
        
        # ワークシートが存在しなければ作成
        try:
            self.worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            self.worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=1000, cols=10
            )
    
    def ensure_header(self):
        """ヘッダー行がなければ追加する"""
        first_row = self.worksheet.row_values(1)
        if first_row != self.HEADER:
            if not first_row:
                self.worksheet.append_row(self.HEADER)
            else:
                self.worksheet.update('A1:G1', [self.HEADER])
    
    def append_row(self, data: Dict):
        """1件分のデータを末尾に追加する"""
        row = [
            data.get('processed_at', ''),
            data.get('file_name', ''),
            data.get('date', ''),
            data.get('store', ''),
            data.get('amount', 0),
            data.get('category', ''),
            '',  # メモ欄(手動記入用)
        ]
        self.worksheet.append_row(row, value_input_option='USER_ENTERED')
