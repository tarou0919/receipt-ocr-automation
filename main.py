"""
レシート自動データ化システム
==============================
レシート画像をOCRで読み取り、日付・店名・金額・科目を抽出して
Google スプレッドシートに自動転記します。

実行方法:
    python main.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

from receipt_parser import ReceiptParser
from ocr_engine import OCREngine
from sheet_writer import SheetWriter
from config import Config

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_receipts():
    """レシート画像を一括処理してスプレッドシートに書き込む"""
    
    config = Config()
    
    # 画像ファイル一覧を取得
    receipt_dir = Path(config.RECEIPT_DIR)
    image_files = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'):
        image_files.extend(receipt_dir.glob(ext))
    
    if not image_files:
        logger.warning(f"画像が見つかりません: {receipt_dir}")
        return
    
    logger.info(f"処理対象: {len(image_files)}件")
    
    # 各モジュールを初期化
    ocr = OCREngine(config.GOOGLE_CREDENTIALS_PATH)
    parser = ReceiptParser()
    writer = SheetWriter(
        config.GOOGLE_CREDENTIALS_PATH,
        config.SPREADSHEET_ID,
        config.SHEET_NAME
    )
    
    # ヘッダー行を準備
    writer.ensure_header()
    
    results = []
    errors = []
    
    for idx, image_path in enumerate(image_files, 1):
        logger.info(f"[{idx}/{len(image_files)}] 処理中: {image_path.name}")
        
        try:
            # OCRでテキスト抽出
            raw_text = ocr.extract_text(str(image_path))
            
            if not raw_text:
                logger.warning(f"  → テキスト抽出失敗: {image_path.name}")
                errors.append(image_path.name)
                continue
            
            # 構造化データに変換
            receipt_data = parser.parse(raw_text)
            receipt_data['file_name'] = image_path.name
            receipt_data['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # スプレッドシートに書き込み
            writer.append_row(receipt_data)
            
            results.append(receipt_data)
            logger.info(
                f"  → OK: {receipt_data['date']} | "
                f"{receipt_data['store']} | "
                f"¥{receipt_data['amount']:,} | "
                f"{receipt_data['category']}"
            )
            
        except Exception as e:
            logger.error(f"  → エラー: {image_path.name} - {e}")
            errors.append(image_path.name)
    
    # 実行サマリー
    logger.info("=" * 60)
    logger.info(f"処理完了: 成功 {len(results)}件 / 失敗 {len(errors)}件")
    if results:
        total = sum(r['amount'] for r in results)
        logger.info(f"合計金額: ¥{total:,}")
    if errors:
        logger.info(f"失敗ファイル: {', '.join(errors)}")
    logger.info("=" * 60)


if __name__ == '__main__':
    try:
        process_receipts()
    except KeyboardInterrupt:
        logger.info("処理を中断しました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"致命的エラー: {e}")
        sys.exit(1)
