import { Outlet } from 'react-router-dom'

/** Provides the shared document structure for all application pages. */
function AppLayout() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <Outlet />
    </main>
  )
}

export default AppLayout
