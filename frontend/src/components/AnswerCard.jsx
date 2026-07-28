/** Presents a retrieval-grounded response or in-progress answer state. */
function AnswerCard({ answer, isLoading }) {
  const responseText = isLoading
    ? 'Consulting the archive and preparing a grounded response…'
    : answer ?? 'Ask a question to consult the knowledge archive.'

  return (
    <article className="relative overflow-hidden rounded-2xl border border-[#dcc9b1] bg-[#fffcf6] p-5 shadow-[0_14px_35px_rgba(75,55,35,0.08)] sm:p-6">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[#c58d4e] to-transparent" />
      <div className="flex items-center gap-2 text-[0.65rem] font-semibold uppercase tracking-[0.15em] text-[#a36e32]">
        <span className={`size-1.5 rounded-full bg-[#bb7f3d] ${isLoading ? 'animate-pulse' : ''}`} />
        {isLoading ? 'Consulting Archive' : 'Archive Response'}
      </div>
      <p className="mt-4 font-serif text-xl leading-relaxed text-[#38332e] sm:text-2xl">{responseText}</p>
      <div className="mt-5 flex items-center gap-2 border-t border-[#eee3d5] pt-4 text-xs text-[#8a7e70]">
        <svg viewBox="0 0 24 24" className="size-4 text-[#b77d3e]" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
          <path d="M12 3.7a8.3 8.3 0 1 0 8.3 8.3A8.3 8.3 0 0 0 12 3.7Z" />
          <path d="M12 7.8v4.7l3.1 1.8" />
        </svg>
        {answer ? 'Synthesized from retrieved archive passages' : 'Answers are grounded in your uploaded documents'}
      </div>
    </article>
  )
}

export default AnswerCard
