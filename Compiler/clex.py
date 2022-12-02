import sly
from rich import print

# Definición Analizador Léxico
class Lexer(sly.Lexer):

    # Definición de Símbolos
    tokens = {
        FUN, VAR, PRINT, IF, ELSE, WHILE, RETURN, TRUE, FALSE,
        CLASS, FOR, WHILE, NIL, THIS, SUPER,
        PLUS, MINUS, TIMES, DIVIDE, POINT, SEMI, COMMA,
        LPAREN, RPAREN, LBRACE, RBRACE,
        LT, LE, GT, GE,EQ, NE, AND, OR, NOT,
        ASSIGN, MODULE,
        LSQBRA, RSQBRA,
        IDENT, NUMBER, 
        ADDEQ, LESSEQ, TIMESEQ, DIVIDEQ, MODULEQ,
        INC, DEC,
        BREAK, CONTINUE,
        LEN, INPUT, ISINTEGER, MATHFUNC,
        SIN, COS, TAN, ATAN, ASIN, ACOS, SINH, COSH , 
        TANH,SQRT, E, PI,DEG,GRA, GAMMA, EPSILON,  G, H, NA,  
        CLOCK, INPUT,LOG, LOG10,
        FORMAT, LOG, LOG10, SQRT, EXP, ABS, GAMMA,
        FLOOR,CEIL, ISQRT, POW 


    }
    
    literals = '+-*/%=(){}[];,'

    # Ignoramos espacios en blanco (white-space)
    ignore = ' \t\r'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'/\*(.|\n)*\*/')
    def ignore_comments(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*\n')
    def ignore_cppcomments(self, t):
        self.lineno += 1

    # Definicion de Tokens a traves de regexp

    #-----------------------------------------
    #deficion de simbolos ++ -- 
    #-----------------------------------------
    INC     = r'\+\+'
    DEC     = r'--'
    ADDEQ   = r'\+='
    LESSEQ  = r'-='
    TIMESEQ = r'\*='
    DIVIDEQ = r'/='
    MODULEQ = r'%='
    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'
    POINT   = r'\.'
    SEMI    = r';'
    COMMA   = r','
    LPAREN  = r'\('
    RPAREN  = r'\)'
    LBRACE  = r'{'
    RBRACE  = r'}'
    LSQBRA  = r'\['
    RSQBRA  = r'\]'
    LE      = r'<='
    LT      = r'<'
    GE      = r'>='
    GT      = r'>'
    EQ      = r'=='
    NE      = r'!='
    AND     = r'&&'
    OR      = r'\|\|'
    NOT     = r'!'
    ASSIGN  = r'='
    MODULE  = r'%'

    

    IDENT = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENT['fun']        = FUN
    IDENT['var']        = VAR
    IDENT['print']      = PRINT
    IDENT['if']         = IF
    IDENT['else']       = ELSE
    IDENT['while']      = WHILE
    IDENT['return']     = RETURN
    IDENT['true']       = TRUE
    IDENT['false']      = FALSE
    IDENT['class']      = CLASS
    IDENT['for']        = FOR
    IDENT['while']      = WHILE
    IDENT['true']       = TRUE
    IDENT['nil']        = NIL
    IDENT['this']       = THIS
    IDENT['super']      = SUPER
    IDENT['break']      = BREAK
    IDENT['continue']   = CONTINUE
    IDENT['clock']      = MATHFUNC
    IDENT['len']        = MATHFUNC
    IDENT['input']      = INPUT
    IDENT['isinteger']  = ISINTEGER
    IDENT['sin']        = MATHFUNC
    IDENT['cos']        = MATHFUNC
    IDENT['tan']        = MATHFUNC
    IDENT['asin']       = MATHFUNC
    IDENT['acos']       = MATHFUNC
    IDENT['atan']       = MATHFUNC
    IDENT['sinh']       = MATHFUNC
    IDENT['cosh']       = MATHFUNC
    IDENT['tanh']       = MATHFUNC
    IDENT['sqrt']       = MATHFUNC
    IDENT['deg']        = MATHFUNC
    IDENT['gra']        = MATHFUNC
    IDENT['log']        = MATHFUNC
    IDENT['log10']      = MATHFUNC
    IDENT['floor']      = MATHFUNC
    IDENT['ceil']       = MATHFUNC
    IDENT['exp']        = MATHFUNC
    IDENT['abs']        = MATHFUNC
    IDENT['isqrt']      = MATHFUNC
    IDENT['pi']         = MATHFUNC
    IDENT['e']          = MATHFUNC
    IDENT['gamma']      = MATHFUNC
    IDENT['epsilon']    = MATHFUNC
    IDENT['g']          = MATHFUNC
    IDENT['planck']     = MATHFUNC
    IDENT['avogadro']   = MATHFUNC
    IDENT['absoluto']   = MATHFUNC
    IDENT['pow']        = MATHFUNC
    IDENT['number']     = NUMBER
    



    @_(r'".*"')
    def STRING(self, t):
        t.value = str(t.value)
        return t

    @_(r'\d*\.\d+|\d+\.?')
    def NUMBER(self, t):
        try:
            t.value = int(t.value)
        except ValueError:
            t.value = float(t.value)
        return t

    def error(self, t):
        print(f"Se encontró en la linea {self.lineno} un caracter ilegal '{t.value[0]}'")
        self.index += 1

