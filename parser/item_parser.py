from typing import NamedTuple

from scrapy import Selector
from scrapy.http import TextResponse, XmlResponse, HtmlResponse


class Token(NamedTuple):
    type: str or None
    value: str


class Tokenizer:
    spec = [
        ('span.syntax-def-name::text', 'NAME'),
        ('a::attr(id)', 'IDENTIFIER'),
        ('span.arrow', 'ARROW'),
        ('span.syntactic-category a::text', 'CATEGORY'),
        ('a[href*="#"]', 'REFERENCE'),
        ('code::text', 'CODE'),
        ('sub::text', 'OPT'),
    ]

    def __init__(self, items: list[Selector]):
        self._items = items
        self._cursor = 0

    def has_more_tokens(self):
        return self._cursor < len(self._items)

    def get_next_token(self) -> Token or None:
        if not self.has_more_tokens():
            return None

        item = self._items[self._cursor]
        if isinstance(item, str):
            # for testing purposes
            item = XmlResponse(encoding='utf-8', body=item, url='').selector

        for css, token_type in self.spec:
            token_value = self._match(css, item)
            if token_value is None:
                continue
            if token_type is None:
                return self.get_next_token()
            return Token(token_type, token_value)
        raise SyntaxError(f'Unexpected token: "{item.extract()}"')

    def _match(self, css: str, item: Selector) -> str:
        matched = item.css(css).extract_first()
        if not matched:
            return None
        self._cursor += 1
        return matched.strip()


class Parser:
    def __init__(self):
        self._items: list[Selector] = []
        self._tokenizer: Tokenizer or None = None
        self._lookahead: Selector or None = None

    def parse(self, items):
        self._items = items
        self._tokenizer = Tokenizer(items)
        self._lookahead = self._tokenizer.get_next_token()

        return self.definition()

    def definition(self) -> str:
        """
        # Main entry point.
        #
        """
        return f'{self.name()} = {self.statement_list()} ;'

    def name(self):
        name = self._eat('NAME')
        self._eat('IDENTIFIER')
        self._eat('ARROW')
        return name.value

    def statement_list(self, stop_lookahead=None) -> str:
        statement_list = [self.statement()]
        while self._lookahead is not None and self._lookahead.type != stop_lookahead:
            statement_list.append(self.statement())

        statement_values = list(map(lambda x: x.value, statement_list))
        return ' '.join(statement_values)

    def statement(self) -> Token:
        match self._lookahead.type:
            case 'CATEGORY':
                return self.category()
            case 'CODE':
                return self.code()

    def category(self) -> Token:
        category = self._eat('CATEGORY')
        self._eat('REFERENCE')
        if self._lookahead.type == 'OPT':
            self._eat('OPT')
            return Token(category.type, f'[ {category.value} ]')
        else:
            return category

    def code(self):
        category = self._eat('CODE')
        return category

    def opt(self):
        category = self._eat('OPT')
        return category

    def _eat(self, token_type: str):
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token.type:
            raise SyntaxError(f'Unexpected token: {token.value}, expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token
