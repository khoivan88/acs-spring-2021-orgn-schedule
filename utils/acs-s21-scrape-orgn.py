import re
from datetime import datetime, timedelta
from pathlib import Path, PurePath
from urllib.parse import urlparse, parse_qs

import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter

from items import SessionItem, PresentationItem

CURRENT_FILEPATH = Path(__file__).resolve().parent
DATA_FOLDER = CURRENT_FILEPATH.parent / 'src' / '_data'
DATA_FOLDER.mkdir(exist_ok=True)
THIS_SPIDER_RESULT_FILE = DATA_FOLDER / 'acs_s21_orgn.json'


class ACSS21Orgn(scrapy.Spider):
    dates = ['2021-04-13', '2021-04-14', '2021-04-15', '2021-04-16']
    name = 'asc-s21-orgn'
    allowed_domains = ['acs.digitellinc.com']
    start_urls = [f'https://acs.digitellinc.com/acs/live/8/page/18/1?timezone=America%2FNew_York&eventSearchInput=&eventSearchDate={date}&eventSearchTrack=171&eventSearchTag=0'
                  for date in dates]
    base_url = 'https://acs.digitellinc.com/'
    # handle_httpstatus_list = [301, 302]


    def parse(self, response):
        date = parse_qs(urlparse(response.url).query)['eventSearchDate'][0]
        date += 'T00:00:00-0500'
        # breakpoint()
        track = '[ORGN] Division of Organic Chemistry'
        # Get all the jobs listing
        # sessions = response.css('.panel.panel-default.panel-session')
        sessions = response.xpath('//div[@id="event-content"]/div[contains(@class, "panel") and contains(@class, "panel-default") and contains(@class, "panel-session")]')

        # # Pick only those ads that has green badge of 'new' on the top right corner:
        # # For 'C&E News' magazine, 'new' is for job posted in the past 2 days:
        # # Use C&E News own 'filter' of ads posted in the past 2 days (have green badge say 'New' in the top left corner of each ads listing)
        # jobs = response.xpath('//*[contains(@class, "lister__item")][.//*[contains(@class, "badge--green")]]//*[contains(@class, "lister__details")]')

        for session in sessions:
            session_id = session.css('.panel-heading').xpath('@id').get()
            id_num = re.search(r'\D*(\d+)', session_id)
            zoom_link = f'https://acs.digitellinc.com/acs/events/{id_num[1]}/attend'
            info = session.css('.panel-heading .panel-title .session-panel-title')
            title = info.css('a::text').get().strip()
            time = info.css('.session-panel-heading')[0].css('::text').get().strip()
            time = re.sub(r"\s{2,}", '', time)
            presiders_info = info.css('.session-panel-heading')[1].css('::text').getall()
            presiders = [t for t in (s.strip() for s in presiders_info) if t and t != '|']
            # print(f'{title=}')
            # breakpoint()

            presentations = []
            session_content = session.css('.panel-body .panel.panel-default.panel-session')
            for presentation in session_content:
                presentation_id = presentation.css('.panel-heading').xpath('@id').get()
                presentation_id_num = re.search(r'\D*(\d+)', presentation_id)
                presentation_zoom_link = f'https://acs.digitellinc.com/acs/events/{presentation_id_num[1]}/attend'

                presentation_info = presentation.css('.panel-heading .panel-title .session-panel-title')
                presentation_title = presentation_info.css('a::text').get().strip()
                presentation_time = presentation_info.css('.session-panel-heading')[0].css('::text').get().strip()
                presentation_time = re.sub(r"\s{2,}", '', presentation_time)
                presenters_info = presentation_info.css('.session-panel-heading')[1].css('::text').getall()
                presenters = [t for t in (s.strip() for s in presenters_info) if t and t != '|']
                presentation_kwargs = {
                    'title': presentation_title,
                    # 'department': department,
                    'time': presentation_time,
                    'presenters': presenters,
                    'zoom_link': presentation_zoom_link,
                }
                presentations.append(PresentationItem(presentation_kwargs))
                # breakpoint()

            cb_kwargs = {
                'date': date,
                'title': title,
                # 'department': department,
                'time': time,
                'presiders': presiders,
                'presentations': presentations,
                'track': track,
                'zoom_link': zoom_link,
            }
            yield SessionItem(cb_kwargs)

        # # Find next page url if exists:
        # # next_page_partial_url = response.xpath('//*[not(contains(@class, "paginator__items"))][contains(@class, "paginator__item")][.//*[contains(@rel, "next")]]//a/@href').get()
        # # # print(f'{next_page_partial_url=}')
        # # # if next_page_partial_url:
        # current_date = datetime.strptime(this.date, '%Y-%m-%d')
        # next_date = current_date + timedelta(days=1)
        # end_date = datetime.strptime('2021-04-16', '%Y-%m-%d')
        # if next_date <= end_date:
        #     # next_page_url = response.urljoin(next_page_partial_url)
        #     # print(f'{next_page_url=}')
        #     this.date = next_date.strftime('%Y-%m-%d')
        #     yield scrapy.Request(url=start_url[0], callback=self.parse)


if __name__ == '__main__':
    # # Remove the result file if exists
    # THIS_SPIDER_RESULT_FILE.unlink(missing_ok=True)

    settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        # 'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        # 'HTTPCACHE_ENABLED': True,
        # 'DEFAULT_REQUEST_HEADERS': {
        #   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #   'Accept-Language': 'en'
        # },
        # 'CSV_EXPORT_FILE': THIS_SPIDER_RESULT_FILE,
        # 'ITEM_PIPELINES': {
            # '__main__.RemoveIgnoredKeywordsPipeline': 100,
            # '__main__.DeDuplicatesPipeline': 800,
            # '__main__.CsvWriteLatestToOldest': 900,
            # },
        'FEEDS': {
            Path(THIS_SPIDER_RESULT_FILE): {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 2,
                # 'fields': FIELDS_TO_EXPORT,
                'fields': None,
                'overwrite': True,
                'store_empty': False,
                'item_export_kwargs': {
                    'export_empty_fields': True,
                },
            },
        },
        'LOG_LEVEL': 'WARNING',
        # 'ROBOTSTXT_OBEY': False,
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(ACSS21Orgn)
    process.start()
