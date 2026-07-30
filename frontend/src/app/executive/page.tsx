'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function ExecutivePage() {
  const [summary, setSummary] = useState<any>(null)
  const [districts, setDistricts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.analytics.executiveSummary(), api.analytics.districtStats()])
      .then(([s, d]) => { setSummary(s); setDistricts(d) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-12 text-gray-500">Loading AP RTGS data...</div>
  if (!summary) return <div className="text-center py-12 text-red-500">Failed to load dashboard</div>

  const utilizationPct = summary.budget?.utilization_pct ?? 0

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Executive Dashboard — AP Governance</h1>
        <span className="text-sm text-gray-500 bg-blue-50 px-3 py-1 rounded-full">AWARE 2.0 Mock</span>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Departments', value: summary.departments?.total ?? 0, sub: `${summary.departments?.anomalous ?? 0} anomalous`, color: 'bg-blue-500' },
          { label: 'Budget Utilization', value: `${utilizationPct.toFixed(1)}%`, sub: `₹${(summary.budget?.spent_crores ?? 0).toLocaleString()} Cr spent`, color: utilizationPct > 90 ? 'bg-red-500' : utilizationPct < 20 ? 'bg-yellow-500' : 'bg-green-500' },
          { label: 'Active Beneficiaries', value: (summary.schemes?.active_beneficiaries ?? 0).toLocaleString(), sub: `${summary.schemes?.total ?? 0} schemes`, color: 'bg-purple-500' },
          { label: 'Pending Applications', value: (summary.schemes?.pending_applications ?? 0).toLocaleString(), sub: `${summary.schemes?.delayed ?? 0} schemes delayed`, color: summary.schemes?.delayed > 0 ? 'bg-orange-500' : 'bg-green-500' },
        ].map(c => (
          <div key={c.label} className="bg-white rounded-lg shadow p-5">
            <div className={`text-2xl font-bold text-white ${c.color} rounded-md px-3 py-2 inline-block mb-2`}>{c.value}</div>
            <p className="text-sm font-medium text-gray-900">{c.label}</p>
            <p className="text-xs text-gray-500">{c.sub}</p>
          </div>
        ))}
      </div>

      {/* District breakdown */}
      <div className="bg-white rounded-lg shadow p-5">
        <h2 className="text-lg font-semibold mb-4">District Scheme Load</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>{['District', 'Schemes', 'Pending Applications', 'Load'].map(h => (
                <th key={h} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {districts.map(d => {
                const maxPending = Math.max(...districts.map(x => x.total_pending))
                const loadPct = maxPending > 0 ? (d.total_pending / maxPending) * 100 : 0
                return (
                  <tr key={d.district} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-medium">{d.district}</td>
                    <td className="px-4 py-2 text-sm">{d.scheme_count}</td>
                    <td className="px-4 py-2 text-sm font-bold text-orange-600">{d.total_pending.toLocaleString()}</td>
                    <td className="px-4 py-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div className={`h-2 rounded-full ${loadPct > 70 ? 'bg-red-500' : loadPct > 40 ? 'bg-yellow-500' : 'bg-green-500'}`} style={{ width: `${loadPct}%` }} />
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
