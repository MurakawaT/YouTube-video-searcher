# Youtube video searcher
## 概要
任意の YouTube 動画チャンネル内のコメントからトピックを分析し、ユーザに検索の補助を提供するwebアプリ

## セットアップ
- このリポジトリをクローン
- `python mySearchVideo/generate_secretkey.py > mySearchVideo/local_setting.py` を実行
- `scapp/management/commands/local_api_key.py`ファイルを作り<br>
`API_KEY = "YouTube Data api のシークレットキー"`　の一行を追加<br>
- 必要があれば`python manage.py makemigrations`、`python manage.py migrate`コマンドを実行
- `python manage.py runserver`を実行し、<br>
`http://127.0.0.1:8000/scapp/top/`にアクセス
- 解析待ち・解析中のチャンネル一覧に何か残っていれば以下の特殊コマンドを実行

## 特殊コマンド
- スクレイピング：<br>
`python manage.py scraping`で、解析待ち・解析中のチャンネル一覧にあるチャンネル名のスクレイピングを開始
- LDA処理:<br>
`python manage.py lda`で、解析待ち・解析中のチャンネル一覧にあるスクレイピング済みのチャンネル内コメントを解析