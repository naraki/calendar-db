import React, { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

type CellState = 'SM'|'S'|'M'|'N'|null

function getMonthGrid(year: number, month: number) {
  // month: 1-12, return weeks starting Monday
  const first = new Date(year, month - 1, 1)
  const last = new Date(year, month, 0)
  const firstWeekdaySunBased = first.getDay() // 0 (Sun) - 6 (Sat)
  // convert to Monday-based index where Monday = 0
  const firstWeekday = (firstWeekdaySunBased + 6) % 7
  const daysInMonth = last.getDate()

  const cells: Array<number|null> = []
  for (let i = 0; i < firstWeekday; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  // pad to 6*7
  while (cells.length < 42) cells.push(null)
  const weeks: number[][] = []
  for (let i = 0; i < 6; i++) weeks.push(cells.slice(i*7, i*7+7).map(v => v ?? 0))
  return { weeks, daysInMonth }
}

export default function Instruction(){
  const [searchParams, setSearchParams] = useSearchParams()
  const queryYear = Number(searchParams.get('year')) || new Date().getFullYear()
  const queryMonth = Number(searchParams.get('month')) || (new Date().getMonth() + 1)
  const idParam = searchParams.get('id')
  // name will be fetched from API later; show placeholder for now
  const nameParam = searchParams.get('name') || '○○○○○'

  const [year, setYear] = useState(queryYear)
  const [month, setMonth] = useState(queryMonth)

  // per-day selection state keyed by day number (1..31)
  const [selections, setSelections] = useState<Record<number, CellState>>({})

  const { weeks } = useMemo(()=> getMonthGrid(year, month), [year, month])

  function setSelection(day: number, val: CellState){
    setSelections(prev => ({ ...prev, [day]: prev[day] === val ? null : val }))
  }

  function applyQuery(){
    const p = new URLSearchParams()
    p.set('year', String(year))
    p.set('month', String(month))
    if (idParam) p.set('id', idParam)
    if (nameParam) p.set('name', nameParam)
    setSearchParams(p)
  }

  // default week headers: Sun - Sat (fixed position)
  // Monday-starting week
  const weekdays = ['月','火','水','木','金','土','日']

  // Storage helpers (dummy API)
  function storageKey(){
    return `instruction:${idParam ? idParam : 'summary'}:${year}-${String(month).padStart(2,'0')}`
  }

  function saveDummy(){
    const key = storageKey()
    localStorage.setItem(key, JSON.stringify(selections))
    alert('保存しました（ダミー）')
  }

  function loadDummy(){
    const key = storageKey()
    const raw = localStorage.getItem(key)
    if (raw) {
      try{
        const parsed = JSON.parse(raw)
        setSelections(parsed)
        alert('読み込みました（ダミー）')
      }catch(e){
        alert('読み込みに失敗しました')
      }
    } else {
      alert('保存データが見つかりません（ダミー）')
    }
  }

  return (
    <div style={{padding: 20}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: 1200, margin: '0 auto', gap: 12}}>
        <div>
          <h1 style={{margin: 0}}>予約指示</h1>
          <div style={{display: 'flex', gap: 8, marginTop: 8}}>
            <label>年: <input type="number" value={year} onChange={(e)=> setYear(Number(e.target.value))} style={{width: 100}} /></label>
            <label>月: <input type="number" value={month} min={1} max={12} onChange={(e)=> setMonth(Number(e.target.value))} style={{width: 70}} /></label>
            <button onClick={applyQuery} style={{padding: '6px 12px'}}>表示</button>
            <button onClick={saveDummy} style={{padding: '6px 12px'}}>保存(ダミー)</button>
            <button onClick={loadDummy} style={{padding: '6px 12px'}}>読み込み(ダミー)</button>
          </div>
        </div>

        <div style={{textAlign: 'right'}}>
          {idParam ? (
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6}}>
              <div style={{border: '1px solid #ddd', padding: '8px 12px', borderRadius: 6, minWidth: 260}}>
                <div style={{fontSize: 12, color: '#666'}}>ID</div>
                <div style={{fontWeight: 700, fontSize: 14}}>{idParam}</div>
              </div>
              <div style={{border: '1px solid #ddd', padding: '8px 12px', borderRadius: 6, minWidth: 260}}>
                <div style={{fontSize: 12, color: '#666'}}>名前</div>
                <div style={{fontWeight: 700, fontSize: 14}}>{nameParam}</div>
              </div>
            </div>
          ) : (
            <div style={{border: '1px dashed #ddd', padding: '8px 12px', borderRadius: 6, minWidth: 200}}>サマリ</div>
          )}
        </div>
      </div>

      <div style={{maxWidth: 1200, margin: '18px auto 0', background: '#fff', padding: 16, borderRadius: 8}}>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 6, marginBottom: 6}}>
          {weekdays.map(w => <div key={w} style={{textAlign:'center', fontWeight: 700, padding: 8, background:'#f0f0f0'}}>{w}</div>)}
        </div>

        <div style={{display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 6}}>
          {weeks.map((week, wi) => (
            week.map((day, di)=> (
              <div key={`${wi}-${di}`} style={{minHeight: 80, border: '1px solid #eee', padding: 8, display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
                {day > 0 ? (
                  <div style={{display:'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <div style={{fontWeight: 700}}>{day}</div>
                    <div style={{fontSize: 12, color: '#999'}}>{/* place for potential small info */}</div>
                  </div>
                ) : (
                  <div style={{color: '#ccc'}}>&nbsp;</div>
                )}

                <div>
                  {idParam ? (
                    day > 0 ? (
                      <div style={{display: 'flex', gap: 6, justifyContent: 'center'}}>
                        {(['SM','S','M','N'] as const).map(opt => (
                          <button
                            key={opt}
                            onClick={() => setSelection(day, opt)}
                            aria-pressed={selections[day] === opt}
                            style={{
                              padding: '4px 8px',
                              borderRadius: 4,
                              border: selections[day] === opt ? '2px solid #007bff' : '1px solid #ddd',
                              background: selections[day] === opt ? '#e6f0ff' : '#fff',
                              cursor: 'pointer',
                              fontSize: 12
                            }}
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                    ) : null
                  ) : (
                    // summary mode: show dummy number 0
                    day > 0 ? (
                      <div style={{textAlign: 'center', fontSize: 20, fontWeight: 700}}>0</div>
                    ) : null
                  )}
                </div>
              </div>
            ))
          ))}
        </div>
      </div>
    </div>
  )
}
