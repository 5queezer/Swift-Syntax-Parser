# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import glob
import os
import shutil
from typing import IO

from slugify import slugify
from humps.main import pascalize,  kebabize
import re
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Selector

from parser.item_parser import Parser
from swift_syntax.items import SectionItem, VersionItem

suffix = '.ebnf'
basedir = 'grammar'

class SwiftSyntaxPipeline():
    def __init__(self):
        super().__init__()
        self.index: IO or None = None

    def open_spider(self, spider):
        files = glob.glob(f'{basedir}/*')
        for f in files:
            try:
                os.remove(f)
            except PermissionError:
                shutil.rmtree(f)

        self.index = open(os.path.join(basedir, 'index' + suffix), 'w')

    def close_spider(self, spider):
        self.index.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if isinstance(item, VersionItem):
            version = item.get('name')
            version = pascalize(slugify(version))
            self.index.write(f'@@grammar :: {version}\n')
            self.index.write(r'@@comments :: /\(\*((?:.|\n)*?)\*\)/' + '\n')
            self.index.write('\n')

        elif adapter.is_item_class(SectionItem):
            dirname = self.parse_section(item)

            self.index.write('#include :: "{}"\n'.format(os.path.join(dirname, '_index' + suffix)))

        return item

    def parse_section(self, item):
        title = f'  {item["title"]}  '
        header = '\n'.join([
            '(* ' + len(title) * '-' + ' *)',
            '(* ' + title + ' *)',
            '(* ' + len(title) * '-' + ' *)',
            '\n'
        ])
        print(header)

        dirname = slugify(title)
        os.makedirs(os.path.join(basedir, dirname))

        files = []
        for group in item['groups']:
            files.append(self.parse_group(group, dirname))

        include_file = os.path.join(basedir, dirname, '_index' + suffix)
        with open(include_file, 'w') as includes:
            includes.write(header)
            includes.writelines(map(lambda filename: f'#include :: "{filename}"\n', files))
        return dirname

    def parse_group(self, item, dirname):
        title = f'{item["title"]}'
        header = '(* ' + title + ' *)\n'
        print()
        print(header)

        filename = re.sub(r'Grammar (of)?\s+?(an|a)? ', '', title)
        filename = slugify(filename) + suffix
        assert filename
        path = os.path.join(basedir, dirname, filename)
        with open(path, 'w') as file:
            file.write(header + '\n')
            for definition in item['defs']:
                self.parse_def(definition, file)

        print()

        return filename

    def parse_def(self, item: Selector, file: IO):
        parser = Parser()
        line = parser.parse(item)
        file.write(str(line) + '\n')
        print(line)
