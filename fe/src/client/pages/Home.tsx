import React from 'react'
import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div style={{height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f7fafc'}}>
      <div style={{background: '#fff', padding: 28, borderRadius: 8, boxShadow: '0 6px 18px rgba(0,0,0,0.08)', textAlign: 'center'}}>
        <h1>ようこそ</h1>
        <p style={{marginTop: 12}}>
          <Link to="/list" style={{padding: '10px 18px', background: '#007bff', color: '#fff', borderRadius: 6, textDecoration: 'none', fontWeight: 600, marginRight: 8}}>予約一覧</Link>
          <Link to="/instruction" style={{padding: '10px 18px', background: '#17a2b8', color: '#fff', borderRadius: 6, textDecoration: 'none', fontWeight: 600}}>予約指示</Link>
        </p>
      </div>
    </div>
  )
}
