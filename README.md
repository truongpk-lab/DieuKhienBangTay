# DieuKhienBangTay

ACV Gesture Control gồm frontend React/Vite và core Python điều khiển chuột bằng camera/hand gesture.

## Cấu trúc logic điều khiển chuột

Logic runtime chính nằm trong `backend/hand_runtime/`. Package này chứa pipeline nhận diện và điều khiển chuột canonical: classifier, geometry correction, pinch drag, smoothing, cooldown, click, scroll, chuyển tab/task, feature utils và model nhận diện đang active.

Các đường dẫn cũ `acv_runtime\...`, `DIEU_KHIEN_CHUOT\hand_mouse\...` và `hand_mouse\...` vẫn được giữ dưới dạng compatibility wrapper để demo/test cũ tiếp tục chạy.

## Cài môi trường

Chạy trong PowerShell tại Windows:

```powershell
cd D:\github\link\DieuKhienBangTay
py -3 -m pip install -r backend\requirements.txt

cd frontend
npm install
```

Nếu cần chạy các script legacy trong `DIEU_KHIEN_CHUOT\` độc lập, có thể cài thêm:

```powershell
py -3 -m pip install -r DIEU_KHIEN_CHUOT\requirements.txt
```

Để bật lệnh giọng nói Gemini, đặt API key trong PowerShell trước khi chạy app:

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

## Khởi động giao diện web

```powershell
cd D:\github\link\DieuKhienBangTay\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Mở:

```text
http://127.0.0.1:5173/
```

## Khởi động backend API

```powershell
cd D:\github\link\DieuKhienBangTay
py -3 -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Kiểm tra:

```text
http://127.0.0.1:8000/api/health
ws://127.0.0.1:8000/ws/runtime
```

## Build kiểm tra frontend

```powershell
cd D:\github\link\DieuKhienBangTay\frontend
npm run build
```

## Chạy desktop app Python

```powershell
cd D:\github\link\DieuKhienBangTay
.\start_acv.bat
```

Lệnh trên gọi `py -3 run_desktop.py`, tự kiểm tra backend, frontend build, camera runtime và trạng thái Gemini/microphone. Nếu thiếu `GEMINI_API_KEY`, app vẫn mở được nhưng lệnh giọng nói AI sẽ bị tắt rõ ràng.

Hoặc gọi trực tiếp launcher:

```powershell
py -3 run_desktop.py
```

Dừng backend/frontend đang chiếm port 8000/5173:

```powershell
stop_acv.bat
```

Kiểm tra launcher không mở cửa sổ:

```powershell
py -3 run_desktop.py --self-test
```

## Chạy demo điều khiển chuột cũ

Lệnh này sẽ mở camera và dùng logic chuột hiện tại:

```powershell
cd D:\github\link\DieuKhienBangTay
py -3 DIEU_KHIEN_CHUOT\demo_run.py
```

## Test nhanh

```powershell
cd D:\github\link\DieuKhienBangTay
py -3 -m compileall .
py -3 -c "from backend.app import app; print('backend app ok')"

cd frontend
npm run build
```
