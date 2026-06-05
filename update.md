# update.md — ACV Gesture Control UI-First Pipeline

> Pipeline cho Codex xây dựng app **ACV Gesture Control**.
>
> Chiến lược:
>
> ```text
> UI-FIRST
> + giữ nguyên hàm điều khiển chuột hiện tại
> + được phép chia nhỏ/đổi tên/tổ chức lại để tạo app hoàn chỉnh
> + không sửa logic điều khiển chuột làm ảnh hưởng hiệu suất
> + sau UI mới bọc MouseController hiện tại bằng adapter
> ```
>
> Lưu ý: Không hiểu câu "không sửa" là cấm tổ chức lại app. Codex **được phép tạo cấu trúc mới**, nhưng phải bảo toàn behavior chuột cũ.

---

## 0. Quy tắc bắt buộc

Trước khi sửa code, Codex phải:

```text
[ ] Đọc AGENTS.md
[ ] Đọc update.md
[ ] Đọc ripgrep.md
[ ] Đọc ACV_GESTURE_SPEC.md
[ ] Dùng rg để tìm file liên quan
[ ] Không đọc toàn bộ repo nếu chưa cần
[ ] Chỉ thực hiện đúng phase được yêu cầu
[ ] Không tự ý làm nhiều phase cùng lúc
```

Trong các phase UI:

```text
[ ] Không sửa logic điều khiển chuột hiện tại
[ ] Không sửa thuật toán MouseController hiện tại
[ ] Không làm giảm hiệu suất điều khiển chuột
[ ] Không xóa demo_run.py
[ ] Không xóa class MouseController cũ
[ ] Không sửa trained_model hiện tại
```

Được phép:

```text
[x] Tạo frontend/
[x] Tạo UI hoàn chỉnh
[x] Tạo cấu trúc module mới
[x] Tạo adapter sau này để gọi MouseController cũ
[x] Tạo profile/action/training module mới
[x] Đổi tên module mới do Codex tạo
[x] Tách app thành frontend/backend/core rõ ràng
```

Sau mỗi phase:

```text
[x] Chạy test/build phù hợp
[x] Cập nhật checklist trong update.md
[x] Báo file đã sửa
[x] Báo lệnh test đã chạy
[x] Báo rủi ro còn lại
```

---

## 1. Mục tiêu sản phẩm

```text
[x] Giao diện hiện đại Cyber-Clean / futuristic
[x] Onboarding chọn camera, tay, tốc độ chuột, độ nhạy, smoothing
[x] Dashboard realtime mock có camera HUD, hand skeleton, gesture log
[x] Configuration Page để gán chức năng với gesture/action
[x] Gesture Training Page để thu mẫu ảnh/video và train cử chỉ
[x] Hướng dẫn thao tác theo chế độ
[x] Giữ lại hành vi điều khiển chuột hiện tại
[ ] Thêm adapter để dùng lại MouseController hiện tại
[x] Thêm profile: Văn phòng, Giải trí, Game 2D, Tùy chỉnh
[x] Thêm thao tác mới: kéo-thả, scroll, chuyển tab, play/pause, game action
[x] Dataset collector
[ ] Training pipeline
[ ] Model registry
[ ] Backend/frontend integration
```

---

## 2. File giao diện bắt buộc: ACV_GESTURE_SPEC.md

`ACV_GESTURE_SPEC.md` là file chuẩn UI.

Codex phải đọc file này trước khi làm:

```text
Phase 1 — Frontend scaffold
Phase 2 — Design system Cyber-Clean
Phase 3 — App shell navigation
Phase 4 — Dashboard UI
Phase 5 — Onboarding UI
Phase 6 — Configuration UI
Phase 7 — Training UI
Phase 8 — Hướng dẫn thao tác UI
Phase 9 — UI polish/build
```

File này quyết định:

```text
[x] Cyber-Clean
[x] Breathable Void
[x] Kinetic Glass
[x] Deep Obsidian background
[x] Neon Cyan + Electric Blue
[x] Glassmorphism
[x] Tailwind CSS v4
[x] Framer Motion
[x] Lucide React
[x] HandSkeleton SVG
[x] TerminalLog
[x] Layout 5 trang
```

---

## 3. Tài liệu/công nghệ tham khảo

### Hand tracking sau này

```text
Google AI Edge Hand Landmarker:
https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker

MediaPipe Hands paper:
https://arxiv.org/abs/2006.10214

MediaPipe Hands docs:
https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
```

### Dynamic gesture sau này

```text
Next-Gen Dynamic Hand Gesture Recognition, Electronics 2024:
https://www.mdpi.com/2079-9292/13/16/3233

Dynamic Gesture Recognition using Transformer and Mediapipe, 2024:
https://thesai.org/Downloads/Volume15No6/Paper_143-Dynamic_Gesture_Recognition_using_a_Transformer_and_Mediapipe.pdf
```

### Virtual mouse

```text
Hand Gesture Controlled Virtual Mouse using OpenCV, MediaPipe in Python:
https://www.irjweb.com/user_upload/HAND%20GESTURE%20CONTROLLED%20VIRTUAL%20MOUSE%20USING%20OPENCV%2CMEDIAPIPE%20IN%20PYTHON.pdf
```

---

# UI-FIRST PHASES

---

## Phase 1 — Frontend scaffold

### Checklist

```text
[x] Dùng rg kiểm tra repo đã có frontend/package.json chưa
[x] Nếu chưa có, tạo thư mục frontend/
[x] Tạo Vite React TypeScript app
[x] Cài Tailwind CSS v4
[x] Cài Framer Motion
[x] Cài Lucide React
[x] Tạo frontend/src/main.tsx
[x] Tạo frontend/src/App.tsx
[x] Tạo frontend/src/index.css
[x] Tạo frontend/src/types.ts
[x] Không sửa logic điều khiển chuột hiện tại
[x] Không sửa MouseController hiện tại
[x] npm run build thành công
```

### Prompt cho Codex

```text
Đọc AGENTS.md, update.md, ripgrep.md và ACV_GESTURE_SPEC.md.
Chỉ thực hiện Phase 1 — Frontend scaffold.
Tạo frontend React TypeScript bằng Vite nếu chưa có. Cài Tailwind CSS v4, Framer Motion, Lucide React.
Không sửa logic điều khiển chuột hiện tại, không sửa MouseController hiện tại.
Được phép tạo cấu trúc frontend mới để xây app hoàn chỉnh.
Sau khi xong chạy npm run build và cập nhật checklist Phase 1.
```

---

## Phase 2 — Design system Cyber-Clean

### Checklist

```text
[x] Đọc phần màu sắc trong ACV_GESTURE_SPEC.md
[x] Cập nhật frontend/src/index.css
[x] Thêm @import "tailwindcss"
[x] Thêm brand-cyan #00f2ff
[x] Thêm brand-blue #4b8eff
[x] Thêm brand-obsidian #0A0A0C
[x] Thêm font display Be Vietnam Pro hoặc fallback sans
[x] Thêm font mono JetBrains Mono hoặc monospace
[x] Tạo utility .glass-panel
[x] Tạo utility .glass-inner
[x] Tạo utility .glow-text
[x] Tạo utility .glow-btn-active
[x] Tạo background grid obsidian
[x] npm run build thành công
```

### Prompt

```text
Chỉ thực hiện Phase 2 — Design system Cyber-Clean.
Dựa trên ACV_GESTURE_SPEC.md để cập nhật index.css, theme màu, glass-panel, glow effects và background grid.
Không sửa logic điều khiển chuột. Build kiểm tra.
```

---

## Phase 3 — App shell, navigation và mock data

### Checklist

```text
[x] Tạo frontend/src/types.ts
[x] Khai báo AppView type
[x] Khai báo Profile type
[x] Khai báo GestureLog type
[x] Khai báo FunctionMapping type
[x] Tạo mock profiles
[x] Tạo mock runtime
[x] Tạo mock logs
[x] Tạo components/SideNavBar.tsx
[x] Tạo components/TopAppBar.tsx
[x] Cập nhật App.tsx navigation state
[x] Có route/state cho 5 view: onboarding, dashboard, config, training, workflow
[x] npm run build thành công
```

### Prompt

```text
Chỉ thực hiện Phase 3 — App shell, navigation và mock data.
Tạo SideNavBar, TopAppBar, types.ts, mock profiles/runtime/logs.
App.tsx điều phối 5 view bằng state. Chưa cần React Router.
Không sửa logic điều khiển chuột. Build kiểm tra.
```

---

## Phase 4 — Dashboard UI

### Checklist

```text
[x] Tạo components/HandSkeleton.tsx
[x] Tạo components/HandCameraHUD.tsx
[x] Tạo components/TerminalLog.tsx
[x] Tạo views/DashboardView.tsx
[x] Camera live viewer mock
[x] LIVE badge đỏ
[x] SVG hand skeleton màu neon cyan
[x] HUD Model: ACV-Hand-v2.1
[x] HUD Res: 1920x1080
[x] FPS card
[x] Accuracy card
[x] Current profile card
[x] Current gesture card
[x] Current action card
[x] STOP button pulse
[x] Terminal log auto-scroll
[x] Clear log button
[x] npm run build thành công
```

### Prompt

```text
Chỉ thực hiện Phase 4 — Dashboard UI.
Bắt buộc đọc phần Dashboard trong ACV_GESTURE_SPEC.md.
Tạo HandSkeleton, HandCameraHUD, TerminalLog và DashboardView theo style Cyber-Clean.
Dùng mock data. Không kết nối camera thật. Không sửa logic chuột. Build kiểm tra.
```

---

## Phase 5 — Onboarding UI

### Checklist

```text
[x] Tạo views/OnboardingView.tsx
[x] Glass panel max-w-4xl
[x] 2 cột: info trái, settings phải
[x] Logo ACV Gesture Control
[x] Tiêu đề Thiết lập ban đầu
[x] Sensor status ping cyan
[x] Dropdown chọn webcam
[x] Segmented control tay trái/tay phải/tự động
[x] Slider tốc độ chuột 0.1x → 3.0x
[x] Slider sensitivity 0 → 100%
[x] Slider smoothing mức 1 → 5
[x] Profile cards: Văn phòng, Giải trí, Game 2D, Tùy chỉnh
[x] Nút Bắt đầu hiệu chỉnh
[x] Nút Bỏ qua
[x] npm run build thành công
```

### Prompt

```text
Chỉ thực hiện Phase 5 — Onboarding UI.
Dựa trên ACV_GESTURE_SPEC.md, tạo OnboardingView với glass panel 2 cột, slider realtime, profile cards và nút hành động.
Dùng local state. Không sửa logic chuột. Build kiểm tra.
```

---

## Phase 6 — Configuration / Setup Profile UI

### Checklist

```text
[x] Tạo views/ConfigView.tsx
[x] Tiêu đề Thiết lập cấu hình
[x] Dropdown mục đích sử dụng
[x] Bento grid function cards
[x] Card Di chuyển chuột
[x] Card Click trái
[x] Card Click phải
[x] Card Kéo thả file/thư mục
[x] Card Cuộn trang
[x] Card Chuyển tab
[x] Card Play/Pause
[x] Card Tấn công trong game
[x] Card thêm mới
[x] Mỗi card có icon/illustration
[x] Mỗi card có gesture hiện tại
[x] Mỗi card có nút Chỉnh sửa
[x] Bottom action bar
[x] Nút Hủy
[x] Nút LƯU CẤU HÌNH
[x] npm run build thành công
```

### Prompt

```text
Chỉ thực hiện Phase 6 — Configuration / Setup Profile UI.
Tạo ConfigView theo ACV_GESTURE_SPEC.md: dropdown profile, bento grid cards, card thêm mới, bottom action bar Save/Cancel.
Dùng mock mappings. Không sửa logic chuột. Build kiểm tra.
```

---

## Phase 7 — Gesture Training UI

### Checklist

```text
[x] Tạo views/TrainingView.tsx
[x] Layout 2 cột: config trái, camera phải
[x] Dropdown chọn profile
[x] Dropdown chọn nhãn/chức năng
[x] Toggle Chụp ảnh / Quay video
[x] Input sample count
[x] Progress 24/30 mẫu
[x] Progress bar gradient cyan
[x] Instruction banner
[x] Camera HUD
[x] Hand skeleton overlay
[x] Nút Ghi hình
[x] Nút Dừng
[x] Nút Xem trước mẫu
[x] Nút Hủy
[x] Nút Huấn luyện
[x] Nút Lưu
[x] npm run build thành công
```

### Prompt

```text
Chỉ thực hiện Phase 7 — Gesture Training UI.
Tạo TrainingView theo ACV_GESTURE_SPEC.md.
Có profile selector, function selector, image/video mode, sample count, progress, instruction banner, camera HUD, Record/Stop/Preview/Train/Save/Cancel.
Với kéo-thả hiển thị hướng dẫn: Kẹp ngón tay để giữ, di chuyển tay, sau đó thả ngón để bỏ.
Không sửa logic chuột. Build kiểm tra.
```

---

## Phase 8 — Hướng Dẫn Thao Tác UI

### Checklist

```text
[x] Tạo views/WorkflowView.tsx
[x] Tiêu đề Hướng dẫn thao tác
[x] Thanh chọn chế độ Văn phòng, Giải trí, Game 2D, Tùy chỉnh
[x] Thư viện chức năng theo chế độ
[x] Mô phỏng điểm tay bằng HandSkeleton
[x] Pulse/radar bằng Framer Motion
[x] Checklist trước khi dùng
[x] Lỗi thường gặp
[x] Badge độ khó/latency/cảm biến
[x] Tín hiệu gần đây
[x] Không dùng realtime workflow API/reset/test trong trang hướng dẫn
[x] npm run build thành công
```

### Prompt

```text
Chỉ thực hiện Phase 8 — Hướng Dẫn Thao Tác UI.
Tạo WorkflowView theo ACV_GESTURE_SPEC.md. Có 4 chế độ, thư viện chức năng, mô phỏng HandSkeleton, checklist, lỗi thường gặp và pulse/radar bằng Framer Motion.
Không sửa logic chuột. Build kiểm tra.
```

### Cập nhật phiên 2026-06-05 — Hướng Dẫn Thao Tác

```text
[x] Đổi nhãn trang workflow thành Hướng dẫn thao tác
[x] Giữ route/component workflow để tương thích layout 5 trang
[x] Thêm thanh chọn chế độ Văn phòng, Giải trí, Game 2D, Tùy chỉnh
[x] Thêm mô phỏng điểm tay bằng HandSkeleton và pulse/radar Framer Motion
[x] Thêm thư viện chức năng, quy trình thực hành, checklist, lỗi thường gặp bằng tiếng Việt
[x] Không dùng realtime workflow API/reset/test trong trang hướng dẫn
[x] Không sửa logic MouseController/demo/backend runtime
[x] npm install thành công bằng Windows runtime
[x] npm run build thành công bằng Windows runtime
[x] Đồng bộ ACV_GESTURE_SPEC.md, ripgrep.md và docs/button_inventory.md theo Hướng Dẫn Thao Tác
```

---

## Phase 9 — UI polish và build final

### Checklist

```text
[x] Kiểm tra tất cả view dùng chung theme
[x] Kiểm tra responsive cơ bản
[x] Kiểm tra navigation hoạt động
[x] Kiểm tra không lỗi TypeScript
[x] Kiểm tra npm run build
[x] Không còn import thừa nghiêm trọng
[x] Không còn TODO UI quan trọng
[x] Cập nhật README hoặc ghi chú cách chạy frontend
[x] Xác nhận không sửa MouseController hiện tại
[x] Xác nhận không sửa logic chuột hiện tại
```

### Prompt

```text
Chỉ thực hiện Phase 9 — UI polish và build final.
Kiểm tra toàn bộ UI, responsive, navigation, TypeScript build.
Không sửa logic chuột hiện tại. Cập nhật checklist và hướng dẫn chạy frontend.
```

---

# PHASE SAU UI: THÊM CHỨC NĂNG NHƯNG GIỮ LOGIC CHUỘT HIỆN TẠI

---

## Phase 10 — Profile JSON/schema tương thích UI

### Checklist

```text
[x] Tạo profiles/__init__.py
[x] Tạo profiles/profile_schema.py
[x] Tạo profiles/profile_manager.py
[x] Tạo profiles/action_mapper.py
[x] Tạo profiles/configs/office.json
[x] Tạo profiles/configs/entertainment.json
[x] Tạo profiles/configs/game_2d.json
[x] Tạo profiles/configs/custom.json
[x] Profile JSON tương thích function cards trong UI
[x] Load profile theo id
[x] Validate profile JSON
[x] Mapping gesture_event sang action
[x] Test load từng profile
```

---

## Phase 11 — Bọc MouseController hiện tại bằng adapter

### Mục tiêu

Dùng lại hàm điều khiển chuột hiện tại, không viết lại từ đầu.

### Checklist

```text
[x] Dùng rg tìm class MouseController hiện tại
[x] Dùng rg tìm các hàm move/click/scroll/mouse_down/mouse_up
[x] Tạo actions/__init__.py nếu chưa có
[x] Tạo actions/mouse_control_adapter.py
[x] Adapter import hoặc bọc MouseController hiện tại
[x] Adapter cung cấp API chuẩn: move, click, right_click, scroll, mouse_down, mouse_up
[x] Không đổi hành vi MouseController cũ
[x] Không đổi thuật toán/logic ảnh hưởng hiệu suất
[x] demo_run.py cũ vẫn chạy được
[x] Test import adapter
```

### Kiểm tra phiên 2026-06-04 — DIEU_KHIEN_CHUOT là logic chuột chính

```text
[x] actions.mouse_controller không còn chứa logic MouseController duplicate
[x] MouseControlAdapter dùng MouseController canonical
[x] Không còn class MouseController duplicate trong actions/
[x] Test import adapter xác nhận dùng class canonical
[x] Test action mapper bằng event giả vẫn chạy qua adapter
[x] compileall Python cho DIEU_KHIEN_CHUOT/actions/core/backend/profiles thành công
```

### Kiểm tra phiên 2026-06-04 — acv_runtime là runtime canonical

```text
[x] Tạo package acv_runtime/ từ logic DIEU_KHIEN_CHUOT/hand_mouse
[x] DIEU_KHIEN_CHUOT/hand_mouse giữ wrapper tương thích
[x] hand_mouse/ top-level giữ wrapper tương thích cho test/import cũ
[x] actions.mouse_controller trỏ về acv_runtime.mouse
[x] Backend HandTrackerService dùng HandGestureClassifier + GestureActionState canonical
[x] Vòng nhận diện thật không execute chuột qua ActionMapper để tránh double-action
[x] TerminalLog chỉ render 30 dòng gần nhất và hiển thị 2-3 dòng mới nhất
[x] Test gesture_state cũ bằng Windows py -3 thành công
[x] Test frontend build bằng Windows npm thành công
```

### Kiểm tra phiên 2026-06-04 — backend/hand_runtime là runtime canonical

```text
[x] Tạo backend/hand_runtime/ chứa logic điều khiển chuột canonical
[x] Copy feature utils vào backend/hand_runtime/feature_utils.py
[x] Copy model active vào backend/hand_runtime/trained_model/
[x] Backend HandTrackerService import trực tiếp backend.hand_runtime
[x] actions.mouse_controller trỏ về backend.hand_runtime.mouse
[x] acv_runtime/ chỉ còn compatibility wrapper
[x] hand_mouse/ và DIEU_KHIEN_CHUOT/hand_mouse chỉ còn compatibility wrapper
[x] Backend runtime không còn phụ thuộc import vào DIEU_KHIEN_CHUOT
```

### Prompt

```text
Chỉ thực hiện Phase 11 — Bọc MouseController hiện tại bằng adapter.
Dùng rg tìm class MouseController và các hàm điều khiển chuột hiện có.
Không viết lại MouseController từ đầu. Không đổi logic ảnh hưởng hiệu suất.
Tạo adapter để các phase sau gọi lại logic cũ.
```

---

## Phase 12 — ActionMapper nối profile với adapter

### Checklist

```text
[x] Tạo action executor nếu cần
[x] ActionMapper đọc gesture_event từ profile JSON
[x] ActionMapper gọi MouseControlAdapter
[x] Hỗ trợ action mouse.move
[x] Hỗ trợ action mouse.left_click
[x] Hỗ trợ action mouse.right_click
[x] Hỗ trợ action mouse.scroll
[x] Hỗ trợ action mouse.down
[x] Hỗ trợ action mouse.up
[x] Hỗ trợ keyboard hotkey nếu đã có controller
[x] Test bằng event giả
```

---

## Phase 13 — Pinch Drag Drop State Machine

### Checklist

```text
[x] Tính pinch_distance = distance(thumb_tip, index_tip) / palm_size
[x] Tính hand_position từ wrist/palm center
[x] Tạo core/gesture_state_machine.py
[x] Tạo PinchDragDropStateMachine
[x] Thêm state idle
[x] Thêm state pinch_candidate
[x] Thêm state holding
[x] Thêm state dragging
[x] Thêm event pinch_start
[x] Thêm event pinch_hold
[x] Thêm event drag_start
[x] Thêm event drag_move
[x] Thêm event drag_release
[x] Thêm event pinch_cancel
[x] drag_start gọi mouse.down qua adapter/action mapper
[x] drag_move gọi mouse.move qua adapter/action mapper
[x] drag_release gọi mouse.up qua adapter/action mapper
[x] Test state machine bằng dữ liệu giả
```

---

## Phase 14 — Thêm thao tác theo profile

### Checklist

```text
[x] Office: scroll tài liệu
[x] Office: chuyển tab
[x] Office: kéo-thả file/thư mục
[x] Entertainment: play/pause
[x] Entertainment: next/previous
[x] Entertainment: volume up/down
[x] Game 2D: move left/right
[x] Game 2D: jump
[x] Game 2D: attack
[x] Game 2D: dash
[x] Các thao tác mới đi qua profile/action mapper
[x] Không hard-code trong demo_run.py
[x] Không đổi MouseController hiện tại
```

---

## Phase 15 — Dataset collector cho Training UI

### Checklist

```text
[x] Tạo training/dataset_collector.py
[x] Tạo training/image_sample_collector.py
[x] Tạo training/video_sample_collector.py
[x] Tạo training/dataset_validator.py
[x] Lưu static sample JSON
[x] Lưu dynamic sample JSON
[x] Lưu profile
[x] Lưu function_id
[x] Lưu gesture_label
[x] Lưu timestamp
[x] Lưu landmarks
[x] Lưu features
[x] Validate sample thiếu bàn tay
```

---

## Phase 16 — Training pipeline

### Checklist

```text
[x] Tạo training/train_static_gesture.py
[x] Tạo training/train_dynamic_gesture.py
[x] Tạo training/evaluate_model.py
[x] Train static classifier bằng landmark features
[x] Dynamic gesture dùng state machine hoặc sequence skeleton
[x] Tính accuracy
[x] Tính precision/recall/f1
[x] In confusion matrix
[x] Lưu model joblib/onnx
[x] Lưu label_mapping.json
```

---

## Phase 17 — Model registry

### Checklist

```text
[x] Tạo models/model_registry.json nếu chưa có
[x] Tạo training/model_registry.py
[x] Ghi model_id
[x] Ghi type static/dynamic
[x] Ghi path
[x] Ghi created_at
[x] Ghi labels
[x] Ghi metrics
[x] Ghi dataset sample_count
[x] Set active model
[x] Rollback model
```

---

## Phase 18 — Backend/frontend integration

### Checklist

```text
[x] Chọn FastAPI/WebSocket hoặc integration phù hợp
[x] Tạo API trạng thái camera
[x] Tạo API profile list
[x] Tạo API current gesture/action
[x] Tạo API start/stop tracking
[x] Tạo API training sample progress
[x] Frontend consume API
[x] UI fallback mock nếu backend offline
[x] Mouse actions vẫn gọi MouseControlAdapter
[x] MouseControlAdapter vẫn dùng logic chuột cũ
```

---

## Phase 19 — Final polish/test

### Checklist

```text
[x] Visual feedback khi hand detected
[x] Visual feedback khi pinch
[x] Visual feedback khi dragging
[x] Cảnh báo camera không tìm thấy
[x] Cảnh báo ánh sáng yếu
[x] Cảnh báo sample lỗi
[x] Trạng thái Saved/Unsaved
[x] Confirm khi ghi đè model
[x] Confirm khi hủy training session
[x] Test frontend build
[ ] Test demo Python cũ
[x] Test adapter import
[x] Test profile Văn phòng
[x] Test profile Giải trí
[x] Test profile Game 2D
[x] Test scroll
[x] Test click
[x] Test kéo-thả
[x] Xác nhận MouseController cũ không bị đổi hành vi
```

---

## Bugfix — Dashboard scroll stability

### Checklist

```text
[x] Sửa TerminalLog auto-scroll không kéo cả Dashboard xuống dưới
[x] Khóa app shell trong viewport, chỉ scroll nội dung chính
[x] Sửa DashboardAction bị gán nhầm giữa Hide app, Mic, Profile và Gemini
[x] npm run build thành công bằng Windows cmd.exe
```

---

## Enhancement — Config action catalog theo mục đích

### Checklist

```text
[x] Config dropdown chỉ hiển thị 3 mục đích: Văn phòng, Giải trí, Game 2D
[x] Thêm catalog local cho Config UI với trên 10 action mỗi mục đích
[x] Đổi mục đích sẽ chuyển grid action tương ứng
[x] Thêm panel gợi ý gesture bên phải, mặc định ẩn đến khi chọn action
[x] Mỗi action có ít nhất 3 gesture gợi ý và nút Áp dụng
[x] Config UI fallback sang catalog local khi backend offline, không còn grid rỗng do Failed to fetch
[x] Bổ sung entertainment/game_2d profile JSON để backend online trả về trên 10 action
[x] Không sửa MouseController/demo_run.py trong enhancement này
[x] npm install thành công bằng Windows cmd.exe
[x] npm run build thành công bằng Windows cmd.exe
[x] py -3 -m compileall profiles backend thành công bằng Windows cmd.exe
[x] ProfileManager load office/entertainment/game_2d thành công với 16/15/16 action
```

---

## Definition of Done

```text
[x] Frontend build thành công
[x] Có UI 5 trang theo ACV_GESTURE_SPEC.md
[x] Có mock data và navigation
[ ] demo_run.py cũ không bị phá
[x] MouseController hiện tại được giữ behavior
[x] Có MouseControlAdapter bọc logic chuột cũ
[x] Có profile JSON/schema
[x] Có action mapper
[x] Có pinch drag-drop state machine
[x] Có dataset collector
[x] Có training pipeline
[x] Có model registry
[x] Có backend/frontend integration hoặc fallback mock
[x] Có hướng dẫn chạy app
```

---

## Prompt tổng mở Codex

```text
Bạn là coding agent cho project ACV Gesture Control.

Chiến lược hiện tại: UI-FIRST và bảo toàn MouseController/hàm điều khiển chuột hiện tại.

Hãy đọc:
1. AGENTS.md
2. update.md
3. ripgrep.md
4. ACV_GESTURE_SPEC.md

Sau đó chỉ thực hiện phase tôi yêu cầu.
Được phép chia nhỏ, đổi tên module mới, tạo cấu trúc app hoàn chỉnh.
Không được thay đổi thuật toán/hành vi điều khiển chuột hiện tại làm ảnh hưởng hiệu suất.
Nếu cần dùng chuột sau này, hãy bọc MouseController hiện tại bằng adapter, không viết lại từ đầu.
Trước khi sửa code, dùng rg theo ripgrep.md.
Sau khi sửa, cập nhật checklist trong update.md, chạy test phù hợp, báo file đã sửa và lệnh test.

Phase hiện tại: <điền phase>.
```
