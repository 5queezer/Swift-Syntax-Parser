from parser.string_tokenizer import StringTokenizer
from parser.token import Token


class StringParser:
    def __init__(self):
        self._string: str = ''
        self._tokenizer: StringTokenizer or None = None
        self._lookahead: Token or None = None

    def lookahead_is(self, *tpe) -> bool:
        return self._lookahead and self._lookahead.type in tpe

    def lookahead_is_not(self, *tpe) -> bool:
        return self._lookahead and self._lookahead.type not in tpe

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
            'body': self.sequence_list()
        }

    def sequence_list(self):
        first = [self.alternation_expression()]
        following = []
        while self.lookahead_is('SEQUENCE'):
            self._eat('SEQUENCE')
            following.append(self.alternation_expression())
        return first + following

    def alternation_expression(self):
        left = self.range_expression()
        if self.lookahead_is('EXCEPT'):
            return self.except_expression(left)
        if self.lookahead_is('COMMA', 'OR'):
            return self.comma_expression(left)
        return left

    def comma_expression(self, left):
        alternations = []
        while self.lookahead_is('COMMA', 'OR'):
            if self.lookahead_is('COMMA'):
                self._eat('COMMA')
            if self.lookahead_is('OR'):
                self._eat('OR')
                alternations.append(self.range_expression())
                break
            alternations.append(self.range_expression())

        if alternations:
            return {
                'type': 'Alternation',
                'items': [left] + alternations
            }
        return left

    def except_expression(self, left):
        self._eat('EXCEPT')

        return {
            'type': 'Exclusion',
            'left': left,
            'right': self.alternation_expression()
        }

    def range_expression(self):
        if self.lookahead_is('ANY'):
            return self.any_range()
        if self.lookahead_is('LETTER'):
            return self.letter_range()
        if self.lookahead_is('UNICODE'):
            return self.unicode_range()
        if self.lookahead_is('DIGIT'):
            return self.digit_range()
        if self.lookahead_is('CHAR'):
            return self.char_range()
        return self.keyword()

    def _range(self, left, right):
        return {
            'type': 'Range',
            'from': left,
            'to': right
        }

    def char_range(self):
        left = self.char()
        self._eat('THROUGH')
        right = self.char()
        return self._range(left, right)

    def digit_range(self):
        self._eat('DIGIT')
        if self.lookahead_is('CHAR'):
            left = self.char()
            self._eat('THROUGH')
            right = self.char()
        else:
            self._eat('GREATER')
            left = self.char()
            left['value'] = chr(ord(left['value']) + 1)
            right = {'type': 'Char', 'value': '9'}

        return self._range(left, right)

    def unicode_range(self):
        left = self.unicode()

        if not self.lookahead_is('RANGE'):
            return left
        self._eat('RANGE')
        right = self.unicode()
        return self._range(left, right)

    def letter_range(self):
        """
        LetterExpression
            : LETTER CHAR THROUGH CHAR
        """
        self._eat('LETTER')
        left = self.char()
        self._eat('THROUGH')
        right = self.char()
        return self._range(left, right)

    def any_range(self):
        self._eat('ANY')
        if self.lookahead_is('UNISCALAR'):
            self._eat('UNISCALAR')
            return {
                'type': 'UnicodeScalarValue'
            }
        else:
            return self.keyword()

    def keyword(self):
        value = self._eat('KEYWORD').title()

        return {
            'type': 'Name',
            'value': value
        }

    def unicode_alternation(self):
        items = [self.unicode()]

        while self.lookahead_is('COMMA'):
            self._eat('COMMA')

            if self.lookahead_is('UNICODE'):
                items.append(self.unicode())

        if self.lookahead_is('OR'):
            self._eat('OR')
            items.append(self.unicode())

        if len(items) == 1:
            return items[0]
        else:
            return {
                'type': 'Alternation',
                'items': items
            }

    def unicode(self):
        return {
            'type': 'Unicode',
            'value': self._eat('UNICODE')
        }

    def char(self):
        if self.lookahead_is('CHAR'):
            value = self._eat('CHAR')
        elif self.lookahead_is('DIGIT'):
            value = self._eat('DIGIT')
        else:
            self._eat('ZERO')
            value = '0'

        return {
            'type': 'Char',
            'value': value
        }

    def _eat(self, token_type: str):
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token.type:
            raise SyntaxError(f'Unexpected token: "{token.value}", expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token.value
