using Microsoft.EntityFrameworkCore;
using ESAPAPI.Models;

namespace ESAPAPI.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(
            DbContextOptions<AppDbContext> options)
            : base(options)
        {
        }

        public DbSet<NewsCategory> NewsCategories
            { get; set; }

        public DbSet<SonaTask> SonaTasks
            { get; set; }

        public DbSet<News> News {get;set;}
    }
}