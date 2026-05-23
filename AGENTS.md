# AGENTS.md — ACV Gesture Control UI-First Agent Rules

> Luật bắt buộc cho Codex/AI Coding Agent khi phát triển **ACV Gesture Control**.
>
> Chiến lược hiện tại:
>
> ```text
> UI-FIRST
> + xây giao diện hiện đại trước
> + được phép chia nhỏ module / đổi tên / tổ chức lại thành app hoàn chỉnh
> + giữ nguyên hành vi và hiệu suất của MouseController/hàm điều khiển chuột hiện tại
> + không sửa thuật toán điều khiển chuột nếu không có test tương đương
> + sau UI mới tạo adapter để gọi lại logic chuột cũ
> ```

---

## 1. Tài liệu bắt buộc phải đọc

Trước khi sửa code, agent phải đọc theo thứ tự:

```text
[ ] AGENTS.md
[ ] update.md
[ ] ripgrep.md
[ ] ACV_GESTURE_SPEC.md
```

`ACV_GESTURE_SPEC.md` là file chuẩn giao diện chính.

Thứ tự ưu tiên:

```text
1. ACV_GESTURE_SPEC.md — chuẩn UI/UX, layout, theme, component
2. update.md — pipeline phase, task, checklist
3. AGENTS.md — luật làm việc của agent
4. ripgrep.md — cách tìm code nhanh bằng rg
```

Nếu thiếu `ACV_GESTURE_SPEC.md`, không được làm phase UI.

---

## 2. Quy tắc bảo toàn logic chuột hiện tại

Project hiện tại có hàm/class điều khiển chuột đang hoạt động tốt. Agent **được phép tổ chức lại app**, nhưng phải bảo toàn behavior.

### Được phép

```text
[x] Tạo frontend/ mới
[x] Tạo ui/ mới
[x] Tạo profiles/ mới
[x] Tạo actions/ mới
[x] Tạo adapter/wrapper gọi lại MouseController cũ
[x] Tạo file mới để chia nhỏ module
[x] Đổi tên module mới do agent tạo
[x] Tạo compatibility layer để demo cũ vẫn chạy
[x] Tạo test bảo vệ behavior cũ
[x] Tạo app hoàn chỉnh theo kiến trúc mới
```

### Không được phép nếu chưa có yêu cầu rõ ràng và test tương đương

```text
[ ] Không đổi thuật toán move/click/scroll/mouse_down/mouse_up hiện tại
[ ] Không làm giảm smoothing/latency/performance của điều khiển chuột
[ ] Không xóa MouseController cũ
[ ] Không xóa demo_run.py cũ
[ ] Không đổi tên file cũ làm demo cũ không chạy
[ ] Không thay đổi tham số điều khiển chuột đang hoạt động tốt nếu chưa được yêu cầu
[ ] Không thay pyautogui/win32api logic bằng logic mới nếu không có test
```

### Nguyên tắc refactor an toàn

Nếu cần tái cấu trúc:

```text
1. Copy/bọc logic cũ bằng adapter trước.
2. Giữ demo_run.py cũ chạy được.
3. Tạo API mới gọi adapter.
4. Không đổi hành vi chuột cũ.
5. Chạy test import + test demo nếu có thể.
```

Kiến trúc mong muốn:

```text
Existing MouseController
  → MouseControlAdapter
  → ActionMapper
  → Profile JSON
  → Backend API/WebSocket
  → Frontend UI
```

---

## 3. Hướng phát triển UI-FIRST

Thứ tự phát triển:

```text
UI mock trước
→ mock data
→ profile/config UI
→ training UI
→ workflow UI
→ sau đó mới nối vào core Python hiện tại
→ sau đó mới thêm thao tác mới/training/model
```

Trong các phase UI, ưu tiên chỉ tạo/sửa:

```text
frontend/
frontend/src/
package.json
vite.config.*
index.css
update.md checklist
```

Không sửa logic chuột trong phase UI.

---

## 4. Nguyên tắc dùng ripgrep tiết kiệm token

Agent phải dùng `rg` trước khi đọc/sửa code.

Không được:

```text
[ ] Đọc toàn bộ repo nếu chưa cần
[ ] Paste file dài vào context
[ ] Sửa nhiều phase cùng lúc
[ ] Tự ý đổi kiến trúc ngoài update.md
[ ] Tự ý xóa file cũ
```

Luôn dùng:

```powershell
rg --files
rg --files | rg "AGENTS.md|update.md|ripgrep.md|ACV_GESTURE_SPEC.md"
rg --files | rg "frontend|package.json|vite.config|src|App.tsx"
```

Khi cần kiểm tra MouseController hiện tại:

```powershell
rg -n "class MouseController"
rg -n "pyautogui|win32api|win32con|mouseDown|mouseUp|click|scroll"
```

---

## 5. Mục tiêu giao diện

Giao diện phải theo `ACV_GESTURE_SPEC.md`:

```text
Cyber-Clean
Breathable Void
Kinetic Glass
Deep Obsidian background
Neon Cyan + Electric Blue
Glassmorphism
Bento Grid
Rounded cards
Framer Motion transitions
Lucide React icons
SVG hand skeleton 21 points
Terminal-style realtime log
```

Stack yêu cầu:

```text
React
TypeScript
Vite
Tailwind CSS v4
Framer Motion
Lucide React
```

Nếu repo chưa có frontend, tạo mới:

```text
frontend/
```

---

## 6. UI bắt buộc có 5 màn hình

```text
[ ] OnboardingView
[ ] DashboardView
[ ] ConfigView
[ ] TrainingView
[ ] WorkflowView
```

### OnboardingView

```text
[ ] Chọn camera
[ ] Chọn tay trái/phải/tự động
[ ] Slider tốc độ chuột
[ ] Slider sensitivity
[ ] Slider smoothing
[ ] Chọn profile: Văn phòng, Giải trí, Game 2D, Tùy chỉnh
[ ] Nút Bắt đầu hiệu chỉnh
[ ] Nút Bỏ qua
```

### DashboardView

```text
[ ] Camera preview mock
[ ] Hand skeleton overlay
[ ] LIVE badge
[ ] FPS card
[ ] Accuracy card
[ ] Current profile
[ ] Current gesture
[ ] Current action
[ ] Start/Stop button
[ ] Terminal gesture log
```

### ConfigView

```text
[ ] Dropdown chọn mục đích sử dụng
[ ] Grid function cards
[ ] Card Di chuyển chuột
[ ] Card Click trái
[ ] Card Click phải
[ ] Card Kéo thả file/thư mục
[ ] Card Cuộn trang
[ ] Card Chuyển tab
[ ] Card Play/Pause
[ ] Card Tấn công trong game
[ ] Card thêm mới
[ ] Nút Chỉnh sửa
[ ] Nút Hủy
[ ] Nút LƯU CẤU HÌNH
```

### TrainingView

```text
[ ] Chọn profile
[ ] Chọn function cần train
[ ] Chọn Chụp ảnh / Quay video
[ ] Nhập số lượng mẫu
[ ] Camera HUD mock
[ ] Hand skeleton overlay
[ ] Instruction banner
[ ] Progress bar
[ ] Record / Stop
[ ] Preview Samples
[ ] Train
[ ] Save
[ ] Cancel
```

### WorkflowView

```text
[ ] Stepper 5 bước kéo-thả
[ ] Kẹp ngón
[ ] Giữ
[ ] Di chuyển tay
[ ] Thả ngón
[ ] Hoàn thành
[ ] Bước active có radar/pulse
[ ] Badge Sensor: Active
[ ] Badge Latency
```

---

## 7. Component bắt buộc

```text
frontend/src/
├── main.tsx
├── App.tsx
├── index.css
├── types.ts
├── components/
│   ├── SideNavBar.tsx
│   ├── TopAppBar.tsx
│   ├── HandSkeleton.tsx
│   ├── HandCameraHUD.tsx
│   └── TerminalLog.tsx
└── views/
    ├── OnboardingView.tsx
    ├── DashboardView.tsx
    ├── ConfigView.tsx
    ├── TrainingView.tsx
    └── WorkflowView.tsx
```

---

## 8. Mock data trong phase UI

Trong phase UI, dùng mock data, chưa cần backend thật.

```ts
const mockRuntime = {
  currentProfile: "Văn phòng",
  currentGesture: "Pinch",
  currentAction: "Kéo thả",
  fps: 60,
  accuracy: 98.5,
  trackingStatus: "Active Tracking",
  latency: 12,
};
```

```ts
const mockLogs = [
  { time: "10:42:01", type: "system", message: "Camera initialized" },
  { time: "10:42:03", type: "detection", message: "Hand detected: Right" },
  { time: "10:42:05", type: "gesture", message: "Pinch detected → drag_start" },
];
```

---

## 9. Sau UI mới nối vào MouseController hiện tại

Sau khi UI hoàn thiện, agent mới được tạo adapter để dùng lại MouseController hiện tại.

Quy tắc:

```text
[ ] Không viết lại MouseController từ đầu
[ ] Không đổi hành vi click/move/scroll cũ nếu không cần
[ ] Tạo wrapper/adapter để gọi lại hàm cũ
[ ] Nếu chia nhỏ file, phải giữ backward compatibility
[ ] demo_run.py cũ vẫn phải chạy được
```

Adapter đề xuất:

```text
actions/mouse_control_adapter.py
```

API adapter:

```text
move(...)
left_click(...)
right_click(...)
scroll(...)
mouse_down(...)
mouse_up(...)
drag_start(...)
drag_move(...)
drag_release(...)
```

---

## 10. Thao tác mới được thêm sau UI

Sau UI có thể thêm:

```text
[ ] Profile Văn phòng
[ ] Profile Giải trí
[ ] Profile Game 2D
[ ] Pinch hold
[ ] Drag move
[ ] Drag release
[ ] Swipe left/right/up/down
[ ] Play/Pause
[ ] Next/Previous
[ ] Game attack/jump/dash
[ ] Training gesture mới
```

Các thao tác mới phải đi qua:

```text
Gesture Event → ActionMapper → MouseControlAdapter/KeyboardController
```

Không hard-code trong `demo_run.py`.

---

## 11. Kéo-thả sau này phải chia event nhỏ

Không làm kéo-thả thành một gesture lớn duy nhất.

Đúng:

```text
pinch_hold → mouse.down
drag_move → mouse.move
drag_release → mouse.up
```

State machine:

```text
idle
pinch_candidate
holding
dragging
released
```

Event:

```text
pinch_start
pinch_hold
drag_start
drag_move
drag_release
pinch_cancel
```

---

## 12. Test bắt buộc

Sau mỗi phase UI:

```powershell
cd frontend
npm install
npm run build
```

Sau mỗi phase Python sau này:

```powershell
python --version
python -m compileall .
```

Nếu phase động tới demo cũ:

```powershell
python DIEU_KHIEN_CHUOT\demo_run.py
```

Nếu tạo adapter:

```powershell
python -c "from actions.mouse_control_adapter import MouseControlAdapter; print('adapter ok')"
```

---

## 13. Cập nhật checklist

Sau khi hoàn thành task, agent phải cập nhật `update.md`:

```text
[ ] Task chưa làm
```

thành:

```text
[x] Task đã làm
```

Không đánh dấu task chưa test.

---

## 14. Format báo cáo

Agent phải báo cáo:

```text
## Completed

- ...

## Files changed

- ...

## Tests

- ...

## Checklist updated

- ...

## Notes / Risks

- ...
```

---

## 15. Prompt mặc định

```text
Bạn là coding agent cho project ACV Gesture Control.

Chiến lược hiện tại: UI-FIRST và bảo toàn MouseController/hàm điều khiển chuột hiện tại.

Hãy đọc:
1. AGENTS.md
2. update.md
3. ripgrep.md
4. ACV_GESTURE_SPEC.md

Chỉ thực hiện phase tôi yêu cầu. Không tự ý làm phase khác.
Nếu đang làm UI, không sửa logic chuột hiện tại.
Được phép chia nhỏ module/đổi tên module mới/tạo app hoàn chỉnh, nhưng không được thay đổi thuật toán hoặc hành vi MouseController hiện tại khi chưa có yêu cầu và test tương đương.
Trước khi sửa, dùng rg theo ripgrep.md.
Sau khi sửa, cập nhật checklist trong update.md, chạy test phù hợp, báo file đã sửa.

Phase hiện tại: <điền phase>.
```
