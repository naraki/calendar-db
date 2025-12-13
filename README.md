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

## フロントエンド
## バックエンド

### BE test
```
cd calendar-db/be
uv run pytest
```

# tutorial
https://developers.google.com/workspace/add-ons/quickstart/cats-quickstart?hl=ja#drive.gs
