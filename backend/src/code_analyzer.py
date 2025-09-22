import ast
from.utils.ast_utils import parse_with_parents

# Defining a more comprehensive mapping for statement types
# These are the AST nodes that represent distinct operations or structures on a line
STATEMENT_NODE_TYPE_MAP = {
    ast.FunctionDef: "Function Definition",
    ast.AsyncFunctionDef: "Async Function Definition",
    ast.ClassDef: "Class Definition",
    ast.Return: "Return Statement",
    ast.Assign: "Assignment",
    ast.AugAssign: "Augmented Assignment (e.g., +=)",
    ast.AnnAssign: "Annotated Assignment",
    ast.For: "For Loop",
    ast.While: "While Loop",
    ast.If: "Conditional (if/elif)",
    ast.With: "Context Manager (with)",
    ast.Raise: "Raise Exception",
    ast.Try: "Try-Except Block",
    ast.Expr: "Expression Statement", 
    ast.Import: "Import Statement",
    ast.ImportFrom: "Import From Statement",
    ast.Delete: "Delete Statement",
    ast.Assert: "Assert Statement",
    ast.Break: "Break Statement",
    ast.Continue: "Continue Statement",
    ast.Pass: "Pass Statement",
    ast.Global: "Global Statement",
    ast.Nonlocal: "Nonlocal Statement",
    
}


class CodeAnalyzer(ast.NodeVisitor):
    """
    Analyzes a Python code string to extract its structure at multiple levels.
    """
    def __init__(self, code_string: str):
        self.code_string = code_string
        self.tree = parse_with_parents(code_string)
        self.lines = code_string.splitlines() # Store lines once for efficiency
        self.analysis = {
            "high_level_summary": {},
            "functions": {},
            "line_by_line": [] # This will be a list of dicts for each significant line
        }
        
        
        self._temp_line_data = {} 
        for i, line_content in enumerate(self.lines, 1):
            stripped_line = line_content.strip()
            # Only consider non-empty, non-comment lines for detailed analysis
            if stripped_line and not stripped_line.startswith('#'):
                self._temp_line_data[i] = {
                    "line_number": i,
                    "content": stripped_line,
                    "types": []
                }

    def analyze(self):
        """Runs the complete multi-level analysis."""
        self._analyze_high_level()
        self.visit(self.tree) # This will trigger visit_FunctionDef and generic_visit
        self._finalize_line_by_line() # Process the collected line data
        return self.analysis

    def _analyze_high_level(self):
        """Analyzes the overall structure, imports, and classes."""
        imports = [node.names[0].name for node in ast.walk(self.tree) if isinstance(node, ast.Import)]
        from_imports = [f"{node.module}.{node.names[0].name}" for node in ast.walk(self.tree) if isinstance(node, ast.ImportFrom)]
        classes = [node.name for node in ast.walk(self.tree) if isinstance(node, ast.ClassDef)]
        
        self.analysis["high_level_summary"] = {
            "imports": imports + from_imports,
            "class_definitions": classes,
            "total_functions": len([n for n in ast.walk(self.tree) if isinstance(n, ast.FunctionDef)]),
            "total_lines": len(self.code_string.splitlines())
        }

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyzes a single function's properties."""
        function_name = node.name
        dependencies = {
            "calls": [],
            "uses_variables": set()
        }
        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Call) and isinstance(sub_node.func, ast.Name):
                dependencies["calls"].append(sub_node.func.id)
            if isinstance(sub_node, ast.Name) and isinstance(sub_node.ctx, ast.Load):
                dependencies["uses_variables"].add(sub_node.id)

        self.analysis["functions"][function_name] = {
            "parameters": [arg.arg for arg in node.args.args],
            "return_statements": len([n for n in ast.walk(node) if isinstance(n, ast.Return)]),
            "start_line": node.lineno,
            "dependencies": {
                "calls": list(set(dependencies["calls"])),
                "uses_variables": list(dependencies["uses_variables"])
            }
        }
        # Continue visiting children for line-by-line analysis
        self.generic_visit(node) 

    def generic_visit(self, node: ast.AST):
        """
        Custom generic_visit to capture statement types for each line.
        This method is called for all nodes that don't have a specific 'visit_X' method.
        """
        node_type_name = STATEMENT_NODE_TYPE_MAP.get(type(node))
        
        if node_type_name:
            start_line = node.lineno
            end_line = getattr(node, 'end_lineno', start_line) 

            # Associate this node's type with all lines it spans
            for i in range(start_line, end_line + 1):
                if i in self._temp_line_data and node_type_name not in self._temp_line_data[i]["types"]:
                    self._temp_line_data[i]["types"].append(node_type_name)
        
        # Ensure that children of the current node are also visited
        super().generic_visit(node)

    def _finalize_line_by_line(self):
        """
        Sorts the collected line data and defaults types for any lines
        that didn't get a specific AST node type.
        """
        # Convert dictionary to a sorted list
        sorted_line_data = sorted(self._temp_line_data.values(), key=lambda x: x["line_number"])
        
        
        for detail in sorted_line_data:
            if not detail["types"]:
                detail["types"].append("Code") 
        
        self.analysis["line_by_line"] = sorted_line_data


if __name__ == '__main__':
    sample_code = """
import pandas as pd

class DataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        df = pd.DataFrame(self.data)
        self.cleaned = self.clean_data(df)
        return self.cleaned

    def clean_data(self, df):
        # Drop rows with any missing values
        df = df.dropna()
        if df.empty:
            print("Warning: DataFrame is empty after cleaning.")
        return df

num1 = 10
num2 = 20
if num1 > num2:
    print("Num1 is greater")
else:
    print("Num2 is greater or equal")
"""
    analyzer = CodeAnalyzer(sample_code)
    analysis_result = analyzer.analyze()

    import json
    print(json.dumps(analysis_result, indent=2))