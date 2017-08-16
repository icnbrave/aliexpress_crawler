from django.contrib import admin

from .models import Country, Query, QueryResult

class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lang_code', 'url')

class QueryAdmin(admin.ModelAdmin):
    list_display = ('id', 'keywords', 'site', 'user', 'timestamp')

class QueryResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'query', 'page', 'rank', 'overall_rank', 'product_code', 'title', 'price', 'orders', 'store')
    list_filter = ('query', )

admin.site.register(Country, SiteAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(QueryResult, QueryResultAdmin)
