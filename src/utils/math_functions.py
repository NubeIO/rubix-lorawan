import ast
import math
import operator as op


operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.FloorDiv: op.floordiv,
             ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg, ast.UAdd: op.pos}


def eval_arithmetic_expression(expression: str):
    """
    >>> eval_arithmetic_expression('15+2')
    17
    >>> eval_arithmetic_expression('15-2')
    13
    >>> eval_arithmetic_expression('15*2')
    30
    >>> eval_arithmetic_expression('15/2')
    7.5
    >>> eval_arithmetic_expression('15//2')
    7
    >>> eval_arithmetic_expression('15**2')
    225
    >>> eval_arithmetic_expression('15%2')
    1
    >>> eval_arithmetic_expression('-15+2')
    13
    >>> eval_arithmetic_expression('+15-2')
    13
    """
    return __eval(ast.parse(expression, mode='eval').body)


def __eval(node):
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return operators[type(node.op)](__eval(node.left), __eval(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return operators[type(node.op)](__eval(node.operand))
    else:
        raise TypeError(node)


# def micro_edge_point_config(value, sensor_type):
#     """
#     Example for TEMP,  543 = 22.08 for 10K
#     :param value:
#     :param sensor_type:
#     :return: float
#     """
#     if sensor_type == MicroEdgeConfig.TEMP:
#         Vref = 3.34
#         V = (value / 1024) * Vref
#         R0 = 10000
#         R = (R0 * V) / (Vref - V)
#         T0 = 273 + 25
#         B = 3850
#         T = 1 / (1 / T0 + (1 / B) * math.log(R / R0))
#         output = T - 273.15
#     elif sensor_type == MicroEdgeConfig.VOLTAGE:
#         output = (value / 1024) * 10
#     elif sensor_type == MicroEdgeConfig.DIGITAL:
#         if value is None or value >= 1000:
#             output = 0
#         else:
#             output = 1
#     else:
#         output = value
#     return output
