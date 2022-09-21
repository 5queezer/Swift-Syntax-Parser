from typing import Iterator

from scrapy import Selector
from parser.item_tokenizer import Tokenizer
import humps


class Parser:
    def __init__(self):
        self._items: list[Selector] = []
        self._tokenizer: Tokenizer or None = None
        self._lookahead: Selector or None = None

    def parse(self, items) -> Iterator:
        self._items = items
        self._tokenizer = Tokenizer(items)
        self._lookahead = self._tokenizer.get_next_token()

        return self.definition()

    def definition(self) -> str:
        """
        # Main entry point.
        #
        """
        return f'{self.name()} {self.assignment()} {self.statement_list()} ;'

    def name(self) -> str:
        name = self._eat('NAME')
        value = humps.pascalize(name.value)
        return value

    def statement_list(self, stop_lookahead=None) -> str:
        statement_list = [self.statement()]
        while self._lookahead is not None and self._lookahead.type != stop_lookahead:
            statement_list.append(self.statement())

        return ' '.join(statement_list)

    def statement(self) -> str:
        match self._lookahead.type:
            case 'ALTERNATION':
                return self.alternation()
            case 'CONCATENATION':
                return self.concatenation()
            case 'STRING' | 'CATEGORY' | 'CODE':
                return self.nonterminal()

    def nonterminal(self) -> str:
        value = ''
        match self._lookahead.type:
            case 'CATEGORY':
                value = self.category()
            case 'CODE':
                value = self.terminal_string()
            case 'STRING':
                value = self.string()
        assert value
        if self._lookahead and self._lookahead.type == 'OPT':
            self._eat('OPT')
            return f'[ {value} ]'
        else:
            return value

    def alternation(self) -> str:
        self._eat('ALTERNATION')
        return '|'

    def concatenation(self) -> str:
        self._eat('CONCATENATION')
        return ','

    def category(self) -> str:
        category = self._eat('CATEGORY')
        value = humps.pascalize(category.value)
        # value = category.value.replace('-', ' ')
        return value

    def assignment(self) -> str:
        self._eat('ARROW')
        return '='

    def terminal_string(self) -> str:
        code = self._eat('CODE')
        if '"' in code.value:
            return f"'{code.value}'"
        else:
            return f'"{code.value}"'

    def string(self) -> str:
        text = self._eat('STRING')
        # not implemented for now, return special sequence
        with open('strings.txt', 'a') as file:
            file.write(text.value + '\n')
        return f'? {text.value} ?'

    def _eat(self, token_type: str):
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token.type:
            raise SyntaxError(f'Unexpected token: {token.value}, expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token
