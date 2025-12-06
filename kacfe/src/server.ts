import express, { Request, Response } from 'express';
import mysql from 'mysql2/promise';
import cors from 'cors';
import path from 'path';

const app = express();
const PORT = process.env.PORT || 3000;

// ミドルウェア
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// MySQL接続プール
const pool = mysql.createPool({
  host: process.env.MYSQL_HOST || 'localhost',
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD || '',
  database: process.env.MYSQL_DATABASE || 'kac_db',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  enableKeepAlive: true,
  keepAliveInitialDelay: 0,
});

// 予約データ取得API
app.get('/api/reservations', async (req: Request, res: Response) => {
  try {
    const connection = await pool.getConnection();
    const [rows] = await connection.query(
      'SELECT organization_name, id, status, reservation_number, full_datetime_string, facility_name FROM reservation_data ORDER BY date DESC, start_time ASC'
    );
    connection.release();
    res.json(rows);
  } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ error: 'データベースエラーが発生しました' });
  }
});

// CSVインポートAPI
app.post('/api/import-csv', express.text({ type: 'text/csv' }), async (req: Request, res: Response) => {
  try {
    const parse = require('csv-parse/sync');
    const csvText = req.body;
    
    const records = parse.parse(csvText, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    });

    const connection = await pool.getConnection();

    for (const record of records) {
      // CSVのカラム名に対応
      const reservationNumber = parseInt(record['予約番号'] || record.reservation_number);
      const yearAd = parseInt(record['西暦年'] || record.year_ad);
      const month = parseInt(record['月'] || record.month);
      const day = parseInt(record['日'] || record.day);

      // NaN チェック
      if (isNaN(reservationNumber) || isNaN(yearAd) || isNaN(month) || isNaN(day)) {
        console.warn('Invalid number in record:', record);
        continue;
      }

      await connection.query(
        'INSERT INTO reservation_data (organization_name, id, status, reservation_number, full_datetime_string, facility_name, year_ad, month, day, date, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [
          record['団体名'] || null,
          record['ID'] || null,
          record['状況'] || null,
          reservationNumber,
          record['利用日時'] || null,
          record['利用施設'] || null,
          yearAd,
          month,
          day,
          record['年月日'] || null,
          record['曜日'] || null,
          record['開始時刻'] || null,
          record['終了時刻'] || null,
        ]
      );
    }

    connection.release();
    res.json({ message: `${records.length}件のレコードをインポートしました` });
  } catch (error) {
    console.error('Import error:', error);
    res.status(500).json({ error: 'インポートに失敗しました' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});