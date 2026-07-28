const steps = [
  {
    title: 'Archive Documents',
    icon: (
      <svg viewBox="0 0 24 24" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
        <path d="M6.5 3.8h7l4 4v12.4H6.5z" />
        <path d="M13.5 3.8v4h4M9 13h6M9 16h4.3" />
      </svg>
    ),
  },
  {
    title: 'Retrieve Knowledge',
    icon: (
      <svg viewBox="0 0 24 24" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
        <path d="M12 3.5a8.5 8.5 0 1 0 8.5 8.5A8.5 8.5 0 0 0 12 3.5Z" />
        <path d="m8.8 13 2.1 2.1 4.5-5" />
      </svg>
    ),
  },
  {
    title: 'Ask Anything',
    icon: (
      <svg viewBox="0 0 24 24" className="size-4" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
        <path d="M5 18.5 3.8 21l3.4-1.2A8.2 8.2 0 1 0 5 18.5Z" />
        <path d="M8.5 12h.01M12 12h.01M15.5 12h.01" strokeLinecap="round" strokeWidth="2.2" />
      </svg>
    ),
  },
]

/** Visualizes the compact archive-to-answer process. */
function Workflow() {
  return (
    <div className="mx-auto mt-7 flex max-w-full items-center justify-start gap-2 overflow-x-auto px-1 pb-1 sm:justify-center" aria-label="RAVEN AI workflow">
      {steps.map((step, index) => (
        <div key={step.title} className="flex shrink-0 items-center gap-2">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#d9ccba] bg-[#fcf8f0]/85 px-3.5 py-2 shadow-[0_5px_14px_rgba(77,60,43,0.045)] transition duration-300 hover:-translate-y-0.5 hover:border-[#b8874e]/60 hover:shadow-[0_9px_20px_rgba(77,60,43,0.08)]">
            <span className="grid size-6 place-items-center rounded-full bg-[#f0e2cb] text-[#a16e36]">{step.icon}</span>
            <span className="whitespace-nowrap text-xs font-semibold text-[#3d3731]">{step.title}</span>
          </div>
          {index < steps.length - 1 && (
            <span className="text-lg leading-none text-[#b8874e]" aria-hidden="true">→</span>
          )}
        </div>
      ))}
    </div>
  )
}

export default Workflow
