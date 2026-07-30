'use client'
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

const EXAMPLE_QUERIES = [
  "Show pending housing applications in Krishna district above 90 days",
  "Which departments have anomalies?",
  "Show all delayed pension schemes in Guntur",
  "Give me an executive summary of all schemes",
  "Show health schemes with more than 30 days pending",
]

export default function QueryPage() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.query.history().then(setHistory).catch(console.error) }, [])

  const submit = async () => {
    if (!query.trim()) return
    setLoading(true); setResult(null)
    try {
      const r = await api.query.submit(query)
      setResult(r)
      api.query.history().then(setHistory)
    } catch (e: any) { setResult({ error: e.message }) }
    finally { setLoading(false) }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Natural Language Query</h1>
      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Ask a governance question</label>
          <textarea
            className="border rounded px-3 py-2 text-sm w-full h-24 resize-none"
            placeholder="e.g. Show pending housing applications in Krishna district above 90 days"
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-2">Examples:</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUERIES.map(q => (
              <button key={q} onClick={() => setQuery(q)} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded hover:bg-blue-100">{q}</button>
            ))}
          </div>
        </div>
        <button onClick={submit} disabled={loading || !query.trim()} className="bg-blue-700 text-white px-6 py-2 rounded text-sm hover:bg-blue-800 disabled:opacity-50">
          {loading ? 'Querying...' : 'Submit Query'}
        </button>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow p-5">
          <h2 className="font-semibold mb-2">Result</h2>
          {result.error ? (
            <p className="text-red-600 text-sm">{result.error}</p>
          ) : (
            <>
              <div className="flex gap-4 mb-3 text-xs">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">Intent: {result.parsed_intent}</span>
                {result.parsed_filters && <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded">Filters: {result.parsed_filters}</span>}
              </div>
              <p className="text-sm text-gray-800 leading-relaxed">{result.result_summary}</p>
            </>
          )}
        </div>
      )}

      {history.length > 0 && (
        <div className="bg-white rounded-lg shadow p-5">
          <h2 className="font-semibold mb-3">Query History</h2>
          <div className="space-y-3">
            {history.map(h => (
              <div key={h.id} className="border-b pb-3 last:border-0">
                <p className="text-sm font-medium text-blue-700 mb-1">&ldquo;{h.query}&rdquo;</p>
                <p className="text-xs text-gray-600">{h.result}</p>
                <p className="text-xs text-gray-400 mt-1">{new Date(h.created_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
