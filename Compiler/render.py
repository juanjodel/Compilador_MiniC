# render.py
from cast      import *
from graphviz  import Digraph
from rich.text import Text
from rich.tree import Tree

class DotRender(Visitor):

    node_default = {
        'shape' : 'box',
        'color' : 'deepskyblue',
        'style' : 'filled',
    }
    edge_defaults = {
        'arrowhead' : 'none',
    }
    color = 'chartreuse'

    def __init__(self):
        self.dot = Digraph('AST')

        self.dot.attr('node', **self.node_default)
        self.dot.attr('edge', **self.edge_defaults)
        self.program = False
        self.seq = 0
        self.cont=0

    def __repr__(self):
        return self.dot.source

    def __str__(self):
        return self.dot.source


    @classmethod
    def render(cls, model):
        dot = cls()
        model.accept(dot)
        return dot.dot


    def name(self):
        self.seq +=1
        return f'n{self.seq:02d}'

    # nodos de Declaration

    def visit(self, node : ClassDeclaration):
        name = self.name()
        self.dot.node(name, label=f"ClassDeclaration\nname='{node.name}' - {node.sclass}")
        for meth in node.methods:
            self.dot.edge(name, self.visit(self))
        return name

    def visit(self, node : FuncDeclaration):
        name = self.name()
        self.dot.node(name,
            label=f"FuncDeclaration\nname:'{node.name}'\nparams: {node.parameters}",
            color=self.color)
        self.dot.edge(name, self.visit(node.stmts))
        return name

    def visit(self, node : VarDeclaration):
        name = self.name()
        self.dot.node(name,
            label=f"VarDeclaration\nname={node.name}",
            color=self.color)
        if node.expr:
            self.dot.edge(name, self.visit(node.expr), label='init')
        return name

    # Statement

    def visit(self, node : Program):
        name = self.name()
        self.dot.node(name, label="Program", color=self.color)
        for d in node.decl:
            self.dot.edge(name, self.visit(d))
        return name

    def visit(self, node : Print):
        name = self.name()
        self.dot.node(name,
            label='Print',
            color=self.color)
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node : IfStmt):
        name = self.name()
        self.dot.node(name,
            label='IfStmt',
            color=self.color)
        self.dot.edge(name, self.visit(node.cond), label='test')
        if node.cons:
            self.dot.edge(name, self.visit(node.cons), label='then')
        if node.altr:
            self.dot.edge(name, self.visit(node.altr), label='else')
        return name

    def visit(self, node : WhileStmt):
        name = self.name()
        self.dot.node(name,
            label='WhileStmt',
            color=self.color)
        self.dot.edge(name, self.visit(node.cond), label='test')
        self.dot.edge(name, self.visit(node.body), label='body')
        return name

    def visit(self, node : Return):
        name = self.name()
        self.dot.node(name,
            label='Return',
            color=self.color)
        if node.expr:
            self.dot.edge(name, self.visit(node.expr))
        return name

  
    def visit(self, node : ExprStmt):
        name = self.name()
        self.dot.node(name,
            label='ExprStmt',
            color=self.color)
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node : Block):
        name  = self.name()
        label = 'Block'
        if not self.program:
            self.program = True
            label = 'Block'
        else:
            label = str("Block")
        self.dot.node(name,
            label=label,
            color=self.color)
        for stmt in node.stmts:
            self.dot.edge(name, self.visit(stmt))
        return name

    def visit(self, node: Continue):
        name = self.name()
        self.dot.node(name, label=f'Continue {node.name}')
        return name

    def visit(self, node: Break):
        name = self.name()
        self.dot.node(name, label=f'Break {node.name}')
        return name


    # Expression

    def visit(self, node : Literal):
        name = self.name()
        value = node.value
        if node.value is None:
            value = "nil"
        elif node.value is True:
            value = "true"
        elif node.value is False:
            value = "false"
        self.dot.node(name, label=f"Literal\nvalue={value}")
        return name

    def visit(self, node : Binary):
        name = self.name()
        self.dot.node(name, label=f"Binary'{node.op}'")
        self.dot.edge(name, self.visit(node.left))
        self.dot.edge(name, self.visit(node.right))
        return name

    def visit(self, node : Logical):
        name = self.name()
        self.dot.node(name, label=f"Logical'{node.op}'")
        self.dot.edge(name, self.visit(node.left))
        self.dot.edge(name, self.visit(node.right))
        return name

    def visit(self, node: Unary):
        name = self.name()
        self.dot.node(name, label=f'Unary{node.op}')
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node : Grouping):
        name = self.name()
        self.dot.node(name, label='Grouping')
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node : Variable):
        name = self.name()
        self.dot.node(name, label=f"Variable{node.name}")
        return name

    def visit(self, node : Assign):
        name = self.name()
        label = 'Assign' if node.op == '=' else node.op
        self.dot.node(name, label=fr"{label}\nname: '{node.name}'")
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node : Call):
        name = self.name()
        self.dot.node(name, label=f"Call")
        self.dot.edge(name, self.visit(node.func))
        for arg in node.args:
            self.dot.edge(name, self.visit(arg))
        return name

    def visit(self, node : Get):
        name = self.name()
        self.dot.node(name, label='')

        f'(get {self.visit(node.object)} {node.name})'
        return name

    def visit(self, node : Set):
        name = self.name()
        self.dot.node(name, label='')
        f'(set {self.visit(node.object)} {node.name} {self.visit(node.value)})'
        return name

    def visit(self, node : This):
        name = self.name()
        self.dot.node(name, label='this')
        return name

    def visit(self, node : Super):
        name = self.name()
        self.dot.node(name, label=f'super {node.name}')
        return name

    def visit(self, node : List):
        name = self.name()
        self.dot.node(name, label=f'List {node.name}')
        return name

    def visit(self, node: MathFunc):
        name = self.name()
        self.dot.node(name, label=f'math function {node.name}')
        self.dot.edge(name, self.visit(node.name))
        return name

    def visit(self, node : PreDec):
        name = self.name()
        self.dot.node(name, label='PreDec')
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node : PostDec):
        name = self.name()
        self.dot.node(name, label='PostDec')
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node : PreInc):
        name = self.name()
        self.dot.node(name, label='PreInc')
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node : PostInc):
        name = self.name()
        self.dot.node(name, label='PostInc')
        self.dot.edge(name, self.visit(node.expr))
        return name

    


class TreeRender(Visitor):

    @classmethod
    def render(cls, model):
        dot = cls()
        model.accept(dot)
        return dot.dot

    # nodos de Declaration

    def visit(self, node: ClassDeclaration, tree: Tree):
        pass

    def visit(self, node: FuncDeclaration, tree: Tree):
        pass

    def visit(self, node: VarDeclaration):
        pass

    # Statement

    def visit(self, node: Print):
        pass

    def visit(self, node: IfStmt, tree: Tree):
        pass

    def visit(self, node: WhileStmt, tree: Tree):
        pass

    def visit(self, node: Return, tree: Tree):
        pass

    def visit(self, node: ExprStmt, tree: Tree):
        pass

    def visit(self, node: Block, tree: Tree):
        pass
    
    def visit(self, node: Continue, tree: Tree):
        pass

    def visit(self, node: Break, tree: Tree):
        pass
    # Expression

    def visit(self, node: Literal, tree: Tree):
        pass

    def visit(self, node: Binary, tree: Tree):
        pass

    def visit(self, node: Logical, tree: Tree):
        pass

    def visit(self, node: Unary, tree: Tree):
        pass

    def visit(self, node: Grouping, tree: Tree):
        pass

    def visit(self, node: Variable, tree: Tree):
        pass

    def visit(self, node: Assign, tree: Tree):
        pass

    def visit(self, node: Call, tree: Tree):
        pass

    def visit(self, node: Get, tree: Tree):
        pass
        
    def visit(self, node: Set, tree: Tree):
        pass

    def visit(self, node: This, tree: Tree):
        pass
        
    def visit(self, node: Super, tree: Tree):
        pass

    def visit(self, node: List, tree: Tree):
        pass

    def visit(self, node: PreDec, tree: Tree):
        pass

    def visit(self, node: PostDec, tree: Tree):
        pass
        
    def visit(self, node: PreInc, tree: Tree):
        pass

    def visit(self, node: PostInc, tree: Tree):
        pass
    def visit(self, node: MathFunc, tree: Tree):
        pass