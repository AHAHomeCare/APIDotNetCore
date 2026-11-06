# 1. Đọc cấu trúc ESAPAPI

## Công nghệ

| Thành phần | Giá trị đọc từ project |
|---|---|
| SDK project | Microsoft.NET.Sdk.Web |
| Framework | .NET 10 (`net10.0`) |
| Kiểu API | ASP.NET Core controller-based API |
| Microsoft.AspNetCore.OpenApi | 10.0.13 |
| Microsoft.EntityFrameworkCore.Sqlite | 10.0.0 |
| Microsoft.EntityFrameworkCore.Design | 10.0.0 |
| Database | SQLite, `Data Source=esap.db` |

## Cây thư mục

```text
ESAPAPI/
├── Controllers/
│   ├── HelloController.cs          # Ví dụ GET, POST và JSON
│   ├── NewsCategoryController.cs   # File rỗng, chưa có endpoint
│   ├── SonaTaskController.cs       # GetAll và Create
│   └── WeatherForecastController.cs
├── Data/AppDbContext.cs           # DbContext và hai DbSet
├── Models/
│   ├── NewsCategory.cs
│   └── SonaTask.cs
├── Migrations/
│   ├── 20261023075225_InitialCreate.cs (+ Designer)
│   ├── 20261023075928_sonatask.cs (+ Designer)
│   └── AppDbContextModelSnapshot.cs
├── Properties/launchSettings.json
├── Program.cs
├── appsettings.json
├── appsettings.Development.json
├── ESAPAPI.csproj
├── ESAPAPI.http
├── WeatherForecast.cs
├── esap.db
├── bin/                          # Kết quả biên dịch
└── obj/                          # File trung gian/restore
```

`bin` và `obj` do công cụ sinh ra; sửa mã ở thư mục nguồn. Có thư mục `.git`; tài liệu không thay đổi lịch sử Git.

## Luồng xử lý

```text
Client → HTTP route → Controller → AppDbContext → EF Core → esap.db
Client ← HTTP status + JSON ← Controller ← kết quả truy vấn/lưu dữ liệu
```

Ví dụ `GET /SonaTask/GetAll`: router chọn `GetAll()`, Dependency Injection cung cấp `AppDbContext`, EF đọc `SonaTasks`, controller trả `{ status: 200, data: [...] }`.

## Vai trò Program.cs

1. `WebApplication.CreateBuilder(args)` nạp cấu hình và tạo service container.
2. `AddControllers()` đăng ký hỗ trợ controller và model binding.
3. `AddOpenApi()` đăng ký tạo mô tả API.
4. `AddDbContext<AppDbContext>(...UseSqlite(...))` lấy `ConnectionStrings:DefaultConnection` để kết nối SQLite. DbContext mặc định có vòng đời scoped theo request.
5. `builder.Build()` tạo ứng dụng.
6. `MapOpenApi()` chỉ được gọi trong Development.
7. `UseHttpsRedirection()` hỗ trợ chuyển HTTP sang HTTPS khi xác định được cổng HTTPS.
8. `UseAuthorization()` đưa authorization middleware vào pipeline. Project chưa cấu hình cơ chế đăng nhập và chưa có `[Authorize]` bảo vệ các controller hiện tại.
9. `MapControllers()` ánh xạ route; `Run()` bắt đầu phục vụ request.

Project chưa gọi `Database.Migrate()` khi khởi động; chạy app không thay thế bước cập nhật database bằng CLI. OpenAPI JSON mặc định ở `/openapi/v1.json`; project chưa cài giao diện Swagger UI nên không mặc định có `/swagger`.

## Model và database

`NewsCategory` và `SonaTask` đều có:

| Trường | C# | Quy tắc |
|---|---|---|
| Id | int | `[Key]`, khóa chính; migration dùng SQLite autoincrement |
| Name | string | `[Required]`, `[MaxLength(100)]`, mặc định chuỗi rỗng |
| Description | string? | Cho phép null, `[MaxLength(500)]` |

`AppDbContext` có `DbSet<NewsCategory> NewsCategories` và `DbSet<SonaTask> SonaTasks`. Migration `InitialCreate` tạo `NewsCategories`; migration `sonatask` tạo `SonaTasks`. Snapshot là mô hình EF dùng để so sánh khi tạo migration tiếp theo, không phải bản sao dữ liệu.

Các thuộc tính validation được ASP.NET Core kiểm tra khi nhận request vào controller có `[ApiController]`. Không nên coi `MaxLength` là giới hạn độ dài được SQLite cưỡng chế cho mọi thao tác ghi ngoài API.

## Endpoint thực sự có trong mã

| Method | URL | Input | Output thành công |
|---|---|---|---|
| GET | `/Hello/today` | Không | status 200, message Welcome, version 1.0 |
| GET | `/Hello/tomorrow` | Không | message Welcome tomorrow |
| POST | `/Hello/nextday` | Không | message Welcome nextday |
| POST | `/Hello/newscategory` | JSON string | message nối Welcome nextday với chuỗi nhận vào |
| GET | `/SonaTask/GetAll` | Không | `{ "status": 200, "data": [...] }` |
| POST | `/SonaTask/Create` | JSON SonaTask | status 200, message Insert Success, data là model đã lưu |
| GET | `/WeatherForecast` | Không | Mảng 5 dự báo giả lập, dữ liệu thay đổi mỗi lần gọi |

`Hello` dùng `[Route("[Controller]/[Action]")]`; `SonaTask` dùng cùng dạng route. Token controller bỏ hậu tố `Controller`. `WeatherForecast` chỉ có token controller nên URL không chứa `/Get`.

Chú ý:

- `POST /Hello/newscategory` chỉ minh họa nhận chuỗi; không ghi bảng NewsCategories.
- `NewsCategoryController.cs` rỗng nên `/NewsCategory/GetAll` chưa tồn tại.
- SonaTask chưa có GetById, Update hoặc Delete; chú thích `POST: NewsCategory/Create` trong controller này là chú thích sao chép, route thực là `/SonaTask/Create`.
- `Create` hiện trả HTTP 200; trường JSON `status` là dữ liệu ứng dụng và không tự quyết định mã HTTP.
- `.AsNoTracking()` ở GetAll phù hợp cho đọc dữ liệu không cần cập nhật; `ToListAsync()` chạy truy vấn, `SaveChangesAsync()` ghi thay đổi.

## Cấu hình địa chỉ

`Properties/launchSettings.json` định nghĩa profile `http` ở `http://localhost:5279`, profile `https` ở `https://localhost:7262;http://localhost:5279`, cả hai dùng Development.

`appsettings.json` còn chứa một khối `profiles` với địa chỉ `0.0.0.0`. Đây không phải nơi `dotnet run --launch-profile` đọc launch profile; không suy ra rằng ứng dụng đang lắng nghe toàn mạng từ khối này. Luôn xem dòng `Now listening on` hoặc cấu hình URL khi khởi chạy.
