# mc.py
'''
usage: mc.py [-h] [-d] [-o OUT] [-l] [-D] [-p] [-I] [--sym] [-S] [-R] input

Compiler for MiniC programs

positional arguments:
  input              MiniC program file to compile

optional arguments:
  -h, --help         show this help message and exit
  -d, --debug        Generate assembly with extra information (for debugging purposes)
  -o OUT, --out OUT  File name to store generated executable
  -l, --lex          Store output of lexer
  -D, --dot          Generate AST graph as DOT format
  -p, --png          Generate AST graph as png format
  -I, --ir           Dump the generated Intermediate representation
  --sym              Dump the symbol table
  -S, --asm          Store the generated assembly file
  -R, --exec         Execute the generated program
'''

import argparse
from contextlib import redirect_stdout
from rich import print
from clex import print_lexer
from cparser import print_ast
from context import Context

#Configuracion interface linea de comandos (cli)
#Librerías:
#docopt 0.6.2 
#argopt 0.7.1 pypi
#click  pypi

cli = argparse.ArgumentParser(
    program = 'mc.py',
    description = 'Compiler for minic programs'
)

cli.add_argument(
    'input',
    type=str,
    help='MiniC program file to compile'
)

args = cli.parse_args(['-h'])