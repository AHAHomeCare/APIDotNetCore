# 3. Thực hành xây dựng một API từ đầu

Bài này tạo **ESAPAPIPractice** ở thư mục ngang cấp ESAPAPI, sử dụng cùng cách tổ chức Controller → DbContext → SQLite. Đây là bài mở rộng: controller NewsCategory bên dưới chưa có trong project gốc.

## Bước 1 — Tạo project

Nếu thư mục `ESAPAPIPractice` đã có, chọn tên khác và thay namespace tương ứng; không ghi đè project cũ.

```powershell
Set-Location 'D:\Project\801 Sonadezi\API DotNetCore'
dotnet new webapi --use-controllers --framework net10.0 --name ESAPAPIPractice
Set-Location '.\ESAPAPIPractice'
dotnet add package Microsoft.AspNetCore.OpenApi --version 10.0.13
dotnet add package Microsoft.EntityFrameworkCore.Sqlite --version 10.0.0
dotnet add package Microsoft.EntityFrameworkCore.Design --version 10.0.0
New-Item -ItemType Directory -Path Models,Data -Force
```

Template có thể sinh ví dụ WeatherForecast. Có thể giữ lại; bài thực hành dùng controller NewsCategory riêng. Các file mã bên dưới được tạo trong project **ESAPAPIPractice**, không chép vào Manual.

## Bước 2 — Model

Tạo `Models/NewsCategory.cs`:

```csharp
using System.ComponentModel.DataAnnotations;

namespace ESAPAPIPractice.Models;

public class NewsCategory
{
    [Key]
    public int Id { get; set; }

    [Required]
    [MaxLength(100)]
    public string Name { get; set; } = "";

    [MaxLength(500)]
    public string? Description { get; set; }
}
```

Model mô tả dữ liệu lưu trữ. Bài học tiếp tục nhận model trực tiếp cho ngắn gọn; hệ thống lớn nên dùng DTO riêng để kiểm soát trường client được phép gửi.

## Bước 3 — DbContext

Tạo `Data/AppDbContext.cs`:

```csharp
using ESAPAPIPractice.Models;
using Microsoft.EntityFrameworkCore;

namespace ESAPAPIPractice.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options)
        : base(options) { }

    public DbSet<NewsCategory> NewsCategories { get; set; }
}
```

## Bước 4 — Cấu hình SQLite

Thay nội dung `appsettings.json` của project thực hành bằng:

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=esap-practice.db"
  }
}
```

Tên database khác project gốc để tránh ghi nhầm dữ liệu. Launch profile thuộc `Properties/launchSettings.json`, không đặt vào appsettings.

## Bước 5 — Đăng ký dịch vụ

Thay nội dung `Program.cs` của project thực hành:

```csharp
using ESAPAPIPractice.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddOpenApi();
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

var app = builder.Build();
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}
app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

Đây là cấu hình học tập tương ứng project gốc. Đăng ký DbContext trước Build để Dependency Injection tạo được controller.

## Bước 6 — Controller CRUD hoàn chỉnh

Tạo `Controllers/NewsCategoryController.cs`:

```csharp
using ESAPAPIPractice.Data;
using ESAPAPIPractice.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace ESAPAPIPractice.Controllers;

[ApiController]
[Route("[controller]/[action]")]
public class NewsCategoryController : ControllerBase
{
    private readonly AppDbContext _context;

    public NewsCategoryController(AppDbContext context)
    {
        _context = context;
    }

    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var data = await _context.NewsCategories.AsNoTracking()
            .OrderBy(x => x.Id).ToListAsync();
        return Ok(new { status = 200, data });
    }

    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id)
    {
        var data = await _context.NewsCategories.AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == id);
        if (data is null)
            return NotFound(new { status = 404, message = "Category not found" });
        return Ok(new { status = 200, data });
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] NewsCategory model)
    {
        // Không nhận khóa bản ghi do client tự đặt trong bài thực hành.
        if (model.Id != 0)
            return BadRequest(new { status = 400, message = "Do not supply Id when creating" });
        _context.NewsCategories.Add(model);
        await _context.SaveChangesAsync();
        return CreatedAtAction(nameof(GetById), new { id = model.Id },
            new { status = 201, message = "Insert Success", data = model });
    }

    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(int id, [FromBody] NewsCategory model)
    {
        if (model.Id != 0 && model.Id != id)
            return BadRequest(new { status = 400, message = "Id mismatch" });
        var entity = await _context.NewsCategories.FindAsync(id);
        if (entity is null)
            return NotFound(new { status = 404, message = "Category not found" });
        entity.Name = model.Name;
        entity.Description = model.Description;
        await _context.SaveChangesAsync();
        return Ok(new { status = 200, message = "Update Success", data = entity });
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var entity = await _context.NewsCategories.FindAsync(id);
        if (entity is null)
            return NotFound(new { status = 404, message = "Category not found" });
        _context.NewsCategories.Remove(entity);
        await _context.SaveChangesAsync();
        return NoContent();
    }
}
```

GetAll dùng no-tracking; Update dùng entity được theo dõi để EF biết trường nào thay đổi. Create trả 201 và header Location tới GetById. Delete trả 204 và không có JSON body. Đây là sự mở rộng so với SonaTask/Create trong project gốc (đang trả 200).

## Bước 7 — Migration và database

Chạy trong thư mục **ESAPAPIPractice**:

```powershell
dotnet build
dotnet ef migrations add InitialCreate
dotnet ef database update
```

Chỉ tạo InitialCreate một lần cho project mới. Kiểm tra migration có bảng NewsCategories với Id, Name, Description. File `esap-practice.db` được tạo/cập nhật ở thư mục đang chạy lệnh.

Khi thêm trường mới sau này: sửa model → `dotnet ef migrations add TenThayDoi` → đọc migration → `dotnet ef database update`. Không xóa migration hoặc database để xử lý tùy tiện trên dữ liệu cần giữ.

## Bước 8 — Chạy trên cổng riêng

```powershell
$env:ASPNETCORE_ENVIRONMENT = 'Development'
dotnet run --no-launch-profile --urls http://localhost:5280
```

`--no-launch-profile` tránh profile template ghi đè môi trường/URL; cổng 5280 giúp chạy song song với ESAPAPI 5279. Biến môi trường chỉ đặt trong terminal này. Với cấu hình HTTP không xác định cổng HTTPS, có thể xuất hiện cảnh báo redirection; xem chương 4.

## Bước 9 — Kiểm tra toàn bộ CRUD

Mở PowerShell thứ hai:

```powershell
$baseUrl = 'http://localhost:5280'
$created = Invoke-RestMethod -Uri "$baseUrl/NewsCategory/Create" -Method Post -ContentType 'application/json' -Body '{"name":"Tin noi bo","description":"Danh muc thuc hanh"}'
$categoryId = $created.data.id
Invoke-RestMethod -Uri "$baseUrl/NewsCategory/GetById/$categoryId"
Invoke-RestMethod -Uri "$baseUrl/NewsCategory/GetAll"
Invoke-RestMethod -Uri "$baseUrl/NewsCategory/Update/$categoryId" -Method Put -ContentType 'application/json' -Body '{"name":"Tin da cap nhat","description":null}'
Invoke-WebRequest -Uri "$baseUrl/NewsCategory/Delete/$categoryId" -Method Delete
```

Kỳ vọng lần lượt: 201 → 200 → 200 → 200 → 204. Sau Delete, gọi lại GetById với cùng id phải trả 404. Không dùng id cố định nếu database có dữ liệu.

Thử Name rỗng (400), id không tồn tại (404), và id body khác id URL khi Update (400). Mở `/openapi/v1.json` để kiểm tra hợp đồng API đã xuất hiện các route mới.

## Bài tập tiếp theo

1. Thêm model SonaTask giống project gốc, đăng ký DbSet và tạo migration `AddSonaTasks`.
2. Viết SonaTaskController với GetAll/Create, sau đó mở rộng GetById/Update/Delete.
3. Thêm phân trang GetAll và giới hạn pageSize để tránh trả toàn bộ bảng.
4. Tạo DTO Create/Update chỉ có Name, Description; giữ Id trong response.
5. Trước khi dùng thật, bổ sung xác thực, phân quyền và xử lý lỗi thống nhất theo yêu cầu nghiệp vụ.

Hoàn thành khi project build được, database có bảng đúng, CRUD chạy qua HTTP, validation từ chối dữ liệu sai và dữ liệu vẫn còn sau khi khởi động lại ứng dụng.
