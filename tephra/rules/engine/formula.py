"""Tiny safe evaluator for modifier formulas like ``1 + brawl // 6``."""

import ast
import operator

_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv,
}
_FUNCS = {"min": min, "max": max}


class FormulaError(ValueError):
    pass


def var_name(name):
    """Normalize a skill/attribute name to a formula variable (``Bio-Flux`` -> ``bioflux``)."""
    return name.lower().replace("-", "").replace(" ", "_")


def evaluate(expr, variables):
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise FormulaError(f"bad formula {expr!r}") from exc
    return int(_eval(tree.body, variables))


def _eval(node, variables):
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in variables:
            raise FormulaError(f"unknown variable {node.id!r}")
        return variables[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](_eval(node.left, variables), _eval(node.right, variables))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand, variables)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        return _FUNCS[node.func.id](*[_eval(a, variables) for a in node.args])
    raise FormulaError(f"unsupported expression in formula: {ast.dump(node)}")
