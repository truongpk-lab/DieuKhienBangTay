# Button Inventory — ACV Gesture Control Frontend

Phase 20 audit target: find all frontend buttons/selects/inputs/sliders and classify whether they are navigation-only, backend/runtime actions, persistence actions, training/model actions, mock controls, confirmation points, and loading/error/success candidates.

Audit commands used:

```powershell
rg -n "<button|onClick=|<select|<input|type=\"range\"|type='range'" frontend/src
rg -n "startRuntime|stopRuntime|createRuntimeSocket|getRuntimeStatus|getProfiles|getGestureLogs" frontend backend
rg -n "Bắt đầu|Khởi động|START|STOP|LƯU|Hủy|Chỉnh sửa|Thêm mới|Ghi hình|Dừng|Huấn luyện|Lưu" frontend/src
```

## Summary

| Category | Count | Notes |
|---|---:|---|
| Navigation-only controls | 10 | Side navigation buttons in desktop and mobile layouts. |
| Backend-connected controls | 1 | Dashboard Start/Stop calls `POST /api/runtime/start` or `POST /api/runtime/stop`, with local mock fallback. |
| Backend-read controls | 4 | App loads runtime, profiles, gesture logs, and WebSocket updates through `frontend/src/api/backend.ts`. |
| Mock controls needing backend/API wiring | 29 | Mostly onboarding, config, training, top app bar, and workflow actions. |
| Confirmation controls | 2 | Training overwrite model and cancel training use `window.confirm`. |
| Loading/error/success gaps | 31 | Most actionable controls need explicit disabled/loading/error/success handling. |

## Existing API Coverage

| Frontend API | Endpoint | Current usage | Status |
|---|---|---|---|
| `getRuntimeStatus` | `GET /api/runtime/status` | `App.tsx` snapshot polling | Connected |
| `startRuntime` | `POST /api/runtime/start` | Dashboard power button | Connected, needs loading/error UI |
| `stopRuntime` | `POST /api/runtime/stop` | Dashboard power button | Connected, needs loading/error UI |
| `getProfiles` | `GET /api/profiles` | `App.tsx`, passed into Config/Training | Connected for read |
| `getGestureLogs` | `GET /api/gestures/logs` | `App.tsx`, Dashboard log | Connected for read |
| `createRuntimeSocket` | `WS /ws/runtime` | `App.tsx` runtime/log updates | Connected, needs reconnect/error UX |

## App Shell

| Label/control | File | Type | Current behavior | Intended behavior | API needed | State needs |
|---|---|---|---|---|---|---|
| Dashboard | `frontend/src/components/SideNavBar.tsx` | A. Navigation | Calls `onChange('dashboard')` | Change local view only | None | Active state already present |
| Thiết lập ban đầu | `frontend/src/components/SideNavBar.tsx` | A. Navigation | Calls `onChange('onboarding')` | Change local view only | None | Active state already present |
| Cấu hình | `frontend/src/components/SideNavBar.tsx` | A. Navigation | Calls `onChange('config')` | Change local view only | None | Active state already present |
| Huấn luyện cử chỉ | `frontend/src/components/SideNavBar.tsx` | A. Navigation | Calls `onChange('training')` | Change local view only | None | Active state already present |
| Hướng dẫn thao tác | `frontend/src/components/SideNavBar.tsx` | A. Navigation | Calls `onChange('workflow')` | Change local view only | None | Active state already present |
| Mobile nav icons | `frontend/src/components/SideNavBar.tsx` | A. Navigation | Same as desktop nav with icon-only buttons | Change local view only | None | Active state already present |
| Bell icon | `frontend/src/components/TopAppBar.tsx` | E. Mock | No handler | Open notification/error panel | Later: `GET /api/notifications` or local alert store | Loading optional, empty/error state |
| Help icon | `frontend/src/components/TopAppBar.tsx` | E. Mock | No handler | Open help/about/support panel | None or `GET /api/help` if docs become backend-driven | Open/closed state |

## DashboardView

| Label/control | File | Type | Current behavior | Intended behavior | API needed | State needs |
|---|---|---|---|---|---|---|
| Power Start/Stop | `frontend/src/views/DashboardView.tsx` | B. Runtime backend | Calls `startRuntime` or `stopRuntime`; Start success calls app minimize with browser fallback; Stop calls app show; on failure toggles local mock runtime | Start/stop runtime idempotently, update status via WebSocket, auto-hide app in desktop mode after start | `POST /api/runtime/start`, `POST /api/runtime/stop`, `POST /api/app/minimize`, `POST /api/app/show` | Loading while starting/stopping, disabled repeat clicks, backend error, fallback guidance |
| Clear | `frontend/src/components/TerminalLog.tsx` via `DashboardView.tsx` | B. Runtime backend | Calls backend log clear and falls back to local clear if backend is offline | Clear backend gesture log and UI log together | `DELETE /api/gestures/logs` | Loading, error, success/empty log state |
| Pause/Resume | `frontend/src/views/DashboardView.tsx` | B. Runtime backend | Calls runtime pause/resume with Mock Mode fallback | Pause active tracking without releasing the whole app session | `POST /api/runtime/pause`, `POST /api/runtime/resume` | Loading, disabled while idle, backend error, fallback log |
| Recenter | `frontend/src/views/DashboardView.tsx` | B. Runtime backend | Calls runtime recenter with Mock Mode fallback | Recenter/calibrate runtime state | `POST /api/runtime/recenter` | Loading, disabled while idle, backend error, fallback log |
| Show/Hide app | `frontend/src/views/DashboardView.tsx` | B. App visibility backend | Calls app visibility API with browser fallback guidance | Hide/minimize app during active tracking and show it again | `POST /api/app/minimize`, `POST /api/app/show` | Loading, unsupported-browser warning |
| Settings | `frontend/src/views/DashboardView.tsx` | A. Navigation | Switches to ConfigView | Open profile/settings configuration | Local view state | Disabled while another dashboard action is busy |
| Emergency stop | `frontend/src/views/DashboardView.tsx` | B. Runtime backend | Calls runtime stop and app show with Mock Mode fallback | Stop tracking quickly and return control to visible app | `POST /api/runtime/stop`, `POST /api/app/show` | Loading, backend error, fallback stopped state |
| Switch profile nhanh | `frontend/src/views/DashboardView.tsx` | B. Profile backend | Calls active profile API with Mock Mode fallback | Activate selected profile and update runtime context | `POST /api/profiles/{id}/activate` | Loading, backend error, fallback local profile |
| Hand detected badge | `frontend/src/views/DashboardView.tsx` | E. Mock status | Static badge | Reflect backend hand/camera state | Runtime WebSocket payload | Warning/error state |
| Pinch badge | `frontend/src/views/DashboardView.tsx` | E. Mock status | Static badge | Reflect current gesture | Runtime WebSocket payload | Confidence/unknown state |
| Dragging badge | `frontend/src/views/DashboardView.tsx` | E. Mock status | Static badge | Reflect action/drag state | Runtime WebSocket payload | Active/inactive/error state |

## OnboardingView

| Label/control | File | Type | Current behavior | Intended behavior | API needed | State needs |
|---|---|---|---|---|---|---|
| Webcam select | `frontend/src/views/OnboardingView.tsx` | E. Mock select | Static `Webcam HD Camera` option | Load camera list and persist selected camera | `GET /api/cameras`, `PUT /api/settings` | Loading cameras, no-camera warning, save error |
| Tay trái / Tay phải / Tự động | `frontend/src/views/OnboardingView.tsx` | E. Mock segmented control | Static visual active on `Tay phải` | Update hand mode setting | `PUT /api/settings` | Local selected state, save pending/error |
| Tốc độ chuột slider | `frontend/src/views/OnboardingView.tsx` | E. Mock range | Static default value | Persist speed multiplier | `PUT /api/settings` | Dirty/saved state, validation |
| Sensitivity slider | `frontend/src/views/OnboardingView.tsx` | E. Mock range | Static default value | Persist sensitivity | `PUT /api/settings` | Dirty/saved state, validation |
| Smoothing slider | `frontend/src/views/OnboardingView.tsx` | E. Mock range | Static default value | Persist smoothing level | `PUT /api/settings` | Dirty/saved state, validation |
| Profile cards | `frontend/src/views/OnboardingView.tsx` | E. Mock selection | Static visual active on `Văn phòng` | Activate selected profile | `POST /api/profiles/{id}/activate`, optionally `PUT /api/settings` | Selected/loading/error/success state |
| Bắt đầu hiệu chỉnh | `frontend/src/views/OnboardingView.tsx` | B/C. Calibration backend | No handler | Save settings, start calibration, then route to Dashboard when ready | `PUT /api/settings`, `POST /api/calibration/start` | Loading, calibration active, error, success |
| Bỏ qua | `frontend/src/views/OnboardingView.tsx` | C. Settings backend | No handler | Save defaults/selected profile and route to Dashboard | `PUT /api/settings`, `POST /api/calibration/skip` | Loading, error, success |

## ConfigView

| Label/control | File | Type | Current behavior | Intended behavior | API needed | State needs |
|---|---|---|---|---|---|---|
| Profile dropdown | `frontend/src/views/ConfigView.tsx` | E. Partially connected read | Options come from `GET /api/profiles`, but changing selection does not load mappings | Load selected profile detail and mappings | `GET /api/profiles/{id}` | Loading profile, not found/error |
| Chỉnh sửa | `frontend/src/views/ConfigView.tsx` | E. Mock action | No handler | Open edit modal/drawer for gesture/action mapping | Local modal plus later `PUT /api/profiles/{id}` | Editing, validation, duplicate gesture errors |
| Thêm mới | `frontend/src/views/ConfigView.tsx` | E. Mock action | No handler | Add new function mapping draft | Local draft plus later `PUT /api/profiles/{id}` | Editing, validation, dirty state |
| Hủy | `frontend/src/views/ConfigView.tsx` | E. Mock action | No handler | Roll back local changes after confirm if dirty | `GET /api/profiles/{id}` if reload from source | Confirm, dirty reset |
| LƯU CẤU HÌNH | `frontend/src/views/ConfigView.tsx` | C. Mock save | Sets local `saved=true` | Validate and persist selected profile mapping | `PUT /api/profiles/{id}` | Loading, validation errors, success, conflict/error |
| Saved/Unsaved label | `frontend/src/views/ConfigView.tsx` | G. State indicator | Local only | Reflect real dirty/saved status | Same profile save/load APIs | Dirty, saving, saved, failed |

Missing Config controls from `updatas.md`: enable/disable function, delete function, action/gesture selectors in edit modal.

## TrainingView

| Label/control | File | Type | Current behavior | Intended behavior | API needed | State needs |
|---|---|---|---|---|---|---|
| Profile select | `frontend/src/views/TrainingView.tsx` | E. Partially connected read | Options come from profiles prop; no selected state/API side effect | Select training target profile | Local plus `POST /api/training/session/start` payload | Selected state, profile load error |
| Function/label select | `frontend/src/views/TrainingView.tsx` | E. Mock select | Static options `Kéo thả`, `Click đơn` | Load functions from selected profile | `GET /api/profiles/{id}` | Loading, empty functions state |
| Chụp ảnh | `frontend/src/views/TrainingView.tsx` | E. Mock mode button | Static active visual | Set capture mode to image | Local plus training session payload | Selected state |
| Quay video | `frontend/src/views/TrainingView.tsx` | E. Mock mode button | No handler | Set capture mode to video | Local plus training session payload | Selected state |
| Sample count input | `frontend/src/views/TrainingView.tsx` | E. Mock input | Static default `30` | Set target sample count | Local plus training session payload | Validation, min/max |
| Ghi hình | `frontend/src/views/TrainingView.tsx` | D. Mock training action | No handler | Start training/capture session | `POST /api/training/session/start` | Loading, recording, error |
| Dừng | `frontend/src/views/TrainingView.tsx` | D. Mock training action | No handler | Stop capture/session and release camera/session resources | `POST /api/training/session/stop` | Loading, stopped, error |
| Xem trước mẫu | `frontend/src/views/TrainingView.tsx` | D. Mock training action | No handler | Load captured sample previews | `GET /api/training/samples/preview` | Loading, empty/error preview state |
| Huấn luyện | `frontend/src/views/TrainingView.tsx` | D/F. Mock confirm action | Confirms overwrite, then only sets `saved=false` | Run training pipeline or explicit stub | `POST /api/training/train` | Confirm, loading, metrics/success, error |
| Lưu | `frontend/src/views/TrainingView.tsx` | D. Mock save | Sets local `saved=true` | Save model/session to registry | Existing backend has `POST /api/training/session/save`; target plan says `POST /api/training/save` | Loading, saved, error |
| Hủy | `frontend/src/views/TrainingView.tsx` | D/F. Mock confirm action | Confirms cancel only; no state/API call | Cancel training session and discard draft samples | Existing backend has `POST /api/training/session/cancel`; target plan says `POST /api/training/cancel` | Confirm, loading, cancelled, error |
| Sample error alert | `frontend/src/views/TrainingView.tsx` | G. Mock state | Static warning | Reflect backend sample validation errors | `GET /api/training/status` or WebSocket | Error details, dismiss/retry state |
| Unsaved changes alert | `frontend/src/views/TrainingView.tsx` | G. Mock state | Local saved flag | Reflect session/model dirty state | Training status/model registry APIs | Dirty/saved/error state |

Backend currently exposes `GET /api/training/status`, `POST /api/training/session/start`, `POST /api/training/session/stop`, `POST /api/training/session/save`, and `POST /api/training/session/cancel`. Preview, train, and target endpoint aliases are not yet present.

## WorkflowView

| Label/control | File | Type | Current behavior | Intended behavior | API needed | State needs |
|---|---|---|---|---|---|---|
| Stepper active state | `frontend/src/views/WorkflowView.tsx` | E. Mock status | Step 3 is always active | Reflect drag state from runtime/state machine | Runtime WebSocket payload with drag state | idle/holding/dragging/released/cancelled |
| Sensor badge | `frontend/src/views/WorkflowView.tsx` | E. Mock status | Static `Sensor: Active` | Reflect backend hand/camera sensor state | Runtime WebSocket payload | active/lost/error |
| Latency badge | `frontend/src/views/WorkflowView.tsx` | E. Mock status | Static `Latency: 12ms` | Reflect real runtime latency | Runtime WebSocket payload | stale/unknown state |

Missing Workflow controls from `updatas.md`: Dev-mode test state button and reset workflow button.

## API Gaps To Create Later

| Needed by | Endpoint | Purpose |
|---|---|---|
| Dashboard Clear log | `DELETE /api/gestures/logs` | Clear backend log store |
| Dashboard Pause/Resume | `POST /api/runtime/pause`, `POST /api/runtime/resume` | Pause without full runtime stop |
| Dashboard Recenter | `POST /api/runtime/recenter` or `POST /api/calibration/recenter` | Recenter pointer/calibration |
| Dashboard Show/Hide | `POST /api/app/minimize`, `POST /api/app/show` | Desktop shell visibility |
| Onboarding Cameras | `GET /api/cameras` | List camera devices |
| Onboarding Settings | `GET /api/settings`, `PUT /api/settings` | Persist camera/hand/speed/sensitivity/smoothing/profile |
| Onboarding Calibration | `POST /api/calibration/start`, `POST /api/calibration/skip` | Start or skip setup workflow |
| Config Save | `PUT /api/profiles/{id}` | Persist profile mapping changes |
| Config Delete | `DELETE /api/profiles/{id}/functions/{function_id}` or profile PUT | Remove mapping |
| Training Preview | `GET /api/training/samples/preview` | Preview captured samples |
| Training Train | `POST /api/training/train` | Run training pipeline |
| Training Save alias | `POST /api/training/save` | Save model/session using target plan naming |
| Training Cancel alias | `POST /api/training/cancel` | Cancel using target plan naming |
| Workflow State | Runtime WebSocket `drag_state` payload | Drive workflow UI from real state machine |

## Phase 21 Preparation Notes

`frontend/src/api/backend.ts` is a useful starting point but mixes all endpoints in one file. Phase 21 should split it into `http.ts`, `runtimeApi.ts`, `profileApi.ts`, `trainingApi.ts`, `modelApi.ts`, `settingsApi.ts`, and `websocket.ts`, then make every feature control call through those typed modules.

No MouseController, demo, or Python control logic was changed during this audit.
