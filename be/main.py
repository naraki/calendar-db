"""Compatibility shim: expose the FastAPI `app` at `be.main`.

Tests and some run commands import `be.main:app`. The implementation lives
in `be/src/main.py`, so re-export the `app` here.
"""
from be.src.main import app

__all__ = ["app"]
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import csv
import sys
from pathlib import Path

# PYTHONPATHに親ディレクトリを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from be import db

app = FastAPI(title="kac-be (FastAPI)")

# CORS: 開発中は全許可。必要に応じて限定してください。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/reservations")
def get_reservations():
    try:
        rows = db.fetch_reservations()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail="データベースエラーが発生しました")


@app.post("/api/import-csv")
def import_csv(file: UploadFile = File(...)):
    if file.content_type not in ("text/csv", "application/vnd.ms-excel", "text/plain"):
        raise HTTPException(status_code=400, detail="CSV ファイルを送信してください")

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(content.splitlines())
    try:
        count = db.import_csv_records(reader)
        return {"message": f"{count}件のレコードをインポートしました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="インポートに失敗しました")
