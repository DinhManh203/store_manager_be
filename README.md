# Hướng dẫn chạy Backend (FastAPI)

Tài liệu này hướng dẫn cách khởi chạy server backend dựa trên FastAPI cho dự án của bạn.

## Các bước khởi chạy

**Trạng thái hiện tại:** Đảm bảo bạn đang mở terminal tại thư mục gốc của dự án là `doan_thanh`.

### Bước 1: Kích hoạt môi trường ảo (Virtual Environment)
Nếu bạn chưa kích hoạt môi trường ảo đang chứa các thư viện Python, hãy thao tác lệnh sau trên terminal của Windows (dành cho PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```
*(Lưu ý: Nếu bạn sử dụng Command Prompt (CMD) cũ của Windows, hãy chạy: `.\venv\Scripts\activate.bat`)* 

Sau khi kích hoạt, bạn sẽ thấy chữ `(venv)` hiển thị ở đầu dòng lệnh của terminal.

### Bước 2: Di chuyển vào thư mục backend
Do file `main.py` dùng để khởi chạy dự án nằm bên trong thư mục `backend`, bạn phải di chuyển terminal vào thư mục này:
```powershell
cd backend
```

### Bước 3: Khởi chạy Server
Sử dụng Uvicorn để chạy ứng dụng (tham số `--reload` giúp server tự động khởi động lại mỗi khi bạn chỉnh sửa và lưu file code):
```powershell
uvicorn main:app --reload
```

---

## 🎯 Kiểm tra kết quả
Nếu terminal báo `Application startup complete.`, bạn có thể truy cập các đường dẫn sau trên trình duyệt:

- **Trang chủ API:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Tài liệu Swagger UI (Dùng để test API):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Tài liệu ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
