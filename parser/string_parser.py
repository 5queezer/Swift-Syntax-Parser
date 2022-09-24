from copy import deepcopy

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

    def parse(self, string) -> str:
        """
        Parses a string into an AST.
        """
        self._string = string
        self._tokenizer = StringTokenizer(string)
        self._lookahead = self._tokenizer.get_next_token()
        return self.sequence_list()

    def sequence_list(self):
        first = [self.choice_expression()]
        following = []
        while self.lookahead_is('SEQUENCE'):
            self._eat('SEQUENCE')
            following.append(self.choice_expression())
        return ' '.join(first + following)

    def choice_expression(self, left=None):
        left = left or self.range_expression()
        if self.lookahead_is('EXCEPT'):
            return f'{self.except_expression(left)}'
        if self.lookahead_is('COMMA', 'OR'):
            return f'{self.comma_expression(left)}'

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
            return self._choice([left] + alternations)
        return left

    def except_expression(self, left):
        self._eat('EXCEPT')
        choices = self.choice_expression()
        return f'{left} ~ {choices}'

    def range_expression(self):
        if self.lookahead_is('ANY'):
            return self.any_range()
        if self.lookahead_is('BETWEEN'):
            return self.between_range()
        if self.lookahead_is('UNICODE'):
            return self.unicode_range()
        if self.lookahead_is('DIGIT'):
            return self.digit_range()
        if self.lookahead_is('INTEGER'):
            return self.integer_range_greater_zero()
        if self.lookahead_is('CHAR'):
            return self.char_range()
        if self.lookahead_is('LETTER'):
            return self.letter_range()
        return self.keyword()

    @staticmethod
    def _range(left, right):
        return f'[{left}-{right}]'

    def between_range(self):
        self._eat('BETWEEN')
        from_ = self.char()
        self._eat('AND')
        to = self.char()
        range_ = f'/[0-9a-fA-F]{{{from_},{to}}}/'
        return range_


    def integer_range_greater_zero(self):
        self._eat('INTEGER')
        self._eat('GREATER')
        self._eat('ZERO')
        return '/[1-9][0-9]*/'

    def char_range(self):
        left = self.char()
        self._eat('THROUGH')
        right = self.char()
        return f'/{self._range(left, right)}/'

    def digit_range(self):
        self._eat('DIGIT')
        if self.lookahead_is('CHAR'):
            left = self.char()
            self._eat('THROUGH')
            right = self.char()
        else:
            self._eat('GREATER')
            left = self.char()
            left['value'] = chr(ord(left) + 1)
            right = '9'

        range_ = self._range(left, right)
        return f'/{range_}/'

    def unicode_range(self):
        left = self.unicode()

        if not self.lookahead_is('RANGE'):
            return f'/{left}/'
        self._eat('RANGE')
        right = self.unicode()
        return f'/{self._range(left, right)}/'

    def letter_range(self):
        """
        Letter
            : 'Upper- or lowercase letter' CHAR THROUGH CHAR
        """
        self._eat('LETTER')
        left = self.char()
        self._eat('THROUGH')
        right = self.char()
        lower_alternation = deepcopy(self._range(left.lower(), right.lower()))
        upper_alternation = deepcopy(self._range(left.upper(), right.upper()))
        choice = self._choice([f'/{lower_alternation}/', f'/{upper_alternation}/'])
        return choice

    def _choice(self, items):
        return '( ' + ' | '.join(items) + ' )'

    def any_range(self):
        self._eat('ANY')
        if self.lookahead_is('UNISCALAR'):
            return self.uniscalar_values()
        elif self.lookahead_is('KEYWORD'):
            return self.keyword()

    def uniscalar_values(self):
        self._eat('UNISCALAR')
        uni_scalar_range = (0x0, 0xD7FF), (0xE000, 0x10FFFF)
        x = self._range(self._unicode_formatter(uni_scalar_range[0][0]),
                        self._unicode_formatter(uni_scalar_range[0][1]))
        y = self._range(self._unicode_formatter(uni_scalar_range[1][0]),
                        self._unicode_formatter(uni_scalar_range[1][1]))
        a = self._choice([f'/{x}/', f'/{y}/'])
        return a

    def keyword(self):
        first = self._eat('KEYWORD')
        alternations = []

        while self.lookahead_is('COMMA', 'OR'):
            if self.lookahead_is('COMMA'):
                self._eat('COMMA')
            if self.lookahead_is('OR'):
                self._eat('OR')
                alternations.append(self._eat('KEYWORD'))
                break
            alternations.append(self._eat('KEYWORD'))

        if alternations:
            return ' | '.join([first] + alternations)
        else:
            return first

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
            return self._choice(items)

    def unicode(self):
        value = int(self._eat('UNICODE')[2:], 16)
        return self._unicode_formatter(value)

    @staticmethod
    def _unicode_formatter(value: int):
        return r"\U{0:0{1}X}".format(value, 8)

    def char(self):
        if self.lookahead_is('CHAR'):
            value = self._eat('CHAR')
        elif self.lookahead_is('DIGIT'):
            value = self._eat('DIGIT')
        elif self.lookahead_is('ZERO'):
            self._eat('ZERO')
            value = '0'
        elif self.lookahead_is('ONE'):
            self._eat('ONE')
            value = '1'
        else:
            self._eat('EIGHT')
            value = '8'

        return value

    def _eat(self, token_type: str):
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token.type:
            raise SyntaxError(f'Unexpected token: "{token.value}", expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token.value






