export type AppView =
  | 'onboarding'
  | 'dashboard'
  | 'config'
  | 'training'
  | 'workflow'

export type TrackingStatus = 'idle' | 'active' | 'paused'

export type GestureLog = {
  time: string
  type: 'system' | 'detection' | 'gesture'
  message: string
}

export type RuntimeStatus = {
  currentProfile: string
  currentGesture: string
  currentAction: string
  fps: number
  accuracy: number
  trackingStatus: string
  latency: number
}

export type Profile = {
  id: string
  name: string
  description: string
}

export type FunctionMapping = {
  id: string
  label: string
  gesture: string
  action?: string
  tone?: 'cyan' | 'blue' | 'red'
}

export const mockProfiles: Profile[] = [
  {
    id: 'office',
    name: 'Văn phòng',
    description: 'Điều hướng desktop, tài liệu và kéo thả hằng ngày.',
  },
  {
    id: 'entertainment',
    name: 'Giải trí',
    description: 'Điều khiển phát media, chuyển bài và âm lượng.',
  },
  {
    id: 'game_2d',
    name: 'Game 2D',
    description: 'Ánh xạ hành động nhanh cho game platformer.',
  },
  {
    id: 'custom',
    name: 'Tùy chỉnh',
    description: 'Bộ cấu hình cá nhân do người dùng tinh chỉnh.',
  },
]

export const mockRuntime: RuntimeStatus = {
  currentProfile: 'Văn phòng',
  currentGesture: 'Pinch',
  currentAction: 'Kéo thả',
  fps: 60,
  accuracy: 98.5,
  trackingStatus: 'Active Tracking',
  latency: 12,
}

export const mockLogs: GestureLog[] = [
  { time: '10:42:01', type: 'system', message: 'Camera initialized' },
  { time: '10:42:03', type: 'detection', message: 'Hand detected: Right' },
  { time: '10:42:05', type: 'gesture', message: 'Pinch detected -> drag_start' },
]

export const mockFunctionMappings: FunctionMapping[] = [
  { id: 'move', label: 'Di chuyển chuột', gesture: 'Open Palm Move', action: 'mouse.move' },
  { id: 'left_click', label: 'Click trái', gesture: 'Pinch Index', action: 'mouse.left_click' },
  { id: 'right_click', label: 'Click phải', gesture: 'Pinch Middle', action: 'mouse.right_click' },
  { id: 'drag_drop', label: 'Kéo thả file/thư mục', gesture: 'Closed Fist Hold', action: 'mouse.drag' },
  { id: 'scroll', label: 'Cuộn trang', gesture: 'Two Finger Swipe', action: 'mouse.scroll' },
  { id: 'switch_tab', label: 'Chuyển tab', gesture: 'Three Finger Left/Right', action: 'keyboard.switch_tab' },
  { id: 'play_pause', label: 'Play/Pause', gesture: 'Open Close Palm', action: 'media.play_pause' },
  { id: 'game_attack', label: 'Tấn công trong game', gesture: 'Rapid Punch', action: 'game.attack', tone: 'red' },
]
