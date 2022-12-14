from cast import *
from rich.tree import Tree
from rich import print as rprint
from clex import Lexer
from checker import Checker
import sly
from render import DotRender, TreeRender

class Parser(sly.Parser):
    #---------------------------------------
    # La lista de tokens se copia desde Lexer
    #---------------------------------------
    tokens = Lexer.tokens
    def __init__(self, ctxt):
        self.ctxt=ctxt

    #---------------------------------------
    # preceencia de operadores
    #---------------------------------------
    precedence = (
        ('right', ADDEQ, LESSEQ, TIMESEQ, DIVIDEQ, MODULEQ),    
        ('left', OR),
        ('left', AND),
        ('left', EQ, NE),
        ('left', LT, LE, GT, GE),
        ('left', INC,DEC),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE, MODULE),
        ('right', UNARY),
        ('nonassoc', 'ELSE')
    )

    #---------------------------------------
    # Definimos las reglas en BNF (o en EBNF)
    #---------------------------------------
    @_("{ declaration }")
    def program(self, p):
        return Program(p.declaration)

    @_("class_declaration",
       "func_declaration",
       "var_declaration",
       "statement")
    def declaration(self, p):
        return p[0]

    @_("CLASS IDENT [ LPAREN LT IDENT RPAREN ] LBRACE { function } RBRACE ")
    def class_declaration(self, p):
        return ClassDeclaration(p.IDENT0, p.IDENT1, p.function)

    @_("FUN function")
    def func_declaration(self, p):
        return p[1]

    @_("VAR IDENT [ ASSIGN expression ] SEMI")
    def var_declaration(self, p):
        return VarDeclaration(p.IDENT, p.expression)

    @_("expr_stmt",
       "for_stmt",
       "if_stmt",
       "print_stmt",
       "return_stmt",
       "while_stmt",
       "block")
    def statement(self, p):
        return p[0]

    @_("expression SEMI")
    def expr_stmt(self, p):
        return ExprStmt(p.expression)

    @_("FOR LPAREN for_initialize [ expression ] SEMI [ expression ] RPAREN statement")
    def for_stmt(self, p):
        body = p.statement
        if p.expression1:
            if not isinstance(body, Block):
                body = Block([ body ])

            body.stmts.append(ExprStmt(p.expression1))
        body = WhileStmt(p.expression0 or Literal(True), body)
        body = Block([p.for_initialize, body])
        return body


    @_("FOR LPAREN SEMI [ expression ] SEMI [ expression ] RPAREN statement")
    def for_stmt(self, p):
        body = p.statement
        if p.expression1:
            if not isinstance(body, Block):
                body = Block([ body ])

            body.stmts.append(ExprStmt(p.expression1))
        body = WhileStmt(p.expression0 or Literal(True), body)
        return body

    @_("var_declaration",
        "expr_stmt")
    def for_initialize(self, p):
        return p[0]
    #---------------------------------------
    #If colgante
    #---------------------------------------
    @_("IF '(' expr ')' statement %prec ELSE",
    "IF '(' expr ')' statement ELSE statement")
    def if_stmt(self, p):
        return IfStmt(p.expression, p.statement0, p.statement1)

    

    @_("PRINT LPAREN expression RPAREN SEMI")
    def print_stmt(self, p):
        return Print(p.expression)

    @_("RETURN [ expression ] SEMI")
    def return_stmt (self, p):
        return Return(p.expression)

    @_("WHILE LPAREN expression RPAREN statement")
    def while_stmt(self, p):
        return WhileStmt(p.expression, p.statement)

    @_("LBRACE { declaration } RBRACE")
    def block(self, p):
        return Block(p.declaration)
    #---------------------------------------
    # += -= *= /=
    #---------------------------------------
    @_("expression ASSIGN expression",
       "expression ADDEQ expression",
       "expression LESSEQ expression",
       "expression TIMESEQ expression",
       "expression DIVIDEQ expression",
       "expression MODULEQ expression")
    def expression(self, p):
        if isinstance(p.expression0, Variable):
            return Assign(p.expression0.name, p.expression1)
        elif isinstance(p.expression0, Get):
            return Set(p.expression0.obj, p.expression0.name, p.expression1)
        else:
            raise SyntaxError(f"{p.lineno}: No se pudo asignar {p.expression0}")

    @_("expression OR  expression",
       "expression AND expression")
    def expression(self, p):
        return Logical(p[1], p.expression0, p.expression1)

    @_("expression PLUS expression",
       "expression MINUS expression",
       "expression TIMES expression" ,
       "expression DIVIDE expression" ,
       "expression MODULE expression" ,
       "expression LT  expression" ,
       "expression LE  expression" ,
       "expression GT  expression" ,
       "expression GE  expression" ,
       "expression EQ  expression" ,
       "expression NE  expression" )
    def expression(self, p):
        return Binary(p[1], p.expression0, p.expression1)

    @_("factor")
    def expression(self, p):
        return p.factor

    @_("NUMBER", "STRING")
    def factor(self, p):
        return Literal(p[0])

    @_("TRUE", "FALSE")
    def factor(self, p):
        return Literal(p[0] == 'true')

    @_("NIL")
    def factor(self, p):
        return Literal(None)

    @_("THIS")
    def factor(self, p):
        return This()

    @_("IDENT")
    def factor(self, p):
        return Variable(p.IDENT)

    @_("SUPER POINT IDENT")
    def factor(self, p):
        return Super(p.IDENT)

    @_("factor POINT IDENT")
    def factor(self, p):
        return Get(p.factor, p.IDENT)

    @_("factor LPAREN [ arguments ] RPAREN ")
    def factor(self, p):
        return Call(p.factor, p.arguments)

    @_(" LPAREN expression RPAREN ")
    def factor(self, p):
        return Grouping(p.expression)

    @_("MINUS factor %prec UNARY",
       "NOT factor %prec UNARY")
    def factor(self, p):
        return Unary(p[0], p.factor)

    @_("IDENT LPAREN [ parameters ] RPAREN block")
    def function(self, p):
        return FuncDeclaration(p.IDENT, p.parameters, p.block)

    @_("IDENT { COMMA IDENT }")
    def parameters(self, p):
        return [ p.IDENT0 ] + p.IDENT1

    @_("expression { COMMA expression }")
    def arguments(self, p):
        return [ p. expression0 ] + p.expression1
    
    @_("MATHFUNC LPAREN expression RPAREN SEMI")
    def factor(self, p):
        return MathFunc(p.name, p.expression)
    

    @_("CONTINUE SEMI")
    def continue_stmt(self, p):
        return Continue(p.name, p.expression)

    @_("BREAK SEMI")
    def break_stmt(self, p):
        return Break(p.name, p.expression)

    #---------------------------------------
    #Incremento y decremento 
    #---------------------------------------
    @_("INC expression")
    def expression(self, p):
        if isinstance(p.expression, Variable):
            return PreInc(p[0], p.expression.name, p.expression)
        else:
            raise SyntaxError(f"{p.expression} error")

    @_("DEC expression")
    def expression(self, p):
        if isinstance(p.expression, Variable):
            return PreDec(p[0], p.expression.name, p.expression)
        else:
            raise SyntaxError(f"{p.expression} error")

    @_("expression INC")
    def expression(self, p):
        if isinstance(p.expression, Variable):
            return PostInc(p[0], p.expression.name, p.expression)
        else:
            raise SyntaxError(f"{p.expression} error")
        

    @_("expression DEC")
    def expression(self, p):
        if isinstance(p.expression, Variable):
            return PostDec(p[0], p.expression.name, p.expression)
        else:
            raise SyntaxError(f"{p.expression} error")

    def error(self, p):
        lineno = p.lineno if p else 'EOF'
        value = repr(p.value) if p else 'EOF'
        if(self.context):
            self.context.error(lineno, f"Error de sintaxis en {value}")
        else:
            print(f"[red]{lineno}: Error de sintaxis en {value}[/red]")

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('Usage: python cparser.py filename')
        exit(0)
        
    txt = open(sys.argv[1], encoding='utf-8').read()
    l   = Lexer()     # Analizador Lexico
    p   = Parser()    # Analizador Sintactico

    ast = p.parse(l.tokenize(txt))
    Checker.check(ast)
    dot = DotRender.render(ast)
    rprint(dot)        
