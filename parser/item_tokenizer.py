from typing import NamedTuple
from scrapy import Selector
import re

class Token(NamedTuple):
    type: str or None
    value: str


class Tokenizer:
    # Regex selectors for strings
    spec_str = [
        (r'\|', 'ALTERNATION'),
        (r',', 'CONCATENATION'),
        (r'.*', 'STRING')
    ]

    # CSS selectors for tags
    spec_css = [
        ('.syntax-def-name::text', 'NAME'),
        # ('a[id]::attr(id)', 'IDENTIFIER'),
        ('span[class="arrow"]::text', 'ARROW'),
        ('span[class="syntactic-category"] > a::text', 'CATEGORY'),
        # ('a[href*="#"]', 'REFERENCE'),
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
            for pattern, token_type in self.spec_str:
                token_value = self._match_str(pattern, item)
                if token_value is None:
                    continue
                if token_type is None:
                    return self.get_next_token()
                return Token(token_type, token_value)
        else:
            for css, token_type in self.spec_css:
                token_value = self._match_css(css, item)
                if token_value is None:
                    continue
                if token_type is None:
                    return self.get_next_token()
                return Token(token_type, token_value)
        raise SyntaxError(f'Unexpected token: "{item.extract()}"')

    def _match_css(self, selector: str, item: Selector) -> str or None:
        matched = item.css(selector).extract_first()
        if not matched:
            return None
        matched = matched.strip()
        if not matched:
            return None
        self._cursor += 1
        return matched

    def _match_str(self, pattern, item: str) -> str or None:
        matched = re.match(pattern, item)
        if not matched:
            return None
        self._cursor += 1
        return matched.group(0)
