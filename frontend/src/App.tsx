import { useEffect, useMemo, useState } from 'react'
import { createRuntimeSocket, getGestureLogs, getProfiles, getRuntimeStatus } from './api/backend'
import SideNavBar from './components/SideNavBar'
import TopAppBar from './components/TopAppBar'
import { mockLogs, mockProfiles, mockRuntime, type AppView, type GestureLog, type Profile, type RuntimeStatus } from './types'
import ConfigView from './views/ConfigView'
import DashboardView from './views/DashboardView'
import OnboardingView from './views/OnboardingView'
import TrainingView from './views/TrainingView'
import WorkflowView from './views/WorkflowView'

const viewTitles: Record<AppView, string> = {
  onboarding: 'Thiết lập ban đầu',
  dashboard: 'Dashboard trung tâm',
  config: 'Thiết lập cấu hình',
  training: 'Huấn luyện cử chỉ',
  workflow: 'Quy trình kéo thả',
}

function App() {
  const [activeView, setActiveView] = useState<AppView>('dashboard')
  const [runtime, setRuntime] = useState<RuntimeStatus>(mockRuntime)
  const [profiles, setProfiles] = useState<Profile[]>(mockProfiles)
  const [logs, setLogs] = useState<GestureLog[]>(mockLogs)
  const [backendOnline, setBackendOnline] = useState(false)
  const title = useMemo(() => viewTitles[activeView], [activeView])

  useEffect(() => {
    let canceled = false

    async function loadBackendSnapshot() {
      try {
        const [runtimeStatus, profileList, gestureLogs] = await Promise.all([
          getRuntimeStatus(),
          getProfiles(),
          getGestureLogs(),
        ])
        if (!canceled) {
          setRuntime(runtimeStatus)
          setProfiles(profileList)
          setLogs(gestureLogs)
          setBackendOnline(true)
        }
      } catch {
        if (!canceled) {
          setRuntime(mockRuntime)
          setProfiles(mockProfiles)
          setLogs(mockLogs)
          setBackendOnline(false)
        }
      }
    }

    loadBackendSnapshot()
    const interval = window.setInterval(loadBackendSnapshot, 5000)
    return () => {
      canceled = true
      window.clearInterval(interval)
    }
  }, [])

  useEffect(() => {
    let socket: WebSocket | null = null
    try {
      socket = createRuntimeSocket()
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data) as { runtime?: RuntimeStatus; logs?: GestureLog[] }
        if (payload.runtime) {
          setRuntime(payload.runtime)
          setBackendOnline(true)
        }
        if (payload.logs) {
          setLogs(payload.logs)
        }
      }
      socket.onerror = () => setBackendOnline(false)
    } catch {
      setBackendOnline(false)
    }

    return () => socket?.close()
  }, [])

  return (
    <main className="min-h-screen overflow-hidden text-slate-50">
      <div className="flex min-h-screen">
        <SideNavBar activeView={activeView} onChange={setActiveView} />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopAppBar title={title} runtime={runtime} backendOnline={backendOnline} />
          <section className="min-h-0 flex-1 overflow-y-auto px-4 pb-24 sm:px-5 lg:pb-5">
            {activeView === 'onboarding' && <OnboardingView />}
            {activeView === 'dashboard' && <DashboardView runtime={runtime} logs={logs} onRuntimeChange={setRuntime} />}
            {activeView === 'config' && <ConfigView profiles={profiles} />}
            {activeView === 'training' && <TrainingView profiles={profiles} />}
            {activeView === 'workflow' && <WorkflowView />}
          </section>
        </div>
      </div>
    </main>
  )
}

export default App
