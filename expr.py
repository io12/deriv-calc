import ast
from fractions import Fraction as Frac


# Transform the `ast` module's nodes into redefined nodes
def trans_ast(node):
    if isinstance(node, ast.BinOp):
        return BinOp(trans_ast(node.left), node.op, trans_ast(node.right))
    elif isinstance(node, ast.UnaryOp):
        return UnaryOp(node.op, trans_ast(node.operand))
    elif isinstance(node, ast.Num):
        return Num(node.n)
    elif isinstance(node, ast.Name):
        return Name(node.id)
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return Call(node.func.id, trans_ast(node.args[0]))
    else:
        return Undefined()


def sqr(u):
    return u ** Num(2)


def sqrt(u):
    return u ** Num(Frac(1, 2))


def make_func(id):
    return lambda x: Call(id, x)


# Make AST node shorthand constructors
for fn in ['ln', 'sin', 'cos', 'tan', 'csc', 'sec', 'cot']:
    globals()[fn] = make_func(fn)


class Expr(ast.Expr):
    def __add__(self, other):
        return BinOp(self, ast.Add(), other)

    def __sub__(self, other):
        return BinOp(self, ast.Sub(), other)

    def __mul__(self, other):
        return BinOp(self, ast.Mult(), other)

    def __truediv__(self, other):
        return BinOp(self, ast.Div(), other)

    def __pow__(self, other):
        return BinOp(self, ast.Pow(), other)

    def __neg__(self):
        return UnaryOp(ast.USub(), self)

    def simpl(self):
        return self


class Undefined(Expr):
    def __str__(self, parent_prec=0):
        return 'undefined'

    def deriv(self):
        return Undefined()


class BinOp(Expr):
    def __init__(self, f, op, g):
        self.f = f
        self.g = g
        self.op = op

    def __str__(self, parent_prec=0):
        ops = {
            ast.Add: ('+', 1),
            ast.Sub: ('-', 1),
            ast.Mult: ('*', 2),
            ast.Div: ('/', 2),
            ast.Pow: ('^', 3),
        }
        op_s, prec = ops[self.op.__class__]
        f_s = self.f.__str__(prec)
        g_s = self.g.__str__(prec)
        if prec < parent_prec:
            return f'({f_s} {op_s} {g_s})'
        else:
            return f'{f_s} {op_s} {g_s}'

    def deriv(self):
        op = self.op
        f = self.f
        g = self.g
        df = f.deriv()
        dg = g.deriv()
        if isinstance(op, (ast.Add, ast.Sub)):
            return BinOp(df, op, dg)
        elif isinstance(op, ast.Mult):
            return f * dg + g * df
        elif isinstance(op, ast.Div):
            return (df * g - dg * f) / sqr(g)
        elif isinstance(op, (ast.Pow, ast.BitXor)):
            return f ** (g - Num(1)) * (g * df + f * ln(f) * dg)
        else:
            return Undefined()

    def simpl(self):
        op = self.op
        f = self.f.simpl()
        g = self.g.simpl()
        if isinstance(f, Undefined) or isinstance(g, Undefined):
            return Undefined()
        f_is_num = isinstance(f, Num)
        g_is_num = isinstance(g, Num)
        if isinstance(op, (ast.Add, ast.Sub)):
            if f_is_num and g_is_num:
                if isinstance(op, ast.Add):
                    return Num(f.val + g.val)
                else:
                    return Num(f.val - g.val)
            elif f_is_num and f.val == 0:
                return g
            elif g_is_num and g.val == 0:
                return f
            else:
                return BinOp(f, op, g)
        elif isinstance(op, ast.Mult):
            if f_is_num and g_is_num:
                return Num(f.val * g.val)
            elif f_is_num and f.val == 1:
                return g
            elif g_is_num and g.val == 1:
                return f
            elif f_is_num and f.val == 0 or g_is_num and g.val == 0:
                return Num(0)
            else:
                return f * g
        elif isinstance(op, ast.Div):
            if f_is_num and g_is_num:
                return Num(Frac(f.val, g.val))
            elif g_is_num and g.val == 1:
                return f
            else:
                return f / g
        elif isinstance(op, (ast.Pow, ast.BitXor)):
            if f_is_num and g_is_num:
                return Num(f.val ** g.val)
            elif f_is_num and f.val == 0:
                return Num(0)
            elif g_is_num and g.val == 1:
                return f
            elif f_is_num and f.val == 1 or g_is_num and g.val == 0:
                return Num(1)
            elif g_is_num and g.val < 0:
                return Num(1) / f ** Num(-g.val)
            else:
                return f ** g
        else:
            return Undefined


class UnaryOp(Expr):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __str__(self, parent_prec=0):
        ops = {
            ast.UAdd: '+',
            ast.USub: '-',
        }
        op_s = ops[self.op.__class__]
        if isinstance(self.operand, BinOp):
            return f'{op_s}({self.operand})'
        else:
            return f'{op_s}{self.operand}'

    def deriv(self):
        if isinstance(self.op, ast.UAdd):
            return self.operand.deriv()
        elif isinstance(self.op, ast.USub):
            return -self.operand.deriv()
        else:
            return Undefined()

    def simpl(self):
        op = self.op
        operand = self.operand.simpl()
        if isinstance(operand, Undefined):
            return Undefined()
        if isinstance(op, ast.UAdd):
            return operand
        elif isinstance(op, ast.USub):
            if isinstance(operand, Num):
                return Num(-operand.val)
            else:
                return -operand
        else:
            return Undefined()


# TODO: make this implicit somehow
class Num(Expr):
    def __init__(self, val):
        self.val = val

    def __str__(self, parent_prec=0):
        return str(self.val)

    def deriv(self):
        return Num(0)


class Name(Expr):
    def __init__(self, id):
        self.id = id

    def __str__(self, parent_prec=0):
        return self.id

    def deriv(self):
        if self.id == 'x':
            return Num(1)
        else:
            return Num(0)


class Call(Expr):
    def __init__(self, id, arg):
        self.id = id
        self.arg = arg

    def __str__(self, parent_prec=0):
        return f'{self.id}({self.arg})'

    def deriv(self):
        u = self.arg
        du = u.deriv()
        if self.id == 'ln':
            return Num(1) / u * du
        elif self.id == 'sqrt':
            return Num(Frac(1, 2)) * u ** Num(-Frac(1, 2)) * du
        elif self.id == 'sin':
            return cos(u) * du
        elif self.id == 'cos':
            return -sin(u) * du
        elif self.id == 'tan':
            return sqr(sec(u)) * du
        elif self.id == 'cot':
            return -sqr(csc(u)) * du
        elif self.id == 'sec':
            return sec(u) * tan(u) * du
        elif self.id == 'csc':
            return -(csc(u) * cot(u)) * du
        elif self.id in ['arcsin', 'asin']:
            return (Num(1) / sqrt(Num(1) - sqr(u))) * du
        elif self.id in ['arccos', 'acos']:
            return -(Num(1) / sqrt(Num(1) - sqr(u))) * du
        elif self.id in ['arctan', 'atan']:
            return (Num(1) / (u ** Num(2) + Num(1))) * du
        elif self.id in ['arccsc', 'acsc']:
            return -(Num(1) / (abs(u) * sqrt(sqr(u) - 1))) * du
        elif self.id in ['arcsec', 'asec']:
            return (Num(1) / (abs(u) * sqrt(sqr(u) - 1))) * du
        elif self.id in ['arccot', 'acot']:
            return -(Num(1) / (u ** Num(2) + Num(1))) * du
        else:
            return Undefined()

    def simpl(self):
        u = self.arg.simpl()
        if isinstance(u, Undefined):
            return Undefined()
        u_is_num = isinstance(u, Num)
        if self.id == 'ln':
            if u_is_num and u.val <= 0:
                return Undefined()
            elif u_is_num and u.val == 1:
                return Num(0)
            else:
                return ln(u)
        elif self.id == 'sqrt':
            if u_is_num and u.val < 0:
                return Undefined()
            else:
                return sqrt(u)
        elif self.id == 'sin':
            return sin(u)
        elif self.id == 'cos':
            return cos(u)
        elif self.id == 'tan':
            return tan(u)
        elif self.id == 'cot':
            return cot(u)
        elif self.id == 'sec':
            return sec(u)
        elif self.id == 'csc':
            return csc(u)
        elif self.id in ['arcsin', 'asin']:
            return asin(u)
        elif self.id in ['arccos', 'acos']:
            return acos(u)
        elif self.id in ['arctan', 'atan']:
            return atan(u)
        elif self.id in ['arccsc', 'acsc']:
            return acsc(u)
        elif self.id in ['arcsec', 'asec']:
            return asec(u)
        elif self.id in ['arccot', 'acot']:
            return acot(u)
        else:
            return Undefined()


def parse(s):
    return trans_ast(ast.parse(s).body[0].value)
