"""
OCRエンジン
===========
Google Cloud Vision APIを使ってレシート画像からテキストを抽出する。
"""

import io
from google.cloud import vision
from google.oauth2 import service_account


class OCREngine:
    """Google Cloud Vision APIでOCR処理を行うクラス"""
    
    def __init__(self, credentials_path: str):
        """
        Args:
            credentials_path: サービスアカウントのJSONキーファイルパス
        """
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        self.client = vision.ImageAnnotatorClient(credentials=credentials)
    
    def extract_text(self, image_path: str) -> str:
        """
        画像からテキストを抽出する。
        
        Args:
            image_path: 画像ファイルのパス
        
        Returns:
            抽出したテキスト全文(抽出失敗時は空文字)
        """
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # document_text_detection はレシートや文書向けに最適化されている
        response = self.client.document_text_detection(
            image=image,
            image_context={'language_hints': ['ja']}
        )
        
        if response.error.message:
            raise Exception(f'Vision API エラー: {response.error.message}')
        
        if response.full_text_annotation:
            return response.full_text_annotation.text
        return ''
