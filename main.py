# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from swift_syntax.spiders.swift import SwiftSpider
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
process.crawl(SwiftSpider)
process.start()
