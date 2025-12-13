"""DB access helpers for the FastAPI backend.

This module uses mysql-connector-python and a simple pooling strategy.
Functions are written to be easy to mock in tests.
"""
import os
import mysql.connector
from mysql.connector import pooling
from typing import Iterable, Dict, Any, List

DB_POOL = None


def get_pool():
    global DB_POOL
    if DB_POOL is None:
        DB_POOL = pooling.MySQLConnectionPool(
            pool_name="kac_pool",
            pool_size=5,
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "kac_db"),
        )
    return DB_POOL


def fetch_reservations() -> List[Dict[str, Any]]:
    pool = get_pool()
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT organization_name, id, status, reservation_number, full_datetime_string, facility_name FROM reservation_data ORDER BY date DESC, start_time ASC"
        )
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()


def import_csv_records(rows: Iterable[Dict[str, str]]) -> int:
    pool = get_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    inserted = 0
    try:
        for record in rows:
            try:
                reservationNumber = int(record.get("予約番号") or record.get("reservation_number") or 0)
                yearAd = int(record.get("西暦年") or record.get("year_ad") or 0)
                month = int(record.get("月") or record.get("month") or 0)
                day = int(record.get("日") or record.get("day") or 0)
            except Exception:
                # 数値にパースできない場合はスキップ
                continue

            cursor.execute(
                "INSERT INTO reservation_data (organization_name, id, status, reservation_number, full_datetime_string, facility_name, year_ad, month, day, date, day_of_week, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    record.get("団体名") or None,
                    record.get("ID") or None,
                    record.get("状況") or None,
                    reservationNumber,
                    record.get("利用日時") or None,
                    record.get("利用施設") or None,
                    yearAd,
                    month,
                    day,
                    record.get("年月日") or None,
                    record.get("曜日") or None,
                    record.get("開始時刻") or None,
                    record.get("終了時刻") or None,
                ],
            )
            inserted += 1
        conn.commit()
        return inserted
    finally:
        cursor.close()
        conn.close()
