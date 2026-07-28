/** Displays one retrieved document citation for the answer. */
function SourceCard({ source }) {
  const score = Number.isFinite(source.score) ? `${Math.round(source.score * 100)}% match` : 'Retrieved source'
  const pageLabel = source.page_number ? `Page ${source.page_number}` : 'Source passage'

  return (
    <article className="rounded-xl border border-[#e2d7c6] bg-[#faf6ef] p-4 transition duration-300 hover:border-[#c99b63] hover:bg-[#fffaf3]">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-[#403a34]">{source.filename}</h3>
          <p className="mt-1 text-[0.68rem] font-medium uppercase tracking-[0.1em] text-[#a1794d]">{pageLabel}</p>
        </div>
        <span className="rounded-full bg-[#eee0cb] px-2 py-1 text-[0.63rem] font-semibold text-[#906331]">{score}</span>
      </div>
      <p className="mt-3 text-xs leading-relaxed text-[#81766a]">“{source.text}”</p>
    </article>
  )
}

export default SourceCard
