using System.ComponentModel.DataAnnotations;

namespace ESAPAPI.Models
{
    public class SonaTask    {
        [Key]
        public int Id { get; set; }

        [Required]
        [MaxLength(100)]
        public string Name { get; set; } = "";

        [MaxLength(500)]
        public string? Description { get; set; }
    }
}