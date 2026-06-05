# ripgrep.md — UI-First + Preserve MouseController Code Search Playbook

> Hướng dẫn Codex dùng `ripgrep` (`rg`) để tìm code nhanh, tiết kiệm token và tránh sửa nhầm file.
>
> Chiến lược:
>
> ```text
> UI-FIRST
> + được phép chia nhỏ/đổi tên/tổ chức lại app
> + giữ nguyên behavior/hiệu suất MouseController hiện tại
> + sau UI mới bọc MouseController bằng adapter
> ```

---

## 1. Kiểm tra đủ file hướng dẫn

Trước khi làm bất kỳ phase nào:

```powershell
rg --files | rg "AGENTS.md|update.md|ripgrep.md|ACV_GESTURE_SPEC.md"
```

Nếu làm UI, kiểm tra spec giao diện:

```powershell
rg -n "Cyber-Clean|Breathable Void|Kinetic Glass|Deep Obsidian|Neon Cyan|Glassmorphism|Bento Grid" ACV_GESTURE_SPEC.md
rg -n "Onboarding|Dashboard|Configuration|Training|Hướng Dẫn Thao Tác|Hướng dẫn thao tác" ACV_GESTURE_SPEC.md
rg -n "Tailwind|Framer Motion|Lucide React|HandSkeleton|TerminalLog" ACV_GESTURE_SPEC.md
```

---

## 2. Kiểm tra rg đã cài

```powershell
rg --version
where.exe rg
```

Nếu PowerShell chưa nhận `rg`:

```powershell
& "$env:LOCALAPPDATA\Microsoft\WinGet\Links\rg.exe" --version
$env:Path += ";$env:LOCALAPPDATA\Microsoft\WinGet\Links"
rg --version
```

---

## 3. Nguyên tắc dùng rg

```text
[ ] Không đọc toàn bộ repo khi chưa cần
[ ] Không paste file dài nếu chỉ cần vài dòng
[ ] Dùng rg để tìm file/symbol trước
[ ] Chỉ mở file liên quan
[ ] Sau khi sửa, dùng rg kiểm tra lại
```

Xem cấu trúc repo:

```powershell
rg --files -g "!node_modules" -g "!dist" -g "!build" -g "!__pycache__" -g "!data/raw" -g "!models"
```

---

# UI-FIRST SEARCH COMMANDS

---

## 4. Phase 1 — Frontend scaffold

Kiểm tra frontend đã tồn tại chưa:

```powershell
rg --files | rg "package.json|vite.config|frontend|src/main|src/App|index.css"
```

Kiểm tra React/Vite:

```powershell
rg -n "react|vite|typescript|tailwind|lucide|framer" -g "package.json" -g "*.ts" -g "*.tsx" -g "*.css"
```

Kiểm tra file chuột cũ để tránh sửa nhầm:

```powershell
rg --files | rg "DIEU_KHIEN_CHUOT|demo_run.py|train_model.py|collect_hand_gesture_data.py"
rg -n "class MouseController"
```

Trong Phase 1 không sửa các file này.

---

## 5. Phase 2 — Design system Cyber-Clean

```powershell
rg --files | rg "index.css|tailwind|vite.config|postcss"
rg -n "@import \"tailwindcss\"|glass-panel|brand-cyan|brand-blue|brand-obsidian|glow-text" frontend src
rg -n "Kinetic Glass|Deep Obsidian|#00f2ff|#4b8eff|Glassmorphism|glass-panel" ACV_GESTURE_SPEC.md
```

Sau khi sửa:

```powershell
rg -n "glass-panel|glass-inner|glow-text|glow-btn-active|brand-cyan|brand-blue|brand-obsidian" frontend/src/index.css
```

---

## 6. Phase 3 — App shell, navigation và mock data

```powershell
rg --files frontend/src | rg "App.tsx|types.ts|components|views"
rg -n "AppView|Profile|GestureLog|FunctionMapping|useState|SideNavBar|TopAppBar" frontend/src
```

Sau khi tạo:

```powershell
rg --files frontend/src | rg "SideNavBar|TopAppBar|types"
rg -n "onboarding|dashboard|config|training|workflow" frontend/src/App.tsx frontend/src/types.ts
rg -n "mockRuntime|mockLogs|mockProfiles" frontend/src
```

---

## 7. Phase 4 — Dashboard UI

```powershell
rg -n "Dashboard Trung Tâm|Dashboard View|Nguồn Video|LIVE|FPS|Độ chính xác|Terminal" ACV_GESTURE_SPEC.md
rg --files frontend/src | rg "DashboardView|HandSkeleton|HandCameraHUD|TerminalLog"
```

Sau khi tạo:

```powershell
rg -n "HandSkeleton|HandCameraHUD|TerminalLog|DashboardView" frontend/src
rg -n "ACV-Hand-v2.1|1920x1080|LIVE|FPS|98.5|Pinch|Kéo thả" frontend/src
```

---

## 8. Phase 5 — Onboarding UI

```powershell
rg -n "Thiết Lập Ban Đầu|Onboarding|Webcam|Tay trái|Tay phải|Tự động|Tốc độ chuột|Độ nhạy|Smoothing" ACV_GESTURE_SPEC.md
rg --files frontend/src | rg "OnboardingView"
rg -n "OnboardingView|Thiết lập ban đầu|Bắt đầu hiệu chỉnh|Bỏ qua|Văn phòng|Giải trí|Game 2D|Tùy chỉnh" frontend/src
```

---

## 9. Phase 6 — Configuration / Setup Profile UI

```powershell
rg -n "Thiết Lập Cấu Hình|Configuration|Di chuyển chuột|Click trái|Click phải|Kéo thả|Cuộn trang|Tấn công" ACV_GESTURE_SPEC.md
rg --files frontend/src | rg "ConfigView"
rg -n "ConfigView|Thiết lập cấu hình|LƯU CẤU HÌNH|Chỉnh sửa|Di chuyển chuột|Click trái|Kéo thả" frontend/src
```

---

## 10. Phase 7 — Gesture Training UI

```powershell
rg -n "Huấn Luyện Cử Chỉ|Training View|Chụp ảnh|Quay video|24 / 30|Ghi hình|Dừng|Huấn luyện|Lưu" ACV_GESTURE_SPEC.md
rg --files frontend/src | rg "TrainingView"
rg -n "TrainingView|Huấn luyện cử chỉ|Chụp ảnh|Quay video|Ghi hình|Dừng|Xem trước mẫu|Kẹp ngón" frontend/src
```

---

## 11. Phase 8 — Hướng Dẫn Thao Tác UI

```powershell
rg -n "Hướng Dẫn Thao Tác|Hướng dẫn thao tác|Văn phòng|Giải trí|Game 2D|Tùy chỉnh|HandSkeleton|Checklist trước khi dùng|Lỗi thường gặp" ACV_GESTURE_SPEC.md
rg --files frontend/src | rg "WorkflowView"
rg -n "WorkflowView|Hướng dẫn thao tác|Văn phòng|Giải trí|Game 2D|Tùy chỉnh|Sensor: Active" frontend/src
```

---

## 12. Phase 9 — UI polish/build

```powershell
rg -n "TODO|FIXME|any|console.log|NotImplemented" frontend/src
rg -n "from ['\"]|import " frontend/src
cd frontend
npm run build
```

Kiểm tra không sửa logic chuột:

```powershell
git diff -- DIEU_KHIEN_CHUOT
git diff -- demo_run.py
rg -n "class MouseController"
```

---

# SAU UI: GIỮ VÀ BỌC MOUSECONTROLLER HIỆN TẠI

---

## 13. Tìm MouseController hiện tại

Dùng khi tới phase adapter, không dùng trong phase UI.

```powershell
rg -n "class MouseController"
rg -n "def .*move|def .*click|def .*scroll|def .*down|def .*up"
rg -n "pyautogui|win32api|win32con|mouseDown|mouseUp|click|scroll"
```

Tìm file chứa demo:

```powershell
rg --files | rg "demo_run|DIEU_KHIEN_CHUOT"
```

Mục tiêu:

```text
[ ] Xác định MouseController hiện tại nằm ở đâu
[ ] Xác định hàm move/click/scroll/down/up
[ ] Không sửa behavior cũ
```

---

## 14. Phase 10 — Profile JSON/schema

```powershell
rg -n "mockProfiles|FunctionMapping|Văn phòng|Giải trí|Game 2D|Tùy chỉnh" frontend/src
rg --files | rg "profiles|configs|json"
```

Sau khi tạo:

```powershell
rg --files profiles
rg -n "\"id\": \"office\"|\"id\": \"entertainment\"|\"id\": \"game_2d\"" profiles
rg -n "\"gesture_event\"|\"action\"|\"functions\"" profiles
```

---

## 15. Phase 11 — MouseControlAdapter

Tìm MouseController gốc:

```powershell
rg -n "class MouseController"
rg -n "mouse_down|mouse_up|move|click|scroll|pyautogui|win32api"
```

Sau khi tạo adapter:

```powershell
rg -n "MouseControlAdapter|MouseController" actions
rg -n "def move|def click|def right_click|def scroll|def mouse_down|def mouse_up" actions
```

Test import:

```powershell
python -c "from actions.mouse_control_adapter import MouseControlAdapter; print('adapter ok')"
```

Kiểm tra logic cũ không bị phá:

```powershell
git diff -- DIEU_KHIEN_CHUOT
git diff -- demo_run.py
```

---

## 16. Phase 12 — ActionMapper nối adapter

```powershell
rg -n "ActionMapper|gesture_event|mouse.move|mouse.left_click|mouse.down|mouse.up"
rg -n "MouseControlAdapter"
```

Test:

```powershell
python -c "from profiles.action_mapper import ActionMapper; print('mapper ok')"
```

---

## 17. Phase 13 — Pinch Drag Drop State Machine

```powershell
rg -n "drag|mouseDown|mouseUp|fist|hold|release|pinch"
rg -n "landmark|thumb|index|distance|palm"
rg -n "distance|euclidean|norm|sqrt|hypot"
```

Sau khi implement:

```powershell
rg -n "PinchDragDropStateMachine"
rg -n "pinch_start|pinch_hold|drag_start|drag_move|drag_release|pinch_cancel"
```

---

## 18. Phase 14 — Thao tác theo profile

```powershell
rg -n "office|entertainment|game_2d|gesture_event|action" profiles
rg -n "hotkey|ctrl|tab|play|pause|volume|attack|jump|dash"
```

Đảm bảo không hard-code trong demo:

```powershell
rg -n "if .*gesture|elif .*gesture|if .*stable_label|elif .*stable_label" DIEU_KHIEN_CHUOT
```

---

## 19. Phase 15 — Dataset collector

```powershell
rg --files | rg "collect|dataset|process|train"
rg -n "collect|sample|label|dataset|csv|json|pickle|landmarks"
rg -n "cv2.imwrite|VideoWriter|frames|timestamp"
```

Sau khi implement:

```powershell
rg -n "DatasetCollector|ImageSampleCollector|VideoSampleCollector"
rg -n "sample_id|function_id|gesture_label|data_type|created_at"
```

---

## 20. Phase 16 — Training pipeline

```powershell
rg --files | rg "train|model|evaluate"
rg -n "SVC|RandomForest|MLP|joblib|pickle|accuracy|classification_report|confusion_matrix"
rg -n "train_test_split|fit|predict|score"
```

Sau khi implement:

```powershell
rg -n "train_static_gesture|train_dynamic_gesture|evaluate_model"
rg -n "accuracy|macro_f1|precision|recall|confusion_matrix"
```

---

## 21. Phase 17 — Model registry

```powershell
rg --files | rg "models|trained_model|joblib|pkl|onnx|label_mapping|registry"
```

Sau khi implement:

```powershell
rg -n "ModelRegistry|model_id|active|rollback|set_active|metrics|sample_count"
rg --files models
```

---

## 22. Phase 18 — Backend/frontend integration

```powershell
rg --files | rg "app.py|main.py|server.py|FastAPI|websocket|package.json|vite.config|App.tsx"
rg -n "FastAPI|WebSocket|uvicorn|socket|subprocess|api"
rg -n "fetch|WebSocket|axios|useEffect|useState" frontend/src
```

Sau khi implement:

```powershell
rg -n "start_tracking|stop_tracking|current_gesture|current_action|profile"
rg -n "WebSocket|FastAPI|uvicorn|fetch"
```

---

## 23. Final safety check

Trước khi báo hoàn thành:

```powershell
rg -n "\[ \]" update.md
python -m compileall .
cd frontend
npm run build
```

Kiểm tra MouseController không bị phá:

```powershell
rg -n "class MouseController"
git diff -- DIEU_KHIEN_CHUOT
git diff -- demo_run.py
```

Nếu phase không yêu cầu sửa logic chuột, `git diff -- DIEU_KHIEN_CHUOT` và `git diff -- demo_run.py` nên không có thay đổi.
