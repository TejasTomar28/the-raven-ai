import { useRef } from 'react'
import RavenMark from './RavenMark'

/** Renders the persistent application header and archive action. */
function Header({ isUploading, onArchiveDocument }) {
  const fileInputRef = useRef(null)

  const handleFileChange = (event) => {
    const [file] = event.target.files
    if (file) {
      onArchiveDocument(file)
    }
    event.target.value = ''
  }

  return (
    <header className="border-b border-[#cfc1ae]/60 bg-[#f5efe5]/80 backdrop-blur-sm">
      <div className="mx-auto flex h-[76px] max-w-[1440px] items-center justify-between px-5 sm:px-8 lg:px-12">
        <RavenMark />
        <input ref={fileInputRef} type="file" accept="application/pdf,.pdf" className="sr-only" onChange={handleFileChange} />
        <button type="button" disabled={isUploading} onClick={() => fileInputRef.current?.click()} className="group inline-flex items-center gap-2 rounded-full bg-[#2a2825] px-4 py-2.5 text-xs font-semibold tracking-wide text-[#fbf6ed] shadow-[0_7px_16px_rgba(42,40,37,0.15)] transition duration-300 hover:-translate-y-0.5 hover:bg-[#403a34] focus:outline-none focus:ring-2 focus:ring-[#b8874e] focus:ring-offset-2 focus:ring-offset-[#f5efe5] disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0 sm:px-5">
          <svg viewBox="0 0 24 24" className="size-4 text-[#e5bb7c]" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
            <path d="M12 16V4m0 0L8.2 7.8M12 4l3.8 3.8M5 14.8v3.4A1.8 1.8 0 0 0 6.8 20h10.4a1.8 1.8 0 0 0 1.8-1.8v-3.4" />
          </svg>
          <span className="hidden sm:inline">{isUploading ? 'Archiving…' : 'Archive Document'}</span>
          <span className="sm:hidden">{isUploading ? 'Archiving…' : 'Archive'}</span>
        </button>
      </div>
    </header>
  )
}

export default Header
