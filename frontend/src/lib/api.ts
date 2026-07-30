const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
async function f<T>(path: string, opts?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, opts)
  if (!r.ok) throw new Error(`API ${r.status}`)
  return r.json()
}
export const api = {
  analytics: {
    executiveSummary: () => f<any>('/api/v1/analytics/executive-summary'),
    districtStats: () => f<any[]>('/api/v1/analytics/district-stats'),
    seed: () => f<any>('/api/v1/analytics/seed', { method: 'POST' }),
  },
  departments: {
    list: (params?: string) => f<any[]>(`/api/v1/departments/${params ? '?' + params : ''}`),
    runAnomalyDetection: () => f<any>('/api/v1/departments/run-anomaly-detection', { method: 'POST' }),
    anomalies: () => f<any>('/api/v1/departments/anomalies'),
  },
  schemes: {
    list: (params?: string) => f<any[]>(`/api/v1/schemes/${params ? '?' + params : ''}`),
  },
  query: {
    submit: (query: string) => f<any>('/api/v1/query/', { method: 'POST', body: JSON.stringify({ query }), headers: { 'Content-Type': 'application/json' } }),
    history: () => f<any[]>('/api/v1/query/history'),
  },
}
