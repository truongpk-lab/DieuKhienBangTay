# updata.md — Kế hoạch mở rộng ACV Gesture Control thành hệ thống hoàn chỉnh

> File này dùng cho Codex/Gemini/Cursor Agent tiếp tục phát triển repo `DieuKhienBangTay` nhánh `update`.
>
> Mục tiêu chính:
>
> ```text
> 1. Tất cả nút/chức năng trên frontend phải gọi được backend hoặc logic thật.
> 2. Nút khởi động hệ thống xong phải ẩn/minimize app để người dùng bắt đầu điều khiển bằng tay.
> 3. Không phá logic điều khiển chuột cũ.
> 4. Không sửa thuật toán MouseController hiện tại nếu chưa có test bảo vệ.
> 5. Xây app theo hướng hệ thống hoàn chỉnh: frontend + backend + runtime service + adapter + profile + training + model registry + logs + settings.
> ```

---

## 0. Nguyên tắc bắt buộc trước khi sửa code

Trước khi làm bất kỳ phase nào, agent phải đọc:

```text
[ ] AGENTS.md
[ ] update.md
[ ] updata.md
[ ] ripgrep.md
[ ] ACV_GESTURE_SPEC.md
[ ] README.md
```

Bắt buộc dùng `rg` trước khi đọc/sửa file:

```powershell
rg --files
rg --files | rg "frontend|backend|actions|profiles|training|models|core|DIEU_KHIEN_CHUOT"
rg -n "startRuntime|stopRuntime|createRuntimeSocket|getRuntimeStatus|getProfiles|getGestureLogs" frontend backend
rg -n "class MouseController|MouseControlAdapter|move_to|click|scroll|mouse_down|mouse_up" .
rg -n "Bắt đầu|Khởi động|START|STOP|LƯU|Hủy|Chỉnh sửa|Thêm mới|Ghi hình|Dừng|Huấn luyện|Lưu" frontend/src
```

Không được:

```text
[ ] Không xóa demo_run.py
[ ] Không xóa hoặc đổi hành vi MouseController cũ
[ ] Không hard-code action trực tiếp trong UI
[ ] Không để nút frontend chỉ setState giả nếu nút đó là chức năng thật
[ ] Không gọi OpenCV/camera trực tiếp trong React
[ ] Không nhúng logic điều khiển chuột trong frontend
[ ] Không lưu API key hoặc config nhạy cảm trong frontend
```

Được phép:

```text
[x] Tạo file/service mới
[x] Tạo backend routers mới
[x] Tạo frontend api client mới
[x] Tạo adapter để gọi lại logic cũ
[x] Tạo runtime manager/service
[x] Tạo desktop shell/minimize helper
[x] Tạo profile/settings persistence
[x] Tạo test bảo vệ hành vi cũ
```

---

## 1. Kiến trúc mục tiêu

Luồng hệ thống chuẩn:

```text
Frontend React/Vite
  ↓ gọi REST/WebSocket
Backend FastAPI
  ↓ điều phối trạng thái
RuntimeService / TrackingService
  ↓ dùng camera + hand tracker
Gesture Engine / State Machine
  ↓ sinh gesture_event
ActionMapper
  ↓ đọc Profile JSON
MouseControlAdapter / KeyboardController
  ↓ gọi lại logic cũ
MouseController hiện tại
```

Luồng khi người dùng bấm Start:

```text
User click Start / Khởi động
  ↓
Frontend gọi POST /api/runtime/start
  ↓
Backend start camera + hand tracker + gesture engine
  ↓
Backend trả active=true
  ↓
Frontend hiển thị trạng thái Starting/Active
  ↓
Desktop shell minimize/hide app
  ↓
Người dùng điều khiển bằng tay
```

Luồng khi người dùng bấm Stop hoặc phím tắt dừng:

```text
User bấm Stop / hotkey / tray menu
  ↓
Backend POST /api/runtime/stop
  ↓
RuntimeService dừng camera + release resource
  ↓
Frontend hoặc tray hiện lại app
  ↓
Log trạng thái dừng
```

---

## 2. Phase 20 — Audit toàn bộ nút frontend

### Mục tiêu

Tìm tất cả button/select/input/slider trong frontend và phân loại:

```text
A. Nút điều hướng UI
B. Nút gọi backend runtime
C. Nút lưu cấu hình
D. Nút training/model
E. Nút chỉ mock cần chuyển thành chức năng thật
F. Nút cần confirm
G. Nút cần loading/error/success state
```

### Checklist

```text
[x] Dùng rg tìm tất cả button trong frontend/src
[x] Dùng rg tìm tất cả onClick trong frontend/src
[x] Dùng rg tìm tất cả select/input/range trong frontend/src
[x] Lập bảng Button Inventory trong docs/button_inventory.md
[x] Ghi rõ file, label, chức năng mong muốn, API cần gọi
[x] Đánh dấu nút nào đang mock
[x] Đánh dấu nút nào đã gọi backend
[x] Đánh dấu nút nào cần tạo API mới
[x] Không sửa logic chuột
[x] npm run build thành công
```

### Prompt cho agent

```text
Đọc AGENTS.md, update.md, updata.md, ripgrep.md và ACV_GESTURE_SPEC.md.
Chỉ thực hiện Phase 20 — Audit toàn bộ nút frontend.
Dùng rg tìm toàn bộ button/onClick/select/input trong frontend/src.
Tạo docs/button_inventory.md gồm: label nút, file, trạng thái hiện tại, chức năng thật cần có, API cần gọi, loading/error state.
Không sửa logic chuột hiện tại. Sau khi xong chạy npm run build nếu có sửa frontend.
```

---

## 3. Phase 21 — Chuẩn hóa frontend API client

### Mục tiêu

Tách toàn bộ API frontend thành module rõ ràng để mọi nút gọi qua một lớp duy nhất.

Cấu trúc đề xuất:

```text
frontend/src/api/
├── http.ts
├── runtimeApi.ts
├── profileApi.ts
├── trainingApi.ts
├── modelApi.ts
├── settingsApi.ts
└── websocket.ts
```

### API cần có

```text
GET    /api/health
GET    /api/runtime/status
POST   /api/runtime/start
POST   /api/runtime/stop
POST   /api/runtime/pause
POST   /api/runtime/resume
POST   /api/runtime/recenter
GET    /api/profiles
GET    /api/profiles/{id}
PUT    /api/profiles/{id}
POST   /api/profiles/{id}/activate
POST   /api/profiles
DELETE /api/profiles/{id}
GET    /api/settings
PUT    /api/settings
POST   /api/training/session/start
POST   /api/training/session/stop
POST   /api/training/sample/capture
POST   /api/training/train
POST   /api/training/save
GET    /api/models
POST   /api/models/{id}/activate
POST   /api/models/{id}/rollback
```

### Checklist

```text
[x] Tạo frontend/src/api/http.ts có timeout, error handling, base URL
[x] Tách runtime API khỏi backend.ts
[x] Tách profile API
[x] Tách training API
[x] Tách model API
[x] Tách settings API
[x] Tách websocket client
[x] Tất cả API trả typed response
[x] UI không gọi fetch trực tiếp
[x] Có fallback mock khi backend offline
[x] npm run build thành công
```

---

## 4. Phase 22 — RuntimeService backend thật

### Mục tiêu

Không để `/api/runtime/start` chỉ đổi state giả. Backend cần có service quản lý vòng đời runtime.

Cấu trúc đề xuất:

```text
backend/services/
├── runtime_service.py
├── camera_service.py
├── hand_tracker_service.py
├── gesture_engine_service.py
├── action_service.py
└── app_visibility_service.py
```

### Runtime state chuẩn

```python
RuntimeStatus = {
    "active": bool,
    "mode": "idle|starting|active|paused|stopping|error",
    "currentProfile": str,
    "currentProfileId": str,
    "currentGesture": str,
    "currentAction": str,
    "fps": int,
    "accuracy": float,
    "latency": int,
    "cameraStatus": str,
    "handStatus": str,
    "lastError": str | None,
}
```

### Checklist

```text
[x] Tạo RuntimeService singleton
[x] RuntimeService.start() idempotent: bấm Start nhiều lần không crash
[x] RuntimeService.stop() release camera/resource
[x] RuntimeService.pause()
[x] RuntimeService.resume()
[x] RuntimeService.recenter()
[x] RuntimeService cập nhật runtime_state
[x] RuntimeService ghi logs
[x] RuntimeService gọi CameraService
[x] RuntimeService gọi HandTrackerService
[x] RuntimeService gọi ActionMapper khi tracking thật sẵn sàng
[x] RuntimeService có error handling
[x] RuntimeService không sửa MouseController cũ
[x] python -m compileall . thành công
```

---

## 5. Phase 23 — Nút Start xong ẩn app để điều khiển bằng tay

### Mục tiêu

Khi người dùng bấm Start/Khởi động:

```text
1. Backend khởi động tracking thành công.
2. Frontend nhận active=true.
3. App tự ẩn/minimize xuống taskbar hoặc system tray.
4. Người dùng bắt đầu điều khiển bằng tay.
```

### Lưu ý quan trọng

React web chạy trong browser không thể tự ẩn toàn bộ app desktop một cách chuẩn nếu không có desktop shell. Vì vậy cần chọn một trong hai hướng:

```text
Hướng A — Desktop shell bằng PySide6 / Tkinter / pywebview:
Frontend chạy trong WebView, backend Python điều khiển app window.
Phù hợp nhất với project Python hiện tại.

Hướng B — Electron/Tauri:
Frontend React chạy trong desktop app, gọi window minimize/hide API.
Phù hợp nếu muốn app desktop hiện đại nhưng thêm stack build.

Hướng C — Browser fallback:
Nếu chạy bằng trình duyệt, chỉ chuyển sang Dashboard active + hiển thị hướng dẫn "hãy minimize trình duyệt".
Không thể ép browser tự ẩn an toàn.
```

### Chọn mặc định

Chọn **Hướng A — pywebview/PySide6 shell** để phù hợp repo Python.

### Cấu trúc đề xuất

```text
desktop/
├── __init__.py
├── desktop_shell.py
├── window_controller.py
├── tray_controller.py
└── hotkey_controller.py
```

### Backend API visibility

```text
POST /api/app/minimize
POST /api/app/show
POST /api/app/hide
POST /api/app/toggle
GET  /api/app/status
```

### Checklist

```text
[x] Tạo backend/routers/app_control.py
[x] Tạo backend/services/app_visibility_service.py
[x] Tạo desktop/window_controller.py
[x] Tạo desktop/tray_controller.py nếu dùng tray
[x] Tạo desktop/hotkey_controller.py
[x] Khi start runtime thành công, frontend gọi minimize/hide app
[x] Nếu đang chạy trong browser thường, hiển thị fallback hướng dẫn minimize
[x] Có nút Hiện lại app từ tray hoặc hotkey
[x] Có phím tắt khẩn cấp Stop, ví dụ Ctrl+Alt+G
[x] Stop runtime thì có thể hiện lại app
[x] Không làm mất quyền điều khiển chuột
[x] Test start -> active -> hide/minimize
[x] Test hotkey -> stop -> show
[x] python -m compileall . thành công
[x] npm run build thành công
```

### Prompt cho agent

```text
Chỉ thực hiện Phase 23 — Nút Start xong ẩn app.
Không sửa MouseController cũ.
Tạo cơ chế app visibility theo hướng desktop shell Python. Nếu chưa có desktop shell, tạo lớp window_controller/tray_controller dạng an toàn, có fallback khi chạy browser.
Khi frontend bấm Start và backend trả active=true, UI gọi API minimize/hide. Nếu minimize thất bại, hiển thị hướng dẫn người dùng minimize thủ công.
Thêm Stop hotkey/tray theo mức tối thiểu nếu khả thi.
Chạy python -m compileall . và npm run build.
```

---

## 6. Phase 24 — Làm tất cả nút Dashboard dùng được

### Nút cần hoàn thiện

```text
[x] Start/Stop runtime
[x] Clear log
[x] Recenter/calibrate
[x] Pause/Resume
[x] Open settings
[x] Switch profile nhanh
[x] Show/Hide app
[x] Emergency stop
```

### API cần nối

```text
POST /api/runtime/start
POST /api/runtime/stop
POST /api/runtime/pause
POST /api/runtime/resume
POST /api/runtime/recenter
DELETE /api/gestures/logs
POST /api/app/minimize
POST /api/app/show
```

### Checklist

```text
[x] Dashboard có loading khi Start/Stop
[x] Dashboard không cho bấm nhiều lần liên tục khi đang starting/stopping
[x] Dashboard hiển thị lỗi nếu backend fail
[x] Clear log gọi backend thật
[x] Recenter gọi backend thật
[x] Pause/Resume gọi backend thật
[x] Runtime status cập nhật qua WebSocket
[x] Khi active=true và người dùng chọn auto-hide, app minimize/hide
[x] Nếu backend offline, UI fallback mock nhưng phải ghi rõ Mock Mode
[x] npm run build thành công
```

---

## 7. Phase 25 — Làm Onboarding dùng được

### Chức năng cần thật

```text
[x] Chọn camera
[x] Chọn tay trái/phải/tự động
[x] Slider tốc độ chuột
[x] Slider sensitivity
[x] Slider smoothing
[x] Chọn profile
[x] Bắt đầu hiệu chỉnh
[x] Bỏ qua
[x] Lưu settings xuống backend
```

### API cần có

```text
GET  /api/cameras
GET  /api/settings
PUT  /api/settings
POST /api/calibration/start
POST /api/calibration/skip
POST /api/profiles/{id}/activate
```

### Checklist

```text
[x] Dropdown camera lấy từ backend
[x] Nếu không có camera, hiện cảnh báo rõ
[x] Slider cập nhật local state
[x] Bấm Bắt đầu hiệu chỉnh gọi API calibration/start
[x] Bấm Bỏ qua lưu default settings rồi chuyển dashboard
[x] Profile card chọn được và lưu active profile
[x] Settings persist ra JSON
[x] Reload app vẫn giữ settings
[x] npm run build thành công
```

---

## 8. Phase 26 — Làm ConfigView dùng được

### Chức năng cần thật

```text
[x] Chọn mục đích sử dụng/profile
[x] Chỉnh sửa gesture cho từng function
[x] Enable/disable từng function
[x] Thêm function mới
[x] Xóa function
[x] Hủy thay đổi
[x] Lưu cấu hình
[x] Validate trùng gesture_event
[x] Validate action không hợp lệ
```

### Cấu trúc profile JSON mong muốn

```json
{
  "id": "office",
  "name": "Văn phòng",
  "description": "Điều khiển tài liệu, tab, kéo thả",
  "is_active": true,
  "functions": [
    {
      "id": "drag_drop",
      "label": "Kéo thả file/thư mục",
      "enabled": true,
      "gesture": "Pinch Drag",
      "gesture_event": "drag_move",
      "action": "mouse.drag_move",
      "payload": {
        "smoothing": 0.7
      }
    }
  ]
}
```

### Checklist

```text
[x] ConfigView load profiles từ backend
[x] Chọn profile thì load mapping thật
[x] Nút Chỉnh sửa mở modal/drawer
[x] Modal cho chọn gesture_event và action
[x] Nút Thêm mới thêm function mapping
[x] Nút Hủy rollback local changes
[x] Nút Lưu gọi PUT /api/profiles/{id}
[x] Hiển thị Saved/Unsaved đúng
[x] Validate lỗi trước khi lưu
[x] Không hard-code mapping trong React
[x] npm run build thành công
```

---

## 9. Phase 27 — Làm TrainingView dùng được

### Chức năng cần thật

```text
[x] Chọn profile
[x] Chọn function/label cần train
[x] Chọn chụp ảnh hoặc quay video
[x] Nhập số mẫu
[x] Ghi hình
[x] Dừng
[x] Xem trước mẫu
[x] Huấn luyện
[x] Lưu model
[x] Hủy session
```

### API cần có

```text
POST /api/training/session/start
POST /api/training/session/stop
POST /api/training/sample/capture
GET  /api/training/samples/preview
POST /api/training/train
POST /api/training/save
POST /api/training/cancel
GET  /api/training/status
```

### Checklist

```text
[x] Training session có session_id
[x] Record gọi backend thật
[x] Stop release camera/session
[x] Preview hiển thị danh sách mẫu
[x] Train gọi pipeline thật hoặc stub rõ ràng
[x] Save ghi model registry
[x] Cancel hỏi confirm
[x] Khi sample lỗi, hiển thị lý do
[x] Progress lấy từ backend/WebSocket
[x] Không train trực tiếp trong React
[x] npm run build thành công
[x] python -m compileall . thành công
```

---

## 10. Phase 28 — Làm WorkflowView phản ánh runtime thật

### Mục tiêu

Workflow kéo-thả không chỉ là UI active cố định. Nó phải nhận state thật từ backend/state machine.

### State machine chuẩn

```text
idle
pinch_candidate
holding
dragging
released
cancelled
```

### Event chuẩn

```text
pinch_start
pinch_hold
drag_start
drag_move
drag_release
pinch_cancel
```

### Checklist

```text
[x] WorkflowView nhận runtime drag state từ WebSocket
[x] Step active đổi theo state thật
[x] Hiển thị pinch distance
[x] Hiển thị confidence
[x] Hiển thị latency
[x] Hiển thị mouse.down/move/up event log
[x] Có nút test giả lập state cho dev mode
[x] Có cảnh báo nếu hand lost khi đang dragging
[x] npm run build thành công
```

---

## 11. Phase 29 — KeyboardController cho tab/media/game

### Mục tiêu

Các action không phải chuột phải đi qua controller riêng.

Cấu trúc:

```text
actions/
├── mouse_control_adapter.py
├── keyboard_controller.py
└── action_executor.py
```

### Action cần hỗ trợ

```text
keyboard.hotkey
keyboard.press
media.play_pause
media.next
media.previous
game.left
game.right
game.jump
game.attack
game.dash
```

### Checklist

```text
[x] Tạo KeyboardController
[x] Hỗ trợ press key
[x] Hỗ trợ hotkey Ctrl+Tab / Ctrl+Shift+Tab
[x] Hỗ trợ media play/pause nếu khả thi
[x] ActionExecutor gọi đúng mouse hoặc keyboard
[x] Profile JSON không hard-code trong UI
[x] Test action bằng event giả
[x] Không ảnh hưởng MouseController cũ
[x] python -m compileall . thành công
```

---

## 12. Phase 30 — Persistence layer cho settings/profile/model

### Mục tiêu

App không mất cấu hình sau khi tắt mở.

Cấu trúc đề xuất:

```text
data/
├── settings.json
├── runtime_state.json
├── profiles/
│   ├── office.json
│   ├── entertainment.json
│   ├── game_2d.json
│   └── custom.json
└── models/
    └── model_registry.json
```

### Checklist

```text
[x] Tạo storage service đọc/ghi JSON an toàn
[x] Atomic write tránh hỏng file
[x] Backup profile trước khi ghi đè
[x] Validate schema trước khi lưu
[x] Settings lưu camera_id, hand_mode, speed, sensitivity, smoothing, auto_hide_on_start
[x] Profile lưu functions mapping
[x] Model registry lưu active model
[x] Có default seed nếu thiếu file
[x] python -m compileall . thành công
```

---

## 13. Phase 31 — WebSocket realtime chuẩn

### Mục tiêu

Frontend không polling quá nhiều. Runtime trạng thái nên đẩy qua WebSocket.

### Payload chuẩn

```json
{
  "type": "runtime_update",
  "runtime": {
    "active": true,
    "mode": "active",
    "currentProfile": "Văn phòng",
    "currentGesture": "Pinch",
    "currentAction": "Kéo thả",
    "fps": 60,
    "latency": 12
  },
  "logs": [
    {
      "time": "10:42:05",
      "type": "gesture",
      "message": "Pinch detected -> drag_start"
    }
  ]
}
```

### Checklist

```text
[x] WebSocket gửi runtime_update định kỳ
[x] WebSocket gửi gesture_event khi có event mới
[x] WebSocket gửi training_progress
[x] WebSocket gửi error/warning
[x] Frontend reconnect nếu mất kết nối
[x] UI hiển thị Backend Online/Offline
[x] Không crash nếu payload lỗi
[x] npm run build thành công
[x] python -m compileall . thành công
```

---

## 14. Phase 32 — System tray, hotkey và emergency stop

### Mục tiêu

Khi app ẩn, người dùng vẫn có cách dừng hệ thống.

### Chức năng

```text
[x] Tray icon
[x] Menu: Show App
[x] Menu: Start Tracking
[x] Menu: Stop Tracking
[x] Menu: Exit
[x] Hotkey: Ctrl+Alt+G để Stop/Show
[x] Emergency stop nếu mất kiểm soát chuột
```

### Checklist

```text
[x] Tạo tray controller
[x] Tạo hotkey controller
[x] Hotkey gọi RuntimeService.stop()
[x] Stop xong show app
[x] Exit release camera/resource
[x] Không để app chạy ngầm không kiểm soát
[x] Test trên Windows
[x] python -m compileall . thành công
```

---

## 15. Phase 33 — Error handling và cảnh báo người dùng

### Cảnh báo cần có

```text
[x] Không tìm thấy camera
[x] Camera đang bị app khác dùng
[x] Ánh sáng yếu
[x] Không phát hiện bàn tay
[x] Backend offline
[x] Model chưa active
[x] Profile mapping lỗi
[x] Training sample lỗi
[x] Runtime crash
[x] Không thể ẩn app do đang chạy browser
```

### Checklist

```text
[x] Backend trả error code/message chuẩn
[x] Frontend có toast/alert panel
[x] Log lỗi vào TerminalLog
[x] Không hiện lỗi kỹ thuật khó hiểu cho người dùng thường
[x] Có hướng dẫn fix nhanh
[x] npm run build thành công
[x] python -m compileall . thành công
```

---

## 16. Phase 34 — Test bảo vệ hệ thống

### Test bắt buộc

```text
[x] Test import backend app
[x] Test /api/health
[x] Test runtime start/stop idempotent
[x] Test profile load/save
[x] Test action mapper event giả
[x] Test MouseControlAdapter import
[x] Test drag state machine
[x] Test settings persistence
[x] Test frontend build
[x] Test demo_run.py cũ vẫn chạy/import được
```

### Lệnh test

```powershell
cd D:\github\link\DieuKhienBangTay
py -3 -m compileall .
py -3 -c "from backend.app import app; print('backend ok')"
py -3 -c "from actions.mouse_control_adapter import MouseControlAdapter; print('adapter ok')"

cd frontend
npm install
npm run build
```

Nếu có pytest:

```powershell
py -3 -m pytest tests -q
```

---

## 17. Phase 35 — Đóng gói app chạy một lệnh

### Mục tiêu

Người dùng không phải mở backend và frontend thủ công quá nhiều.

### Cách chạy mong muốn

```powershell
py -3 run_desktop.py
```

Hoặc:

```powershell
start_acv.bat
```

### Checklist

```text
[x] Tạo run_desktop.py
[x] Tự start backend FastAPI
[x] Tự mở frontend hoặc WebView
[x] Tự kiểm tra port 8000/5173
[x] Tự báo thiếu npm/node/python package
[x] Có start_acv.bat cho Windows
[x] Có stop_acv.bat nếu cần
[x] README cập nhật cách chạy
[x] Test chạy từ thư mục repo root
```

---

## 18. Button Inventory mục tiêu

| Màn hình | Nút/chức năng | Hành vi thật cần có |
|---|---|---|
| Dashboard | Start/Stop | Gọi runtime start/stop, cập nhật WebSocket, Start xong auto-hide nếu bật |
| Dashboard | Clear log | Xóa log backend và UI |
| Dashboard | Recenter | Gọi calibration/recenter |
| Dashboard | Pause/Resume | Tạm dừng tracking không tắt app |
| Dashboard | Show/Hide | Gọi app visibility service |
| Onboarding | Bắt đầu hiệu chỉnh | Gọi calibration/start |
| Onboarding | Bỏ qua | Lưu default settings, chuyển dashboard |
| Onboarding | Profile card | Set active profile |
| Config | Chỉnh sửa | Mở modal edit mapping |
| Config | Thêm mới | Tạo function mapping mới |
| Config | Hủy | Rollback local changes |
| Config | Lưu cấu hình | PUT profile vào backend |
| Training | Ghi hình | Start capture session |
| Training | Dừng | Stop capture session |
| Training | Xem trước mẫu | Load sample preview |
| Training | Huấn luyện | Gọi training pipeline |
| Training | Lưu | Lưu model vào registry |
| Training | Hủy | Confirm và cancel session |
| Workflow | Test state | Dev mode giả lập state |
| Workflow | Reset workflow | Reset state machine nếu kẹt |

---

## 19. Definition of Done mới

Một phase chỉ được đánh dấu xong khi:

```text
[x] Nút liên quan gọi được API thật hoặc có fallback mock rõ ràng
[x] Có loading state
[x] Có error state
[x] Có success state nếu cần
[x] Có log vào TerminalLog/backend logs
[x] Không phá demo_run.py cũ
[x] Không đổi hành vi MouseController cũ
[x] npm run build thành công nếu sửa frontend
[x] python -m compileall . thành công nếu sửa Python
[x] update.md hoặc updata.md được cập nhật checklist
```

Definition of Done toàn hệ thống:

```text
[x] App mở được bằng một lệnh
[x] Frontend hiển thị đủ 5 màn hình
[x] Backend health OK
[x] WebSocket runtime OK
[x] Start runtime OK
[x] Start xong app tự minimize/hide trong desktop mode
[x] Có cách show app lại bằng tray/hotkey
[x] Stop runtime OK
[x] Tất cả nút chính trên frontend dùng được
[x] Profile lưu/load được
[x] Training session chạy được ở mức tối thiểu
[x] Model registry lưu active model
[x] Kéo-thả dùng event nhỏ: pinch_hold, drag_move, drag_release
[x] MouseControlAdapter vẫn bọc MouseController cũ
[x] demo_run.py cũ không bị phá
```

---

## 22. Phase 36 — Runtime thật camera + mic Gemini

### Checklist

```text
[x] CameraService dùng OpenCV thật, không trả mock camera
[x] HandTrackerService bọc core HandTracker/FeatureExtractor/GestureClassifier/TemporalFilter
[x] Runtime start tạo tracking loop nền và release camera khi stop
[x] Runtime/WebSocket có micStatus, aiStatus, lastVoiceCommand, lastTranscript, commandConfidence
[x] Thêm MicrophoneService và API /api/mic/status/devices/start/stop
[x] Thêm GeminiCommandService và API /api/ai/command
[x] Gemini API key đọc từ GEMINI_API_KEY/GOOGLE_API_KEY, không lưu trong frontend
[x] Voice command chỉ execute intent whitelist và confidence >= 0.7
[x] Frontend Dashboard không tự bật mock runtime khi backend lỗi
[x] Onboarding chọn microphone và bật/tắt voice command
[x] start_acv.bat vẫn là lệnh chính qua run_desktop.py
[x] README và requirements cập nhật google-genai/sounddevice
```

---

## 20. Prompt tổng để tiếp tục trong cửa sổ mới

```text
Bạn là coding agent cho repo DieuKhienBangTay nhánh update.

Hãy đọc các file:
1. AGENTS.md
2. update.md
3. updata.md
4. ripgrep.md
5. ACV_GESTURE_SPEC.md
6. README.md

Mục tiêu hệ thống:
- Biến toàn bộ frontend từ mock UI thành app dùng được thật.
- Tất cả nút chức năng phải gọi backend/service tương ứng.
- Nút Start/Khởi động sau khi runtime active phải ẩn/minimize app để bắt đầu điều khiển bằng tay.
- Phải có cách hiện lại app bằng tray/hotkey hoặc fallback rõ ràng.
- Không sửa thuật toán MouseController hiện tại.
- Không phá demo_run.py.
- Mọi action đi qua: Gesture Event -> ActionMapper -> MouseControlAdapter/KeyboardController.
- Dùng rg trước khi đọc/sửa file.

Chỉ thực hiện phase tôi yêu cầu: PHASE <điền số phase>.
Sau khi làm xong phải báo:
1. Files changed
2. Chức năng hoàn thành
3. Lệnh test đã chạy
4. Checklist đã cập nhật
5. Rủi ro còn lại
```

---

## 21. Thứ tự ưu tiên nên làm tiếp

Nên làm theo thứ tự này để app thật sự chạy được:

```text
1. Phase 20 — Audit toàn bộ nút frontend
2. Phase 21 — Chuẩn hóa frontend API client
3. Phase 22 — RuntimeService backend thật
4. Phase 24 — Dashboard buttons dùng được
5. Phase 23 — Start xong ẩn/minimize app
6. Phase 25 — Onboarding dùng được
7. Phase 26 — ConfigView dùng được
8. Phase 27 — TrainingView dùng được
9. Phase 28 — WorkflowView runtime thật
10. Phase 30 — Persistence layer
11. Phase 31 — WebSocket realtime chuẩn
12. Phase 32 — Tray/hotkey/emergency stop
13. Phase 34 — Test bảo vệ hệ thống
14. Phase 35 — Đóng gói chạy một lệnh
```
