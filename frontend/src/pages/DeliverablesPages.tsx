import { useEffect, useState } from 'react'
import { ApiError, request } from '../api/client'
import { Icon } from '../components/ui/Icon'
import { Card, Note, PageHeader } from '../components/ui/Layout'

interface DecisionsDoc {
  path: string
  content: string
  digest: string
}
interface ReportDoc {
  path: string
  analysis_complete: boolean
  message: string | null
  content: string
  bytes?: number
}

const post = <T,>(path: string, body: unknown) =>
  request<T>(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })

export function DecisionsPage() {
  const [doc, setDoc] = useState<DecisionsDoc | null>(null)
  const [text, setText] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const load = () =>
    request<DecisionsDoc>('/api/deliverables/decisions')
      .then((d) => {
        setDoc(d)
        setText(d.content)
      })
      .catch((e: ApiError) => setStatus(e.message))
  useEffect(() => {
    void load()
  }, [])
  const save = async () => {
    try {
      const d = await post<DecisionsDoc>('/api/deliverables/decisions', { content: text, digest: doc?.digest })
      setDoc(d)
      setStatus(`Saved to ${d.path}`)
    } catch (e) {
      setStatus(e instanceof ApiError ? e.message : 'Save failed')
    }
  }
  return (
    <>
      <PageHeader eyebrow="Deliverables" title="Decisions" description="Every update and change of direction, saved as DECISIONS.md at the repository root." />
      <Card
        title="DECISIONS.md"
        subtitle={doc?.path}
        actions={
          <button type="button" className="btn btn-primary" onClick={() => void save()} disabled={!doc || text === doc.content}>
            <Icon name="check" size={15} /> Save file
          </button>
        }
      >
        {status && <Note>{status}</Note>}
        <textarea className="md-editor" value={text} onChange={(e) => setText(e.target.value)} spellCheck={false} aria-label="DECISIONS.md content" />
      </Card>
    </>
  )
}

export function ReportPage() {
  const [doc, setDoc] = useState<ReportDoc | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    request<ReportDoc>('/api/deliverables/report').then(setDoc).catch((e: ApiError) => setError(e.message))
  }, [])
  const generate = async () => {
    setBusy(true)
    setError(null)
    setSaved(null)
    try {
      const d = await post<ReportDoc>('/api/deliverables/report/generate', {})
      setDoc(d)
      setSaved(`Saved REPORT.md (${(d.bytes ?? 0).toLocaleString()} bytes) to ${d.path}`)
    } catch (e) {
      setError(`Report not saved: ${e instanceof ApiError ? e.message : 'generation failed'}`)
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <PageHeader eyebrow="Deliverables" title="Report" description="Preview and generate REPORT.md at the repository root." />
      {doc && !doc.analysis_complete && <Note tone="warning">{doc.message}</Note>}
      {saved && <Note>✓ {saved}</Note>}
      {error && <Note tone="warning">{error}</Note>}
      <Card
        title="REPORT.md"
        subtitle={doc?.path}
        actions={
          <button type="button" className="btn btn-primary" onClick={() => void generate()} disabled={!doc || busy}>
            <Icon name="refresh" size={15} /> {busy ? 'Generating…' : 'Generate report'}
          </button>
        }
      >
        {doc?.content ? <pre className="md-preview">{doc.content}</pre> : <p className="muted">No REPORT.md yet.</p>}
      </Card>
    </>
  )
}
