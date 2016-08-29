# -*- coding: utf-8; -*-

import gherkin
from gherkin import Lexer, Parser, Ast


def test_lex_test_eof():
    "lex_text() Should be able to find EOF"

    # Given a lexer that takes '' as the input string
    lexer = gherkin.Lexer('')

    # When we try to lex any text from ''
    new_state = lexer.lex_text()

    # Then we see we've got to EOF and that new state is nil
    lexer.tokens.should.equal([(1, gherkin.TOKEN_EOF, '')])
    new_state.should.be.none


def test_lex_text():
    "lex_text() Should be able to find text before EOF"

    # Given a lexer that takes some text as input string
    lexer = gherkin.Lexer('some text')

    # When we lex it
    new_state = lexer.lex_text()

    # Then we see we found both the text and the EOF token
    lexer.tokens.should.equal([
        (1, gherkin.TOKEN_TEXT, 'some text'),
        (1, gherkin.TOKEN_EOF, '')
    ])

    # And the new state is nil
    new_state.should.be.none


def test_lex_hash_with_text():
    "lex_text() Should stop lexing at # (we found a comment!)"

    # Given a lexer with some text and some comment
    lexer = gherkin.Lexer(' some text # random comment')

    # When the input is lexed through the text lexer
    new_state = lexer.lex_text()

    # Then we see the following token on the output list
    lexer.tokens.should.equal([
        (1, gherkin.TOKEN_TEXT, 'some text '),
    ])

    # And that the next state will lex comments
    new_state.should.equal(lexer.lex_comment)


def test_lex_comment():
    "lex_comment() Should stop lexing at \\n"

    # Given a lexer loaded with some comments
    lexer = gherkin.Lexer('   random comment')

    # When We lex the input text
    new_state = lexer.lex_comment()

    # Then we see the comment above was captured
    lexer.tokens.should.equal([
        (1, gherkin.TOKEN_COMMENT, 'random comment'),
    ])

    # And that new state is lex_text()
    new_state.should.equal(lexer.lex_text)


def test_lex_comment_meta_label():
    "lex_comment() Should stop lexing at : (we found a label)"

    # Given a lexer loaded with a comment that contains a label
    lexer = gherkin.Lexer('     metadata: test')

    # When we lex the comment
    new_state = lexer.lex_comment()

    # Then we see that a label was found
    lexer.tokens.should.equal([
        (1, gherkin.TOKEN_META_LABEL, 'metadata'),
    ])

    # And that new state is going to read the value of the variable we
    # just found
    new_state.should.equal(lexer.lex_comment_metadata_value)


def test_lex_comment_metadata_value():
    "lex_comment_metadata_value() Should stop lexing at \n"

    # Given a lexer loaded with the value of a label and a new line
    # with more text
    lexer = gherkin.Lexer(' test value\nblah')

    # When we lex the input string
    new_state = lexer.lex_comment_metadata_value()

    # Then we see that only the value present is the one before the
    # \n, everything else will be lexed by lex_text
    lexer.tokens.should.equal([
        (1, gherkin.TOKEN_META_VALUE, 'test value'),
    ])

    # And we also see that the next
    new_state.should.equal(lexer.lex_text)

def test_lex_comment_no_newline():

    # Given a lexer loaded with a comment without the newline marker
    lexer = gherkin.Lexer(' test comment')

    # When we lex the input string
    new_state = lexer.lex_comment_metadata_value()

    # Then we see the whole line was captured
    lexer.tokens.should.equal([
        (1, gherkin.TOKEN_META_VALUE, 'test comment'),
    ])

    # And we also see that the next
    new_state.should.equal(lexer.lex_text)


def test_lex_comment_until_newline():
    "Lexer.lex_comment() Should parse comments until the newline character"

    # Given a lexer loaded with comments containing a metadata field
    lexer = gherkin.Lexer('# one line\n# another line')

    # When I run the lexer
    tokens = lexer.run()

    # Then we see both lines were captured
    lexer.tokens.should.equal([
        (1, gherkin.TOKEN_COMMENT, 'one line'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_COMMENT, 'another line'),
        (2, gherkin.TOKEN_EOF, ''),
    ])


def test_lex_comment_full():
    "Lexer.run() Should be able to process metadata in comments"

    # Given a lexer loaded with comments containing a metadata field
    lexer = gherkin.Lexer('some text # metadata-field: blah-value\ntext')

    # When I run the lexer
    tokens = lexer.run()

    # Then I see the tokens collected match some text, a field, more
    # text and EOF
    tokens.should.equal([
        (1, gherkin.TOKEN_TEXT, 'some text '),
        (1, gherkin.TOKEN_META_LABEL, 'metadata-field'),
        (1, gherkin.TOKEN_META_VALUE, 'blah-value'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TEXT, 'text'),
        (2, gherkin.TOKEN_EOF, '')
    ])


def test_lex_text_with_label():
    "Lexer.run() Should be able to parse a label with some text"

    # Given a lexer loaded with a feature
    lexer = gherkin.Lexer(
        'Feature: A cool feature\n  some more text\n  even more text')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see the token list matches the label, text, text EOF
    # sequence
    tokens.should.equal([
        (1, gherkin.TOKEN_LABEL, 'Feature'),
        (1, gherkin.TOKEN_TEXT, 'A cool feature'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TEXT, 'some more text'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_TEXT, 'even more text'),
        (3, gherkin.TOKEN_EOF, '')
    ])


def test_lex_text_with_labels():
    "Lexer.run() Should be able to tokenize a feature with a scenario"

    # Given a lexer with a more complete feature+scenario
    lexer = gherkin.Lexer('''

Feature: Some descriptive text
  In order to parse a Gherkin file
  As a parser
  I want to be able to parse scenarios

  Even more text

  Scenario: The user wants to describe a feature
''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see it was broken down into the right list of tokens
    tokens.should.equal([
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_LABEL, 'Feature'),
        (3, gherkin.TOKEN_TEXT, 'Some descriptive text'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TEXT, 'In order to parse a Gherkin file'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_TEXT, 'As a parser'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_TEXT, 'I want to be able to parse scenarios'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TEXT, 'Even more text'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_NEWLINE, '\n'),
        (10, gherkin.TOKEN_LABEL, 'Scenario'),
        (10, gherkin.TOKEN_TEXT, 'The user wants to describe a feature'),
        (10, gherkin.TOKEN_NEWLINE, '\n'),
        (11, gherkin.TOKEN_EOF, '')
    ])


def test_lex_text_with_steps():
    "Lexer.run() Should be able to tokenize steps"

    # Given a lexer loaded with feature+background+scenario+steps
    lexer = gherkin.Lexer('''\
Feature: Feature title
  feature description
  Background: Some background
    about the problem
  Scenario: Scenario title
    Given first step
     When second step
     Then third step
''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see that everything, including the steps was properly
    # tokenized
    tokens.should.equal([
        (1, gherkin.TOKEN_LABEL, 'Feature'),
        (1, gherkin.TOKEN_TEXT, 'Feature title'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TEXT, 'feature description'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_LABEL, 'Background'),
        (3, gherkin.TOKEN_TEXT, 'Some background'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TEXT, 'about the problem'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_LABEL, 'Scenario'),
        (5, gherkin.TOKEN_TEXT, 'Scenario title'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_TEXT, 'Given first step'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_TEXT, 'When second step'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TEXT, 'Then third step'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_EOF, '')
    ])


def test_lex_load_languages():
    "Lexer.run() Should be able to parse different languages"

    # Given the following lexer instance loaded with another language
    lexer = gherkin.Lexer('''# language: pt-br

    Funcionalidade: Interpretador para gherkin
      Para escrever testes de aceitação
      Como um programador
      Preciso de uma ferramenta de BDD
    Contexto:
      Dado que a variavel "X" contém o número 2
    Cenário: Lanche
      Dada uma maçã
      Quando mordida
      Então a fome passa
    ''')

    # When we run the lexer
    tokens = lexer.run()

    # Then the following list of tokens is generated
    tokens.should.equal([
        (1, gherkin.TOKEN_META_LABEL, 'language'),
        (1, gherkin.TOKEN_META_VALUE, 'pt-br'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_LABEL, 'Funcionalidade'),
        (3, gherkin.TOKEN_TEXT, 'Interpretador para gherkin'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TEXT, 'Para escrever testes de aceitação'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_TEXT, 'Como um programador'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_TEXT, 'Preciso de uma ferramenta de BDD'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_LABEL, 'Contexto'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TEXT, 'Dado que a variavel "X" contém o número 2'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_LABEL, 'Cenário'),
        (9, gherkin.TOKEN_TEXT, 'Lanche'),
        (9, gherkin.TOKEN_NEWLINE, '\n'),
        (10, gherkin.TOKEN_TEXT, 'Dada uma maçã'),
        (10, gherkin.TOKEN_NEWLINE, '\n'),
        (11, gherkin.TOKEN_TEXT, 'Quando mordida'),
        (11, gherkin.TOKEN_NEWLINE, '\n'),
        (12, gherkin.TOKEN_TEXT, 'Então a fome passa'),
        (12, gherkin.TOKEN_NEWLINE, '\n'),
        (13, gherkin.TOKEN_EOF, '')
    ])


def test_lex_tables():
    "Lexer.run() Should be able to lex tables"

    # Given the following lexer loaded with an examples label followed
    # by a table that ends before '\n'
    lexer = gherkin.Lexer('''\
  Examples:
    | column1 | column2 | ''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see the scenario outline case was properly parsed
    tokens.should.equal([
        (1, gherkin.TOKEN_LABEL, 'Examples'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TABLE_COLUMN, 'column1'),
        (2, gherkin.TOKEN_TABLE_COLUMN, 'column2'),
        (2, gherkin.TOKEN_EOF, ''),
    ])


def test_lex_tables_full():
    "Lexer.run() Should be able to lex scenario outlines"

    lexer = gherkin.Lexer('''\
  Feature: gherkin has steps with examples
  Scenario Outline: Add two numbers
    Given I have <input_1> and <input_2> the calculator
    When I press "Sum"!
    Then the result should be <output> on the screen
  Examples:
    | input_1 | input_2 | output |
    | 20      | 30      | 50     |
    | 0       | 40      | 40     |
''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see the scenario outline case was properly parsed
    tokens.should.equal([
        (1, gherkin.TOKEN_LABEL, 'Feature'),
        (1, gherkin.TOKEN_TEXT, 'gherkin has steps with examples'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_LABEL, 'Scenario Outline'),
        (2, gherkin.TOKEN_TEXT, 'Add two numbers'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_TEXT, 'Given I have <input_1> and <input_2> the calculator'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TEXT, 'When I press "Sum"!'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_TEXT, 'Then the result should be <output> on the screen'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_LABEL, 'Examples'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'input_1'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'input_2'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'output'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TABLE_COLUMN, '20'),
        (8, gherkin.TOKEN_TABLE_COLUMN, '30'),
        (8, gherkin.TOKEN_TABLE_COLUMN, '50'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_TABLE_COLUMN, '0'),
        (9, gherkin.TOKEN_TABLE_COLUMN, '40'),
        (9, gherkin.TOKEN_TABLE_COLUMN, '40'),
        (9, gherkin.TOKEN_NEWLINE, '\n'),
        (10, gherkin.TOKEN_EOF, '')
    ])


def test_lex_tables_within_steps():
    "Lexer.run() Should be able to lex example tables from steps"

    # Given a lexer loaded with steps that contain example tables
    lexer = gherkin.Lexer('''\
	Feature: Check models existence
		Background:
	   Given I have a garden in the database:
	      | @name  | area | raining |
	      | Secret Garden | 45   | false   |
	    And I have gardens in the database:
	      | name            | area | raining |
	      | Octopus' Garden | 120  | true    |
    ''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see that steps that contain : will be identified as
    # labels
    tokens.should.equal([
        (1, gherkin.TOKEN_LABEL, 'Feature'),
        (1, gherkin.TOKEN_TEXT, 'Check models existence'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_LABEL, 'Background'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_LABEL, 'Given I have a garden in the database'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TABLE_COLUMN, '@name'),
        (4, gherkin.TOKEN_TABLE_COLUMN, 'area'),
        (4, gherkin.TOKEN_TABLE_COLUMN, 'raining'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_TABLE_COLUMN, 'Secret Garden'),
        (5, gherkin.TOKEN_TABLE_COLUMN, '45'),
        (5, gherkin.TOKEN_TABLE_COLUMN, 'false'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_LABEL, 'And I have gardens in the database'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'name'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'area'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'raining'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TABLE_COLUMN, 'Octopus\' Garden'),
        (8, gherkin.TOKEN_TABLE_COLUMN, '120'),
        (8, gherkin.TOKEN_TABLE_COLUMN, 'true'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_EOF, '')
    ])


def test_lex_multi_line_str():
    "Lexer.run() Should be able to find multi quoted strings after labels"

    # Given a lexer loaded with steps that contain example tables
    lexer = gherkin.Lexer('''\
    Given the following email template:
       ''\'Here we go with a pretty
       big block of text
       surrounded by triple quoted strings
       ''\'
    And a cat picture
       """Now notice we didn't use (:) above
       """
    ''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see that triple quoted strings are captured by the lexer
    tokens.should.equal([
        (1, gherkin.TOKEN_LABEL, 'Given the following email template'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_QUOTES, "'''"),
        (2, gherkin.TOKEN_TEXT, '''Here we go with a pretty
       big block of text
       surrounded by triple quoted strings
       '''),
        (5, gherkin.TOKEN_QUOTES, "'''"),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_TEXT, 'And a cat picture'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_QUOTES, '"""'),
        (7, gherkin.TOKEN_TEXT, "Now notice we didn't use (:) above\n       "),
        (8, gherkin.TOKEN_QUOTES, '"""'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_EOF, '')
    ])

def test_lex_tags_empty():
    "Lexer.lex_tag() Should bail if we reach EOF"

    # Given a lexer loaded with an empty string
    lexer = gherkin.Lexer('')

    # When we try to lex tags
    lexer.lex_tag()

    # Then we see we found no tokens
    lexer.tokens.should.be.empty


def test_lex_tags():
    "Lexer.run() Should be able to find tags"

    # Given a lexer loaded with steps that contain example tables
    lexer = gherkin.Lexer('''\
    @tagged-feature
    Feature: Parse tags

    @tag1 @tag2
    Scenario: Test
    ''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see that triple quoted strings are captured by the lexer
    tokens.should.equal([
        (1, gherkin.TOKEN_TAG, 'tagged-feature'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_LABEL, 'Feature'),
        (2, gherkin.TOKEN_TEXT, 'Parse tags'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TAG, 'tag1'),
        (4, gherkin.TOKEN_TAG, 'tag2'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_LABEL, 'Scenario'),
        (5, gherkin.TOKEN_TEXT, 'Test'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_EOF, ''),
    ])


def test_parse_metadata_empty():

    Parser([(1, gherkin.TOKEN_EOF, '')]).parse_metadata().should.be.none

    Parser([None]).parse_metadata().should.be.none


def test_parse_metadata_incomplete():

    parser = Parser([
        (1, gherkin.TOKEN_META_LABEL, 'language'),
        (1, gherkin.TOKEN_EOF, ''),
    ])

    parser.parse_metadata().should.be.none


def test_parse_metadata_syntax_error():

    parser = Parser([
        (1, gherkin.TOKEN_META_LABEL, 'language'),
        (1, gherkin.TOKEN_TEXT, 'pt-br'),
    ])

    parser.parse_metadata.when.called.should.throw(
        SyntaxError, 'No value found for the meta-field `language\'')


def test_parse_metadata():

    parser = Parser([
        (1, gherkin.TOKEN_META_LABEL, 'language'),
        (1, gherkin.TOKEN_META_VALUE, 'pt-br'),
    ])

    metadata = parser.parse_metadata()

    metadata.should.equal(Ast.Metadata(line=1, key='language', value='pt-br'))


def test_parse_empty_title():

    parser = Parser([
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TEXT, 'more text after title'),
    ])

    feature = parser.parse_title()

    feature.should.be.none


def test_parse_title():

    parser = Parser([
        (1, gherkin.TOKEN_TEXT, 'Scenario title'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
    ])

    feature = parser.parse_title()

    feature.should.equal(Ast.Text(line=1, text='Scenario title'))


def test_parse_table():

    parser = Parser([
        (1, gherkin.TOKEN_TABLE_COLUMN, 'name'),
        (1, gherkin.TOKEN_TABLE_COLUMN, 'email'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TABLE_COLUMN, 'Lincoln'),
        (2, gherkin.TOKEN_TABLE_COLUMN, 'lincoln@clarete.li'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_TABLE_COLUMN, 'Gabriel'),
        (3, gherkin.TOKEN_TABLE_COLUMN, 'gabriel@nacaolivre.org'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_LABEL, 'Scenario'),
        (4, gherkin.TOKEN_EOF, ''),
    ])

    feature = parser.parse_table()

    feature.should.equal(Ast.Table(line=1, fields=[
        ['name', 'email'],
        ['Lincoln', 'lincoln@clarete.li'],
        ['Gabriel', 'gabriel@nacaolivre.org'],
    ]))


def test_parse_background():

    # Background: title
    #  Given two users in the database:
    #    | name | email |
    #    | Lincoln | lincoln@clarete.li |
    #    | Gabriel | gabriel@nacaolivre.org |
    # Scenario:
    parser = Parser([
        (1, gherkin.TOKEN_LABEL, 'Background'),
        (1, gherkin.TOKEN_TEXT, 'title'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_LABEL, 'Given two users in the database'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_TABLE_COLUMN, 'name'),
        (3, gherkin.TOKEN_TABLE_COLUMN, 'email'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TABLE_COLUMN, 'Lincoln'),
        (4, gherkin.TOKEN_TABLE_COLUMN, 'lincoln@clarete.li'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_TABLE_COLUMN, 'Gabriel'),
        (5, gherkin.TOKEN_TABLE_COLUMN, 'gabriel@nacaolivre.org'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_LABEL, 'Scenario'),
    ])

    # When the background is parsed
    feature = parser.parse_background()

    # Then I see the output contains a valid background with a step
    # with examples. Notice the scenario label is not returned
    # anywhere here
    feature.should.equal(Ast.Background(
        line=1,
        title=Ast.Text(line=1, text='title'),
        steps=[
            Ast.Step(
                line=2,
                title=Ast.Text(line=2, text='Given two users in the database'),
                table=Ast.Table(line=3, fields=[
                    ['name', 'email'],
                    ['Lincoln', 'lincoln@clarete.li'],
                    ['Gabriel', 'gabriel@nacaolivre.org'],
                ]))
        ]))


## Scenarios


def teste_parse_scenario():

    parser = Parser([
        (1, gherkin.TOKEN_LABEL, 'Scenario'),
        (1, gherkin.TOKEN_TEXT, 'Scenario title'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TEXT, 'Given first step'),
    ])

    feature = parser.parse_scenarios()

    feature.should.equal([Ast.Scenario(
        line=1,
        title=Ast.Text(line=1, text='Scenario title'),
        steps=[Ast.Step(line=2, title=Ast.Text(line=2, text='Given first step'))],
    )])


def teste_parse_scenario_with_description():

    parser = Parser([
        (1, gherkin.TOKEN_LABEL, 'Scenario'),
        (1, gherkin.TOKEN_TEXT, 'Scenario title'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TEXT, 'Scenario description'),
        (2, gherkin.TOKEN_TEXT, 'More description'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_TEXT, 'Given first step'),
    ])

    feature = parser.parse_scenarios()

    feature.should.equal([Ast.Scenario(
        line=1,
        title=Ast.Text(line=1, text='Scenario title'),
        description=Ast.Text( line=2, text='Scenario description More description'),
        steps=[Ast.Step(line=3, title=Ast.Text(line=3, text='Given first step'))],
    )])


def test_parse_scenario_outline_with_examples():
    ""

    # Given a parser loaded with the following gherkin document:
    #
    #     Scenario Outline: Plant a tree
    #       Given the <name> of a garden
    #       When I plant a tree
    #        And wait for <num_days> days
    #       Then I see it growing
    #     Examples:
    #       | name | num_days |
    #       | Secret | 2 |
    #       | Octopus | 5 |
    parser = Parser([
        (1, gherkin.TOKEN_LABEL, 'Scenario Outline'),
        (1, gherkin.TOKEN_TEXT, 'Plant a tree'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TEXT, 'Given the <name> of a garden'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_TEXT, 'When I plant a tree'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TEXT, 'And wait for <num_days> days'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_TEXT, 'Then I see it growing'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_LABEL, 'Examples'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'name'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'num_days'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TABLE_COLUMN, 'Secret'),
        (8, gherkin.TOKEN_TABLE_COLUMN, '2'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_TABLE_COLUMN, 'Octopus'),
        (9, gherkin.TOKEN_TABLE_COLUMN, '5'),
        (9, gherkin.TOKEN_NEWLINE, '\n'),
        (10, gherkin.TOKEN_EOF, '')
    ])

    scenarios = parser.parse_scenarios()

    scenarios.should.equal([
        Ast.ScenarioOutline(
            line=1,
            title=Ast.Text(line=1, text='Plant a tree'),
            steps=[Ast.Step(line=2, title=Ast.Text(line=2, text='Given the <name> of a garden')),
                   Ast.Step(line=3, title=Ast.Text(line=3, text='When I plant a tree')),
                   Ast.Step(line=4, title=Ast.Text(line=4, text='And wait for <num_days> days')),
                   Ast.Step(line=5, title=Ast.Text(line=5, text='Then I see it growing'))],
            examples=Ast.Examples(line=6, table=Ast.Table(line=7, fields=[
                ['name', 'num_days'],
                ['Secret', '2'],
                ['Octopus', '5'],
            ]))
        )])


def test_parse_not_starting_with_feature():

    parser = gherkin.Parser(gherkin.Lexer('''
Scenario: Scenario title
  Given first step
   When second step
   Then third step
    ''').run())

    parser.parse_feature.when.called.should.throw(
        SyntaxError,
        "Feature expected in the beginning of the file, "
        "found `Scenario' though.")


def test_parse_feature_two_backgrounds():

    parser = gherkin.Parser(gherkin.Lexer('''
Feature: Feature title
  feature description
  Background: Some background
    about the problem
  Background: Some other background
    will raise an exception
  Scenario: Scenario title
    Given first step
     When second step
     Then third step
    ''').run())

    parser.parse_feature.when.called.should.throw(
        SyntaxError,
        "`Background' should not be declared here, Scenario or Scenario Outline expected")


def test_parse_feature_background_wrong_place():

    parser = gherkin.Parser(gherkin.Lexer('''
Feature: Feature title
  feature description
  Scenario: Scenario title
    Given first step
     When second step
     Then third step
  Background: Some background
    about the problem
    ''').run())

    parser.parse_feature.when.called.should.throw(
        SyntaxError,
        "`Background' should not be declared here, Scenario or Scenario Outline expected")


def test_parse_feature():

    parser = Parser([
        (1, gherkin.TOKEN_LABEL, 'Feature'),
        (1, gherkin.TOKEN_TEXT, 'Feature title'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TEXT, 'feature description'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_LABEL, 'Background'),
        (3, gherkin.TOKEN_TEXT, 'Some background'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TEXT, 'Given the problem'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_LABEL, 'Scenario'),
        (5, gherkin.TOKEN_TEXT, 'Scenario title'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_TEXT, 'Given first step'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_LABEL, 'Scenario'),
        (7, gherkin.TOKEN_TEXT, 'Another scenario'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TEXT, 'Given this step'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_TEXT, 'When we take another step'),
        (9, gherkin.TOKEN_NEWLINE, '\n'),
        (10, gherkin.TOKEN_EOF, ''),
    ])

    feature = parser.parse_feature()

    feature.should.equal(Ast.Feature(
        line=1,
        title=Ast.Text(line=1, text='Feature title'),
        description=Ast.Text(line=2, text='feature description'),
        background=Ast.Background(
            line=3,
            title=Ast.Text(line=3, text='Some background'),
            steps=[Ast.Step(line=4, title=Ast.Text(line=4, text='Given the problem'))]),
        scenarios=[
            Ast.Scenario(line=5,
                         title=Ast.Text(line=5, text='Scenario title'),
                         steps=[Ast.Step(line=6, title=Ast.Text(line=6, text='Given first step'))]),
            Ast.Scenario(line=7,
                         title=Ast.Text(line=7, text='Another scenario'),
                         steps=[Ast.Step(line=8, title=Ast.Text(line=8, text='Given this step')),
                                Ast.Step(line=9, title=Ast.Text(line=9, text='When we take another step'))]),
        ],
    ))


def test_parse_tables_within_steps():
    "Lexer.run() Should be able to parse example tables from steps"

    # Given a parser loaded with steps that contain example tables
    '''Feature: Check models existence
		Background:
	   Given I have a garden in the database:
	      | @name  | area | raining |
	      | Secret Garden | 45   | false   |
	    And I have gardens in the database:
	      | name            | area | raining |
	      | Octopus' Garden | 120  | true    |
         Scenario: Plant a tree
           Given the <name> of a garden
           When I plant a tree
            And wait for <num_days> days
           Then I see it growing
    '''
    parser = Parser([
        (1, gherkin.TOKEN_LABEL, 'Feature'),
        (1, gherkin.TOKEN_TEXT, 'Check models existence'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_LABEL, 'Background'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_LABEL, 'Given I have a garden in the database'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TABLE_COLUMN, '@name'),
        (4, gherkin.TOKEN_TABLE_COLUMN, 'area'),
        (4, gherkin.TOKEN_TABLE_COLUMN, 'raining'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_TABLE_COLUMN, 'Secret Garden'),
        (5, gherkin.TOKEN_TABLE_COLUMN, '45'),
        (5, gherkin.TOKEN_TABLE_COLUMN, 'false'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_LABEL, 'And I have gardens in the database'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'name'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'area'),
        (7, gherkin.TOKEN_TABLE_COLUMN, 'raining'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TABLE_COLUMN, "Octopus' Garden"),
        (8, gherkin.TOKEN_TABLE_COLUMN, '120'),
        (8, gherkin.TOKEN_TABLE_COLUMN, 'true'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_LABEL, 'Scenario'),
        (9, gherkin.TOKEN_TEXT, 'Plant a tree'),
        (9, gherkin.TOKEN_NEWLINE, '\n'),
        (10, gherkin.TOKEN_TEXT, 'Given the <name> of a garden'),
        (10, gherkin.TOKEN_NEWLINE, '\n'),
        (11, gherkin.TOKEN_TEXT, 'When I plant a tree'),
        (11, gherkin.TOKEN_NEWLINE, '\n'),
        (12, gherkin.TOKEN_TEXT, 'And wait for <num_days> days'),
        (12, gherkin.TOKEN_NEWLINE, '\n'),
        (13, gherkin.TOKEN_TEXT, 'Then I see it growing'),
        (13, gherkin.TOKEN_NEWLINE, '\n'),
        (14, gherkin.TOKEN_EOF, '')
    ])

    feature = parser.parse_feature()

    feature.should.equal(Ast.Feature(
        line=1,
        title=Ast.Text(line=1, text='Check models existence'),
        background=Ast.Background(
            line=2,
            steps=[
                Ast.Step(
                    line=3,
                    title=Ast.Text(line=3, text='Given I have a garden in the database'),
                    table=Ast.Table(line=4, fields=[
                        ['@name', 'area', 'raining'],
                        ['Secret Garden', '45', 'false']])),
                Ast.Step(
                    line=6,
                    title=Ast.Text(line=6, text='And I have gardens in the database'),
                    table=Ast.Table(line=7, fields=[
                        ['name', 'area', 'raining'],
                        ['Octopus\' Garden', '120', 'true']])),
            ]
        ),
        scenarios=[
            Ast.Scenario(
                title=Ast.Text(line=9, text='Plant a tree'),
                line=9,
                steps=[
                    Ast.Step(line=10, title=Ast.Text(line=10, text='Given the <name> of a garden')),
                    Ast.Step(line=11, title=Ast.Text(line=11, text='When I plant a tree')),
                    Ast.Step(line=12, title=Ast.Text(line=12, text='And wait for <num_days> days')),
                    Ast.Step(line=13, title=Ast.Text(line=13, text='Then I see it growing'))
                ])
        ],
    ))


def test_parse_quoted_strings_on_steps():

    # Given a parser loaded with the following Gherkin document
    #    Given the following email template:
    #       '''Here we go with a pretty
    #       big block of text
    #       surrounded by triple quoted strings
    #       '''
    #    And a cat picture
    #       """Now notice we didn't use (:) above
    #       """
    parser = Parser([
        (1, gherkin.TOKEN_LABEL, 'Given the following email template'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_QUOTES, "'''"),
        (2, gherkin.TOKEN_TEXT, '''Here we go with a pretty
       big block of text
       surrounded by triple quoted strings
       '''),
        (5, gherkin.TOKEN_QUOTES, "'''"),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_TEXT, 'And a cat picture'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_QUOTES, '"""'),
        (7, gherkin.TOKEN_TEXT, "Now notice we didn't use (:) above\n       "),
        (8, gherkin.TOKEN_QUOTES, '"""'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_EOF, '')
    ])

    steps = parser.parse_steps()

    steps.should.equal([
        Ast.Step(
            line=1,
            title=Ast.Text(line=1, text='Given the following email template'),
            text=Ast.Text(line=2, text='''Here we go with a pretty
       big block of text
       surrounded by triple quoted strings
       ''')),
        Ast.Step(
            line=6,
            title=Ast.Text(line=6, text='And a cat picture'),
            text=Ast.Text(line=7, text="Now notice we didn't use (:) above\n       "))])


def test_parse_text():
    parser = Parser([
        (1, gherkin.TOKEN_TAG, 'tag1'),
        (1, gherkin.TOKEN_TAG, 'tag2'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_TAG, 'tag3'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_LABEL, 'Feature'),
    ])

    tags = parser.parse_tags()

    tags.should.equal(['tag1', 'tag2', 'tag3'])


def test_parse_tags_on_scenario_outline_examples():
    "Parser should allow tags to be defined in examples"

    # Given a parser loaded with a document that contains tags on
    # scenario outline examples
    #   @tagged-feature
    #   Feature: Parse tags
    #   @tag1 @tag2
    #   Scenario Outline: Test
    #   @example-tag1
    #   @example-tag2
    #   Examples:
    #     | Header |

    parser = Parser([
        (1, gherkin.TOKEN_TAG, 'tagged-feature'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_LABEL, 'Feature'),
        (2, gherkin.TOKEN_TEXT, 'Parse tags'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_TAG, 'tag1'),
        (3, gherkin.TOKEN_TAG, 'tag2'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_LABEL, 'Scenario Outline'),
        (4, gherkin.TOKEN_TEXT, 'Test'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_TAG, 'example-tag1'),
        (5, gherkin.TOKEN_NEWLINE, '\n'),
        (6, gherkin.TOKEN_TAG, 'example-tag2'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_LABEL, 'Examples'),
        (7, gherkin.TOKEN_NEWLINE, '\n'),
        (8, gherkin.TOKEN_TABLE_COLUMN, 'Header'),
        (8, gherkin.TOKEN_NEWLINE, '\n'),
        (9, gherkin.TOKEN_EOF, ''),
    ])

    # When I parse the document
    feature = parser.parse_feature()

    # Then I see all the tags were found
    feature.should.equal(Ast.Feature(
        line=2,
        title=Ast.Text(line=2, text='Parse tags'),
        tags=['tagged-feature'],
        scenarios=[Ast.ScenarioOutline(
            line=4,
            title=Ast.Text(line=4, text='Test'),
            tags=['tag1', 'tag2'],
            examples=Ast.Examples(
                line=7,
                tags=['example-tag1', 'example-tag2'],
                table=Ast.Table(line=8, fields=[['Header']])),
        )]))


def test_parse_tags_on_feature_and_scenario():

    # Given a parser loaded with a gherkin document with one tag on
    # the feature and two tags on a scenario:
    #
    #   @tagged-feature
    #   Feature: Parse tags
    #
    #   @tag1 @tag2
    #   Scenario: Test
    parser = Parser([
        (1, gherkin.TOKEN_TAG, 'tagged-feature'),
        (1, gherkin.TOKEN_NEWLINE, '\n'),
        (2, gherkin.TOKEN_LABEL, 'Feature'),
        (2, gherkin.TOKEN_TEXT, 'Parse tags'),
        (2, gherkin.TOKEN_NEWLINE, '\n'),
        (3, gherkin.TOKEN_NEWLINE, '\n'),
        (4, gherkin.TOKEN_TAG, 'tag1'),
        (4, gherkin.TOKEN_TAG, 'tag2'),
        (4, gherkin.TOKEN_NEWLINE, '\n'),
        (5, gherkin.TOKEN_LABEL, 'Scenario'),
        (5, gherkin.TOKEN_TEXT, 'Test'),
        (6, gherkin.TOKEN_NEWLINE, '\n'),
        (7, gherkin.TOKEN_EOF, ''),
    ])

    feature = parser.parse_feature()

    feature.should.equal(Ast.Feature(
        line=2,
        title=Ast.Text(line=2, text='Parse tags'),
        tags=['tagged-feature'],
        scenarios=[Ast.Scenario(
            line=5,
            title=Ast.Text(line=5, text='Test'),
            tags=['tag1', 'tag2'])]))


def test_ast_node_equal():

    # Given two different AST nodes
    n1 = Ast.Node()
    n2 = Ast.Node()

    # And different attributes to each node
    n1.name = 'Lincoln'
    n2.color = 'green'

    # When I compare them
    equal = n1 == n2

    # Then I see they're different
    equal.should.be.false
