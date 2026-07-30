'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function SchemesPage() {
  const [schemes, setSchemes] = useState<any[]>([])
  const [filter, setFilter] = useState<string>('')
  const [loading, setLoading] = useState(true)

  const load = (params?: string) => {
    setLoading(true)
    api.schemes.list(params).then(setSchemes).catch(console.error).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const FILTERS = [
    { label: 'All', params: '' },
    { label: 'Delayed', params: 'is_delayed=true' },
    { label: 'Housing', params: 'scheme_type=housing' },
    { label: 'Pension', params: 'scheme_type=pension' },
    { label: 'Health', params: 'scheme_type=health' },
  ]

  return (
    <div className="max-w-7xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Scheme Status</h1>
      <div className="flex gap-2">
        {FILTERS.map(f => (
          <button key={f.label} onClick={() => { setFilter(f.params); load(f.params) }} className={`px-3 py-1 rounded text-sm ${filter === f.params ? 'bg-blue-700 text-white' : 'bg-white text-gray-700 border'}`}>{f.label}</button>
        ))}
      </div>
      {loading ? <div className="text-center py-12 text-gray-500">Loading...</div> : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>{['Scheme', 'Type', 'District', 'Pending', 'Avg Days', 'Completion', 'Status'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {schemes.map(s => (
                <tr key={s.id} className={`hover:bg-gray-50 ${s.is_delayed ? 'bg-red-50' : ''}`}>
                  <td className="px-4 py-3 text-sm font-medium">{s.name}</td>
                  <td className="px-4 py-3 text-sm"><span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">{s.scheme_type}</span></td>
                  <td className="px-4 py-3 text-sm">{s.district}</td>
                  <td className="px-4 py-3 text-sm font-bold text-orange-600">{s.pending_applications.toLocaleString()}</td>
                  <td className={`px-4 py-3 text-sm font-bold ${s.avg_pending_days > s.sla_days ? 'text-red-600' : 'text-green-600'}`}>{s.avg_pending_days.toFixed(0)}d</td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2"><div className="h-2 rounded-full bg-blue-500" style={{ width: `${s.completion_pct}%` }} /></div>
                      <span className="text-xs">{s.completion_pct.toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">{s.is_delayed ? <span className="text-red-600 font-bold text-xs">DELAYED</span> : <span className="text-green-600 text-xs">On Track</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {schemes.length === 0 && <div className="text-center py-12 text-gray-500">No schemes found</div>}
        </div>
      )}
    </div>
  )
}
