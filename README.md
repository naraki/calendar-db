# calendar-db
施設予約情報に基づいてGoogle Calendarに反映させるシステム

[Google Auth client](https://console.cloud.google.com/auth/clients?hl=ja&project=naraki-calendar)


## 環境変数
.env
- MYSQL_HOST=localhost
- MYSQL_DATABASE=kac_db
- MYSQL_USER=kac-api
- MYSQL_PASSWORD=<ユーザー用パスワード>
- MYSQL_ROOT_PASSWORD=<root用パスワード>

## 起動確認

DBテスト
```sh
docker exec -it mysql /bin/sh
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE
```

カレンダーテスト
```sh
python export_calendar.py --output my_events.csv --max-results 50
python gcal_sync_tool.py \
  --host $MYSQL_HOST \
  --user $MYSQL_USER \
  --password $MYSQL_PASSWORD \
  --db $MYSQL_DATABASE \
  --max-results 50
```

## フロントエンド / バックエンドの分離 ✅

フロントエンドは `fe` に、API（バックエンド）は `be` に分離しました。

- フロントエンド: `fe` を起動（デフォルト: http://localhost:3000）
- バックエンド(API): `be` を起動（デフォルト: http://localhost:3001）
  - 直接起動 (uvicorn):
    ```sh
    cd be
    chmod +x ./uv ./test || true  # 初回のみ実行
    ./uv       # DEV=1 ./uv で autoreload
    ```
  - Makefile から:
    ```sh
    cd be
    make run    # 本番起動
    make dev    # 開発 (autoreload)
    make test   # 単体テスト
    ```

バックエンドは **FastAPI** に移行しました（`be/main.py`）。`be` は MySQL に接続して API を提供します。

Docker Compose で起動する場合はそのまま `docker compose up --build` を実行してください。`fe` は静的ファイルを配信し、`be` が API を提供します。

フロントエンドは API を直接 `http://localhost:3001` に問い合わせるように設定されています。コンテナ環境で別ホスト名を使う場合は `fe/public/index.html` 内の `API_BASE` を適宜変更してください。

## BE test
```
cd calendar-db
uv run pytest be/tests/ -q
```

# tutorial
https://developers.google.com/workspace/add-ons/quickstart/cats-quickstart?hl=ja#drive.gs
