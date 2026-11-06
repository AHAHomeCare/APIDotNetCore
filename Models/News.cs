using System.ComponentModel.DataAnnotations;

namespace ESAPAPI.Models
{
    public class News    {
        [Key]
        public int Id { get; set; }

        [Required]
        [MaxLength(100)]
        public string Name { get; set; } = "";

        [MaxLength(500)]
        public string? Description { get; set; }
         [MaxLength(5000)]
        public string? Content { get; set; }
    }
}