using System.ComponentModel.DataAnnotations;

namespace ESAPAPI.Models
{
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
}