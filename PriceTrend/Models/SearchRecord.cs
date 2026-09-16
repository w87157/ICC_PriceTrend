using System;
using System.ComponentModel.DataAnnotations;

namespace PriceTrend.Models
{
    public class SearchRecord
    {
        [Key]
        public int Id { get; set; }
        public string Keyword { get; set; } = string.Empty;
        public DateTime SearchedAt { get; set; } = DateTime.Now;
    }
}