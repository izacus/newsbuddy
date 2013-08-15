from cornice import Service

stats_service = Service(name="news_stats", path="/news/stats/", description="Returns news statistics")

@stats_service.get()
def get_stats(request):
    return {}