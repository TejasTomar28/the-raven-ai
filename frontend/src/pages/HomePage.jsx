import { useMemo, useState } from 'react'
import AnswerCard from '../components/AnswerCard'
import ArchiveDocumentCard from '../components/ArchiveDocumentCard'
import DeleteDocumentModal from '../components/DeleteDocumentModal'
import Header from '../components/Header'
import SourceCard from '../components/SourceCard'
import Workflow from '../components/Workflow'
import { useArchive } from '../hooks/useArchive'
import { askArchiveQuestion } from '../services'

/** Renders the connected RAVEN AI knowledge archive experience. */
function HomePage() {
  const { archiveDocument, deletingFilename, documents, error: archiveError, isLoading: isArchiveLoading, isUploading, removeDocument } = useArchive()
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [sources, setSources] = useState([])
  const [supported, setSupported] = useState(null)
  const [chatError, setChatError] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [documentPendingDeletion, setDocumentPendingDeletion] = useState(null)
  const [categoryFilter, setCategoryFilter] = useState('all')
  const filteredDocuments = useMemo(() => categoryFilter === 'all' ? documents : documents.filter((document) => (document.category ?? 'general') === categoryFilter), [categoryFilter, documents])

  const handleAsk = async () => {
    const normalizedQuestion = question.trim()
    if (!normalizedQuestion) {
      setChatError('Enter a question to consult the archive.')
      return
    }

    setIsGenerating(true)
    setChatError('')
    setAnswer(null)
    setSources([])

    try {
      const chatResponse = await askArchiveQuestion(normalizedQuestion)
      setAnswer(chatResponse.answer)
      setSupported(chatResponse.supported)
      setSources(chatResponse.sources)
    } catch (requestError) {
      setChatError(requestError.message)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDeleteDocument = async () => {
    if (!documentPendingDeletion) {
      return
    }

    const deleted = await removeDocument(documentPendingDeletion.filename)
    if (deleted) {
      setDocumentPendingDeletion(null)
    }
  }

  return (
    <>
      <Header isUploading={isUploading} onArchiveDocument={archiveDocument} />
      <DeleteDocumentModal document={documentPendingDeletion} isDeleting={Boolean(deletingFilename)} onCancel={() => setDocumentPendingDeletion(null)} onConfirm={handleDeleteDocument} />
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 opacity-[0.45] [background-image:radial-gradient(rgba(113,88,59,0.16)_0.65px,transparent_0.65px)] [background-size:12px_12px]" />
        <div className="pointer-events-none absolute -top-32 left-1/2 h-80 w-[48rem] -translate-x-1/2 rounded-full bg-[#edcf9d]/20 blur-3xl" />
        <section className="relative mx-auto max-w-[1440px] px-5 pb-9 pt-9 text-center sm:px-8 lg:px-12 lg:pb-10 lg:pt-12">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-[#a77035]">The intelligent archive</p>
          <h1 className="mt-3 font-serif text-4xl tracking-[-0.055em] text-[#2e2b27] sm:text-5xl lg:text-6xl">RAVEN AI</h1>
          <p className="mt-2 font-serif text-lg text-[#62584e] sm:text-xl">Enterprise Knowledge Platform</p>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-[#82776b]">Transform documents into searchable knowledge using Retrieval-Augmented Generation.</p>
          <Workflow />
        </section>

        <section className="relative border-y border-[#d9cab5] bg-[#f7f0e5]/80 py-9 sm:py-10">
          <div className="mx-auto grid max-w-[1440px] gap-8 px-5 sm:px-8 lg:grid-cols-[minmax(280px,0.82fr)_minmax(0,1.75fr)] lg:gap-12 lg:px-12">
            <aside>
              <div className="mb-5 flex items-end justify-between">
                <div>
                  <p className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-[#a06b32]">Collection</p>
                  <h2 className="mt-1 font-serif text-2xl text-[#332f2a]">Knowledge Archive</h2>
                </div>
                <span className="rounded-full border border-[#d6c3aa] bg-[#fdf9f2] px-2.5 py-1 text-[0.65rem] font-medium text-[#8b7256]">{filteredDocuments.length} documents</span>
              </div>
              <label className="mb-3 block">
                <span className="sr-only">Filter documents by category</span>
                <select value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)} className="w-full rounded-lg border border-[#d8c8b5] bg-[#fffdf8] px-3 py-2 text-xs font-medium text-[#6d6257] outline-none transition focus:border-[#b98246] focus:ring-2 focus:ring-[#d7a768]/15">
                  <option value="all">All categories</option>
                  <option value="finance">Finance</option>
                  <option value="hr">HR</option>
                  <option value="legal">Legal</option>
                  <option value="research">Research</option>
                  <option value="resume">Resume</option>
                  <option value="technical">Technical</option>
                  <option value="general">General</option>
                </select>
              </label>
              {archiveError && <p className="mb-3 text-xs leading-relaxed text-[#9b572e]" role="alert">{archiveError}</p>}
              {isArchiveLoading ? (
                <p className="text-sm text-[#8b8175]">Loading archive…</p>
              ) : filteredDocuments.length > 0 ? (
                <div className="raven-scrollbar max-h-[25.5rem] space-y-3 overflow-y-auto pr-2">{filteredDocuments.map((document) => <ArchiveDocumentCard key={document.filename} document={document} isDeleting={Boolean(deletingFilename)} onDelete={setDocumentPendingDeletion} />)}</div>
              ) : (
                <p className="text-sm leading-relaxed text-[#8b8175]">{documents.length > 0 ? 'No archived documents match this category.' : 'Archive a PDF to begin building your knowledge base.'}</p>
              )}
            </aside>

            <section className="rounded-2xl border border-[#ded0be] bg-[#fbf7ef]/75 p-5 shadow-[0_20px_48px_rgba(73,55,36,0.07)] sm:p-7">
              <div className="flex flex-col justify-between gap-3 border-b border-[#e6d8c7] pb-5 sm:flex-row sm:items-end">
                <div>
                  <p className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-[#a06b32]">Consultation</p>
                  <h2 className="mt-1 font-serif text-3xl text-[#322f2a]">Consult the Archive</h2>
                </div>
                <p className="text-xs text-[#8d8175]">Grounded in your documents</p>
              </div>
              <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                <label className="sr-only" htmlFor="archive-question">Ask a question about your archive</label>
                <input id="archive-question" value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter') handleAsk() }} disabled={isGenerating} className="min-h-14 flex-1 rounded-xl border border-[#d8c8b5] bg-[#fffdf8] px-4 text-sm text-[#484139] outline-none transition placeholder:text-[#9a8d7e] focus:border-[#b98246] focus:ring-4 focus:ring-[#d7a768]/15 disabled:cursor-not-allowed disabled:opacity-70" placeholder="How many annual leave days are employees entitled to?" />
                <button type="button" onClick={handleAsk} disabled={isGenerating} className="inline-flex min-h-14 items-center justify-center gap-2 rounded-xl bg-[#b47b3d] px-6 text-sm font-semibold text-white shadow-[0_8px_18px_rgba(136,87,38,0.22)] transition duration-300 hover:-translate-y-0.5 hover:bg-[#9e682e] focus:outline-none focus:ring-2 focus:ring-[#b98246] focus:ring-offset-2 focus:ring-offset-[#fbf7ef] disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0">
                  {isGenerating ? 'Asking…' : 'Ask'}
                  <svg viewBox="0 0 24 24" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="m5 12 14-7-4.7 14-3.1-5.1L5 12Z" /></svg>
                </button>
              </div>
              {chatError && <p className="mt-3 text-xs leading-relaxed text-[#9b572e]" role="alert">{chatError}</p>}
              <div className="mt-7"><AnswerCard answer={answer} isLoading={isGenerating} /></div>
              {answer && !isGenerating && (
                <div className="mt-8">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="font-serif text-xl text-[#3c3731]">Knowledge Sources</h3>
                    <span className="text-[0.68rem] font-medium uppercase tracking-[0.12em] text-[#9c7d5a]">{sources.length} passages</span>
                  </div>
                  {supported && sources.length > 0 ? (
                    <div className="raven-scrollbar max-h-44 overflow-y-auto pr-2"><div className="grid gap-3 xl:grid-cols-3">{sources.map((source, index) => <SourceCard key={`${source.filename}-${source.chunk_id ?? index}`} source={source} />)}</div></div>
                  ) : (
                    <div className="rounded-xl border border-[#e2d7c6] bg-[#faf6ef] p-4 text-sm leading-relaxed text-[#81766a]">
                      <p>No relevant supporting passages were found for this question.</p>
                      <p className="mt-1">Try asking a question related to your uploaded documents.</p>
                    </div>
                  )}
                </div>
              )}
            </section>
          </div>
        </section>
      </div>
    </>
  )
}

export default HomePage
