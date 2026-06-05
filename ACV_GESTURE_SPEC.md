# TÀI LIỆU CẤU HÌNH CHI TIẾT & CHUẨN KIẾN TRÚC GIAO DIỆN ACV GESTURE CONTROL

Tài liệu này đóng vai trò là **Specification chuẩn hóa** mô tả chi tiết kiến trúc, cấu trúc UI/UX, hệ màu sắc, token tinh chỉnh, cách chia component, và các thư viện cần sử dụng để giúp Code Agent xây dựng ứng dụng **ACV Gesture Control** chính xác 100% so với bản thiết kế mẫu trên cả 5 trang giao diện: **Onboarding (Thiết lập ban đầu), Dashboard (Bảng điều khiển trung tâm), Configuration (Thiết lập cấu hình), Training (Huấn luyện cử chỉ),** và **Hướng dẫn thao tác**.

---

## 1. TRIẾT LÝ THIẾT KẾ & HỆ THỐNG TOKEN (BRAND & IDENTITY)

Giao diện mang phong cách **"Cyber-Clean"** tối tân kết hợp với triết lý **"Breathable Void"** (Khoảng trống có chiều sâu). Phong cách này tạo cảm giác chiều sâu như trong buồng lái khí tài hiện đại thông qua kỹ thuật **Glassmorphism** cường độ cao.

### 1.1 Khai Báo Tone Màu Tailwind (Theme Config)
Hệ thống sử dụng bảng màu **Kinetic Glass** (Deep Obsidian phối Neon Cyan & Electric Blue):

*   **Background chính:** Deep Obsidian (`#0A0A0C`) phối với lưới lưới ảo mờ (Grid size `40px x 40px` màu `rgba(0, 242, 255, 0.03)`).
*   **Thành phần cơ bản:**
    *   `background-color: #131315` (Base Surface)
    *   `surface-container-low: #1c1b1d` (Nền các thanh search, ô nhập liệu)
    *   `surface-container-high: #2a2a2c` (Nền nút chuyển đổi phân đoạn)
    *   `surface-container-lowest: #0e0e10` (Bên trong khung nhìn camera)
*   **Màu tương phản & Viền:**
    *   `primary-container` (Neon Cyan): `#00f2ff` — Dành cho tiêu điểm, khớp bàn tay, trạng thái Active.
    *   `primary-fixed-dim`: `#00dbe7` — Cho viền, chữ sáng hiển thị thông số.
    *   `secondary-container` (Electric Blue): `#4b8eff` — Thể hiện mức độ liên kết hoặc phân loại phụ.
    *   `error` (Alert Red): `#ffb4ab` & `error-container`: `#93000a` — Cho nút Ghi hình, trạng thái LIVE camera.
    *   `outline-variant`: `#3a494b` (Màu viền tối mặc định cho Glass panels).
*   **Độ bo tròn (Rounded Radius):**
    *   Thẻ bảng điều khiển chính: `xl` (24px) hoặc `lg` (16px).
    *   Các nút chức năng, ô dropdown, input: `md` (12px) hoặc `sm` (8px).

---

## 2. KIẾN TRÚC COMPONENT RECT & DANH SÁCH THƯ VIỆN BẮT BUỘC

Để đảm bảo hiệu năng tối đa và tính mượt mà của hiệu ứng chuyển động trong không gian 2D/3D, dự án sử dụng các gói thư viện chuẩn sau:

### 2.1 Các thư viện cốt lõi (Core Library Selection)
1.  **CSS Engine:** **Tailwind CSS v4** (sử dụng trực tiếp các class đa dụng).
2.  **Chuyển động & Hiệu ứng:** **Framer Motion** (import từ `motion/react`) — Bắt buộc dùng cho Stepper, Tag pulse, Flash Capture effect, và các transition chuyển đổi giữa các module.
3.  **Hệ thống Icon:** **Lucide React** — Đồng bộ tất cả các biểu tượng điều hướng và cảm biến (ví dụ: `Mouse`, `Layers`, `Video`, `Brain`, `Settings`, `Play`, `StopCircle`, `Plus`, `Search`, `Bell`, `HelpCircle`, `Activity`, v.v.).
4.  **Hand-Tracking UI simulation:** Vẽ vector hoặc dùng Canvas/SVG thuần với dữ liệu Landmark tọa độ không gian mô phỏng hoặc lấy thực tế từ webcam thông qua SDK.

### 2.2 Kiến trúc File đề xuất (Modular File Tree)
Để chia nhỏ logic, tránh quá tải token khi sinh mã, cấu trúc source code cần tuân thủ cấu trúc sau:

```
/src
  ├── main.tsx                # Điểm khởi chạy của React
  ├── App.tsx                 # Điều phối trang và State Machine chính
  ├── index.css               # Import Tailwind và khai báo các class Glassmorphism
  ├── types.ts                # Khai báo enum màn hình, cấu trúc dữ liệu Gestures & Logs
  ├── components/
  │     ├── SideNavBar.tsx    # Thanh điều hướng trái thống nhất cho toàn app
  │     ├── TopAppBar.tsx     # Header chứa thanh tìm kiếm, trạng thái tracking và avatar
  │     ├── HandCameraHUD.tsx # Module Camera Viewport hiển thị khung xương xương tay 21 điểm
  │     └── TerminalLog.tsx   # Khung console hiển thị nhật ký thời gian thực
  └── views/
        ├── OnboardingView.tsx# Màn hình cấu hình ban đầu
        ├── DashboardView.tsx # Màn hình Dashboard trung tâm
        ├── ConfigView.tsx    # Màn hình thiết lập ánh xạ hạt cử chỉ (Bento grid)
        └── TrainingView.tsx  # Màn hình thu thập dữ liệu và huấn luyện cử chỉ
```

---

## 3. THIẾT KẾ CHI TIẾT CHO TỪNG TRANG & DOM SKELETON

Dưới đây là đặc tả chi tiết cho từng cấu trúc khung HTML của 5 trang chính để Code Agent dễ dàng render khớp hoàn toàn.

---

### Trang 1: Thiết Lập Ban Đầu (Onboarding Modal / View)
**Mục tiêu:** Cung cấp trải nghiệm cấu hình phần cứng trước khi vào Dashboard.

#### Sơ đồ Layout và DOM chính:
*   **Outer Layout:** Centered flex container, phủ một lớp quét mờ CRT nhấp nháy mảnh (`background: repeating-linear-gradient(...)`).
*   **Main Container:** Một Glass Panel lớn (`max-w-4xl`), chia làm hai cột (`flex-col md:flex-row`).
    *   **Cột Trái (Sidebar Info - 1/3 chiều rộng):**
        *   Logo "ACV Gesture Control" kèm icon `View3D`.
        *   Tiêu đề display lớn "Thiết lập ban đầu", đi cùng đoạn hướng dẫn môi trường.
        *   Hộp chỉ báo "Trạng thái cảm biến" dùng hiệu ứng ping không ngừng (`animate-ping`) màu Cyan biểu thị "Sẵn sàng hiệu chỉnh".
        *   Mô phỏng 3D hand nodes tĩnh bằng SVG mờ phía dưới góc trái.
    *   **Cột Phải (Bảng thông số - 2/3 chiều rộng):**
        *   **Thiết bị quay (Webcam Select):** Dropdown được bọc trong một border phát sáng nhẹ khi hover. Sử dụng icon `expand_more` tùy chỉnh.
        *   **Lựa chọn tay chính:** Segmented Control (`Tay trái`, `Tay phải` - Active, `Tự động` - kèm icon ngôi sao lấp lánh).
        *   **Thành phần thanh trượt (Range Sliders):**
            *   Tốc độ chuột (Dải trị `0.1x` -> `3.0x`, mặc định `1.5x`).
            *   Độ nhạy Sensitivity (Phần trăm `0%` -> `100%`, mặc định `75%`).
            *   Khử rung Smoothing (Thang cấp `Mức 1` -> `Mức 5`, mặc định `Mức 3`).
            *   *Lưu ý:* Các thanh trượt phải có điểm hiển thị giá trị hiện tại bằng màu Neon Cyan.
        *   **Lựa chọn cấu hình sử dụng:** Lưới 4 cột chứa các card nhỏ: `Văn phòng` (icon Vali), `Giải trí` (icon Play active), `Game 2D`, `Tùy chỉnh`. Card Active bo viền mờ Cyan rực rỡ và phát bóng đổ dịu.
        *   **Khối nút hành động ở cuối:**
            *   Nút `Bắt đầu hiệu chỉnh`: Phủ mảng màu Gradient rực rỡ từ `inverse-primary` sang `primary-container`.
            *   Nút `Bỏ qua`: Viền bán trong suốt Cyan, hiệu ứng hover phồng nhẹ 2%.

---

### Trang 2: Dashboard Trung Tâm (Dashboard View)
**Mục tiêu:** Màn hình giám sát chính có luồng xử lý thời gian thực, hiển thị chỉ số, camera mô phỏng và Terminal log.

#### Sơ đồ Layout và DOM chính:
*   Trang Dashboard sử dụng lưới **Bento Grid** 12 cột.
*   **Hàng trên (Cốt lõi - 12 cột):** Lưới chia làm 2 phần: **Cột trái (8 cột)** và **Cột phải (4 cột)**.
    *   **Bên trái: Nguồn Video (Camera Live Viewer):**
        *   Header của card chứa text "Nguồn Video" và Badge đỏ lấp lánh chữ "LIVE".
        *   Màn hình giả lập video màu tối, lồng hiệu ứng Grid nền 50px phát sáng dịu.
        *   Sử dụng SVG để vẽ một bàn tay 3D động với các ống liên kết (`stroke="#00f2ff"`) rực rỡ kết hợp bóng mờ, và các chấm khớp tròn có bộ lọc `filter="drop-shadow(...)"`.
        *   Khối HUD hiển thị độ phân giải góc dưới bên trái (`Model: ACV-Hand-v2.1` và `Res: 1920x1080`).
    *   **Bên phải:** Chia làm 2 Block nhỏ xếp lớp:
        *   **Card Hiệu suất điện năng/Hệ thống:** Hiển thị 2 chỉ số dạng đồng hồ/thanh nén:
            *   `FPS 60` — Thanh tiến trình đầy 100%.
            *   `Độ chính xác 98.5%` — Thanh tiến trình đầy 98.5% rực rỡ Cyan.
        *   **Card Ngữ cảnh hoạt động:** Hiển thị các nhãn văn bản:
            *   Hồ sơ: `Văn phòng`.
            *   Cử chỉ đang ghi nhận: `Pinch` (kèm icon bàn tay co ngón phát sáng xanh dương).
            *   Ứng dụng ánh xạ: `Kéo thả`.
            *   **Nút dứt điểm STOP lớn:** Nút tròn khổng lồ ở trung tâm có xung lực sóng mờ LAN TỎA đều ra xung quanh. Khi nhấn vào, trạng thái chuyển từ "Active Tracking" sang dừng cảm biến.
*   **Hàng dưới: Nhật Ký Cử Chỉ (Action Logs):**
    *   Thẻ Bento rộng toàn bề ngang hiển thị dữ liệu log dạng Terminal của lập trình viên.
    *   Giao diện hộp chữ đơn dòng (Font chữ `JetBrains Mono` hoặc `monospace`), hỗ trợ Auto-scroll, có nút `Clear` nhật ký góc trên bên phải.
    *   Cử chỉ đặc biệt (như *Pinch detected*) hiển thị dòng sáng nổi bật màu nền Cyan nhạt và icon ghim đầu dòng màu xanh lá mượt mà.

---

### Trang 3: Thiết Lập Cấu Hình Ánh Xạ (Configuration View)
**Mục tiêu:** Cho phép người dùng kết nối cử chỉ của bàn tay với các lệnh máy tính tương ứng.

#### Sơ đồ Layout và DOM chính:
*   **Tiêu đề trang:** "Thiết lập cấu hình", đi kèm mô tả mục đích.
*   **Bộ lọc mục đích sử dụng:** Một bộ chọn Dropdown kích thước lớn đặt góc phải để đổi chế độ tức thời: `Game 2D (Platformer)`, `Desktop Navigation`, `Presentation Mode`.
*   **Lưới thẻ ánh xạ (6 Card Bento cố định + 1 Card Add Custom):**
    Có 6 thẻ chức năng tiêu chuẩn. Mỗi card mang phong cách Glassmorphism đồng nhất, rực sáng khi con trỏ hover lên:
    1.  *Di chuyển chuột:* Ánh xạ tới cử chỉ `Open Palm Move`. Chứa hình đồ họa vector một bàn tay xòe rực rỡ Cyan nét mảnh trên ảnh nền đêm sâu tối giản.
    2.  *Click trái:* Ánh xạ tới `Pinch Index` (Kẹp ngón trỏ). Hình phác họa ngón tay chụm tạo điểm chạm.
    3.  *Click phải:* Ánh xạ tới `Pinch Middle`. Hình mô phỏng hắt sáng sóng tròn đồng tâm.
    4.  *Kéo thả file:* Ánh xạ tới `Closed Fist Hold`.
    5.  *Cuộn trang:* Ánh xạ tới `Two Finger Swipe`.
    6.  *Tấn công trong game:* Ánh xạ tới `Rapid Punch` (Đấm nhanh - có viền mờ màu đỏ mờ rực lửa thay vì Cyan).
    *   Mỗi thẻ đều có nút chỉnh sửa `Chỉnh sửa` (Sử dụng icon bút chì của Lucide).
    *   **Card thêm mới:** Thẻ có thiết kế viền nét đứt dạng Card Dashboard đầy kích thích, chứa dấu cộng `Plus` lớn rực sáng khi di trỏ chuột tới.
*   **Thanh điều hướng dưới cùng (Bottom Action Bar):**
    Nằm cố định dưới chân trang, mờ kính, phân tách rõ nút hủy `Hủy` (Màu tối) và nút Lưu `LƯU CẤU HÌNH` rực rỡ gradient Cyan-Bluer, có nút Save icon để lưu toàn bộ dữ liệu.

---

### Trang 4: Huấn Luyện Cử Chỉ (Training View)
**Mục tiêu:** Ghi nhận mẫu thực tế từ camera để huấn luyện Custom Model cho người dùng.

#### Sơ đồ Layout và DOM chính:
*   Trang được phân chia theo cấu trúc hai cột dọc cân đối: **Cột tùy biến cấu hình bên trái (1/3)** và **Cột camera ghi nhận bên phải (2/3)**.
*   **Cột Trái (Tùy biến dữ liệu):**
    *   **Bảng điều khiển:** Gồm 2 ô Dropdown lớn: Chọn hồ sơ sử dụng (Profile: Văn phòng, Giải trí,...) và Chọn nhãn cử chỉ huấn luyện (Nhãn chức năng: Kéo thả, Click đơn, Vuốt trái, Vuốt phải,...).
    *   **Chế độ thu thập:** Nút trượt hai lựa chọn: `Chụp ảnh` (Active - bo nền xanh nhạt) hoặc `Quay video`.
    *   **Số lượng mẫu yêu cầu:** Ô nhập số thông minh (Khuyên dùng >50 mẫu, mặc định hiển thị `30` hoặc `50`).
    *   **Tiến độ thu thập mẫu:**
        *   Hiển thị con số lớn phát sáng rực: `24 / 30 mẫu`.
        *   Thành phần Progress Bar có hiệu ứng màu gradient chuyển động rực sắc Cyan.
        *   Báo tỷ lệ phần trăm chính xác bên phải góc chân bar (`80% Hoàn thành`).
*   **Cột Phải (Camera HUD & Nút hành động):**
    *   **Thanh chỉ dẫn banner:** Hộp thông báo có viền dọc nét dày màu Cyan giúp người dùng biết tư thế chuẩn để huấn luyện: *"Kẹp ngón tay để giữ, di chuyển tay, sau đó thả ngón để bỏ."*
    *   **Camera Viewport:** Khung camera rộng, hiển thị tốc độ khung hình và trạng thái thiết bị. Bên trong có khung xương HUD bàn tay màu Neon Cyan mảnh dẻ tự co duỗi nhẹ mô phỏng hoạt động quét thời gian thực.
    *   **Khối nút điều khiển chân Card camera:**
        *   Nhóm bộc phát: Nút `Ghi hình` (Bộ viền đỏ rực sáng, hạt nhân tròn nhấp nháy phát nhịp thở liên tục), nút `Dừng` (icon Stop vuông màu tối).
        *   Nhóm quản lý: Nút `Xem trước mẫu`, nút `Hủy`, nút gradient rực rỡ `Huấn luyện`, và nút `Lưu` vật lý.

---

### Trang 5: Hướng Dẫn Thao Tác
**Mục tiêu:** Cung cấp trung tâm hướng dẫn tiếng Việt giúp người dùng chọn chế độ, hiểu thao tác tay, luyện cử chỉ và xử lý lỗi thường gặp trong ACV Gesture Control.

#### Sơ đồ Layout và DOM chính:
*   Màn hình dùng Bento Grid nhiều Glass Panel, giữ nền Deep Obsidian, viền Neon Cyan và Electric Blue.
*   **Header khu vực:** Hiển thị nhãn `Trung tâm hướng dẫn`, tiêu đề **Hướng dẫn thao tác**, mô tả ngắn và thanh chọn chế độ.
*   **Thanh chọn chế độ:** 4 chế độ `Văn phòng`, `Giải trí`, `Game 2D`, `Tùy chỉnh`; trạng thái active có glow Cyan và icon Lucide tương ứng.
*   **Thư viện chức năng theo chế độ:** Mỗi chế độ hiển thị card chức năng, gesture gợi ý, mô tả thao tác và icon. Các nhóm bắt buộc gồm di chuyển chuột, click, kéo thả, cuộn trang, chuyển tab/phím tắt, play/pause, game action và tác vụ tùy chỉnh.
*   **Khu mô phỏng bàn tay:** Tái dùng `HandSkeleton` để hiển thị điểm tay neon, có hiệu ứng pulse/radar bằng Framer Motion, badge sensor và gesture đang minh họa.
*   **Khối hướng dẫn chuyên nghiệp:** Có quy trình thực hành nhanh, checklist trước khi dùng, lỗi thường gặp, badge độ khó/latency/cảm biến và tín hiệu gần đây bằng tiếng Việt.
*   **Lưu ý kỹ thuật:** Trang này là hướng dẫn thao tác, không gọi realtime workflow API/reset/test; route `workflow` và file `WorkflowView.tsx` vẫn giữ nguyên để tương thích cấu trúc 5 màn hình.

---

## 4. CÁC THIẾT LẬP LẬP TRÌNH & SNIPPETS MẪU DÀNH CHO AGENT

Khi bắt đầu viết code thực tế, Code Agent cận theo các template snippet dưới đây để tạo hiệu quả đồ họa giống hệt bản mẫu thiết kế.

### 4.1 Khai báo Tailwind configuration cho các hiệu ứng phát sáng đặc trưng (index.css)
Để tạo ra các panel phát sáng mờ không gian sâu, Agent cần đưa mẫu CSS Glassmorphism này vào file CSS gốc:

```css
@import "tailwindcss";

@theme {
  --color-brand-cyan: #00f2ff;
  --color-brand-blue: #4b8eff;
  --color-brand-obsidian: #0A0A0C;
  --font-sans: "Inter", sans-serif;
  --font-display: "Be Vietnam Pro", sans-serif;
  --font-mono: "JetBrains Mono", monospace;
}

@layer utilities {
  /* Panel kính mờ thủy tinh tối tân */
  .glass-panel {
    background: rgba(19, 19, 21, 0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(0, 242, 255, 0.15);
  }
  
  .glass-panel:hover {
    background: rgba(19, 19, 21, 0.7);
    border-color: rgba(0, 242, 255, 0.3);
    box-shadow: 0 0 20px rgba(0, 242, 255, 0.1);
  }

  /* Kính mờ trắng cấp 2 */
  .glass-inner {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  /* Chữ phát sáng neon rực rỡ */
  .glow-text {
    text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
  }

  /* Nút tròn phát rung sóng pulse cho phím Stop/Ghi hình */
  .glow-btn-active {
    box-shadow: 0 0 15px rgba(0, 242, 255, 0.5), inset 0 0 8px rgba(0, 242, 255, 0.2);
  }
}
```

### 4.2 Component Mẫu: Khung Vector HUD Bàn Tay 21 Điểm (`HandSkeleton.tsx`)
Vẽ trực tiếp bằng SVG để đảm bảo tốc độ đáp ứng 60FPS không bị lag hay răng cưa:

```tsx
import React from 'react';

export default function HandSkeleton() {
  return (
    <svg viewBox="0 0 200 220" className="w-80 h-80 drop-shadow-lg" xmlns="http://www.w3.org/2000/svg">
      {/* Các liên kết xương bàn tay mảnh mai */}
      <g stroke="#00f2ff" strokeWidth="2" strokeLinecap="round" opacity="0.8">
        {/* Kết nối cổ tay đến các gốc ngón */}
        <line x1="100" y1="180" x2="60" y2="120" />
        <line x1="100" y1="180" x2="80" y2="100" />
        <line x1="100" y1="180" x2="110" y2="90" />
        <line x1="100" y1="180" x2="140" y2="105" />
        <line x1="100" y1="180" x2="160" y2="130" />

        {/* Ngón Cái */}
        <polyline points="60,120 40,105 30,80" fill="none" />
        {/* Ngón Trỏ */}
        <polyline points="80,100 75,55 70,25" fill="none" />
        {/* Ngón Giữa */}
        <polyline points="110,90 110,45 110,15" fill="none" />
        {/* Ngón Áp Út */}
        <polyline points="140,105 145,65 150,35" fill="none" fillOpacity="0" />
        {/* Ngón Út */}
        <polyline points="160,130 170,100 180,75" fill="none" />
      </g>

      {/* Các điểm khớp tròn lấp lánh */}
      <g fill="#e1fdff">
        {/* Điểm Cổ Tay */}
        <circle cx="100" cy="180" r="5" fill="#00f2ff" filter="drop-shadow(0 0 4px #00f2ff)" />
        {/* Các Gốc Ngón */}
        <circle cx="60" cy="120" r="3.5" />
        <circle cx="80" cy="100" r="3.5" />
        <circle cx="110" cy="90" r="3.5" />
        <circle cx="140" cy="105" r="3.5" />
        <circle cx="160" cy="130" r="3.5" />
        {/* Khớp Giữa các ngón */}
        <circle cx="40" cy="105" r="2.5" />
        <circle cx="75" cy="55" r="2.5" />
        <circle cx="110" cy="45" r="2.5" />
        <circle cx="145" cy="65" r="2.5" />
        <circle cx="170" cy="100" r="2.5" />
        {/* Các đầu mút ngón tay cực sáng màu Cyan phát sáng */}
        <circle cx="30" cy="80" r="4" fill="#00dbe7" filter="drop-shadow(0 0 6px #00f2ff)" />
        <circle cx="70" cy="25" r="4" fill="#00dbe7" filter="drop-shadow(0 0 6px #00f2ff)" />
        <circle cx="110" cy="15" r="4" fill="#00dbe7" filter="drop-shadow(0 0 6px #00f2ff)" />
        <circle cx="150" cy="35" r="4" fill="#00dbe7" filter="drop-shadow(0 0 6px #00f2ff)" />
        <circle cx="180" cy="75" r="4" fill="#00dbe7" filter="drop-shadow(0 0 6px #00f2ff)" />
      </g>
    </svg>
  );
}
```

### 4.3 Component Mẫu: Console Log tự cuộn hiển thị hoạt động cử chỉ (`TerminalLog.tsx`)
Đảm bảo mượt mà và trực quan hóa hoạt động thời gian thực:

```tsx
import React, { useEffect, useRef } from 'react';

interface LogEntry {
  time: string;
  type: 'system' | 'detection' | 'gesture' | 'normal';
  message: string;
}

interface TerminalLogProps {
  logs: LogEntry[];
}

export default function TerminalLog({ logs }: TerminalLogProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="flex-grow overflow-y-auto p-4 font-mono text-sm text-on-surface-variant/80 flex flex-col gap-2 relative min-h-[180px]">
      <div className="absolute top-0 left-0 right-0 h-4 bg-gradient-to-b from-surface/80 to-transparent pointer-events-none" />
      
      {logs.map((log, index) => {
        let textClass = 'text-on-surface-variant/90';
        let customBorder = '';
        
        if (log.type === 'system') {
          textClass = 'text-brand-blue';
        } else if (log.type === 'detection') {
          textClass = 'text-brand-cyan font-semibold';
        } else if (log.type === 'gesture') {
          textClass = 'text-brand-cyan bg-brand-cyan/5 border-l-2 border-brand-cyan pl-2';
        }

        return (
          <div key={index} className={`flex items-start gap-4 hover:bg-white/5 p-1 rounded transition-colors ${customBorder}`}>
            <span className="text-gray-500 shrink-0 w-20">{log.time}</span>
            <span className={textClass}>{log.message}</span>
          </div>
        );
      })}
      
      <div ref={endRef} />
    </div>
  );
}
```

---

## 5. HƯỚNG DẪN KIỂM QUÁT (TESTING & VERIFICATION FOR AGENTS)

Để đảm bảo code chạy trơn tru, không có lỗi lặt vặt và chuẩn cấu trúc thiết kế sau khi lắp ghép:

1.  **Lập lờ lặp biến State:** Tất cả các luồng màn hình phụ nên truyền qua một hàm xử lý chuyển trang trong React (phối hợp với `motion.div` để fade-in mượt mà).
2.  **Sử dụng SVG tuyệt đối cho hình vẽ tay cực mảnh:** Tuyệt đối không tải các file hình lớn ngốn bộ nhớ, vẽ bàn tay trực tiếp bằng SVG hoặc dùng canvas gọn nhẹ.
3.  **Hormone Responsive:** Đảm bảo khi kích hoạt ở màn hình di động, thanh SideNavBar sẽ tự biến đổi thành cơ chế Hamburger Drawer ở góc trái trên cùng để tối ưu không hột diện tích.
4.  **Kiểm thử biên tập lỗi:** Chạy `npm run lint` hoặc `npm run build` để rà soát tất cả các lỗi TS hoặc biến chưa khai báo trước khi hoàn thành công việc.

---
*Tài liệu này được biên soạn tỉ mỉ bởi Hệ thống Phân tích Bản Thiết kế Google AI Studio.*
