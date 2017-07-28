from django.core.management.base import BaseCommand
from aliexpress.models import Country

sites = [
    {'name': '英文总站', 'lang': 'en-us', 'url': 'https://www.aliexpress.com'},
    {'name': '俄罗斯站', 'lang': 'ru', 'url': 'https://ru.aliexpress.com'},
    {'name': '法国站', 'lang': 'fr', 'url': 'https://fr.aliexpress.com'},
    {'name': '西班牙站', 'lang': 'es', 'url': 'https://es.aliexpress.com'},
    {'name': '葡萄牙站', 'lang': 'pt', 'url': 'https://pt.aliexpress.com'},
    {'name': '巴西站', 'lang': 'br', 'url': 'https://pt.aliexpress.com'},
]

def init_sites():
    for site in sites:
        Country.objects.get_or_create(name = site['name'], lang_code = site['lang'], url = site['url'])

class Command(BaseCommand):
    help = '初始化站点'
    def handle(self, *args, **options):
        return init_sites()