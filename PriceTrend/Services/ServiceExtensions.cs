namespace PriceTrend.Services
{
    public static class ServiceExtensions
    {
        public static IServiceCollection AddAppServices(this IServiceCollection services)
        {
            services.AddScoped<CrawlerService>();

            services.AddScoped<ComparisonService>();

            services.AddScoped<MemberService>();

            services.AddScoped<AnalyticsService>();

            return services;
        }
    }
}