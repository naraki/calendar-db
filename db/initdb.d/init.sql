CREATE TABLE IF NOT EXISTS google_calendar_events (
    event_id VARCHAR(255) PRIMARY KEY,
    summary VARCHAR(255),
    start_time DATETIME,
    end_time DATETIME,
    status VARCHAR(50),
    last_synced DATETIME
);

CREATE TABLE `reservation_data` (
    `organization_name` VARCHAR(255) NOT NULL COMMENT '団体名',
    `id` VARCHAR(10) NOT NULL COMMENT 'ID',
    `status` VARCHAR(10) NOT NULL COMMENT '予約の状況 (当選/落選)',
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