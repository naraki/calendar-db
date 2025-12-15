import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import List from './pages/List'
import Instruction from './pages/Instruction'

export default function App() {
  return (
    <div>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/list" element={<List />} />
        <Route path="/instruction" element={<Instruction />} />
      </Routes>
    </div>
  )
}
