# AGENTS.md — ACV Coding Agent Rules

## 1. Mục tiêu dự án

Nâng cấp project ACV từ demo điều khiển chuột bằng cử chỉ tay thành một app hoàn chỉnh có:

- Giao diện hiện đại.
- Dashboard realtime.
- Profile theo mục đích sử dụng:
  - Văn phòng
  - Giải trí
  - Game 2D
  - Custom
- Trang setup profile/action mapping.
- Trang huấn luyện cử chỉ.
- Workflow kéo-thả chính xác theo từng bước nhỏ.
- Dataset collector.
- Training pipeline.
- Model registry.
- Dễ mở rộng thêm gesture/action/profile mới.

Tài liệu chính cần tuân thủ:

```text
README_ACV_UPGRADE.md
2. Quy tắc bắt buộc trước khi sửa code

Trước khi sửa bất kỳ file nào:

[ ] Đọc AGENTS.md
[ ] Đọc README_ACV_UPGRADE.md
[ ] Dùng rg để tìm file liên quan
[ ] Không đọc toàn bộ repo nếu chưa cần
[ ] Chỉ làm đúng nhóm task được yêu cầu trong prompt

Luôn ưu tiên dùng:

rg "MouseController"
rg "gesture"
rg "pyautogui"
rg "stable_label"
rg "demo_run"
rg "mediapipe"

Không được tự ý làm nhiều phase cùng lúc.

3. Nguyên tắc tiết kiệm token

Agent phải làm theo nguyên tắc:

Không paste lại file dài nếu không cần.
Không đọc toàn bộ repo một lần.
Không sửa file ngoài phạm vi task.
Tìm đúng file bằng rg trước.
Chỉ mở file liên quan trực tiếp.
Nếu cần refactor lớn, chia thành nhiều bước nhỏ.
Nếu task chưa rõ, đọc lại README trước thay vì đoán.
4. Kiến trúc mục tiêu

Core flow của app:

Camera
→ Hand Tracking
→ Landmark Extraction
→ Gesture Recognition
→ Gesture State Machine
→ Gesture Event
→ Profile Action Mapping
→ Mouse/Keyboard/App Action

Không để logic chính bị dồn vào một file lớn.

Không để demo_run.py chứa toàn bộ:

Camera handling
MediaPipe tracking
Gesture classifier
Mouse control
Profile mapping
Training logic
UI logic
5. Cấu trúc thư mục mục tiêu

Nếu chưa có, tạo dần theo từng task:

ACV/
│
├── README_ACV_UPGRADE.md
├── AGENTS.md
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

Không bắt buộc tạo tất cả cùng lúc. Chỉ tạo thư mục/file tương ứng với task hiện tại.

6. Quy tắc refactor

Khi refactor:

Không phá demo cũ.
Không đổi behavior nếu task chỉ yêu cầu tách module.
Nếu tách class/function, giữ API đơn giản.
Nếu file cũ đang chạy được, phải giữ đường chạy tương thích.
Không xóa code cũ khi chưa có module thay thế chạy ổn.
Nếu đổi import, kiểm tra lại đường dẫn import.

Với project hiện tại, ưu tiên tách:

MouseController → actions/mouse_controller.py
Camera capture → core/camera_service.py
MediaPipe hand tracking → core/hand_tracker.py
Feature extraction → core/feature_extractor.py
Model predict → core/gesture_classifier.py
Gesture smoothing/filter → core/temporal_filter.py
Gesture event/state → core/gesture_state_machine.py
7. Quy tắc profile/action mapping

Không hard-code kiểu:

if gesture == "fist":
    mouse_down()

Thay vào đó phải dùng mapping:

{
  "gesture_event": "pinch_hold",
  "action": "mouse.down"
}

Mapping phải nằm trong:

profiles/configs/*.json

Các profile bắt buộc:

office.json
entertainment.json
game_2d.json
custom.json

Profile phải có tối thiểu:

{
  "id": "office",
  "name": "Văn phòng",
  "description": "...",
  "mouse": {},
  "gesture_filter": {},
  "functions": []
}
8. Quy tắc kéo-thả

Kéo-thả không được làm thành một gesture lớn duy nhất.

Sai:

pinch_drag_drop → kéo thả toàn bộ

Đúng:

pinch_hold → mouse.down
drag_move → mouse.move
drag_release → mouse.up

State machine cần có các state:

idle
pinch_candidate
holding
dragging
released

Event bắt buộc:

pinch_start
pinch_hold
drag_start
drag_move
drag_release
pinch_cancel

Khi test kéo-thả, phải test tối thiểu:

[ ] Kéo file trong Windows Explorer
[ ] Kéo folder
[ ] Kéo icon desktop
[ ] Kéo tab browser nếu có thể
9. Quy tắc UI

UI phải theo hướng hiện đại:

Dark mode
Card layout
Bo góc lớn
Có preview camera
Có skeleton hand overlay
Có trạng thái realtime
Có nút Save/Cancel rõ ràng

Các trang chính:

[ ] Onboarding Page
[ ] Dashboard Page
[ ] Setup Profile Page
[ ] Gesture Training Page
[ ] Live Test Page
[ ] Settings Page

Không được trộn UI logic với AI core.

UI chỉ gọi service/core module.

10. Quy tắc Gesture Training Page

Trang huấn luyện cử chỉ phải cho phép:

[ ] Chọn mục đích sử dụng/profile
[ ] Chọn chức năng cần train
[ ] Chọn chụp ảnh hoặc quay video
[ ] Chọn số lượng mẫu
[ ] Preview camera
[ ] Hiển thị hướng dẫn thao tác
[ ] Thu sample
[ ] Xem lại sample
[ ] Xóa sample lỗi
[ ] Train
[ ] Save
[ ] Cancel

Dữ liệu ảnh dùng cho gesture tĩnh:

open_hand
fist
one_finger
two_fingers
palm_stop
pinch

Dữ liệu video dùng cho gesture động:

swipe_left
swipe_right
swipe_up
swipe_down
pinch_drag_drop
11. Quy tắc dataset

Mỗi sample phải có metadata:

{
  "sample_id": "...",
  "profile": "...",
  "function_id": "...",
  "gesture_label": "...",
  "data_type": "image_or_video",
  "created_at": "...",
  "landmarks": [],
  "features": {}
}

Với dynamic/video sample, phải lưu theo frame:

{
  "frames": [
    {
      "t": 0.0,
      "landmarks": [],
      "features": {}
    }
  ],
  "segments": [
    {
      "name": "pinch_hold",
      "start": 0.2,
      "end": 0.7
    }
  ]
}

Không lưu dữ liệu thiếu label.

Không lưu sample không phát hiện được bàn tay.

12. Quy tắc training

Static gesture:

Collect image samples
→ Extract landmarks
→ Normalize landmarks
→ Extract features
→ Train classifier
→ Evaluate
→ Save model

Dynamic gesture:

Collect video samples
→ Extract landmark sequence
→ Normalize sequence
→ Pad/trim sequence
→ Train temporal model hoặc state machine
→ Evaluate
→ Save model

Giai đoạn đầu có thể dùng rule-based state machine cho dynamic gesture. Không bắt buộc train LSTM ngay nếu chưa đủ dữ liệu.

13. Quy tắc model registry

Sau khi train model, phải lưu metadata:

{
  "model_id": "static_gesture_v1",
  "type": "static",
  "path": "models/static_gesture_model.joblib",
  "created_at": "...",
  "profiles": ["office"],
  "labels": [],
  "metrics": {
    "accuracy": 0.0,
    "macro_f1": 0.0
  },
  "dataset": {
    "sample_count": 0
  }
}

Cần hỗ trợ:

[ ] Ghi version mới
[ ] Set active model
[ ] Rollback model cũ
[ ] Hiển thị model active trong UI
14. Quy tắc test

Sau mỗi task, phải kiểm tra tối thiểu:

python --version
pip install -r requirements.txt

Nếu task liên quan demo cũ:

python DIEU_KHIEN_CHUOT\demo_run.py

Nếu task thêm module mới, phải test import:

python -c "from core.hand_tracker import HandTracker; print('ok')"
python -c "from actions.mouse_controller import MouseController; print('ok')"

Nếu có test file thì chạy:

pytest

Nếu chưa có test, tạo test đơn giản cho module mới khi phù hợp.

15. Quy tắc cập nhật checklist

Sau khi hoàn thành task:

Mở README_ACV_UPGRADE.md.
Đổi task đã xong từ [ ] thành [x].
Không đánh dấu task chưa test.
Không đánh dấu toàn bộ phase nếu chỉ làm một phần.

Ví dụ:

[ ] Tạo camera_service.py

sau khi xong:

[x] Tạo camera_service.py
16. Quy tắc báo cáo sau khi hoàn thành

Sau khi sửa xong, agent phải báo cáo theo format:

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

Không chỉ nói “done”.

17. Thứ tự phase bắt buộc

Làm theo thứ tự:

1. Refactor core project
2. Thêm profile system
3. Thêm PinchDragDropStateMachine
4. Xây Dashboard UI
5. Xây Setup Profile Page
6. Xây Gesture Training Page
7. Dataset collector
8. Training pipeline
9. Model registry
10. Polish UX + test

Không nhảy sang UI khi core chưa tách.

Không làm training pipeline khi dataset collector chưa xong.

18. Prompt mặc định cho mỗi task

Khi nhận task, agent phải tự tuân thủ:

- Đọc README_ACV_UPGRADE.md.
- Đọc AGENTS.md.
- Dùng rg để tìm file liên quan.
- Làm đúng task hiện tại.
- Không tự ý mở rộng phạm vi.
- Cập nhật checklist.
- Test cơ bản.
- Báo cáo file đã sửa.
19. Những điều không được làm

Không được:

[ ] Xóa demo cũ khi chưa có bản thay thế
[ ] Hard-code profile trong demo_run.py
[ ] Hard-code gesture-action trong core
[ ] Trộn UI với training logic
[ ] Trộn UI với mouse control logic
[ ] Tạo một file quá lớn chứa mọi thứ
[ ] Đánh dấu checklist khi chưa test
[ ] Thêm dependency mà không cập nhật requirements.txt
[ ] Sửa nhiều phase trong một lần nếu prompt không yêu cầu
20. Lưu ý cho project ACV

Project hiện tại có thể đang có thư mục:

DIEU_KHIEN_CHUOT/

Không đổi tên thư mục này nếu chưa cần.

Khi refactor, có thể tạo module mới ở root, nhưng phải giữ đường chạy cũ:

python DIEU_KHIEN_CHUOT\demo_run.py

Nếu cần import từ root vào file trong DIEU_KHIEN_CHUOT, phải xử lý đường dẫn cẩn thận để không lỗi module.

21. Tiêu chí hoàn thành cuối cùng

App đạt yêu cầu khi:

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
[ ] Có thể train/cập nhật gesture
[ ] Có thể save/cancel cấu hình
[ ] Có kéo-thả bằng pinch_hold → drag_move → drag_release
[ ] Có profile JSON dễ chỉnh sửa
[ ] Có model registry
[ ] Có thể mở rộng thêm gesture/action mới

Sau khi tạo file này, chạy kiểm tra:

```powershell
dir AGENTS.md