# DieuKhienBangTay

ACV Gesture Control gồm frontend React/Vite và core Python điều khiển chuột bằng camera/hand gesture.

## Cài môi trường

Chạy trong PowerShell tại Windows:

```powershell
cd D:\github\link\DieuKhienBangTay
py -3 -m pip install -r DIEU_KHIEN_CHUOT\requirements.txt

cd frontend
npm install
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
py -3 DIEU_KHIEN_CHUOT\desktop_app.py
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
