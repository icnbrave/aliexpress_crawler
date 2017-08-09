from tools.selenium_crawler import AliCrawler

import os, django

os.environ['DJANGO_SETTINGS_MODULE'] = 'crawler.settings'
django.setup()

from aliexpress.models import Country as Site

crawler = AliCrawler()
crawler.login()

# test for crawler
# site = Site.objects.first()
#
# results = crawler.parse(site, 'woman bag 2017', 1)
#
# for result in results:
#     print(result)

# Test for get_english_translation
print(crawler.get_english_translation('Женская сумка'))