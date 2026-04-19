# レシート自動データ化システム

紙のレシート画像をOCRで読み取り、日付・店名・金額・科目を自動で抽出して、Google スプレッドシートに転記するPythonスクリプト。

## 機能

- Google Cloud Vision API による高精度な日本語OCR
- 日付・店名・金額の自動抽出（複数フォーマット対応）
- キーワードマッチングによる科目の自動分類
- Google スプレッドシートへの自動追記
- 月次の科目別集計レポート生成（CSV出力）

## Before / After

| 項目 | Before | After |
|------|--------|-------|
| 作業時間 | 月4時間 | 月10分 |
| 入力ミス率 | 約5% | ほぼ0% |
| 月次集計 | 手動で1時間 | 自動で数秒 |

## ディレクトリ構成

```
receipt_ocr/
├── main.py              # メイン処理
├── ocr_engine.py        # OCRモジュール
├── receipt_parser.py    # テキスト解析モジュール
├── sheet_writer.py      # スプレッドシート書き込みモジュール
├── monthly_report.py    # 月次レポート生成
├── config.py            # 設定管理
├── requirements.txt     # 依存パッケージ
├── .env.example         # 環境変数テンプレート
├── credentials/         # 認証ファイル置き場
├── receipts/            # レシート画像置き場
└── output/              # レポート出力先
```

## セットアップ手順

### 1. Google Cloud の準備

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクトを作成（例: `receipt-ocr-project`）
3. 「APIとサービス」→「ライブラリ」で以下を有効化:
   - Cloud Vision API
   - Google Sheets API
   - Google Drive API
4. 「APIとサービス」→「認証情報」→「サービスアカウントを作成」
5. サービスアカウントのキーをJSON形式でダウンロード
6. ダウンロードしたJSONを `credentials/service_account.json` として配置

### 2. スプレッドシートの準備

1. Google ドライブで新規スプレッドシートを作成（名前は任意）
2. URLから ID を控える（`/d/` と `/edit` の間の文字列）
3. サービスアカウントのメールアドレス（`xxx@xxx.iam.gserviceaccount.com`）を
   スプレッドシートの「共有」で**編集者**として追加

### 3. Python環境のセットアップ

```bash
# 仮想環境を作成
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
# .env.example をコピーして .env を作成
cp .env.example .env
```

`.env` を開いて `SPREADSHEET_ID` を上の手順2で控えたIDに書き換える。

## 使い方

### レシートを一括処理

```bash
# receipts/ フォルダにレシート画像（jpg/png）を入れる

python main.py
```

実行ログの例:
```
2025-11-10 14:23:05 [INFO] 処理対象: 8件
2025-11-10 14:23:07 [INFO] [1/8] 処理中: receipt001.jpg
2025-11-10 14:23:09 [INFO]   → OK: 2025-11-08 | セブンイレブン | ¥456 | 消耗品費
2025-11-10 14:23:10 [INFO] [2/8] 処理中: receipt002.jpg
2025-11-10 14:23:12 [INFO]   → OK: 2025-11-09 | スターバックス | ¥620 | 会議費
...
2025-11-10 14:23:30 [INFO] 処理完了: 成功 8件 / 失敗 0件
2025-11-10 14:23:30 [INFO] 合計金額: ¥12,480
```

### 月次レポートを生成

```bash
# 当月
python monthly_report.py

# 指定月
python monthly_report.py 2025-10
```

出力例:
```
============================================================
  2025-11 月次経費レポート
============================================================
  件数: 32件
  合計: ¥48,560
------------------------------------------------------------
  科目           件数           金額     割合
------------------------------------------------------------
  交通費          12件  ¥    18,240   37.6%
  会議費           8件  ¥    12,400   25.5%
  消耗品費         7件  ¥     9,820   20.2%
  接待交際費       3件  ¥     6,500   13.4%
  雑費             2件  ¥     1,600    3.3%
============================================================
CSVレポート出力: output/report_2025-11.csv
```

## カスタマイズ

### 科目分類キーワードの追加

`receipt_parser.py` の `CATEGORY_KEYWORDS` 辞書にキーワードを追加する:

```python
CATEGORY_KEYWORDS = {
    '交通費': ['JR', '私鉄', ..., '追加したいキーワード'],
    ...
}
```

### 新しい科目を追加

同じ辞書に新規キーを追加するだけ:

```python
'研修費': ['セミナー', '講座', '研修', 'Udemy'],
```

## 費用の目安

- Google Cloud Vision API: 月1,000枚まで無料、以降 $1.5/1,000枚
- Google Sheets API: 無料
- 個人〜中小企業の経費処理であれば、ほぼ無料枠で運用可能

## ライセンス

MIT
