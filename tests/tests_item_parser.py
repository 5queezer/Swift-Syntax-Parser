import unittest
from parser.item_parser import Parser
from scrapy.http import TextResponse


class ItemParserTests(unittest.TestCase):
    def test_parse_whitespace(self):
        test_items = ['<span class="syntax-def-name"><a id="grammar_whitespace_1233"></a>whitespace</span>',
                      '<a id="grammar_whitespace_1233"></a>', '<span class="arrow"> → </span>',
                      '<span class="syntactic-category"><a href="../ReferenceManual/LexicalStructure.html#grammar_whitespace-item">whitespace-item</a></span>',
                      '<a href="../ReferenceManual/LexicalStructure.html#grammar_whitespace-item">whitespace-item</a>',
                      '<span class="syntactic-category"><a href="../ReferenceManual/LexicalStructure.html#grammar_whitespace">whitespace</a></span>',
                      '<a href="../ReferenceManual/LexicalStructure.html#grammar_whitespace">whitespace</a>',
                      '<sub>opt</sub>']
        expected = {'name': ('NAME', 'whitespace'),
                    'body': [
                        ('CATEGORY', 'whitespace-item'),
                        ('CATEGORY', '[ whitespace ]')
                    ]}
        expected = 'whitespace = whitespace-item [ whitespace ] ;'

        parser = Parser()
        result = parser.parse(test_items)
        self.assertEqual(expected, result)
