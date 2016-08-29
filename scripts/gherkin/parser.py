# -*- coding: utf-8; -*-

from . import languages
import re


(
    TOKEN_EOF,                  # 0
    TOKEN_NEWLINE,              # 1
    TOKEN_TEXT,                 # 2
    TOKEN_COMMENT,              # 3
    TOKEN_META_LABEL,           # 4
    TOKEN_META_VALUE,           # 5
    TOKEN_LABEL,                # 6
    TOKEN_TABLE_COLUMN,         # 7
    TOKEN_QUOTES,               # 8
    TOKEN_TAG,                  # 9
) = range(10)


def compiled_languages():
    compiled = {}
    for language, values in languages.LANGUAGES.items():
        compiled[language] = dict(
            (keyword, re.compile(regex))
            for (keyword, regex) in values.items())
    return compiled


## This should happen just once in the module life time
LANGUAGES = compiled_languages()


class BaseParser(object):

    def __init__(self, stream):
        self.stream = stream
        self.start = 0
        self.position = 0
        self.width = 0

    def next_(self):
        if self.position >= len(self.stream):
            self.width = 0
            return None # EOF
        next_item = self.stream[self.position]
        self.width = 1
        self.position += self.width
        return next_item

    def ignore(self):
        self.start = self.position

    def backup(self, steps=1):
        self.position -= self.width * steps

    def peek(self):
        value = self.next_()
        self.backup()
        return value

    def accept(self, valid):
        if self.next_() in valid:
            return True
        self.backup()
        return False


class Lexer(BaseParser):

    def __init__(self, stream):
        super(Lexer, self).__init__(stream)
        self.current_line = 1
        self.tokens = []

    def emit(self, token, strip=False):
        value = self.stream[self.start:self.position]
        if strip: value = value.strip()
        self.tokens.append((self.current_line, token, value))
        self.start = self.position

    def emit_s(self, token, strip=False):
        if self.position > self.start:
            self.emit(token, strip)

    def run(self):
        state = self.lex_text
        while state:
            state = state()
        return self.tokens

    def eat_whitespaces(self):
        while self.accept([' ', '\t']):
            self.ignore()

    def match_quotes(self, cursor):
        stream_at_cursor = self.stream[self.position:]
        return cursor in ('"', "'") and (
            stream_at_cursor.startswith('""') or
            stream_at_cursor.startswith("''"))

    def lex_field(self):
        self.eat_whitespaces()
        while True:
            cursor = self.next_()
            if cursor is None: # EOF
                break
            elif cursor == '\n':
                self.backup()
                return self.lex_text
            elif cursor == '|':
                self.backup()
                self.emit_s(TOKEN_TABLE_COLUMN, strip=True)
                return self.lex_text
        return self.lex_text

    def lex_comment(self):
        self.eat_whitespaces()
        while True:
            cursor = self.next_()
            if cursor is None: # EOF
                break
            elif cursor == '\n':
                self.backup()
                break
            elif cursor == ':':
                self.backup()
                self.emit(TOKEN_META_LABEL)
                self.next_()
                self.ignore()
                return self.lex_comment_metadata_value
        self.emit_s(TOKEN_COMMENT)
        return self.lex_text

    def lex_comment_metadata_value(self):
        self.eat_whitespaces()
        while True:
            cursor = self.next_()
            if cursor is None or cursor == '\n':
                self.backup()
                self.emit_s(TOKEN_META_VALUE)
                return self.lex_text

    def lex_quotes(self):
        internal_lines = 0
        while True:
            cursor = self.next_()
            if self.match_quotes(cursor):
                # Consume all the text inside of the quotes
                self.backup()
                self.emit_s(TOKEN_TEXT)
                self.current_line += internal_lines

                # Consume the closing quotes
                for _ in range(3): self.accept(['"', "'"])
                self.emit_s(TOKEN_QUOTES)
                break
            elif cursor == '\n':
                internal_lines += 1
        return self.lex_text

    def lex_tag(self):
        while True:
            cursor = self.next_()
            if cursor is None: # EOF
                break
            elif cursor in (' ', '\n'):
                self.backup()
                break
        self.emit_s(TOKEN_TAG)
        return self.lex_text

    def lex_text(self):
        self.eat_whitespaces()
        while True:
            cursor = self.next_()
            if cursor is None: # EOF
                break
            elif cursor == ':':
                self.backup()
                self.emit_s(TOKEN_LABEL)
                self.next_()
                self.ignore()
                return self.lex_text
            elif cursor == '#':
                self.backup()
                self.emit_s(TOKEN_TEXT)
                self.next_()
                return self.lex_comment
            elif cursor == '|':
                self.ignore()
                return self.lex_field
            elif cursor == '@':
                self.ignore()
                return self.lex_tag
            elif cursor == '\n':
                self.backup()
                self.emit_s(TOKEN_TEXT)
                self.next_()
                self.emit_s(TOKEN_NEWLINE)
                self.current_line += 1
                return self.lex_text
            elif self.match_quotes(cursor):
                for _ in range(2): self.accept(['"', "'"])
                self.emit_s(TOKEN_QUOTES)
                return self.lex_quotes

        self.emit_s(TOKEN_TEXT)
        self.emit(TOKEN_EOF)
        return None


class Parser(BaseParser):

    def __init__(self, stream):
        super(Parser, self).__init__(stream)
        self.output = []
        self.encoding = 'utf-8'
        self.language = 'en'
        self.languages = LANGUAGES

    def accept(self, valid):
        _, token, value = self.next_()
        if (token, value) in valid:
            return True
        self.backup()
        return False

    def next_(self):
        "Same as BaseParser.next_() but returns (None, None) instead of None on EOF"
        output = super(Parser, self).next_()
        return (None, None, None) if output is None else output

    def match_label(self, type_, label):
        return self.languages[self.language][type_].match(label)

    def eat_newlines(self):
        count = 0
        while self.accept([(TOKEN_NEWLINE, '\n')]):
            self.ignore()
            count += 1
        return count


    def parse_title(self):
        "Parses the stream until token != TOKEN_TEXT than returns Text()"
        line, token, value = self.next_()
        if token == TOKEN_TEXT:
            return Ast.Text(line=line, text=value)
        else:
            self.backup()
            return None

    def parse_description(self):
        description = []
        start_line = -1
        while True:
            line, token, value = self.next_()
            if not len(description):
                start_line = line
            if self.match_label('given', value):
                self.backup()
                break
            elif token == TOKEN_TEXT:
                description.append(value)
            elif token == TOKEN_NEWLINE:
                self.ignore()
            else:
                self.backup()
                break
        if description:
            return Ast.Text(line=start_line, text=' '.join(description))
        else:
            return None

    def parse_background(self):
        line, _, label = self.next_()
        if not self.match_label('background', label):
            self.backup()
            return None
        return Ast.Background(
            line,
            self.parse_title(),
            self.parse_steps())

    def parse_step_text(self):
        self.next_(); self.ignore()  # Skip enter QUOTES
        line, token, step_text = self.next_()
        assert token == TOKEN_TEXT
        _, token, _ = self.next_()   # Skip exit QUOTES
        assert token == TOKEN_QUOTES
        self.ignore()
        return Ast.Text(line=line, text=step_text)

    def parse_steps(self):
        steps = []
        while True:
            line, token, value = self.next_()
            backup = self.eat_newlines()
            _, next_token, _ = self.peek()
            if token == TOKEN_NEWLINE:
                self.ignore()
            elif (token in (TOKEN_LABEL, TOKEN_TEXT) and
                  next_token == TOKEN_TABLE_COLUMN and not
                  self.match_label('examples', value)):
                steps.append(Ast.Step(
                    line=line,
                    title=Ast.Text(line=line, text=value),
                    table=self.parse_table()))
            elif (token in (TOKEN_LABEL, TOKEN_TEXT) and
                  next_token == TOKEN_QUOTES):
                steps.append(Ast.Step(
                    line=line,
                    title=Ast.Text(line=line, text=value),
                    text=self.parse_step_text()))
            elif token == TOKEN_TEXT:
                steps.append(Ast.Step(
                    line=line,
                    title=Ast.Text(line=line, text=value)))
            else:
                self.backup(backup + 1)
                break
        return steps

    def parse_table(self):
        table = []
        row = []
        start_line = -1
        while True:
            line, token, value = self.next_()
            if not len(table):
                start_line = line
            if token == TOKEN_TABLE_COLUMN:
                row.append(value)
            elif token == TOKEN_NEWLINE:
                table.append(row)
                row = []
            else:
                self.backup()
                break
        return Ast.Table(line=start_line, fields=table)

    def parse_examples(self):
        self.eat_newlines()
        tags = self.parse_tags()
        line, token, value = self.next_()
        assert token == TOKEN_LABEL and self.match_label('examples', value)
        self.eat_newlines()
        return Ast.Examples(line=line, tags=tags, table=self.parse_table())

    def parse_scenarios(self):
        scenarios = []
        while True:
            self.eat_newlines()
            tags = self.parse_tags()

            line, token, value = self.next_()
            if token in (None, TOKEN_EOF):
                break  # EOF
            elif self.match_label('scenario_outline', value):
                scenario = Ast.ScenarioOutline(line=line)
                scenario.tags = tags
                scenario.title = self.parse_title()
                scenario.description = self.parse_description()
                scenario.steps = self.parse_steps()
                scenario.examples = self.parse_examples()
            elif self.match_label('scenario', value):
                scenario = Ast.Scenario(line=line)
                scenario.tags = tags
                scenario.title = self.parse_title()
                scenario.description = self.parse_description()
                scenario.steps = self.parse_steps()
            else:
                raise SyntaxError(
                    ('`{}\' should not be declared here, '
                     'Scenario or Scenario Outline expected').format(value))
            scenarios.append(scenario)
        return scenarios

    def parse_tags(self):
        tags = []
        while True:
            line, token, value = self.next_()
            if token == TOKEN_TAG:
                tags.append(value)
            elif token == TOKEN_NEWLINE:
                self.ignore()
            else:
                self.backup()
                break
        return tags

    def parse_feature(self):
        feature = Ast.Feature()
        feature.tags = self.parse_tags()

        line, _, label = self.next_()
        if not self.match_label('feature', label):
            raise SyntaxError(
                'Feature expected in the beginning of the file, '
                'found `{}\' though.'.format(label))

        feature.line = line
        feature.title = self.parse_title()
        feature.description = self.parse_description()
        feature.background = self.parse_background()
        feature.scenarios = self.parse_scenarios()
        return feature

    def parse_metadata(self):
        line, token, key = self.next_()
        if token in (None, TOKEN_EOF): return
        assert token == TOKEN_META_LABEL

        line, token, value = self.next_()
        if token in (None, TOKEN_EOF):
            return
        elif token != TOKEN_META_VALUE:
            raise SyntaxError(
                'No value found for the meta-field `{}\''.format(key))
        return Ast.Metadata(line, key, value)


class Ast(object):

    class Node(object):
        def __eq__(self, other):
            return getattr(other, '__dict__', None) == self.__dict__

        def __repr__(self):
            fields = ['{}={}'.format(x[0], repr(x[1]))
                      for x in self.__dict__.items()]
            return '{}({})'.format(self.__class__.__name__, ', '.join(fields))

    class Metadata(Node):
        def __init__(self, line, key, value):
            self.line = line
            self.key = key
            self.value = value

    class Text(Node):
        def __init__(self, line, text):
            self.line = line
            self.text = text

    class Background(Node):
        def __init__(self, line, title=None, steps=None):
            self.line = line
            self.title = title
            self.steps = steps or []

    class Feature(Node):
        def __init__(self, line=None, title=None, tags=None, description=None, background=None, scenarios=None):
            self.line = line
            self.title = title
            self.tags = tags or []
            self.description = description
            self.background = background
            self.scenarios = scenarios or []

    class Scenario(Node):
        def __init__(self, line, title=None, tags=None, description=None, steps=None):
            self.line = line
            self.title = title
            self.tags = tags or []
            self.description = description
            self.steps = steps or []

    class ScenarioOutline(Node):
        def __init__(self, line, title=None, tags=None, description=None, steps=None, examples=None):
            self.line = line
            self.title = title
            self.tags = tags or []
            self.description = description
            self.steps = steps or []
            self.examples = examples

    class Step(Node):
        def __init__(self, line, title, table=None, text=None):
            self.line = line
            self.title = title
            self.table = table
            self.text = text

    class Table(Node):
        def __init__(self, line, fields):
            self.line = line
            self.fields = fields

    class Examples(Node):
        def __init__(self, line, tags=None, table=None):
            self.line = line
            self.tags = tags or []
            self.table = table
