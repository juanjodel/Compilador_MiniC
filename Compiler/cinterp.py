# conterp.py
'''
Tree-walking interpreter
'''
from collections import ChainMap
from cast import *
from checker import Checker
import math
import time

# Veracidad en MiniC 
def _is_truthy(value):
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    else:
        return True

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
	def __init__(self, *args: object) -> None:
		super().__init__(*args)

class MiniCExit(BaseException):
    pass

class CallError(Exception):
    pass

class AttributeError(Exception):
    pass

class Function:
    def __init__(self, node, env):
        self.node = node
        self.env = env

    def __call__(self, interp, *args):
        if len(args) != len(self.node.params):
            raise CallError(f"Experado {len(self.node.params)} argumentos")
        newenv = self.env.new_child()
        for name, arg in zip(self.node.params, args):
            newenv[name] = arg
        
        oldenv = interp.env
        interp.env = newenv
        try:
            interp.visit(self.node.stmts)
            result = None
        except ReturnException as e:
            result = e.value
        finally:
            interp.env = oldenv
        return result

    def bind(self, instance):
        env = self.env.new_child()
        env['this'] = instance
        return Function(self.node, env)


class Class:
    def __init__(self, name, sclass, methods):
        self.name = name
        self.sclass = sclass
        self.methods = methods

    def __str__(self):
        return self.name

    def __call__(self, *args):
        this = Instance(self)
        init = self.find_method('init')
        if init:
            init.bind(this)(*args)
        return this

    def find_method(self, name):
        meth = self.methods.get(name)
        if meth is None and self.sclass:
            return self.sclass.find_method(name)
        return meth

class Instance:
    def __init__(self, klass):
        self.klass = klass
        self.data = { }

    def __str__(self):
        return self.klass.name + " instance"

    def get(self, name):
        if name in self.data:
            return self.data[name]
        method = self.klass.find_method(name)
        if not method:
            raise AttributeError(f'Propiedad indefinida {name}')
        return method.bind(self)

    def set(self, name, value):
        self.data[name] = value


class Interpreter(Visitor):

    def __init__(self, ctxt):
        self.ctxt = ctxt
        self.env  = ChainMap()
        self.check_env = ChainMap()
        self.localmap  = { }
        
        for name, func in self.builtins.items():
            self.check_env[name] = func

    def _check_numeric_operands(self, node, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True
        else:
            self.error(node, f"En '{node.op}' los operandos deben ser numeros")

    def _check_numeric_operand(self, node, value):
        if isinstance(value, (int, float)):
            return True
        else:
            self.error(node, f"En '{node.op}' el operando debe ser un numero")

    def error(self, position, message):
        self.ctxt.error(position, message)
        raise MiniCExit()
    
    # Punto de entrada alto-nivel
    def interpret(self, node):
        try:
            Checker.check(node, self.check_env, self)
            if not self.ctxt.have_errors:
                self.visit(node)
        except MiniCExit as e:
            pass

    def visit(self, node: Block):
        self.env = self.env.new_child()
        for stmt in node.stmts:
            self.visit(stmt)
        self.env = self.env.parents

    def visit(self, node: Program):
		#self.env = self.env.new_child()
        for d in node.decl:
            self.visit(d)
		#self.env = self.env.parents

    def visit(self, node: ClassDeclaration):
        if node.sclass:
            sclass = self.visit(node.sclass)
            env = self.env.new_child()
            env['super'] = sclass
        else:
            sclass = None
            env = self.env
        methods = { }
        for meth in node.methods:
            methods[meth.name] = Function(meth, env)
        cls = Class(node.name, sclass, methods)
        self.env[node.name] = cls
        
        
    def visit(self, node: FuncDeclaration):
        func = Function(node, self.env)
        self.env[node.name] = func

    def visit(self, node: VarDeclaration):
        if node.expr:
            expr = self.visit(node.expr)
        else:
            expr = None
        self.env[node.name] = expr

    def visit(self, node: Print):
        print(self.visit(node.expr))
        
    def visit(self, node: WhileStmt):
        while _is_truthy(self.visit(node.test)):
            self.visit(node.body)

    def visit(self, node: IfStmt):
        test = self.visit(node.test)
        if _is_truthy(test):
            self.visit(node.cons)
        elif node.altr:
            self.visit(node.altr)
            
    def visit(self, node: Continue):
        num = list(self.env.maps[0])
        self.env[num[0]] += 1
    
    def visit(self, node: Break):
        return BreakException

    def visit(self, node: Return):
        # Ojo: node.expr es opcional
        raise ReturnException(self.visit(node.expr))

    def visit(self, node: ExprStmt):
        self.visit(node.expr)

    def visit(self, node: Literal):
        return node.value

    def visit(self, node: Binary):
        left  = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+':
            (isinstance(left, str) and isinstance(right, str)) or self._check_numeric_operands(node, left, right)
            return left + right
        elif node.op == '-':
            self._check_numeric_operands(node, left, right)
            return left - right
        elif node.op == '*':
            self._check_numeric_operands(node, left, right)            
            return left * right
        elif node.op == '/':
            self._check_numeric_operands(node, left, right)
            return left / right
        elif node.op == '%':
            self._check_numeric_operands(node, left, right)
            return left % right
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '<':
            self._check_numeric_operands(node, left, right)
            return left < right
        elif node.op == '>':
            self._check_numeric_operands(node, left, right)
            return left > right
        elif node.op == '<=':
            self._check_numeric_operands(node, left, right)
            return left <= right
        elif node.op == '>=':
            self._check_numeric_operands(node, left, right)
            return left >= right
        else:
            raise NotImplementedError(f"Mal operador {node.op}")
        
    def visit(self, node: Logical):
        left = self.visit(node.left)
        if node.op == '||':
            return left if _is_truthy(left) else self.visit(node.right)
        if node.op == '&&':
            return self.visit(node.right) if _is_truthy(left) else left
        raise NotImplementedError(f"Mal operador {node.op}")
        
    def visit(self, node: Unary):
        expr = self.visit(node.expr)
        if node.op == "-":
            self._check_numeric_operand(node, expr)
            return - expr
        elif node.op == "!":
            return not _is_truthy(expr)
        else:
            raise NotImplementedError(f"Mal operador {node.op}")

    def visit(self, node: Grouping):
        return self.visit(node.expr)

    def visit(self, node: Assign):
        operation_name = node.op
        expr = self.visit(node.expr)
        if node.op == '=':
            self.env.maps[self.localmap[id(node)]][node.name] = expr
        elif node.op == '+=':
            self.env.maps[self.localmap[id(node)]][node.name] += expr
        elif node.op == '-=':
            self.env.maps[self.localmap[id(node)]][node.name] -= expr
        elif node.op == '*=':
            self.env.maps[self.localmap[id(node)]][node.name] *= expr
        elif node.op == '/=':
            self.env.maps[self.localmap[id(node)]][node.name] /= expr
        elif node.op == '%=':
            self.env.maps[self.localmap[id(node)]][node.name] %= expr

    def visit(self, node: PreInc):
        exp = self.visit(node.expr)
        exp = exp + 1
        self.env[node.name] = exp
        return exp

    def visit(self, node: PreDec):
        exp = self.visit(node.expr)
        exp = exp - 1
        self.env[node.name] = exp
        return exp

    def visit(self, node: PostInc):
        exp = self.visit(node.expr)
        exp = exp + 1
        self.env[node.name] = exp
        return self.visit(node.expr)

    def visit(self, node: PostDec):
        exp = self.visit(node.expr)
        exp = exp - 1
        self.env[node.name] = exp
        return self.visit(node.expr)

    def visit(self, node: MathFunc):
        value = self.visit(node.value) 
        fun = node.name
        if fun == 'sin':
            self.env[node.name] = math.sin(value)
        elif fun == 'cos':
            self.env[node.name] = math.cos(value)
        elif fun == 'tan':
            self.env[node.name] = math.tan(value)
        elif fun == 'sqrt':
            self.env[node.name] = math.sqrt(value)
        elif fun == 'floor':
            self.env[node.name] = math.floor(value)
        elif fun == 'ceil':
            self.env[node.name] = math.ceil(value)
        elif fun == 'atan':
            self.env[node.name] = math.atan(value)
        elif fun == 'asin':
            self.env[node.name] = math.asin(value)
        elif fun == 'acos':
            self.env[node.name] = math.acos(value)
        elif fun == 'sinh':
            self.env[node.name] = math.sinh(value)
        elif fun == 'cosh':
            self.env[node.name] = math.cosh(value)
        elif fun == 'tanh':
            self.env[node.name] = math.tanh(value)
        elif fun == 'log':
            self.env[node.name] = math.log(value)
        elif fun == 'log10':
            self.env[node.name] = math.log10(value)
        elif fun == 'exp':
            self.env[node.name] = math.exp(value)
        elif fun == 'gra':
            self.env[node.name] = math.degrees(value)
        elif fun == 'deg':
            self.env[node.name] = math.radians(value)
        elif fun == 'isqrt':
            self.env[node.name] = math.isqrt(value)
        elif fun == 'abs':
            self.env[node.name] = abs(value)
        elif fun == 'e':
            self.env[node.name] = math.e
        elif fun == 'pi':
            self.env[node.name] = math.pi
        elif fun == 'gamma':
            self.env[node.name] = 0.5772
        elif fun == 'g':
            self.env[node.name] = 9.8
        elif fun == 'planck':
            self.env[node.name] = 1.054
        elif fun == 'avogadro':
            self.env[node.name] =  6.022
        elif fun == 'epsilon':
            self.env[node.name] =  8.854187817
        elif fun == 'pow':
            self.env[node.name] = math.pow(value,2)
        elif fun == 'len':
            self.env[node.name] = len(value)
        elif fun == 'clock':
            self.env[node.name] = time.clock()
        
        
    def visit(self, node: Call):
        callee = self.visit(node.func)
        if not callable(callee):
            self.error(node.func, f'{self.ctxt.find_source(node.func)!r} no es invocable')

        args = [ self.visit(arg) for arg in node.args ]
        try:
            return callee(self, *args)
        except CallError as err:
            self.error(node.func, str(err))

    def visit(self, node: Variable):
        return self.env.maps[self.localmap[id(node)]][node.name]
        
    def visit(self, node: Set):
        obj = self.visit(node.object)
        val = self.visit(node.value)
        if isinstance(obj, Instance):
            obj.set(node.name, val)
            return val
        else:
            self.error(node.object, f'{self.ctxt.find_source(node.object)!r} no es una instancia')
        
    def visit(self, node: Get):
        obj = self.visit(node.object)
        if isinstance(obj, Instance):
            try:
                return obj.get(node.name)
            except AttributeError as err:
                self.error(node.object, str(err))
        else:
            self.error(node.object, f'{self.ctxt.find_source(node.object)!r} no es una instancia')
        
    def visit(self, node: This):
        return self.env.maps[self.localmap[id(node)]]['this']
        
    def visit(self, node: Super):
        distance = self.localmap[id(node)]
        sclass = self.env.maps[distance]['super']
        this = self.env.maps[distance-1]['this']
        method = sclass.find_method(node.name)
        if not method:
            self.error(node.object, f'Propiedad indefinida {node.name!r}')
        return method.bind(this)


