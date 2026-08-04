/** Displays one uploaded document in the knowledge archive. */
function ArchiveDocumentCard({ document, isDeleting, onDelete }) {
  const documentSize = formatFileSize(document.size_bytes)
  const archiveDetail = document.chunks ? `${document.chunks} indexed chunks` : 'Indexed document'
  const updatedAt = document.updated_at
    ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(document.updated_at))
    : 'Recently archived'

  return (
    <article className="group rounded-xl border border-[#e1d5c3] bg-[#fdfaf4] p-4 shadow-[0_5px_14px_rgba(68,53,39,0.035)] transition duration-300 hover:-translate-y-0.5 hover:border-[#c9995d] hover:shadow-[0_10px_24px_rgba(68,53,39,0.08)]">
      <div className="flex items-start gap-3">
        <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-[#f1e5d2] text-[#9c682f]">
          <svg viewBox="0 0 24 24" className="size-[18px]" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
            <path d="M6.5 3.8h7l4 4v12.4H6.5z" />
            <path d="M13.5 3.8v4h4M9 13h6M9 16h4.3" />
          </svg>
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex min-w-0 items-center gap-2">
            <h3 className="truncate text-sm font-semibold text-[#38342f]">{document.filename}</h3>
            <span className="shrink-0 rounded-full border border-[#dcc29e] bg-[#f6ead8] px-1.5 py-0.5 text-[0.56rem] font-semibold uppercase tracking-[0.08em] text-[#96612d]">{formatCategory(document.category)}</span>
          </div>
          <p className="mt-1 text-xs text-[#8b8175]">{documentSize} · {archiveDetail}</p>
        </div>
        <button type="button" aria-label={`Delete ${document.filename}`} disabled={isDeleting} onClick={() => onDelete(document)} className="grid size-8 shrink-0 place-items-center rounded-lg text-[#9c682f] transition hover:bg-[#f1e5d2] hover:text-[#80532b] focus:outline-none focus:ring-2 focus:ring-[#b98246] disabled:cursor-not-allowed disabled:opacity-50">
          <svg viewBox="0 0 24 24" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
            <path d="M5.5 7.5h13M9.5 7.5V5.8c0-.7.6-1.3 1.3-1.3h2.4c.7 0 1.3.6 1.3 1.3v1.7M7.5 7.5l.8 12h7.4l.8-12M10 11v5M14 11v5" />
          </svg>
        </button>
      </div>
      <div className="mt-4 flex items-center justify-between border-t border-[#eee5d8] pt-3 text-[0.68rem] font-medium tracking-wide text-[#a09587]">
        <span>ARCHIVED</span>
        <span>{updatedAt}</span>
      </div>
    </article>
  )
}

function formatCategory(category) {
  return typeof category === 'string' && category.length > 0
    ? category.charAt(0).toUpperCase() + category.slice(1)
    : 'General'
}

function formatFileSize(sizeInBytes) {
  if (!Number.isFinite(sizeInBytes) || sizeInBytes <= 0) {
    return 'PDF document'
  }

  if (sizeInBytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(sizeInBytes / 1024))} KB`
  }

  return `${(sizeInBytes / (1024 * 1024)).toFixed(1)} MB`
}

export default ArchiveDocumentCard
