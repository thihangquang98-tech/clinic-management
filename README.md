# Hệ thống quản lý phòng khám

Dự án triển khai hệ thống quản lý phòng khám bằng Django, PostgreSQL,
Nginx và Docker Compose; tích hợp Prometheus, Grafana, Loki và Promtail
để giám sát tài nguyên, dịch vụ và tập trung log.

## 1. Kiến trúc

- Django/Gunicorn: xử lý nghiệp vụ website.
- PostgreSQL: lưu trữ dữ liệu ứng dụng.
- Nginx: reverse proxy, phục vụ HTTP và HTTPS.
- pgAdmin: giao diện quản trị PostgreSQL.
- Prometheus: thu thập metrics.
- Grafana: trực quan hóa metrics và log.
- cAdvisor, Node Exporter: cung cấp metrics container và máy chủ.
- PostgreSQL Exporter: cung cấp metrics PostgreSQL.
- Loki và Promtail: tập trung và gửi log container.

Mạng `backend` được cấu hình `internal: true`; Nginx kết nối với
mạng `frontend` để chuyển tiếp yêu cầu tới ứng dụng.

## 2. Yêu cầu

- Docker Engine và Docker Compose plugin.
- Git.
- OpenSSL để tạo chứng chỉ HTTPS tự ký.

## 3. Cấu hình môi trường

Sao chép file mẫu:

```bash
cp .env.example .env
```

Chỉnh `.env` và thay tất cả giá trị `CHANGE_ME...` bằng giá trị riêng,
dài và khó đoán. Không đưa `.env`, mật khẩu thật hoặc khóa riêng lên Git.

Tạo chứng chỉ tự ký nếu chưa có `nginx/ssl/clinic.crt` và
`nginx/ssl/clinic.key`:

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/clinic.key \
  -out nginx/ssl/clinic.crt \
  -subj "/CN=localhost"
```

Trình duyệt có thể cảnh báo vì chứng chỉ tự ký; đây không phải chứng chỉ
được cấp bởi một CA công cộng.

## 4. Khởi chạy

Chạy tại thư mục dự án:

```bash
docker compose -f docker-compose.yml \
  -f docker-compose.monitoring.yml config -q

docker compose -f docker-compose.yml \
  -f docker-compose.monitoring.yml up -d --build
```

Kiểm tra trạng thái:

```bash
docker compose -f docker-compose.yml \
  -f docker-compose.monitoring.yml ps
```

## 5. Các địa chỉ truy cập

| Thành phần | Địa chỉ |
|---|---|
| Website HTTP | http://192.168.20.128:8082 |
| Website HTTPS | https://192.168.20.128:8443 |
| pgAdmin | http://192.168.20.128:5050 |
| Prometheus | http://192.168.20.128:9091 |
| Grafana | http://192.168.20.128:3001 |

Thông tin đăng nhập được cấu hình trong `.env`. Không ghi mật khẩu thật
vào README hoặc commit.

## 6. Giám sát bằng Prometheus và Grafana

Trong Prometheus, mở **Status → Targets** và kiểm tra trạng thái các target,
bao gồm Prometheus, Node Exporter, cAdvisor và PostgreSQL Exporter.

Trong Grafana, cấu hình data source Prometheus với địa chỉ nội bộ
`http://prometheus:9090`. Có thể tạo dashboard để theo dõi tài nguyên
máy chủ, container và cơ sở dữ liệu.

## 7. Tập trung log bằng Loki và Promtail

Promtail đọc log container Docker và gửi tới Loki. Trong Grafana, cấu hình
data source Loki với địa chỉ nội bộ `http://loki:3100`.

Ví dụ truy vấn LogQL trong Grafana Explore (tùy thuộc nhãn thực tế):

```logql
{job="docker"}
```

```logql
{job="docker"} |= "error"
```

```logql
{job="docker"} |~ "(?i)warning|exception|failed"
```

## 8. Các biện pháp bảo mật

- Chạy ứng dụng Django bằng tài khoản hệ điều hành không phải root.
- Bật `no-new-privileges` cho một số container.
- Dùng filesystem chỉ đọc cho container ứng dụng và `tmpfs` cho `/tmp`.
- Dùng mạng backend nội bộ cho các dịch vụ dữ liệu.
- Không đưa `.env`, khóa riêng TLS hoặc dữ liệu sao lưu lên Git.
- Nginx cấu hình các security headers và HTTPS bằng chứng chỉ tự ký.

Các biện pháp này cần được kiểm thử trong môi trường triển khai thực tế;
không nên xem cấu hình hiện tại là đã đáp ứng toàn bộ yêu cầu production.

## 9. Kiểm tra ứng dụng

```bash
docker compose exec -T web python manage.py check
```

Kiểm tra cấu hình Compose:

```bash
docker compose -f docker-compose.yml \
  -f docker-compose.monitoring.yml config -q
```

## 10. Lưu ý khi đưa mã nguồn lên GitHub

- Chỉ commit mã nguồn, cấu hình mẫu và tài liệu cần thiết.
- Không commit `.env`, khóa riêng TLS, dữ liệu cơ sở dữ liệu hoặc file backup.
- Sau khi clone, tạo `.env` và chứng chỉ TLS theo hướng dẫn trước khi khởi chạy.
- Các ảnh chụp màn hình và kết quả kiểm thử của báo cáo cần lấy từ lần chạy
  thực tế; không dùng số liệu minh họa như kết quả thật.
