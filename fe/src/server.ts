import express from 'express';
import path from 'path';

const app = express();
const PORT = process.env.PORT || 3000;

// ミドルウェア: フロントエンドの静的配信のみ
app.use(express.static(path.join(__dirname, '../public')));

// SPA のための Fallback: 未定義のルートは index.html にフォールバック
// `/list` は静的な `list.html` を返す（まだクライアントをビルドしていない場合の互換性）
app.get('/list*', (req, res) => {
  res.sendFile(path.join(__dirname, '../public', 'list.html'));
});

// それ以外はトップページ (index.html) にフォールバック
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Frontend server (static) running on port ${PORT}`);
});