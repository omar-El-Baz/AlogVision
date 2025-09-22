# src/utils/ast_utils.py

import ast
import logging
from .loggin_config import setup_logging

setup_logging()

def parse_with_parents(code_string: str) -> ast.Module:
    """
    Parses a code string into an AST and adds parent pointers to each node.
    """
    try:
        tree = ast.parse(code_string)
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        logging.info("AST parsed and parent pointers added successfully.")
        return tree
    except SyntaxError as e:
        logging.error(f"Syntax error in code: {e}")
        raise