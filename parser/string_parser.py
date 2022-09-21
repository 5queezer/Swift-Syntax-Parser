from parser.string_tokenizer import StringTokenizer
from parser.token import Token


class StringParser:
    def __init__(self):
        self._string: str = ''
        self._tokenizer: StringTokenizer or None = None
        self._lookahead: Token or None = None

    def lookahead(self, *tpe) -> bool:
        return self._lookahead and self._lookahead.type in tpe

    def parse(self, string) -> dict:
        """
        Parses a string into an AST.
        """
        self._string = string
        self._tokenizer = StringTokenizer(string)
        self._lookahead = self._tokenizer.get_next_token()
        return self.string()

    def string(self):
        return {
            'type': 'String',
            'body': self.string_list()
        }

    def string_list(self, stop_lookahead=None):
        statement_list = [self.statement()]
        while self._lookahead is not None and self._lookahead.type != stop_lookahead:
            statement_list.append(self.statement())
        return statement_list

    def statement(self):
        match self._lookahead.type:
            case 'UNICODE':
                return self.unicode_alternation()
            case _:
                return self.char()

    def unicode_alternation(self):
        items = [self.unicode()]

        while self.lookahead('COMMA'):
            self._eat('COMMA')

            if self.lookahead('UNICODE'):
                items.append(self.unicode())

            if self.lookahead('ALTERNATION'):
                self._eat('ALTERNATION')
                items.append(self.unicode())

        if len(items) == 1:
            return items[0]
        else:
            return {
                'type': 'Alternation',
                'items': items
            }

    def unicode(self):
        value = self._eat('UNICODE')
        return {
            'type': 'Unicode',
            'value': value
        }

    def char(self):
        value = self._eat('CHAR')
        return {
            'type': 'Char',
            'value': value
        }

    def _eat(self, token_type: str):
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token.type:
            raise SyntaxError(f'Unexpected token: {token.value}, expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token
