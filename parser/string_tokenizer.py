import re
from parser.token import Token

spec = [
    (r'U\+[0-9A-Z]+', 'UNICODE'),
    (r'–', 'RANGE'),
    (r',', 'COMMA'),
    (r'\bor\b', 'OR'),
    (r'\bfollowed by\b', 'SEQUENCE'),
    (r'\bgreater than\b', 'GREATER'),
    (r'\bBetween\b', 'BETWEEN'),
    (r'\band\b', 'AND'),
    (r'\bzero\b', 'ZERO'),
    (r'\bone\b', 'ONE'),
    (r'\beight\b', 'EIGHT'),
    (r'\bAny\b', 'ANY'),
    (r'\bDigit\b', 'DIGIT'),
    (r'\bhexadecimal digit(s)?\b', 'HEXDIGIT'),
    (r'\bA decimal integer\b', 'INTEGER'),
    (r'\bthrough\b', 'THROUGH'),
    (r'\bUnicode scalar value\b', 'UNISCALAR'),
    (r'\bUpper- or lowercase letter\b', 'LETTER'),
    (r'\bexcept\b', 'EXCEPT'),
    (r'\bkeyword\b|\bidentifier\b|\bliteral\b|\bliteral\b|\boperator\b|\bpunctuation\b', 'KEYWORD'),
    (r'\b.\b', 'CHAR'),
    (r'\s+', None),
]

class StringTokenizer:
    def __init__(self, string: str):
        self._string: str = string
        self._cursor: int = 0

    def has_more_tokens(self) -> bool:
        return self._cursor < len(self._string)

    def get_next_token(self) -> Token or None:
        if not self.has_more_tokens():
            return None
        string = self._string[self._cursor:]
        for regexp, token_type in spec:
            token_value = self._match(regexp, string)
            if token_value is None:
                continue
            if token_type is None:
                return self.get_next_token()
            return Token(token_type, token_value)
        raise SyntaxError(f'Unexpected token: "{string[0]}"')

    def _match(self, regexp, string) -> str or None:
        matched = re.match(regexp, string, re.I)
        if not matched:
            return None
        self._cursor += len(matched.group(0))
        return matched.group(0)
