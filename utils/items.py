from scrapy.item import Item, Field


class JobItem(Item):
    posted_date = Field()
    priority_date = Field()
    school = Field()
    department = Field()
    city = Field()
    state = Field()
    country = Field()
    ads_title = Field()
    ads_source = Field()
    ads_job_code = Field()
    rank = Field()
    specialization = Field()
    canada = Field()
    comments1 = Field()

class SessionItem(Item):
    date = Field()
    track = Field()
    title = Field()
    time = Field()
    presiders = Field()
    presentations = Field()
    zoom_link = Field()


class PresentationItem(SessionItem):
    # title = Field()
    # time = Field()
    presenters = Field()
