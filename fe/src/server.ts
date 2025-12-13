import express from 'express';
import path from 'path';

const app = express();
const PORT = process.env.PORT || 3000;

// ミドルウェア: フロントエンドの静的配信のみ
app.use(express.static(path.join(__dirname, '../public')));

// SPA のための Fallback: 未定義のルートは index.html にフォールバック
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

// NOTE: API は backend (be) に移行しました。フロントエンドは API を直接 be に問い合わせるようにしてください。

app.listen(PORT, () => {
  console.log(`Frontend server (static) running on port ${PORT}`);
});