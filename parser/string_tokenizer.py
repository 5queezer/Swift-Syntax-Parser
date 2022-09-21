import re
from parser.token import Token

spec = [
    (r'U\+([0-9A-Z]+)', 'UNICODE'),
    (r',', 'COMMA'),
    (r'\bor', 'COMMA'),
    (r'\bfollowed by\b', 'SEQUENCE'),
    (r'\bAny\b', 'ANY'),
    (r'\bDigit\b', 'DIGIT'),
    (r'\bthrough\b', 'THROUGH'),
    (r'\bUnicode scalar value\b', 'UNISCALAR'),
    (r'\bUpper- or lowercase letter\b', 'LETTER'),
    (r'\bidentifier\b', 'IDENTIFIER'),
    (r'\bkeyword\b', 'KEYWORD'),
    (r'\bliteral\b', 'LITERAL'),
    (r'\boperator\b', 'OPERATOR'),
    (r'\bpunctuation\b', 'PUNCTUATION'),
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
        if matched.groups():
            return matched.groups()[-1]
        else:
            return matched.group(0)
