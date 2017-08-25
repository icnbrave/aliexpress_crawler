from django.contrib import admin

from .models import Country, Query, QueryResult, RelatedQueryResult

class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lang_code', 'url')

class QueryAdmin(admin.ModelAdmin):
    list_display = ('id', 'keywords', 'site', 'user', 'timestamp')

class QueryResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'query', 'page', 'rank', 'overall_rank', 'product_code', 'title', 'price', 'orders', 'store')
    list_filter = ('query', )
    list_max_show_all = 999
    list_per_page = 999

class RelatedQueryResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'query', 'keywords', 'count')
    list_filter = ('query',)

admin.site.register(Country, SiteAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(QueryResult, QueryResultAdmin)
admin.site.register(RelatedQueryResult, RelatedQueryResultAdmin)
