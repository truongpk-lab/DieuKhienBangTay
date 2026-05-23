import { useMemo, useState } from 'react'
import SideNavBar from './components/SideNavBar'
import TopAppBar from './components/TopAppBar'
import { mockRuntime, type AppView } from './types'
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
  const title = useMemo(() => viewTitles[activeView], [activeView])

  return (
    <main className="min-h-screen overflow-hidden text-slate-50">
      <div className="flex min-h-screen">
        <SideNavBar activeView={activeView} onChange={setActiveView} />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopAppBar title={title} runtime={mockRuntime} />
          <section className="min-h-0 flex-1 overflow-y-auto px-5 pb-5">
            {activeView === 'onboarding' && <OnboardingView />}
            {activeView === 'dashboard' && <DashboardView />}
            {activeView === 'config' && <ConfigView />}
            {activeView === 'training' && <TrainingView />}
            {activeView === 'workflow' && <WorkflowView />}
          </section>
        </div>
      </div>
    </main>
  )
}

export default App
