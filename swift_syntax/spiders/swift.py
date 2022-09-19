import scrapy
from scrapy import Selector

from swift_syntax.items import SectionItem, AdmonitionGrammarItem, SyntaxDefItem


class SwiftSpider(scrapy.Spider):
    name = 'swift'
    allowed_domains = ['docs.swift.org']
    start_urls = ['https://docs.swift.org/swift-book/ReferenceManual/zzSummaryOfTheGrammar.html']

    def parse(self, response):
        sections = response.selector.css('#summary-of-the-grammar .section')
        return [dict(self.parse_section(x)) for x in sections]

    def parse_section(self, node):
        title = node.css('h2::text').extract_first()
        groups = [dict(self.parse_admonition_grammar(x)) for x in node.css('.admonition.grammar')]

        return SectionItem(title=title, groups=groups)

    def parse_admonition_grammar(self, node):
        title = node.css('p.admonition-title::text').extract_first()
        defs = [self.parse_syntax_def(x) for x in node.css('div.syntax-group > p.syntax-def')]

        return AdmonitionGrammarItem(title=title, defs=defs)

    def parse_syntax_def(self, node: Selector):
        x = node.css('* *').extract()
        return node
