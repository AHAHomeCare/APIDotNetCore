# Hướng dẫn thực hành ASP.NET Core Web API — ESAPAPI

Ngày khảo sát: **23/10/2026**. Tài liệu dựa trên mã nguồn tại `D:\Project\801 Sonadezi\API DotNetCore\ESAPAPI`.

## Mục tiêu và cách học

Sau khi hoàn thành, bạn có thể chạy project hiện có, hiểu đường đi của một HTTP request, tạo một API mới từ đầu, kết nối SQLite bằng Entity Framework Core, tạo migration và thực hiện CRUD.

Đọc theo thứ tự:

1. [Cấu trúc và API hiện có](01-Cau-truc-project.md).
2. [Chạy project và kiểm thử](02-Chay-va-kiem-thu.md).
3. [Thực hành xây dựng API từ đầu](03-Xay-dung-API.md).
4. [Lỗi thường gặp và hướng phát triển](04-Xu-ly-loi.md).

Mẫu gọi API có trong [ESAPAPI-Practice.http](ESAPAPI-Practice.http), dùng với Visual Studio HTTP Editor hoặc VS Code REST Client. Request tạo dữ liệu sẽ thêm bản ghi vào database của ứng dụng đang chạy; chỉ chạy trên môi trường thực hành.

**Phạm vi:** các file trong Manual là tài liệu và mẫu thực hành. Chương 3 hướng dẫn tạo project riêng, không tự bổ sung endpoint vào ESAPAPI hiện tại. Không đặt project C# thực hành bên trong ESAPAPI vì SDK có thể tự thu thập các file `.cs` con khi build.

## Kết quả kiểm tra thực tế

| Hạng mục | Kết quả |
|---|---|
| SDK trên máy | 10.0.402 |
| Target framework | net10.0 |
| dotnet-ef | 10.0.0 |
| `dotnet build --no-restore` | Thành công, 0 lỗi, 5 cảnh báo |
| Kiểm thử HTTP / ghi database | Chưa thực hiện; các kết quả mong đợi trong tài liệu được suy ra từ mã nguồn |

Cảnh báo build gồm NU1902/NU1903 cho các dependency gián tiếp `System.Security.Cryptography.Pkcs` 9.0.0 và `SQLitePCLRaw.lib.e_sqlite3` 2.1.11, cùng CS8981 do tên migration `sonatask` viết thường. Chi tiết và hướng kiểm tra ở chương 4. Chưa thay đổi package, mã ứng dụng hoặc database.

## Tài liệu chính thức

- [Tutorial controller-based Web API](https://learn.microsoft.com/en-us/aspnet/core/tutorials/first-web-api).
- [OpenAPI trong ASP.NET Core 10](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/overview?view=aspnetcore-10.0).
- [EF Core Getting Started](https://learn.microsoft.com/en-us/ef/core/get-started/?tabs=netcore-cli).
- [EF Core CLI](https://learn.microsoft.com/en-us/ef/core/miscellaneous/cli/dotnet).

Các phiên bản package trong bài học tái hiện cấu hình project tại ngày khảo sát; trước khi triển khai thật cần kiểm tra bản vá và chạy lại kiểm thử.
