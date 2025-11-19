# sdt_tac.py
# Requiere: pip install ply
"""
Script ejemplo que implementa:
 - ETDS (acciones semánticas integradas en el parser)
 - Tabla de símbolos con manejo de ámbitos
 - Generador de código en tres direcciones (TAC) a partir del AST (AST_D: declaraciones/definiciones)

Para ejecutar:
    pip install ply
    python sdt_tac.py

Salida:
 - Impresión de la tabla de símbolos
 - Impresión de los quads (TAC)
"""

import ply.lex as lex
import ply.yacc as yacc
from collections import namedtuple, OrderedDict

# -----------------------
# AST node definitions
# -----------------------
class Node:
    pass

class Program(Node):
    def __init__(self, decls):
        self.decls = decls

class VarDecl(Node):
    def __init__(self, vtype, names):
        self.vtype = vtype
        self.names = names  # list of strings

class FuncDecl(Node):
    def __init__(self, rettype, name, params, body):
        self.rettype = rettype
        self.name = name
        self.params = params  # list of (type,name)
        self.body = body      # list of statements

class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class Return(Node):
    def __init__(self, expr):
        self.expr = expr

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Num(Node):
    def __init__(self, value):
        self.value = value

class Var(Node):
    def __init__(self, name):
        self.name = name

# -----------------------
# Symbol Table
# -----------------------
class SymbolEntry:
    def __init__(self, name, kind, typ, scope_level, offset=None, params=None):
        self.name = name
        self.kind = kind
        self.type = typ
        self.scope_level = scope_level
        self.offset = offset
        self.params = params or []

    def __repr__(self):
        return f"SymbolEntry(name={self.name}, kind={self.kind}, type={self.type}, scope={self.scope_level}, offset={self.offset}, params={self.params})"

class SymbolTable:
    def __init__(self):
        self.scopes = [OrderedDict()]  # global scope level 0
        self.level = 0
        self.offsets = [0]  # offset per scope

    def enter_scope(self):
        self.scopes.append(OrderedDict())
        self.level += 1
        self.offsets.append(0)

    def exit_scope(self):
        popped = self.scopes.pop()
        self.offsets.pop()
        self.level -= 1
        return popped

    def add(self, name, kind, typ, params=None):
        scope = self.scopes[-1]
        if name in scope:
            raise Exception(f"Redeclaration of {name} in same scope")
        offset = self.offsets[-1]
        entry = SymbolEntry(name, kind, typ, self.level, offset, params)
        scope[name] = entry
        # increment offset for next var
        self.offsets[-1] += 1
        return entry

    def add_function(self, name, rettype, params):
        # functions recorded in global scope
        scope = self.scopes[0]
        if name in scope:
            raise Exception(f"Redeclaration of function {name}")
        entry = SymbolEntry(name, 'func', rettype, 0, offset=None, params=params)
        scope[name] = entry
        return entry

    def lookup(self, name):
        # search from innermost to outermost
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

    def __repr__(self):
        out = []
        for i, s in enumerate(self.scopes):
            out.append(f"Scope level {i}:")
            for k, v in s.items():
                out.append(f"  {k} -> {v}")
        return "\n".join(out)

# -----------------------
# Three-address code representation
# -----------------------
Quad = namedtuple('Quad', ['op', 'arg1', 'arg2', 'res'])

class TACGenerator:
    def __init__(self, symtab):
        self.quads = []
        self.temp_count = 0
        self.label_count = 0
        self.symtab = symtab

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, op, a1=None, a2=None, res=None):
        q = Quad(op, a1, a2, res)
        self.quads.append(q)
        return q

    # visitors
    def gen_program(self, prog):
        for decl in prog.decls:
            if isinstance(decl, VarDecl):
                # no code for global var decl (but could allocate)
                for n in decl.names:
                    # record in symbol table already done at parse-time
                    pass
            elif isinstance(decl, FuncDecl):
                self.gen_func(decl)
        return self.quads

    def gen_func(self, f):
        lbl = f"func_{f.name}"
        self.emit('label', lbl, None, None)
        for stmt in f.body:
            self.gen_stmt(stmt)
        # ensure function ends with return if not present
        self.emit('ret', None, None, None)

    def gen_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            # nothing (alloc could be emitted)
            return
        if isinstance(stmt, Assign):
            src = self.gen_expr(stmt.expr)
            self.emit('=', src, None, stmt.name)
            return
        if isinstance(stmt, Return):
            val = self.gen_expr(stmt.expr) if stmt.expr else None
            self.emit('ret', val, None, None)
            return
        # expr as statement
        if isinstance(stmt, (BinOp, Num, Var)):
            self.gen_expr(stmt)
            return

    def gen_expr(self, expr):
        if isinstance(expr, Num):
            return str(expr.value)
        if isinstance(expr, Var):
            return expr.name
        if isinstance(expr, BinOp):
            a = self.gen_expr(expr.left)
            b = self.gen_expr(expr.right)
            t = self.new_temp()
            self.emit(expr.op, a, b, t)
            return t
        raise Exception("Unknown expr type")

# -----------------------
# Lexer (PLY)
# -----------------------
tokens = (
    'ID', 'NUMBER',
    'TYPE',
    'PLUS','MINUS','TIMES','DIV',
    'ASSIGN',
    'LPAREN','RPAREN','LBRACE','RBRACE',
    'SEMI','COMMA',
    'RETURN'
)

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIV     = r'/'
t_ASSIGN  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_SEMI    = r';'
t_COMMA   = r','
t_ignore  = ' \t\r'

reserved = {
    'int' : 'TYPE',
    'float': 'TYPE',
    'return': 'RETURN'
}

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    else:
        t.type = 'ID'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'//.*'
    pass

def t_error(t):
    print("Illegal character", t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

# -----------------------
# Parser (PLY)
# -----------------------
symtab = SymbolTable()

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIV'),
)

def p_program(p):
    "program : decl_list"
    p[0] = Program(p[1])

def p_decl_list(p):
    """decl_list : decl decl_list
                 | empty"""
    if len(p) == 3 and p[1] is not None:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_decl(p):
    "decl : var_decl | func_decl"
    p[0] = p[1]

def p_var_decl(p):
    "var_decl : TYPE id_list SEMI"
    vtype = p[1]
    names = p[2]
    # action: add each var to symbol table (current scope)
    for n in names:
        symtab.add(n, 'var', vtype)
    p[0] = VarDecl(vtype, names)

def p_id_list_single(p):
    "id_list : ID"
    p[0] = [p[1]]

def p_id_list_more(p):
    "id_list : id_list COMMA ID"
    lst = p[1]
    lst.append(p[3])
    p[0] = lst

def p_func_decl(p):
    "func_decl : TYPE ID LPAREN params RPAREN LBRACE stmt_list RBRACE"
    rettype = p[1]; name = p[2]; params = p[4]; body = p[7]
    # Add function to global symbol table
    symtab.add_function(name, rettype, params)
    # Create a new scope for function body and insert params
    symtab.enter_scope()
    for ptype, pname in params:
        symtab.add(pname, 'param', ptype)
    p[0] = FuncDecl(rettype, name, params, body)
    # exit scope after building AST nodes
    symtab.exit_scope()

def p_params_empty(p):
    "params : empty"
    p[0] = []

def p_params_list(p):
    "params : param_list"
    p[0] = p[1]

def p_param_list_single(p):
    "param_list : TYPE ID"
    p[0] = [(p[1], p[2])]

def p_param_list_more(p):
    "param_list : param_list COMMA TYPE ID"
    lst = p[1]
    lst.append((p[3], p[4]))
    p[0] = lst

def p_stmt_list(p):
    """stmt_list : stmt stmt_list
                 | empty"""
    if len(p) == 3 and p[1] is not None:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_stmt(p):
    """stmt : var_decl
            | assignment SEMI
            | return_stmt
            | expr SEMI"""
    if isinstance(p[1], Node):
        p[0] = p[1]
    elif len(p) == 3 and isinstance(p[1], Assign):
        p[0] = p[1]
    else:
        p[0] = p[1]

def p_assignment(p):
    "assignment : ID ASSIGN expr"
    # check existence (we'll allow assignment to previously-declared var)
    entry = symtab.lookup(p[1])
    if entry is None:
        # If not found in current scopes, implicitly add to current scope as an error-tolerant behavior
        symtab.add(p[1], 'var', 'int')  # default type int
    p[0] = Assign(p[1], p[3])

def p_return_stmt(p):
    "return_stmt : RETURN expr SEMI"
    p[0] = Return(p[2])

def p_expr_binop(p):
    """expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIV expr"""
    p[0] = BinOp(p[2], p[1], p[3])

def p_expr_term(p):
    "expr : term"
    p[0] = p[1]

def p_term_num(p):
    "term : NUMBER"
    p[0] = Num(p[1])

def p_term_var(p):
    "term : ID"
    # ensure variable exists (if not, add to current scope - forgiveness)
    if symtab.lookup(p[1]) is None:
        symtab.add(p[1], 'var', 'int')
    p[0] = Var(p[1])

def p_term_paren(p):
    "term : LPAREN expr RPAREN"
    p[0] = p[2]

def p_empty(p):
    "empty :"
    pass

def p_error(p):
    if p:
        print("Syntax error at token", p.type, "value", p.value)
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

# -----------------------
# Example and running
# -----------------------
if __name__ == "__main__":
    sample = r"""
    int x, y;
    int add(int a, int b) {
        int z;
        z = a + b;
        return z;
    }
    int main() {
        int r;
        r = add(3, 4);
        return r;
    }
    """

    print("PARSE: parsing sample program...\n")
    ast = parser.parse(sample, lexer=lexer)
    print("AST built. Now printing symbol table (global scopes):")
    print(symtab)
    print("\nGenerating TAC...")
    tacgen = TACGenerator(symtab)
    quads = tacgen.gen_program(ast)
    print("\nThree-address code (quads):")
    for i, q in enumerate(quads):
        print(f"{i:03}: {q}")

    print("\n--- Fine ---")
