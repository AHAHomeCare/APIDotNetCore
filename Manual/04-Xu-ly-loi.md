# 4. Xử lý lỗi và hướng phát triển

## Tra cứu nhanh

| Hiện tượng | Nguyên nhân cần kiểm tra | Cách xử lý |
|---|---|---|
| Connection refused | App chưa chạy hoặc nhầm cổng | Xem log Now listening on và base URL |
| Address already in use | Cổng đã có tiến trình sử dụng | Dừng đúng app của mình hoặc chọn cổng khác bằng --urls |
| 404 tại `/` | Không có route trang chủ | Gọi /Hello/today hoặc /SonaTask/GetAll |
| 404 NewsCategory ở ESAPAPI gốc | Controller rỗng | Chỉ gọi route đã có; controller chương 3 thuộc project thực hành |
| 405 Method Not Allowed | Sai GET/POST/PUT/DELETE | Đối chiếu attribute Http... trong action |
| 415 Unsupported Media Type | Sai Content-Type | Gửi application/json |
| 400 với Hello/newscategory | Gửi object thay vì JSON string | Body phải là `"Sonadezi"` |
| 400 với Create | JSON sai hoặc validation thất bại | Kiểm tra errors, Name và Description |
| SQLite no such table | Chưa update DB hoặc mở nhầm DB | Kiểm tra working directory, connection string rồi chạy database update |
| Unable to resolve service AppDbContext | Thiếu AddDbContext hoặc sai namespace/type | Đăng ký đúng DbContext trước builder.Build |
| dotnet-ef không tìm thấy | Chưa cài tool hoặc PATH chưa cập nhật | Cài tool đúng version, mở lại terminal |
| Lỗi certificate HTTPS | Chưa trust development certificate | Chạy dotnet dev-certs https --trust |
| `/swagger` trả 404 | Chưa cấu hình Swagger UI | Dùng /openapi/v1.json trong Development |
| OpenAPI 404 ở Production | MapOpenApi chỉ bật trong Development | Kiểm tra ASPNETCORE_ENVIRONMENT của môi trường học tập |
| Failed to determine the https port for redirect | Chạy HTTP mà không xác định được cổng HTTPS | Dùng profile https và certificate phù hợp nếu cần thử chuyển hướng |

## Hai điểm dễ nhầm trong mã hiện có

**Địa chỉ LAN:** khối profiles trong appsettings.json không điều khiển launch profile. Khi cần thử qua LAN, chỉ trên mạng thực hành đã cho phép, có thể chạy `dotnet run --no-launch-profile --urls http://0.0.0.0:5279`; máy khác dùng IP LAN của máy chủ, không dùng localhost hoặc 0.0.0.0. Kiểm tra firewall nếu kết nối không được. API hiện chưa có cơ chế xác thực bảo vệ endpoint.

**HTTP status và JSON status:** `Ok(new { status = 200 })` trả HTTP 200 bởi `Ok`. `new JsonResult(new { status = 400 })` không tự biến HTTP status thành 400. Dùng `BadRequest(...)`, `NotFound(...)`, `CreatedAtAction(...)` hoặc chỉ định StatusCode phù hợp.

## Cảnh báo build ngày khảo sát

`dotnet build --no-restore` thành công với 5 cảnh báo:

- NU1903: SQLitePCLRaw.lib.e_sqlite3 2.1.11.
- NU1902 và NU1903: System.Security.Cryptography.Pkcs 9.0.0.
- Hai CS8981: tên lớp migration `sonatask` trong file migration và Designer.

Các cảnh báo dependency trên là kết quả audit được build sử dụng tại thời điểm kiểm tra; tài liệu không khẳng định đã kiểm thử hoặc khắc phục lỗ hổng. Kiểm tra dependency hiện tại trước khi lựa chọn bản nâng cấp:

```powershell
dotnet list package --include-transitive
dotnet list package --vulnerable --include-transitive
dotnet list package --outdated
```

Đọc advisory do NuGet báo, xác định package cấp trên kéo dependency vào, nâng package lên bản vá phù hợp và kiểm thử lại build, migration, CRUD. Không tự đổi tên/xóa migration đã áp dụng chỉ để làm mất cảnh báo tên lớp; lịch sử migration cần được giữ nhất quán.

## Từ bài học đến ứng dụng thực tế

Project hiện phù hợp để học routing, model binding và EF Core. Khi mở rộng, cân nhắc DTO, service nghiệp vụ, phân trang, logging và xử lý lỗi tập trung. Chỉ thêm repository khi nó giải quyết nhu cầu rõ ràng; project hiện gọi DbContext trực tiếp trong controller.

Khi publish, lệnh `dotnet publish -c Release -o <thu-muc-dich>` tạo output triển khai; không tự cấu hình hosting, HTTPS hay cập nhật database. Cần xác định môi trường chạy, quyền ghi SQLite, đường dẫn database bền vững, backup và cách áp dụng migration trước khi đưa vào sử dụng.
