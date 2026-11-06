# 2. Chạy ESAPAPI hiện có

## Chuẩn bị

Dùng PowerShell và .NET SDK 10. Có thể dùng Visual Studio, VS Code hoặc terminal. Không bắt buộc cài SQL Server vì project dùng SQLite.

```powershell
Set-Location 'D:\Project\801 Sonadezi\API DotNetCore\ESAPAPI'
dotnet --version
dotnet restore
dotnet build
dotnet ef --version
```

Nếu máy chưa có EF CLI:

```powershell
dotnet tool install --global dotnet-ef --version 10.0.0
```

Nếu đã có thì không chạy lại lệnh install. Dùng phiên bản CLI cùng major 10 với EF Core của project. Trên máy khảo sát đã có CLI 10.0.0.

## Chuẩn bị database

Project đã có migration và file `esap.db`. Dừng ứng dụng trước khi sao lưu database. Nếu SQLite đang dùng WAL thì cần sao lưu nhất quán cùng các file liên quan hoặc dùng công cụ backup SQLite; không chỉ chép file chính khi đang ghi dữ liệu.

Sau khi dừng app, có thể sao lưu file rồi kiểm tra migration:

```powershell
Copy-Item -LiteralPath '.\esap.db' -Destination ('.\esap-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.db')
dotnet ef migrations list
dotnet ef database update
```

`database update` có thay đổi database theo migration còn thiếu. Với project hiện tại không tạo lại `InitialCreate`; hai migration đã có trong mã. `Data Source=esap.db` là đường dẫn tương đối, nên chạy ở thư mục project để tránh mở nhầm hoặc tạo một database rỗng ở nơi khác.

## Khởi chạy

```powershell
dotnet run --launch-profile http
```

Giữ terminal này mở. Dùng terminal thứ hai để gọi API. Xác nhận log có `Now listening on: http://localhost:5279`. Dừng bằng Ctrl+C.

Muốn thử HTTPS:

```powershell
dotnet dev-certs https --trust
dotnet run --launch-profile https
```

Lệnh trust có thể hiện hộp thoại tin cậy certificate trên Windows. Dùng `https://localhost:7262` làm base URL khi chạy profile https. Các ví dụ bên dưới dùng profile http.

## Bài 1 — GET đầu tiên

```powershell
$baseUrl = 'http://localhost:5279'
Invoke-RestMethod -Uri "$baseUrl/Hello/today" -Method Get
```

Kết quả mong đợi:

```json
{ "status": 200, "message": "Welcome", "version": "1.0" }
```

`GET /` có thể trả 404 vì project không ánh xạ trang chủ. Dùng đúng route của controller.

## Bài 2 — POST chuỗi JSON

```powershell
Invoke-RestMethod -Uri "$baseUrl/Hello/newscategory" -Method Post -ContentType 'application/json' -Body '"Sonadezi"'
```

Body là chuỗi JSON **`"Sonadezi"`**, gồm dấu nháy kép; không phải object `{ "key": "Sonadezi" }`. Message mong đợi là `Welcome nextdaySonadezi`. Không có bản ghi danh mục nào được tạo.

## Bài 3 — Tạo và đọc SonaTask

Chỉ thực hiện trên database thực hành; mỗi lần POST thành công thêm một bản ghi.

```powershell
$body = @{
    name = 'Thuc hanh API'
    description = 'Tao cong viec dau tien'
} | ConvertTo-Json
$created = Invoke-RestMethod -Uri "$baseUrl/SonaTask/Create" -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
$created | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri "$baseUrl/SonaTask/GetAll" -Method Get | ConvertTo-Json -Depth 5
```

POST mong đợi HTTP 200 và cấu trúc:

```json
{
  "status": 200,
  "message": "Insert Success",
  "data": { "id": 1, "name": "Thuc hanh API", "description": "Tao cong viec dau tien" }
}
```

Id thực tế phụ thuộc dữ liệu sẵn có; không mặc định luôn là 1. Khi tạo, bỏ trường id để SQLite cấp khóa. GET trả mảng trong `data`; không có `OrderBy` nên không dựa vào thứ tự bản ghi.

## Bài 4 — Validation và mã HTTP

```powershell
Invoke-WebRequest -Uri "$baseUrl/SonaTask/Create" -Method Post -ContentType 'application/json' -Body '{"name":"","description":"Kiem tra validation"}'
```

Mong đợi HTTP 400 do Name bắt buộc. PowerShell có thể ném lỗi với response 4xx; xem response trong HTTP Editor/Postman để đọc JSON lỗi. Thử thêm Name dài 101 ký tự và Description dài 501 ký tự: mong đợi 400. Không nên viết client luôn trông chờ JSON lỗi có trường `status` giống response thành công; lỗi validation mặc định dùng dạng ProblemDetails.

| Ca thử | Kết quả mong đợi từ mã hiện tại |
|---|---|
| GET Hello/today | 200 và message Welcome |
| POST Hello/newscategory với JSON string | 200 và chuỗi đã nối |
| POST SonaTask/Create với Name hợp lệ | 200 và id được cấp |
| GET SonaTask/GetAll | 200, data là mảng |
| Name rỗng/vượt 100 ký tự | 400 |
| Description null | Được chấp nhận |
| JSON hỏng | 400 |
| Content-Type không phù hợp khi gửi body | Thường 415 |
| GET /NewsCategory/GetAll | 404 vì chưa có controller triển khai |
| GET /openapi/v1.json trong Development | 200 và mô tả OpenAPI |

## Bài 5 — Xem hợp đồng API

```powershell
Invoke-RestMethod -Uri "$baseUrl/openapi/v1.json" | ConvertTo-Json -Depth 30
```

Hoặc mở URL này trong trình duyệt. Đây là JSON mô tả API, không phải UI tương tác. Có thể nhập URL vào công cụ hỗ trợ OpenAPI để khám phá các endpoint.
