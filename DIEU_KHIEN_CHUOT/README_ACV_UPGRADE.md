# ACV Upgrade README — Modern Gesture Control App

> Mục tiêu: Nâng cấp project ACV từ demo điều khiển chuột bằng cử chỉ tay thành một app giao diện hiện đại, có profile theo mục đích sử dụng, có trang huấn luyện cử chỉ, có trang setup mapping hành động, và dễ mở rộng thêm chức năng/train thêm cử chỉ mới.

---

## 1. Tầm nhìn sản phẩm

ACV mới sẽ là một ứng dụng điều khiển máy tính bằng cử chỉ tay qua camera.

Người dùng có thể:

- Chọn mục đích sử dụng:
  - Văn phòng
  - Giải trí
  - Game 2D
  - Custom profile
- Chỉnh:
  - Tốc độ chuột
  - Độ nhạy
  - Độ mượt
  - Vùng chết
  - Cooldown click/scroll/action
- Huấn luyện cử chỉ mới bằng ảnh hoặc video.
- Gán cử chỉ vào hành động tương ứng.
- Lưu hoặc hủy cấu hình.
- Dễ dàng mở rộng thêm profile, thêm gesture, thêm action.

---

## 2. Nguyên tắc thiết kế hệ thống

Không hard-code trực tiếp gesture trong file chạy chính.

Thiết kế đúng nên là:

```text
Camera
  → Hand Tracking
  → Landmark Extraction
  → Gesture Recognition
  → Gesture State Machine
  → Gesture Event
  → Profile Action Mapping
  → Mouse/Keyboard/App Action
```

Ví dụ:

```text
pinch_start
  → mouse_down

pinch_move
  → mouse_drag_move

pinch_release
  → mouse_up
```

Không nên xử lý kéo-thả bằng một lệnh lớn duy nhất. Phải chia thành hành động nhỏ để giống chuột thật và tăng độ chính xác.

---

## 3. Cấu trúc thư mục đề xuất

```text
ACV/
│
├── README_UPGRADE.md
├── app.py
│
├── core/
│   ├── camera_service.py
│   ├── hand_tracker.py
│   ├── feature_extractor.py
│   ├── gesture_classifier.py
│   ├── temporal_filter.py
│   ├── gesture_state_machine.py
│   └── event_bus.py
│
├── actions/
│   ├── mouse_controller.py
│   ├── keyboard_controller.py
│   ├── office_actions.py
│   ├── entertainment_actions.py
│   └── game_2d_actions.py
│
├── profiles/
│   ├── profile_manager.py
│   ├── action_mapper.py
│   ├── profile_schema.py
│   └── configs/
│       ├── office.json
│       ├── entertainment.json
│       ├── game_2d.json
│       └── custom.json
│
├── training/
│   ├── dataset_collector.py
│   ├── image_sample_collector.py
│   ├── video_sample_collector.py
│   ├── dataset_validator.py
│   ├── train_static_gesture.py
│   ├── train_dynamic_gesture.py
│   ├── evaluate_model.py
│   └── model_registry.py
│
├── ui/
│   ├── onboarding_page.py
│   ├── dashboard_page.py
│   ├── setup_profile_page.py
│   ├── gesture_training_page.py
│   ├── gesture_mapping_page.py
│   ├── live_test_page.py
│   └── settings_page.py
│
├── assets/
│   ├── gestures/
│   │   ├── pinch.png
│   │   ├── open_hand.png
│   │   ├── fist.png
│   │   ├── swipe_left.png
│   │   └── swipe_right.png
│   └── icons/
│
├── models/
│   ├── static_gesture_model.joblib
│   ├── dynamic_gesture_model.onnx
│   └── label_mapping.json
│
└── data/
    ├── raw/
    ├── processed/
    └── sessions/
```

---

## 4. Các trang chính của app

### 4.1. Trang Onboarding

Trang này xuất hiện khi người dùng mở app lần đầu.

Chức năng:

- Chọn camera.
- Chọn tay điều khiển:
  - Tay trái
  - Tay phải
  - Tự động
- Chọn tốc độ chuột.
- Chọn độ nhạy.
- Chọn độ mượt.
- Chọn mục đích sử dụng mặc định:
  - Văn phòng
  - Giải trí
  - Game 2D
- Chạy calibration nhanh.

Checklist:

```text
[ ] Tạo UI chọn camera
[ ] Hiển thị preview camera
[ ] Hiển thị trạng thái nhận diện bàn tay
[ ] Thêm slider tốc độ chuột
[ ] Thêm slider độ nhạy
[ ] Thêm slider smoothing
[ ] Thêm chọn tay trái/phải/tự động
[ ] Thêm chọn profile mặc định
[ ] Lưu cấu hình vào config/user_settings.json
```

---

### 4.2. Trang Dashboard

Trang chính sau khi app chạy.

Chức năng:

- Hiển thị profile đang dùng.
- Hiển thị camera preview.
- Hiển thị skeleton bàn tay.
- Hiển thị gesture đang nhận diện.
- Hiển thị action đang thực hiện.
- Nút Start/Stop điều khiển.
- Nút chuyển nhanh profile.
- Nút mở trang huấn luyện cử chỉ.
- Nút mở trang setup mapping.

Checklist:

```text
[ ] Tạo layout dashboard hiện đại
[ ] Thêm card trạng thái camera
[ ] Thêm card profile hiện tại
[ ] Thêm card FPS
[ ] Thêm card gesture hiện tại
[ ] Thêm card action hiện tại
[ ] Thêm camera preview
[ ] Overlay 21 điểm landmark bàn tay
[ ] Thêm nút Start/Stop
[ ] Thêm nút chuyển profile nhanh
[ ] Thêm nút mở Gesture Training Page
[ ] Thêm nút mở Setup Profile Page
```

---

## 5. Trang huấn luyện cử chỉ

### 5.1. Mục tiêu

Trang này cho phép người dùng tự tạo hoặc cải thiện cử chỉ.

Người dùng có thể:

- Chọn mục đích sử dụng:
  - Văn phòng
  - Giải trí
  - Game 2D
  - Custom
- Chọn chức năng muốn train.
- Chọn kiểu dữ liệu:
  - Chụp ảnh
  - Quay video
- Chọn số lượng mẫu.
- Thu dữ liệu.
- Kiểm tra chất lượng mẫu.
- Bắt đầu huấn luyện.
- Lưu model mới.
- Hủy thao tác.

---

### 5.2. Layout đề xuất

```text
┌──────────────────────────────────────────────────────────────┐
│ Gesture Training                                             │
├──────────────────────────────────────────────────────────────┤
│ Purpose/Profile: [ Văn phòng ▼ ]                             │
│ Function:        [ Kéo thả file/thư mục ▼ ]                  │
│ Gesture Type:    [ Dynamic / Hold-Release ▼ ]                │
│ Data Mode:       [ Chụp ảnh ] [ Quay video ]                 │
│ Sample Count:    [ 30 mẫu ]                                  │
├──────────────────────────────────────────────────────────────┤
│ Camera Preview + Hand Skeleton                               │
│                                                              │
│ Instruction: Kẹp ngón cái và ngón trỏ để bắt đầu giữ         │
│ Progress: [████████░░] 24/30                                 │
├──────────────────────────────────────────────────────────────┤
│ [Record] [Stop] [Preview Samples] [Train] [Save] [Cancel]    │
└──────────────────────────────────────────────────────────────┘
```

---

### 5.3. Các loại huấn luyện

#### A. Huấn luyện bằng ảnh

Dùng cho gesture tĩnh.

Ví dụ:

- Open hand
- Fist
- One finger
- Two fingers
- Three fingers
- Palm stop

Dữ liệu cần:

```text
Mỗi gesture: 50 - 100 ảnh
Mỗi ảnh: 21 landmarks + label
```

Checklist:

```text
[ ] Cho phép chọn chế độ chụp ảnh
[ ] Cho phép nhập số lượng mẫu
[ ] Chụp frame từ camera
[ ] Detect hand landmark
[ ] Lưu ảnh gốc nếu cần
[ ] Lưu landmark normalized
[ ] Lưu label gesture
[ ] Hiển thị tiến độ thu mẫu
[ ] Kiểm tra ảnh bị thiếu bàn tay
[ ] Cảnh báo ánh sáng yếu
```

#### B. Huấn luyện bằng video

Dùng cho gesture động.

Ví dụ:

- Swipe left
- Swipe right
- Swipe up
- Swipe down
- Pinch drag drop
- Hand move attack
- Hand move jump

Dữ liệu cần:

```text
Mỗi gesture động: 20 - 50 video ngắn
Mỗi video: 1 - 3 giây
Mỗi frame: 21 landmarks + timestamp + label
```

Checklist:

```text
[ ] Cho phép chọn chế độ quay video
[ ] Cho phép chọn thời lượng mỗi mẫu
[ ] Cho phép chọn số lượng video
[ ] Ghi landmark theo từng frame
[ ] Lưu timestamp
[ ] Lưu label
[ ] Lưu metadata profile/function
[ ] Hiển thị tiến độ thu video
[ ] Cho phép xem lại sample
[ ] Cho phép xóa sample lỗi
```

---

## 6. Trang setup profile và mapping hành động

### 6.1. Mục tiêu

Trang này cho phép người dùng chọn mục đích sử dụng và gán gesture vào hành động.

Ví dụ:

Mục đích sử dụng: Văn phòng

Các chức năng:

- Di chuyển chuột
- Click trái
- Click phải
- Kéo thả
- Cuộn trang
- Chuyển tab
- Mở file
- Đóng tab
- Copy
- Paste

Mỗi chức năng có một box riêng, có ảnh minh họa gesture.

---

### 6.2. Layout đề xuất

```text
┌──────────────────────────────────────────────────────────────┐
│ Setup Profile                                                │
├──────────────────────────────────────────────────────────────┤
│ Purpose: [ Văn phòng ▼ ]                                    │
├──────────────────────────────────────────────────────────────┤
│ Function Boxes                                               │
│                                                              │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│ │ Click trái   │  │ Click phải   │  │ Kéo thả      │         │
│ │ [pinch.png]  │  │ [two.png]    │  │ [drag.png]   │         │
│ │ Gesture: ... │  │ Gesture: ... │  │ Gesture: ... │         │
│ └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                              │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│ │ Cuộn trang   │  │ Chuyển tab   │  │ Mở menu      │         │
│ │ [scroll.png] │  │ [swipe.png]  │  │ [fist.png]   │         │
│ └──────────────┘  └──────────────┘  └──────────────┘         │
├──────────────────────────────────────────────────────────────┤
│ [Save] [Cancel]                                              │
└──────────────────────────────────────────────────────────────┘
```

Checklist:

```text
[ ] Tạo trang setup profile
[ ] Cho phép chọn profile: Văn phòng/Giải trí/Game 2D/Custom
[ ] Load danh sách chức năng theo profile
[ ] Hiển thị mỗi chức năng dưới dạng box
[ ] Mỗi box có tên chức năng
[ ] Mỗi box có ảnh minh họa gesture
[ ] Mỗi box có dropdown chọn gesture/action
[ ] Cho phép click vào box để sửa mapping
[ ] Cho phép lưu cấu hình
[ ] Cho phép hủy thay đổi
[ ] Lưu mapping vào profiles/configs/*.json
[ ] Validate mapping trước khi lưu
```

---

## 7. Cấu hình chức năng theo từng mục đích sử dụng

### 7.1. Văn phòng

```text
[ ] Di chuyển chuột
[ ] Click trái
[ ] Click phải
[ ] Double click
[ ] Kéo thả file/thư mục
[ ] Cuộn trang lên/xuống
[ ] Chuyển tab trái/phải
[ ] Mở menu chuột phải
[ ] Copy
[ ] Paste
[ ] Quay lại thư mục trước
[ ] Mở file/folder
```

Mapping đề xuất:

```text
Open hand move        → mouse.move
Pinch tap             → mouse.left_click
Two finger tap        → mouse.right_click
Pinch hold            → mouse.down
Pinch move            → mouse.drag_move
Pinch release         → mouse.up
Three fingers up      → mouse.scroll_up
Three fingers down    → mouse.scroll_down
Swipe left            → previous tab
Swipe right           → next tab
Palm stop             → pause control
```

---

### 7.2. Giải trí

```text
[ ] Lướt web
[ ] Chuyển page
[ ] Play/Pause video
[ ] Tăng âm lượng
[ ] Giảm âm lượng
[ ] Tua video tới
[ ] Tua video lùi
[ ] Fullscreen
[ ] Thoát fullscreen
[ ] Next video
[ ] Previous video
```

Mapping đề xuất:

```text
Pinch tap             → play/pause
Swipe left            → previous/back
Swipe right           → next/forward
Swipe up              → volume up
Swipe down            → volume down
Pinch hold + move     → seek video
Two finger tap        → fullscreen
Palm stop             → pause control
```

---

### 7.3. Game 2D

```text
[ ] Di chuyển trái
[ ] Di chuyển phải
[ ] Nhảy
[ ] Cúi
[ ] Tấn công
[ ] Đỡ đòn
[ ] Dash
[ ] Skill 1
[ ] Skill 2
[ ] Pause game
```

Mapping đề xuất:

```text
Hand move left        → key A
Hand move right       → key D
Hand move up          → key W / jump
Hand move down        → key S / crouch
Pinch tap             → attack
Fist hold             → shield
Swipe right           → dash
Two finger tap        → skill 1
Three finger tap      → skill 2
Palm stop             → pause input
```

---

## 8. Workflow kéo-thả giống chuột thật

Kéo-thả không nên nhận là một gesture duy nhất. Phải chia thành các action nhỏ.

### 8.1. Luồng hành động

```text
1. Người dùng đưa chuột tới file/folder
2. Người dùng kẹp ngón cái + ngón trỏ
3. App nhận pinch_start
4. App thực hiện mouse_down
5. Người dùng giữ kẹp và di chuyển tay
6. App nhận pinch_move
7. App thực hiện mouse_drag_move
8. Người dùng thả ngón
9. App nhận pinch_release
10. App thực hiện mouse_up
```

### 8.2. State machine

```text
idle
  → pinch_candidate
  → holding
  → dragging
  → released
  → idle
```

### 8.3. Pseudo-code

```python
class PinchDragDropStateMachine:
    def __init__(self):
        self.state = "idle"
        self.hold_frames = 0
        self.dragging = False

    def update(self, pinch_distance, hand_position):
        if self.state == "idle":
            if pinch_distance < 0.28:
                self.state = "pinch_candidate"
                self.hold_frames = 1
                return "pinch_start"

        elif self.state == "pinch_candidate":
            if pinch_distance < 0.25:
                self.hold_frames += 1
                if self.hold_frames >= 5:
                    self.state = "holding"
                    return "pinch_hold"
            else:
                self.state = "idle"
                return "pinch_cancel"

        elif self.state == "holding":
            if pinch_distance < 0.30:
                self.state = "dragging"
                return "drag_start"
            if pinch_distance > 0.36:
                self.state = "idle"
                return "pinch_release"

        elif self.state == "dragging":
            if pinch_distance < 0.30:
                return "drag_move"
            if pinch_distance > 0.36:
                self.state = "idle"
                return "drag_release"

        return None
```

### 8.4. Mapping sang chuột

```python
if event == "pinch_hold":
    mouse.mouse_down()

elif event == "drag_start":
    mouse.mouse_down()

elif event == "drag_move":
    mouse.move_to(x, y)

elif event == "drag_release":
    mouse.mouse_up()
```

Checklist:

```text
[ ] Tính khoảng cách ngón cái và ngón trỏ
[ ] Chuẩn hóa khoảng cách theo kích thước lòng bàn tay
[ ] Tạo PinchDragDropStateMachine
[ ] Tạo event pinch_start
[ ] Tạo event pinch_hold
[ ] Tạo event drag_start
[ ] Tạo event drag_move
[ ] Tạo event drag_release
[ ] Tạo event pinch_cancel
[ ] Mapping pinch_hold sang mouse_down
[ ] Mapping drag_move sang mouse_move
[ ] Mapping drag_release sang mouse_up
[ ] Thêm visual feedback khi đang giữ
[ ] Thêm visual feedback khi đang kéo
[ ] Test kéo file trong Windows Explorer
[ ] Test kéo thả tab trong browser
[ ] Test kéo icon ngoài desktop
```

---

## 9. Profile JSON mẫu

### 9.1. office.json

```json
{
  "id": "office",
  "name": "Văn phòng",
  "description": "Dùng cho đọc tài liệu, duyệt file, chuyển tab và kéo thả.",
  "mouse": {
    "speed": 2.2,
    "sensitivity": 2.0,
    "smoothing": 0.55,
    "dead_zone": 0.004,
    "max_step": 90
  },
  "gesture_filter": {
    "prediction_buffer": 7,
    "stable_min_count": 4,
    "click_cooldown": 0.45,
    "action_cooldown": 0.8
  },
  "functions": [
    {
      "id": "move_mouse",
      "name": "Di chuyển chuột",
      "illustration": "assets/gestures/open_hand.png",
      "gesture_event": "hand_move",
      "action": "mouse.move"
    },
    {
      "id": "left_click",
      "name": "Click trái",
      "illustration": "assets/gestures/pinch.png",
      "gesture_event": "pinch_tap",
      "action": "mouse.left_click"
    },
    {
      "id": "right_click",
      "name": "Click phải",
      "illustration": "assets/gestures/two_finger.png",
      "gesture_event": "two_finger_tap",
      "action": "mouse.right_click"
    },
    {
      "id": "drag_drop",
      "name": "Kéo thả file/thư mục",
      "illustration": "assets/gestures/pinch_drag_drop.png",
      "gesture_event": "pinch_drag_drop",
      "action_sequence": [
        {
          "event": "pinch_hold",
          "action": "mouse.down"
        },
        {
          "event": "drag_move",
          "action": "mouse.move"
        },
        {
          "event": "drag_release",
          "action": "mouse.up"
        }
      ]
    },
    {
      "id": "scroll_up",
      "name": "Cuộn lên",
      "illustration": "assets/gestures/three_up.png",
      "gesture_event": "three_up",
      "action": "mouse.scroll_up"
    },
    {
      "id": "scroll_down",
      "name": "Cuộn xuống",
      "illustration": "assets/gestures/three_down.png",
      "gesture_event": "three_down",
      "action": "mouse.scroll_down"
    },
    {
      "id": "next_tab",
      "name": "Chuyển tab phải",
      "illustration": "assets/gestures/swipe_right.png",
      "gesture_event": "swipe_right",
      "action": "keyboard.hotkey",
      "keys": ["ctrl", "tab"]
    },
    {
      "id": "previous_tab",
      "name": "Chuyển tab trái",
      "illustration": "assets/gestures/swipe_left.png",
      "gesture_event": "swipe_left",
      "action": "keyboard.hotkey",
      "keys": ["ctrl", "shift", "tab"]
    }
  ]
}
```

---

## 10. Dataset format đề xuất

### 10.1. Static sample

```json
{
  "sample_id": "office_left_click_0001",
  "profile": "office",
  "function_id": "left_click",
  "gesture_label": "pinch_tap",
  "data_type": "image",
  "created_at": "2026-05-23T00:00:00",
  "landmarks": [
    [0.0, 0.0, 0.0],
    [0.1, 0.2, -0.01]
  ],
  "features": {
    "pinch_distance": 0.22,
    "palm_size": 0.18
  }
}
```

### 10.2. Dynamic sample

```json
{
  "sample_id": "office_drag_drop_0001",
  "profile": "office",
  "function_id": "drag_drop",
  "gesture_label": "pinch_drag_drop",
  "data_type": "video",
  "duration_sec": 2.5,
  "created_at": "2026-05-23T00:00:00",
  "frames": [
    {
      "t": 0.00,
      "landmarks": [],
      "features": {
        "pinch_distance": 0.45,
        "hand_x": 0.50,
        "hand_y": 0.52
      }
    },
    {
      "t": 0.08,
      "landmarks": [],
      "features": {
        "pinch_distance": 0.25,
        "hand_x": 0.51,
        "hand_y": 0.52
      }
    }
  ],
  "segments": [
    {
      "name": "pinch_hold",
      "start": 0.20,
      "end": 0.70
    },
    {
      "name": "drag_move",
      "start": 0.70,
      "end": 2.10
    },
    {
      "name": "drag_release",
      "start": 2.10,
      "end": 2.50
    }
  ]
}
```

---

## 11. Model training workflow

### 11.1. Static gesture model

Dùng cho gesture tĩnh.

```text
Collect image samples
  → Extract landmarks
  → Normalize landmarks
  → Extract features
  → Train classifier
  → Evaluate
  → Save model
```

Model phù hợp:

```text
[ ] SVM
[ ] Random Forest
[ ] MLP
[ ] LightGBM nếu cần
```

Checklist:

```text
[ ] Viết image_sample_collector.py
[ ] Viết normalize_landmarks()
[ ] Viết extract_static_features()
[ ] Viết train_static_gesture.py
[ ] In accuracy
[ ] In confusion matrix
[ ] Lưu model joblib
[ ] Lưu label_mapping.json
```

### 11.2. Dynamic gesture model

Dùng cho gesture động.

```text
Collect video samples
  → Extract landmark sequence
  → Normalize each frame
  → Pad/trim sequence length
  → Train temporal model
  → Evaluate
  → Save model
```

Model phù hợp:

```text
[ ] Rule-based state machine cho bản đầu
[ ] HMM nếu muốn nhẹ
[ ] LSTM/GRU nếu có đủ dữ liệu
[ ] TCN nếu muốn realtime tốt
```

Checklist:

```text
[ ] Viết video_sample_collector.py
[ ] Chuẩn hóa sequence landmarks
[ ] Pad/trim sequence
[ ] Tạo train_dynamic_gesture.py
[ ] Train LSTM/GRU hoặc rule-based trước
[ ] Evaluate precision/recall theo từng gesture
[ ] Lưu model ONNX hoặc joblib
[ ] Lưu thông tin model vào model_registry.json
```

---

## 12. Model registry

Mỗi model sau khi train phải có metadata.

```json
{
  "model_id": "static_gesture_v1",
  "type": "static",
  "path": "models/static_gesture_model.joblib",
  "created_at": "2026-05-23T00:00:00",
  "profiles": ["office", "entertainment"],
  "labels": ["open_hand", "pinch", "fist", "two_finger"],
  "metrics": {
    "accuracy": 0.96,
    "macro_f1": 0.94
  },
  "dataset": {
    "sample_count": 800,
    "users": 1
  }
}
```

Checklist:

```text
[ ] Tạo model_registry.py
[ ] Tạo model_registry.json
[ ] Mỗi lần train xong ghi version mới
[ ] Cho phép rollback model cũ
[ ] Hiển thị model hiện tại trong UI
```

---

## 13. UI/UX yêu cầu

Phong cách:

```text
Dark mode
Glassmorphism nhẹ
Card bo góc lớn
Neon blue/purple vừa phải
Icon rõ ràng
Có ảnh minh họa cử chỉ
Có trạng thái realtime
Có animation chuyển trang mượt
```

Yêu cầu UX:

```text
[ ] Người mới dùng phải setup được trong dưới 2 phút
[ ] Có hướng dẫn trực tiếp khi train gesture
[ ] Có cảnh báo nếu camera không thấy tay
[ ] Có cảnh báo nếu sample bị lỗi
[ ] Có nút hủy rõ ràng
[ ] Có xác nhận trước khi ghi đè model
[ ] Có trạng thái Saved/Unsaved
[ ] Có nút khôi phục mặc định profile
```

---

## 14. Task chia nhỏ để làm theo từng khung chat

### Chat 1 — Refactor core project

```text
[x] Đọc cấu trúc project hiện tại
[x] Tách MouseController khỏi demo_run.py
[x] Tạo thư mục core/
[x] Tạo camera_service.py
[x] Tạo hand_tracker.py
[x] Tạo feature_extractor.py
[x] Tạo gesture_classifier.py
[x] Đảm bảo demo cũ vẫn chạy được
[ ] Commit: refactor core gesture engine
```

Prompt gợi ý cho Codex:

```text
Hãy đọc project ACV hiện tại. Refactor phần camera, MediaPipe hand tracking, feature extraction, model prediction và MouseController ra các module riêng theo README_UPGRADE.md. Không thay đổi hành vi demo hiện tại. Sau khi xong đánh dấu task hoàn thành trong README.
```

---

### Chat 2 — Thêm profile system

```text
[ ] Tạo profiles/configs/office.json
[ ] Tạo profiles/configs/entertainment.json
[ ] Tạo profiles/configs/game_2d.json
[ ] Tạo profile_schema.py
[ ] Tạo profile_manager.py
[ ] Tạo action_mapper.py
[ ] Load profile theo id
[ ] Validate profile
[ ] Mapping gesture_event sang action
[ ] Commit: add profile mapping system
```

Prompt gợi ý:

```text
Dựa trên README_UPGRADE.md, hãy thêm profile system cho ACV. Tạo profile JSON cho Văn phòng, Giải trí, Game 2D. Viết ProfileManager và ActionMapper để chuyển gesture_event thành action. Sau khi hoàn thành, cập nhật checklist trong README.
```

---

### Chat 3 — Thêm Pinch Drag Drop State Machine

```text
[ ] Tính pinch_distance từ landmark ngón cái và ngón trỏ
[ ] Chuẩn hóa pinch_distance theo palm_size
[ ] Tạo PinchDragDropStateMachine
[ ] Tạo event pinch_start
[ ] Tạo event pinch_hold
[ ] Tạo event drag_start
[ ] Tạo event drag_move
[ ] Tạo event drag_release
[ ] Tạo event pinch_cancel
[ ] Tích hợp với MouseController
[ ] Test kéo-thả file/folder
[ ] Commit: add pinch drag drop workflow
```

Prompt gợi ý:

```text
Hãy triển khai PinchDragDropStateMachine theo README_UPGRADE.md. Kéo-thả phải chia thành pinch_hold → mouse_down, drag_move → mouse_move, drag_release → mouse_up. Không làm một gesture lớn duy nhất. Cập nhật checklist sau khi hoàn thành.
```

---

### Chat 4 — Xây dựng UI Dashboard

```text
[ ] Chọn framework UI
[ ] Tạo dashboard page
[ ] Hiển thị camera preview
[ ] Overlay hand landmarks
[ ] Hiển thị profile hiện tại
[ ] Hiển thị gesture hiện tại
[ ] Hiển thị action hiện tại
[ ] Thêm nút Start/Stop
[ ] Thêm nút mở Setup Profile
[ ] Thêm nút mở Gesture Training
[ ] Commit: add modern dashboard UI
```

Prompt gợi ý:

```text
Hãy xây dựng UI dashboard hiện đại cho ACV theo README_UPGRADE.md. Giao diện dark mode, card bo góc, có camera preview, skeleton bàn tay, profile hiện tại, gesture/action realtime và nút Start/Stop.
```

---

### Chat 5 — Xây dựng Setup Profile Page

```text
[ ] Tạo setup_profile_page.py
[ ] Cho phép chọn mục đích sử dụng
[ ] Load function boxes theo profile
[ ] Mỗi box có tên chức năng
[ ] Mỗi box có ảnh minh họa
[ ] Mỗi box có gesture/action hiện tại
[ ] Cho phép click để đổi gesture/action
[ ] Có nút Save
[ ] Có nút Cancel
[ ] Lưu vào profile JSON
[ ] Validate trước khi lưu
[ ] Commit: add setup profile page
```

Prompt gợi ý:

```text
Hãy tạo Setup Profile Page. Trang này cho phép chọn mục đích sử dụng Văn phòng/Giải trí/Game 2D, hiển thị các box chức năng có ảnh minh họa, chọn gesture/action tương ứng, sau đó Save hoặc Cancel. Cấu hình lưu vào profiles/configs/*.json.
```

---

### Chat 6 — Xây dựng Gesture Training Page

```text
[ ] Tạo gesture_training_page.py
[ ] Cho phép chọn profile/mục đích sử dụng
[ ] Cho phép chọn function cần train
[ ] Cho phép chọn data mode: image/video
[ ] Cho phép chọn sample count
[ ] Hiển thị camera preview
[ ] Hiển thị hướng dẫn tư thế
[ ] Thu sample ảnh
[ ] Thu sample video
[ ] Hiển thị tiến độ
[ ] Cho phép xem lại sample
[ ] Cho phép xóa sample lỗi
[ ] Nút Train
[ ] Nút Save
[ ] Nút Cancel
[ ] Commit: add gesture training page
```

Prompt gợi ý:

```text
Hãy tạo Gesture Training Page theo README_UPGRADE.md. Trang này cho phép chọn mục đích sử dụng, chọn chức năng cần train, chọn chụp ảnh hoặc quay video, chọn số lượng mẫu, thu dữ liệu bằng camera, hiển thị tiến độ, xem lại sample, Train, Save hoặc Cancel.
```

---

### Chat 7 — Dataset collector

```text
[ ] Tạo training/dataset_collector.py
[ ] Tạo image_sample_collector.py
[ ] Tạo video_sample_collector.py
[ ] Lưu metadata sample
[ ] Lưu landmark normalized
[ ] Lưu raw image/video nếu bật tùy chọn
[ ] Lưu static sample JSON
[ ] Lưu dynamic sample JSON
[ ] Validate sample lỗi
[ ] Commit: add dataset collection pipeline
```

Prompt gợi ý:

```text
Hãy xây dựng dataset collection pipeline cho Gesture Training Page. Hỗ trợ static image sample và dynamic video sample. Mỗi sample phải lưu profile, function_id, gesture_label, timestamp, landmarks, features và metadata.
```

---

### Chat 8 — Training pipeline

```text
[ ] Tạo train_static_gesture.py
[ ] Tạo train_dynamic_gesture.py
[ ] Tạo evaluate_model.py
[ ] Train static classifier
[ ] Train hoặc mô phỏng dynamic gesture bằng state machine trước
[ ] In accuracy
[ ] In confusion matrix
[ ] Lưu model
[ ] Lưu label mapping
[ ] Commit: add training pipeline
```

Prompt gợi ý:

```text
Hãy thêm training pipeline cho ACV. Static gesture dùng landmark features để train classifier. Dynamic gesture trước mắt có thể dùng rule-based state machine, sau đó chuẩn bị cấu trúc để thay bằng LSTM/GRU/TCN. Sau khi train phải lưu model, label mapping và metrics.
```

---

### Chat 9 — Model registry và versioning

```text
[ ] Tạo model_registry.py
[ ] Tạo model_registry.json
[ ] Ghi model version sau mỗi lần train
[ ] Lưu metrics
[ ] Lưu dataset info
[ ] Cho phép chọn model active
[ ] Cho phép rollback model cũ
[ ] Hiển thị model active trong UI
[ ] Commit: add model registry
```

Prompt gợi ý:

```text
Hãy thêm model registry cho ACV. Mỗi model sau khi train phải có model_id, type, path, created_at, labels, metrics, dataset info. Cho phép set active model và rollback model cũ.
```

---

### Chat 10 — Hoàn thiện UX và kiểm thử

```text
[ ] Thêm visual feedback khi đang pinch
[ ] Thêm visual feedback khi đang drag
[ ] Thêm cảnh báo không thấy tay
[ ] Thêm cảnh báo ánh sáng yếu
[ ] Thêm trạng thái Saved/Unsaved
[ ] Thêm confirm khi ghi đè model
[ ] Test profile Văn phòng
[ ] Test profile Giải trí
[ ] Test profile Game 2D
[ ] Test kéo-thả file
[ ] Test chuyển tab
[ ] Test scroll tài liệu
[ ] Commit: polish UX and testing
```

Prompt gợi ý:

```text
Hãy hoàn thiện UX và kiểm thử toàn bộ app. Thêm visual feedback khi pinch/drag, cảnh báo camera không thấy tay, cảnh báo ánh sáng yếu, trạng thái Saved/Unsaved, confirm khi ghi đè model. Test đầy đủ các profile và cập nhật checklist.
```

---

## 15. Tiêu chí hoàn thành

App được coi là đạt yêu cầu khi:

```text
[ ] Có giao diện hiện đại
[ ] Có onboarding chọn tốc độ chuột/độ nhạy/profile
[ ] Có dashboard realtime
[ ] Có profile Văn phòng
[ ] Có profile Giải trí
[ ] Có profile Game 2D
[ ] Có Setup Profile Page
[ ] Có Gesture Training Page
[ ] Có thể thu sample ảnh
[ ] Có thể thu sample video
[ ] Có thể train hoặc cập nhật gesture
[ ] Có thể lưu/hủy cấu hình
[ ] Có kéo-thả bằng pinch_hold → drag_move → drag_release
[ ] Có profile JSON dễ chỉnh sửa
[ ] Có model registry
[ ] Có thể mở rộng thêm gesture/action mới mà không sửa core quá nhiều
```

---

## 16. Ghi chú quan trọng cho Codex/Gemini

Khi thực hiện:

1. Không phá demo cũ nếu chưa refactor xong.
2. Mỗi task hoàn thành phải đánh dấu `[x]` trong README.
3. Mỗi lần làm xong một nhóm task nên commit riêng.
4. Không hard-code mapping gesture-action trong logic chính.
5. Ưu tiên cấu hình bằng JSON.
6. Kéo-thả phải chia nhỏ thành các event nhỏ.
7. Dynamic gesture nên dùng state machine trước, model temporal sau.
8. UI phải có Save và Cancel rõ ràng.
9. Mọi sample train phải có metadata.
10. Hệ thống phải dễ thêm profile mới.

---

## 17. Checklist tổng hợp

```text
[ ] Refactor core
[ ] Tạo profile system
[ ] Tạo action mapper
[ ] Tạo PinchDragDropStateMachine
[ ] Tạo Dashboard UI
[ ] Tạo Setup Profile Page
[ ] Tạo Gesture Training Page
[ ] Tạo image sample collector
[ ] Tạo video sample collector
[ ] Tạo training pipeline
[ ] Tạo model registry
[ ] Thêm visual feedback
[ ] Test profile Văn phòng
[ ] Test profile Giải trí
[ ] Test profile Game 2D
[ ] Đóng gói app
```
