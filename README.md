# Hệ thống Thu thập Thông tin LinkedIn Dành cho Kỹ thuật viên Dược phẩm

## Giới thiệu

Hệ thống tự động này sử dụng CrewAI để thu thập thông tin từ LinkedIn về các Kỹ thuật viên Dược phẩm tại Hoa Kỳ, phân tích hồ sơ của họ, và lưu trữ dữ liệu trong cơ sở dữ liệu PostgreSQL. Hệ thống cung cấp một API để truy cập dữ liệu thu thập được một cách dễ dàng.

### Tính năng chính

- Tự động tìm kiếm và thu thập thông tin hồ sơ LinkedIn của Kỹ thuật viên Dược phẩm
- Trích xuất dữ liệu quan trọng như kinh nghiệm, chứng chỉ, kỹ năng chuyên môn và nơi làm việc
- Tính điểm và xếp hạng ứng viên dựa trên tiêu chí đánh giá
- Lưu trữ tất cả dữ liệu trong cơ sở dữ liệu PostgreSQL
- Cung cấp API RESTful để truy cập và quản lý dữ liệu
- Tạo báo cáo chi tiết về nguồn nhân lực Kỹ thuật viên Dược phẩm

## Yêu cầu hệ thống

- Python 3.9+
- PostgreSQL
- Trình duyệt Firefox (cho Selenium)


## Hướng dẫn cài đặt

### 1. Chuẩn bị môi trường

Đầu tiên, hãy clone repository và cài đặt các phụ thuộc:

```bash
# Clone repository
git clone https://github.com/phuongth20/crew-ai-pharmacy.git
cd crew-ai-pharmacy

# Tạo môi trường ảo (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate

# Cài đặt các phụ thuộc
pip install -r requirements.txt
```

### 2. Cài đặt và cấu hình PostgreSQL

Bạn có thể cài đặt PostgreSQL trực tiếp trên máy hoặc sử dụng Docker:

**Cài đặt trực tiếp:**
- Tải và cài đặt PostgreSQL từ trang chủ: https://www.postgresql.org/download/
- Tạo cơ sở dữ liệu mới có tên `pharmacy_tech_db`
- Tạo người dùng và cấp quyền cho cơ sở dữ liệu



### 3. Cấu hình môi trường

Tạo file `.env` trong thư mục gốc của dự án:

```
# OPENAI
OPENAI_API_KEY=openai_api_value

# LinkedIn
LINKEDIN_COOKIE=your_linkedin_cookie_value

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_DB=pharmacy_tech_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432

# API
API_HOST=0.0.0.0
API_PORT=8000
```

**Lưu ý quan trọng:** Để lấy giá trị cookie LinkedIn:
1. Đăng nhập vào tài khoản LinkedIn của bạn trên trình duyệt
2. Mở Developer Tools (F12 hoặc Ctrl+Shift+I)
3. Chuyển đến tab Application > Cookies
4. Tìm cookie có tên `li_at` và sao chép giá trị của nó

### 4. Chạy hệ thống

# Khởi động API server
python main.py
```


## Hướng dẫn sử dụng

### 1. Thu thập dữ liệu từ LinkedIn
-  Gọi API endpoint:
```bash
curl -X POST http://localhost:8000/api/search -H "Content-Type: application/json" -d '{"criteria": "Pharmacy Technician, California"}'
```

### 2. Truy cập dữ liệu thông qua API

API hỗ trợ các endpoint sau:

- `GET /api/candidates`: Lấy danh sách tất cả các ứng viên
- `GET /api/candidates/{id}`: Lấy thông tin chi tiết của một ứng viên cụ thể
- `GET /api/candidates/top`: Lấy danh sách ứng viên có điểm cao nhất
- `GET /api/statistics`: Lấy thống kê về dữ liệu
- `POST /api/search`: Bắt đầu tìm kiếm mới trên LinkedIn
- `PUT /api/candidates/{id}/score`: Cập nhật điểm của ứng viên

Ví dụ:
```bash
# Lấy danh sách ứng viên
curl http://localhost:8000/api/candidates

# Lấy ứng viên có điểm cao nhất
curl http://localhost:8000/api/candidates/top

# Lấy thống kê
curl http://localhost:8000/api/statistics
```

### 3. Tạo báo cáo

Báo cáo được tạo tự động sau khi hoàn thành quá trình thu thập và phân tích dữ liệu. Bạn có thể xem báo cáo thông qua API:

```bash
curl http://localhost:8000/api/report
```

## Cấu trúc dự án

```
pharmacy_linkedin_agent/
├── config/                  # Cấu hình cho agents và tasks
│   ├── agents.yaml
│   └── tasks.yaml
├── recruitment/             # Mã nguồn chính
│   ├── tools/
│   │   ├── client.py        # LinkedIn client
│   │   ├── database.py      # Xử lý cơ sở dữ liệu
│   │   ├── driver.py        # Selenium WebDriver
│   │   └── linkedin.py      # Công cụ LinkedIn cho CrewAI
│   ├── crew.py              # Định nghĩa CrewAI
│   └── api.py               # API endpoints
├── .env                     # Biến môi trường
├── main.py                  # Máy chủ API
├── docker-compose.yml       # Cấu hình Docker
└── Dockerfile               # Cấu hình Docker
```

## Khắc phục sự cố

### Vấn đề về cookie LinkedIn

Nếu bạn gặp lỗi "Không thể đăng nhập LinkedIn", hãy đảm bảo:
- Cookie `li_at` của bạn còn hiệu lực và chính xác
- Tài khoản LinkedIn của bạn không bị khóa hoặc giới hạn

### Vấn đề cơ sở dữ liệu

Nếu bạn gặp lỗi kết nối đến PostgreSQL:
- Kiểm tra thông tin kết nối trong file `.env`
- Đảm bảo PostgreSQL đang chạy và có thể truy cập được
- Kiểm tra xem cơ sở dữ liệu `pharmacy_tech_db` đã được tạo chưa

### Vấn đề về Selenium

Nếu Selenium gặp lỗi:
- Đảm bảo Firefox đã được cài đặt
- Kiểm tra xem geckodriver đã được cài đặt và có trong PATH
- Thử chạy ở chế độ không headless (sửa file `driver.py`)

## Lưu ý an toàn

- **Không** chia sẻ cookie LinkedIn của bạn
- Cẩn thận với việc thu thập dữ liệu từ LinkedIn, đảm bảo tuân thủ điều khoản dịch vụ
- Sử dụng delay giữa các lượt truy cập để tránh bị chặn
- Chỉ sử dụng dữ liệu thu thập được cho mục đích hợp pháp và có đạo đức

## Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng tạo Pull Request hoặc mở Issue nếu bạn có bất kỳ đề xuất cải tiến nào.
