"""
設定管理モジュール
==================
環境変数または .env ファイルから設定を読み込む。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込む
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """アプリケーション設定"""
    
    # Google Cloud認証ファイル
    GOOGLE_CREDENTIALS_PATH = os.getenv(
        'GOOGLE_CREDENTIALS_PATH',
        str(BASE_DIR / 'credentials' / 'service_account.json')
    )
    
    # スプレッドシート設定
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '')
    SHEET_NAME = os.getenv('SHEET_NAME', '経費データ')
    
    # レシート画像フォルダ
    RECEIPT_DIR = os.getenv(
        'RECEIPT_DIR',
        str(BASE_DIR / 'receipts')
    )
    
    def __init__(self):
        self._validate()
    
    def _validate(self):
        """必須設定が揃っているか確認"""
        if not self.SPREADSHEET_ID:
            raise ValueError(
                'SPREADSHEET_ID が設定されていません。.env ファイルを確認してください。'
            )
        
        if not Path(self.GOOGLE_CREDENTIALS_PATH).exists():
            raise FileNotFoundError(
                f'認証ファイルが見つかりません: {self.GOOGLE_CREDENTIALS_PATH}'
            )
        
        if not Path(self.RECEIPT_DIR).exists():
            Path(self.RECEIPT_DIR).mkdir(parents=True, exist_ok=True)
