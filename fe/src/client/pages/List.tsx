import React, { useEffect, useState } from 'react'

type Reservation = {
  id: string
  organization_name?: string
  status?: string
  reservation_number?: string
  full_datetime_string?: string
  facility_name?: string
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function List() {
  const [data, setData] = useState<Reservation[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [statusMsg, setStatusMsg] = useState<{type: 'success'|'error', text: string}|null>(null)

  useEffect(() => { loadReservations() }, [])

  async function loadReservations() {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/reservations`)
      const json = await res.json()
      setData(json)
    } catch (e) {
      console.error(e)
      setStatusMsg({type: 'error', text: 'データ取得でエラーが発生しました'})
    } finally { setLoading(false) }
  }

  async function onImport(file?: File) {
    if (!file) return setStatusMsg({type: 'error', text: 'ファイルを選択してください'})
    try {
      const text = await file.text()
      const res = await fetch(`${API_BASE}/api/import-csv`, {method: 'POST', headers: {'Content-Type': 'text/csv'}, body: text})
      const json = await res.json()
      if (res.ok) {
        setStatusMsg({type: 'success', text: json.message || '成功'})
        await loadReservations()
      } else {
        setStatusMsg({type: 'error', text: json.error || 'インポートに失敗しました'})
      }
    } catch (e) {
      console.error(e)
      setStatusMsg({type: 'error', text: 'インポート処理でエラーが発生しました'})
    }
  }

  return (
    <div style={{padding: 20}}>
      <div style={{maxWidth: 1200, margin: '0 auto', background: '#fff', padding: 24, borderRadius: 8}}>
        <h1 style={{borderBottom: '3px solid #007bff', paddingBottom: 8}}>予約一覧</h1>

        {loading && <div style={{padding: 40, color: '#999'}}>読み込み中...</div>}
        {!loading && data && data.length === 0 && <div style={{padding:40, color:'#999'}}>データがありません</div>}

        {!loading && data && data.length > 0 && (
          <table style={{width: '100%', borderCollapse: 'collapse'}}>
            <thead style={{background: '#007bff', color: '#fff'}}>
              <tr>
                <th style={{padding: 12, textAlign: 'left'}}>団体名</th>
                <th style={{padding: 12, textAlign: 'left'}}>ID</th>
                <th style={{padding: 12, textAlign: 'left'}}>予約の状況</th>
                <th style={{padding: 12, textAlign: 'left'}}>予約番号</th>
                <th style={{padding: 12, textAlign: 'left'}}>利用日時</th>
                <th style={{padding: 12, textAlign: 'left'}}>利用施設名</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.id} style={{borderBottom: '1px solid #ddd'}}>
                  <td style={{padding: 12}}>{row.organization_name || ''}</td>
                  <td style={{padding: 12}}>{row.id}</td>
                  <td style={{padding: 12}}>{row.status}</td>
                  <td style={{padding: 12}}>{row.reservation_number}</td>
                  <td style={{padding: 12}}>{row.full_datetime_string || ''}</td>
                  <td style={{padding: 12}}>{row.facility_name || ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div style={{marginTop: 40, paddingTop: 20, borderTop: '2px solid #f0f0f0'}}>
          <h2 style={{fontSize: 18, marginBottom: 12}}>CSVインポート</h2>
          <div style={{display: 'flex', gap: 10, alignItems: 'center'}}>
            <input id="csv-file" type="file" accept=".csv" onChange={(e)=> onImport(e.target.files?.[0])} />
            <button onClick={() => { const el = document.getElementById('csv-file') as HTMLInputElement; onImport(el.files?.[0]); }} style={{padding: '10px 20px', background: '#28a745', color: '#fff', border: 'none', borderRadius: 6}}>インポート</button>
          </div>
          {statusMsg && (
            <div style={{marginTop: 10, padding: 10, borderRadius: 6, background: statusMsg.type === 'success' ? '#d4edda' : '#f8d7da', color: statusMsg.type === 'success' ? '#155724' : '#721c24'}}>
              {statusMsg.text}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
