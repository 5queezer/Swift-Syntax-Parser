# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import glob
import os
import shutil
from typing import IO

import humps
import re
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Selector

from parser.item_parser import Parser
from swift_syntax.items import SectionItem

suffix = '.ebnf'
basedir = 'grammar'


class SwiftSyntaxPipeline():
    def __init__(self):
        super().__init__()
        files = glob.glob(f'{basedir}/*')
        for f in files:
            try:
                os.remove(f)
            except PermissionError:
                shutil.rmtree(f)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.is_item_class(SectionItem):
            dirname = self.parse_section(item)

            include_file = os.path.join(basedir, '_index.ebnf')

            with open(include_file, 'a') as includes:
                includes.write('#include :: "{}"\n'.format(os.path.join(dirname, '_index' + suffix)))

        return item

    def parse_section(self, item):
        title = f'  {item["title"]}  '
        header = '\n'.join([
            '(* ' + len(title) * '-' + ' *)',
            '(* ' + title + ' *)',
            '(* ' + len(title) * '-' + ' *)'
        ])
        print(header)

        dirname = humps.kebabize(title.strip().lower())
        os.makedirs(os.path.join(basedir, dirname))

        files = []
        for group in item['groups']:
            files.append(self.parse_group(group, dirname))
        print()

        include_file = os.path.join(basedir, dirname, '_index' + suffix)
        with open(include_file, 'w') as includes:
            includes.writelines(map(lambda filename: f'#include :: "{filename}"\n', files))
        return dirname

    def parse_group(self, item, dirname):
        title = f'{item["title"]}'
        header = '(* ' + title + ' *)\n'
        print()
        print(header)

        filename = re.sub(r'Grammar (of)?\s+?(an|a)? ', '', title)
        filename = humps.kebabize(filename).lower() + suffix
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
