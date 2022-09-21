import unittest
from parser.string_tokenizer import StringTokenizer, Token
from parser.string_parser import StringParser
import re


class StringParserTests(unittest.TestCase):
    parser: StringParser

    def setUp(self):
        self.parser = StringParser()

    def test_single_unicode(self):
        s = 'U+000A'
        tokenizer = StringTokenizer(s)
        self.assertEqual(Token('UNICODE', '000A'), tokenizer.get_next_token())

    def test_multiple_token(self):
        s = 'U+0000, U+000B, or U+000C'
        expected = [
            Token(type='UNICODE', value='0000'),
            Token(type='COMMA', value=','),
            Token(type='UNICODE', value='000B'),
            Token(type='COMMA', value=','),
            Token(type='OR', value='or'),
            Token(type='UNICODE', value='000C')
        ]
        tokenizer = StringTokenizer(s)
        while True:
            res = tokenizer.get_next_token()
            if not res or not res.type: break
            self.assertTupleEqual(expected.pop(0), res)
        self.assertSequenceEqual([], expected)

    def test_parser(self):
        s = 'U+000A'
        expected = {'type': 'String', 'body': [
            {'type': 'Unicode', 'value': Token(type='UNICODE', value='000A')}
        ]}
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_parser_multiple_elements(self):
        s = 'U+000A, U+000B, or U+000C'
        expected = {
            'type': 'String', 'body': [{
                'type': 'Alternation',
                'items': [
                    {'type': 'Unicode', 'value': Token(type='UNICODE', value='000A')},
                    {'type': 'Unicode', 'value': Token(type='UNICODE', value='000B')},
                    {'type': 'Unicode', 'value': Token(type='UNICODE', value='000C')}
                ]
            }]
        }
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_alternation_between_two(self):
        s = 'U+000A or U+000B'
        expected = {
            'type': 'String', 'body': [{
                'type': 'Alternation',
                'items': [
                    {'type': 'Unicode', 'value': Token(type='UNICODE', value='000A')},
                    {'type': 'Unicode', 'value': Token(type='UNICODE', value='000B')},
                ]
            }]
        }
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_followed_by_sequence(self):
        s = 'U+000A followed by U+000B'
        expected = {
            'type': 'String', 'body': [
                {'type': 'Unicode', 'value': Token(type='UNICODE', value='000A')},
                {'type': 'Unicode', 'value': Token(type='UNICODE', value='000B')},
            ]
        }
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_range(self):
        s = 'U+000A–U+000B'
        expected = {
            'type': 'String', 'body': [{
                'type': 'Range',
                'from': {'type': 'Unicode', 'value': Token(type='UNICODE', value='000A')},
                'to': {'type': 'Unicode', 'value': Token(type='UNICODE', value='000B')}
            }]
        }
        result = self.parser.parse(s)
        self.assertEqual(expected, result)
