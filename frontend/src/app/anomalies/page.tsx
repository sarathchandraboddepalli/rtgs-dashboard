'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function AnomaliesPage() {
  const [anomalyData, setAnomalyData] = useState<any>(null)
  const [running, setRunning] = useState(false)

  const load = () => api.departments.anomalies().then(setAnomalyData).catch(console.error)
  useEffect(() => { load() }, [])

  const runDetection = async () => {
    setRunning(true)
    await api.departments.runAnomalyDetection().catch(console.error)
    await load()
    setRunning(false)
  }

  return (
    <div className="max-w-7xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Anomaly Detection</h1>
        <button onClick={runDetection} disabled={running} className="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700 disabled:opacity-50">
          {running ? 'Running...' : 'Run Detection'}
        </button>
      </div>
      {anomalyData && (
        <>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-2xl font-bold text-red-600">{anomalyData.total_anomalous}</p>
            <p className="text-sm text-gray-600">Departments with anomalies</p>
          </div>
          <div className="space-y-3">
            {anomalyData.departments?.map((d: any, i: number) => (
              <div key={i} className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{d.name}</h3>
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded">{d.category}</span>
                </div>
                <p className="text-sm text-red-600">{d.reason}</p>
              </div>
            ))}
          </div>
          {anomalyData.departments?.length === 0 && <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">No anomalies detected</div>}
        </>
      )}
    </div>
  )
}
