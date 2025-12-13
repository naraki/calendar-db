import io
import pytest
from fastapi.testclient import TestClient

from be.main import app
from be import db

client = TestClient(app)


def test_get_reservations(monkeypatch):
    sample = [
        {"organization_name": "団体A", "id": 1, "status": "ok", "reservation_number": 123, "full_datetime_string": "2025-01-01 10:00", "facility_name": "ホール"}
    ]

    def fake_fetch():
        return sample

    monkeypatch.setattr(db, "fetch_reservations", fake_fetch)

    resp = client.get("/api/reservations")
    assert resp.status_code == 200
    assert resp.json() == sample


def test_import_csv(monkeypatch):
    # Prepare a small CSV content
    csv_text = "団体名,ID,状況,予約番号,利用日時,利用施設," \
               "西暦年,月,日,年月日,曜日,開始時刻,終了時刻\n"
    csv_text += "団体A,1,ok,123,2025-01-01 10:00,ホール,2025,1,1,2025-01-01,水,10:00,12:00\n"

    # monkeypatch import_csv_records
    def fake_import(reader):
        # Convert reader to list of dicts
        data = list(reader)
        return len(data)
    monkeypatch.setattr(db, "import_csv_records", fake_import)

    files = {"file": ("test.csv", csv_text, "text/csv")}
    resp = client.post("/api/import-csv", files=files)

    assert resp.status_code == 200
    assert "件のレコードをインポートしました" in resp.json()["message"]
