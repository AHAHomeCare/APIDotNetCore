using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ESAPAPI.Models;
using ESAPAPI.Data;
namespace ESAPAPI.Controllers
{
    [ApiController]
    [Route("[Controller]/[Action]")]
    public class NewsController :ControllerBase
    {
        private readonly AppDbContext _context;
        public NewsController(AppDbContext context)
        {
            this._context = context;
        }
        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            try
            {
             var data = await _context.News
                .AsNoTracking()
                .ToListAsync();

                return Ok(new
                {
                    status = 200,
                    message ="OK",
                    data = data
                });
            }
            catch(Exception e)
            {
                 return Ok(new
                {
                    status = 200,
                    message = e.Message,
                    data = new List<News>()
                });
            }
        }
        [HttpPost]
        public async Task<IActionResult> Create([FromBody] News model)
        {
            _context.News.Add(model);

            await _context.SaveChangesAsync();

            return Ok(new
            {
                status = 200,
                message = "Insert Success",
                data = model
            });
        }
    }
}