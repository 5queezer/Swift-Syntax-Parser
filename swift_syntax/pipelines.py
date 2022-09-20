# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Selector
from swift_syntax.items import SectionItem
from parser.item_parser import Parser


class SwiftSyntaxPipeline():
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.is_item_class(SectionItem):
            self.parse_section(item)
        return item

    def parse_section(self, item):
        title = f'  {item["title"]}  '
        print('(* ' + len(title) * '-' + ' *)')
        print('(* ' + title + ' *)')
        print('(* ' + len(title) * '-' + ' *)')
        for group in item['groups']:
            self.parse_group(group)
        print()

    def parse_group(self, item):
        title = f'{item["title"]}'
        print()
        print('(* ' + title + ' *)')
        print()
        for definition in item['defs']:
            self.parse_def(definition)
        print()

    def parse_def(self, item: Selector):
        parser = Parser()
        line = parser.parse(item)
        print(line)
