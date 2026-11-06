using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ESAPAPI.Data;
using ESAPAPI.Models;
using ESAPAPI.Migrations;

namespace ESAPAPI.Controllers
{
    [ApiController]
    [Route("[controller]/[action]")]
    public class SonaTaskController : ControllerBase
    {
        private readonly AppDbContext _context;

        public SonaTaskController(AppDbContext context)
        {
            _context = context;
        }

        // GET: SonaTask/GetAll
        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var data = await _context.SonaTasks
                .AsNoTracking()
                .ToListAsync();

            return Ok(new
            {
                status = 200,
                data = data
            });
        }

        // POST: NewsCategory/Create
        [HttpPost]
        public async Task<IActionResult> Create(
            [FromBody] SonaTask model)
        {
            _context.SonaTasks.Add(model);

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