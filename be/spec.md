# KACBE
以下のテーブルを扱うAPI
```sql
CREATE TABLE `reservation_data` (
    `organization_name` VARCHAR(255) NOT NULL COMMENT '団体名',
    `id` VARCHAR(10) NOT NULL COMMENT 'ID',
    `status` VARCHAR(10) NOT NULL COMMENT '~~予約の状況~~ (当選/落選)',
    `reservation_number` INT UNSIGNED NOT NULL COMMENT '予約番号',
    `full_datetime_string` VARCHAR(50) COMMENT '利用日時 (元の文字列)',
    `facility_name` VARCHAR(255) COMMENT '利用施設名',
    `year_ad` YEAR(4) NOT NULL COMMENT '利用西暦年',
    `month` TINYINT UNSIGNED NOT NULL COMMENT '利用月',
    `day` TINYINT UNSIGNED NOT NULL COMMENT '利用日',
    `date` DATE NOT NULL COMMENT '利用年月日 (YYYY-MM-DD形式)',
    `day_of_week` CHAR(1) NOT NULL COMMENT '利用曜日',
    `start_time` TIME NOT NULL COMMENT '利用開始時刻 (HH:MM:SS形式)',
    `end_time` TIME NOT NULL COMMENT '利用終了時刻 (HH:MM:SS形式)',
    PRIMARY KEY (`id`, `reservation_number`)
);
```
## API仕様
### 予約テーブルの一覧取得
path: api/reservations
- mysql から reservation_data を取得して返す
### CSVインポート
path: /api/import-csv
- csvファイルを受け取ってMySQLにinsertする
- reservation_numberはユニークなので上書きしない

## 技術仕様
- URL パスは /list
- pythonで記述
- パッケージ管理は uv を利用
- 各API
- データベースはMySQL
- 接続に必要な値は環境変数から取得する
  MYSQL_HOST,MYSQL_DATABASE,MYSQL_USER,MYSQL_PASSWORD
