/** Confirms permanent removal of one archived document. */
function DeleteDocumentModal({ document, isDeleting, onCancel, onConfirm }) {
  if (!document) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-[#2a2825]/35 px-5 backdrop-blur-[2px]" role="presentation">
      <section className="w-full max-w-md rounded-2xl border border-[#dcc9b1] bg-[#fffcf6] p-6 shadow-[0_20px_48px_rgba(42,40,37,0.22)]" role="dialog" aria-modal="true" aria-labelledby="delete-document-title">
        <p className="text-[0.65rem] font-semibold uppercase tracking-[0.15em] text-[#a36e32]">Knowledge Archive</p>
        <h2 id="delete-document-title" className="mt-2 font-serif text-2xl text-[#38332e]">Delete this document from the Knowledge Archive?</h2>
        <p className="mt-3 text-sm leading-relaxed text-[#81766a]">This action will permanently remove the uploaded file and its indexed embeddings.</p>
        <p className="mt-3 truncate text-xs font-semibold text-[#62584e]">{document.filename}</p>
        <div className="mt-6 flex justify-end gap-3">
          <button type="button" disabled={isDeleting} onClick={onCancel} className="rounded-xl border border-[#d8c8b5] bg-[#fffdf8] px-4 py-2.5 text-sm font-semibold text-[#62584e] transition hover:border-[#b98246] disabled:cursor-not-allowed disabled:opacity-70">Cancel</button>
          <button type="button" disabled={isDeleting} onClick={onConfirm} className="rounded-xl bg-[#b47b3d] px-4 py-2.5 text-sm font-semibold text-white shadow-[0_8px_18px_rgba(136,87,38,0.18)] transition hover:bg-[#9e682e] disabled:cursor-not-allowed disabled:opacity-70">{isDeleting ? 'Deleting…' : 'Delete'}</button>
        </div>
      </section>
    </div>
  )
}

export default DeleteDocumentModal
