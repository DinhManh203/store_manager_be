# Hướng dẫn chạy Backend (FastAPI)

Tài liệu này hướng dẫn cách khởi chạy server backend dựa trên FastAPI cho dự án của bạn.

## Các bước khởi chạy

**Trạng thái hiện tại:** Đảm bảo bạn đang mở terminal tại thư mục gốc của dự án là `doan_thanh`.

### Bước 1: Tạo môi trường ảo `venv` (chạy 1 lần)
Nếu dự án chưa có thư mục `venv`, hãy tạo mới bằng lệnh:
```powershell
python -m venv venv
```
*(Nếu máy bạn dùng lệnh `py` thay cho `python`, dùng: `py -m venv venv`)*

### Bước 2: Kích hoạt môi trường ảo (Virtual Environment)
Chạy lệnh phù hợp với terminal bạn đang dùng:

**PowerShell (Windows):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt - CMD (Windows):**
```powershell
.\venv\Scripts\activate.bat
```

**macOS/Linux (bash/zsh):**
```bash
source venv/bin/activate
```

Sau khi kích hoạt, bạn sẽ thấy chữ `(venv)` hiển thị ở đầu dòng lệnh của terminal.

### Bước 3: Cài thư viện cần thiết
Sau khi đã kích hoạt `venv`, cài dependencies:
```powershell
pip install -r backend/requirements.txt
```

### Bước 4: Di chuyển vào thư mục backend
Do file `main.py` dùng để khởi chạy dự án nằm bên trong thư mục `backend`, bạn phải di chuyển terminal vào thư mục này:
```powershell
cd backend
```

### Bước 5: Khởi chạy Server
Sử dụng Uvicorn để chạy ứng dụng (tham số `--reload` giúp server tự động khởi động lại mỗi khi bạn chỉnh sửa và lưu file code):
```powershell
uvicorn main:app --reload
```

Production (Railway) nen dung command:
```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

## 🎯 Kiểm tra kết quả
Nếu terminal báo `Application startup complete.`, bạn có thể truy cập các đường dẫn sau trên trình duyệt:

- **Trang chủ API:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Tài liệu Swagger UI (Dùng để test API):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Tài liệu ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
