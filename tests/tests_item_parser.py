import unittest
from parser.item_parser import Parser
from scrapy.http import TextResponse


class ItemParserTests(unittest.TestCase):
    def test_parse_whitespace(self):
        test_items = '<p class="syntax-def"><span class="syntax-def-name"><a id="grammar_whitespace_1233"></a>whitespace</span><span class="arrow"> → </span> <span class="syntactic-category"><a href="../ReferenceManual/LexicalStructure.html#grammar_whitespace-item">whitespace-item</a></span>  <span class="syntactic-category"><a href="../ReferenceManual/LexicalStructure.html#grammar_whitespace">whitespace</a></span> <sub>opt</sub></p>'
        expected = {'name': ('NAME', 'whitespace'),
                    'body': [
                        ('CATEGORY', 'whitespace-item'),
                        ('CATEGORY', '[ whitespace ]')
                    ]}
        expected = 'whitespace = whitespace-item [ whitespace ] ;'

        parser = Parser()
        result = parser.parse(test_items)
        self.assertEqual(expected, result)

    def test_text(self):
        test_items = [
            '<span class="syntax-def-name"><a id="grammar_whitespace-item_1110"></a>whitespace-item</span>',
            '<span class="arrow"> → </span> U+0000, U+000B, or U+000C'
        ]
