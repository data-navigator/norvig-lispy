"""Implementing a Scheme interpreter in Python."""

#Env = dict             # An environment is a mapping of {variable: value}
Symbol = str           # A Scheme Symbol equals Python str
List = list            # A Scheme List equals a Python list
Number = (int, float)  # A Scheme Number equals a Python int or float


class Procedure(object):
    """A user-defined Scheme Procedure"""
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))


class Env(dict):
    """An environment: a dict of {'var':val} pairs, with an outer Env."""
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears"
        return self if (var in self) else self.outer.find(var)


def standard_env():
    """An environment with some Scheme standard prodcedures"""
    import math  # Map the functions in the math module to the Env instance
    import operator  # Map the functions in the operator module to their symbol
    env = Env()  # new dict as an Env instance
    env.update(vars(math))  # sin, cos, sqrt, pi ...
    env.update({
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.floordiv,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq,
        'abs': abs,
        'append': operator.add,
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x,y: [x] + y,
        'eq?': operator.is_,
        'equal': operator.eq,
        'length': len,
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x,list),
        'map': map,
        'max': max,
        'min': min,
        'not': operator.not_,
        'null?': lambda x: x ==[],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, Symbol)}
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

global_env = standard_env()


def eval(x, env=global_env):
    """Evaluate a Scheme expression in a specified environment.

    variable reference (var):
	A symbol is interpreted as a variable name; its value is the var's value.
    Example: r ⇒ 10 (assuming r was previously defined to be 10)

    constant literal (number):
	A number evaluates to itself.
    Examples: 12 ⇒ 12 or -3.45e+6 ⇒ -3.45e+6

    conditional	(if test conseq alt):
	Evaluate test; if true, evaluate and return conseq; otherwise alt.
    Example: (if (> 10 20) (+ 1 1) (+ 3 3)) ⇒ 6

    definition	(define var exp):
	Define a new variable & give it the value of evaluating the expression exp.
    Examples: (define r 10)

    procedure call	(proc arg...):
	If proc is anything other than one of the symbols if, define, or quote then
    it is treated as a procedure. Evaluate proc and all the args, and then the
    procedure is applied to the list of arg values.
    Example: (sqrt (* 2 8)) ⇒ 4.0"""
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, List):
        return x
    elif x[0] == 'quote':          # quotation
        (_, exp) = x
        return exp
    elif x[0] == 'if':
        (_, test, conseq, alt) = x  # Tuple unpack
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'set!':           # assignment
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':         # procedure
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)


def schemestr(exp):
    """Convert a Python object back into a Scheme-readable string"""
    if isinstance(exp, list):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    if isinstance(exp, map):
        return list(exp)
    else:
        return str(exp)


def repl(prompt='lis.py>'):
    """A prompt Read Eval Print Loop"""
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(schemestr(val))
