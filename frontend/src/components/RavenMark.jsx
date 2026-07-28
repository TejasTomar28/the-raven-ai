/** Displays the RAVEN AI archive mark. */
function RavenMark({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid size-10 place-items-center rounded-full border border-[#b8874e]/45 bg-[#2a2825] text-[#e6c18e] shadow-[0_8px_20px_rgba(42,40,37,0.16)]">
        <svg viewBox="0 0 48 48" className="size-5" aria-hidden="true" fill="none">
          <path d="M10 30.7c3.8-2.3 7.3-4.1 10.7-5.3L16.5 11l15 11.1c3.4 0 6.3.6 8.7 1.7-3.6 1.3-6.6 3.1-9 5.5L37 39l-14.3-8.1c-3.7.5-7.9.4-12.7-.2Z" fill="currentColor" />
          <circle cx="30.2" cy="21.9" r="1.45" fill="#2a2825" />
        </svg>
      </span>
      {!compact && (
        <span className="leading-tight">
          <span className="block font-serif text-[0.95rem] font-semibold tracking-[0.16em] text-[#292724]">RAVEN AI</span>
          <span className="mt-0.5 block text-[0.62rem] font-medium uppercase tracking-[0.13em] text-[#857b70]">Enterprise Knowledge Platform</span>
        </span>
      )}
    </div>
  )
}

export default RavenMark
