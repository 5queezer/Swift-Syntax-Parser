# Define here the models for your scraped items
#
# See documentation in:
# https://docs.org/en/latest/topics/items.html

from scrapy import Field, Item


class VersionItem(Item):
    name = Field()


class SectionItem(Item):
    title = Field()
    groups = Field()


class AdmonitionGrammarItem(Item):
    title = Field()
    defs = Field()


class SyntaxDefItem(Item):
    name = Field()
    identifier = Field()
    items = Field()
