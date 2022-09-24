import math
import unittest
from pprint import pprint

from parser.string_tokenizer import StringTokenizer, Token
from parser.string_parser import StringParser
import re


class StringParserTests(unittest.TestCase):
    parser: StringParser

    def setUp(self):
        self.parser = StringParser()

    def print_token(self, s):
        t = StringTokenizer(s)
        while t.has_more_tokens():
            print(t.get_next_token())

    def test_parser(self):
        s = 'U+000A'
        expected = r'/\U0000000A/'
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_parser_multiple_elements(self):
        s = 'U+000A, U+000B, or U+000C'
        expected = r'( /\U0000000A/ | /\U0000000B/ | /\U0000000C/ )'
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_alternation_between_two(self):
        s = 'U+000A or U+000B'
        expected = r'( /\U0000000A/ | /\U0000000B/ )'
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_unicode_followed_by_unicode(self):
        s = 'U+000A followed by U+000B'
        expected = r'/\U0000000A/ /\U0000000B/'
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_range(self):
        s = 'U+000A–U+000B'
        expected = r'/[\U0000000A-\U0000000B]/'
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_any_expression(self):
        s = 'Any Unicode scalar value except U+000A or U+000'
        expected = r'( /[\U00000000-\U0000D7FF]/ | /[\U0000E000-\U0010FFFF]/ ) ~ ( /\U0000000A/ | /\U00000000/ )'

        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_upper_lowercase_letter(self):
        s = 'Upper- or lowercase letter A through Z'
        expected = r'( /[a-z]/ | /[A-Z]/ )'
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_digit_0_though_9(self):
        s = 'Digit 0 through 9'
        result = self.parser.parse(s)
        expected = '/[0-9]/'
        self.assertEqual(expected, result)

    def test_digit_range_with_alternation(self):
        s = 'Digit 0 through 9, a through f, or A through F'
        result = self.parser.parse(s)
        expected = '( /[0-9]/ | /[a-f]/ | /[A-F]/ )'
        self.assertEqual(expected, result)

    def test_a_decimal_integer_greater_than_zero(self):
        s = 'A decimal integer greater than zero'
        expected = '/[1-9][0-9]*/'
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    def test_any_identifier_keyword_literal_or_operator(self):
        s = 'Any identifier, keyword, literal, or operator'
        expected = 'identifier | keyword | literal | operator'
        result = self.parser.parse(s)
        self.assertEqual(expected, result)

    @unittest.skip
    def test_between_one_and_eight_hexadecimal_digits(self):
        s = 'Between one and eight hexadecimal digits'
        regex = r'/[0-9a-fA-F]{1,8}/'
