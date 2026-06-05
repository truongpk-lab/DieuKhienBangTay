import { useEffect, useMemo, useState } from 'react'
import { getProfiles } from './api/profileApi'
import { getGestureLogs, getRuntimeStatus } from './api/runtimeApi'
import { createRuntimeSocket, type RuntimeSocketMessage } from './api/websocket'
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
  dashboard: 'Bảng điều khiển trung tâm',
  config: 'Thiết lập cấu hình',
  training: 'Huấn luyện cử chỉ',
  workflow: 'Hướng dẫn thao tác',
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
      } catch (error) {
        if (!canceled) {
          setBackendOnline(false)
          setRuntime((current) => ({
            ...current,
            lastError: error instanceof Error ? error.message : 'Backend chưa kết nối',
            trackingStatus: 'Backend chưa kết nối',
          }))
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
    let reconnectTimer = 0
    let closed = false
    try {
      const connect = () => {
        socket = createRuntimeSocket()
      socket.onmessage = (event) => {
        let payload: RuntimeSocketMessage
        try {
          payload = JSON.parse(event.data) as RuntimeSocketMessage
        } catch {
          setBackendOnline(false)
          return
        }
        if (payload.type === 'runtime_update' && payload.runtime) {
          setRuntime(payload.runtime)
          setBackendOnline(true)
        }
        if (payload.logs) {
          setLogs(payload.logs)
        }
      }
        socket.onerror = () => setBackendOnline(false)
        socket.onclose = () => {
          if (!closed) {
            setBackendOnline(false)
            reconnectTimer = window.setTimeout(connect, 1500)
          }
        }
      }
      connect()
    } catch {
      setBackendOnline(false)
    }

    return () => {
      closed = true
      window.clearTimeout(reconnectTimer)
      socket?.close()
    }
  }, [])

  return (
    <main className="h-screen overflow-hidden text-slate-50">
      <div className="flex h-full min-h-0">
        <SideNavBar activeView={activeView} onChange={setActiveView} />
        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <TopAppBar title={title} runtime={runtime} backendOnline={backendOnline} />
          {(!backendOnline || runtime.lastError) && (
            <div className="mx-4 mt-3 rounded-2xl border border-amber-300/20 bg-amber-300/10 px-4 py-3 text-sm text-amber-100 sm:mx-5">
              {runtime.lastError || 'Backend chưa kết nối; chức năng thật đang bị tạm khóa cho đến khi API chạy lại.'}
            </div>
          )}
          <section className="min-h-0 flex-1 overflow-y-auto px-4 pb-24 sm:px-5 lg:pb-5">
            {activeView === 'onboarding' && <OnboardingView profiles={profiles} onComplete={() => setActiveView('dashboard')} />}
            {activeView === 'dashboard' && (
              <DashboardView
                runtime={runtime}
                logs={logs}
                profiles={profiles}
                onRuntimeChange={setRuntime}
                onLogsChange={setLogs}
                onOpenSettings={() => setActiveView('config')}
              />
            )}
            {activeView === 'config' && <ConfigView profiles={profiles} />}
            {activeView === 'training' && <TrainingView profiles={profiles} />}
            {activeView === 'workflow' && <WorkflowView runtime={runtime} logs={logs} profiles={profiles} />}
          </section>
        </div>
      </div>
    </main>
  )
}

export default App
