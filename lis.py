"""Implementing a Scheme interpreter in Python."""

Env = dict             # An environment is a mapping of {variable: value}
Symbol = str           # A Scheme Symbol equals Python str
List = list            # A Scheme List equals a Python list
Number = (int, float)  # A Scheme Number equals a Python int or float

global_env = standard_env()

def standard_env():
    """An environment with some Scheme standard prodcedures"""
    import math
    import operator
    env = Env()  # new dict as an Env
    env.update(vars(math))  # sin, cos, sqrt, pi ...
    env.update(
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.div,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq,
        'abs': abs,
        'append': operator.add,
        'apply': apply,
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x,y: [x] + y,
        'eq?': operator.is_,
        'equal': operator.eq,
        'length' len,
        'list': lambda *x: list(x)
        'list?': lambda x: isinstance(x,list),
        'map': map,
        'max': max,
        'min': min,
        'not': operator.not_,
        'null?': lambda x: x ==[],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, Symbol)
    )
    return env

def tokenize(chars):
    """Convert a string of characters into a list of tokens"""
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(program):
    """Read a scheme expression from a string"""
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens):
    """Read an expression from a sequence of tokens"""
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading.')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # remove ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    """Numbers become numbers, every other token is a symbol"""
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)
