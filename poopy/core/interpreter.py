from core.types.number import Number
from core.types.string import String
from core.types.list import List
import core.constant as cc
from core.error import NotDefined, RTError
from core.runtime import RTResult


class Interpreter:
    def visit(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, context):
        NotDefined(None, None, f"{self.method_name} is not defined")

    def visit_NumberNode(self, node, context):
        res = RTResult()
        return res.success(
            Number(node.tok.value)
            .set_context(context)
            .set_pos(pos_start=node.pos_start, pos_end=node.pos_start)
        )

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res
        if node.op_tok.type == cc.TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == cc.TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == cc.TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == cc.TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == cc.TT_POW:
            result, error = left.raised_to(right)
        elif node.op_tok.type == cc.TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == cc.TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == cc.TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == cc.TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == cc.TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == cc.TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(cc.TT_KEYWORD, "AND"):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(cc.TT_KEYWORD, "OR"):
            result, error = left.ored_by(right)
        elif node.op_tok.matches(cc.TT_KEYWORD, "XOR"):
            result, error = left.xored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        error = None

        if node.op_tok.type == cc.TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(cc.TT_KEYWORD, "NOT"):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(
                RTError(
                    node.pos_start, node.pos_end, f"{var_name} is not defined", context
                )
            )

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))

        if res.error:
            return res

        context.symbol_table.set_val(var_name, value)
        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, case, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res

            if condition_value.is_true():
                case_value = res.register(self.visit(case, context))
                if res.error:
                    return res
                return res.success(None if should_return_null else case_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.error:
                return res
            return res.success(None if should_return_null else else_value)

        return res.success(None)

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error:
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error:
            return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))

            if res.error:
                return res
        else:
            step_value = Number(1)

        stepper = start_value.value

        if stepper >= 0:
            condition = lambda: stepper <= end_value.value
        else:
            condition = lambda: stepper >= end_value.value

        while condition():
            context.symbol_table.set_val(node.var_name_tok.value, Number(stepper))
            stepper = stepper + step_value.value

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error:
                return res

        return res.success( 
            None if node.should_return_null else 
            List(elements)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_ProcNode(self, node, context):
        from core.types.procedure import Procedure

        res = RTResult()
        proc_name = node.var_name_tok.value
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        proc_value = (
            Procedure(proc_name, body_node, arg_names, node.should_return_null)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

        if node.var_name_tok:
            context.symbol_table.set_val(proc_name, proc_value)

        return res.success(proc_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))

        if res.error:
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error:
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.error:
            return res
        try:
            return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        except:
            pass
        return res.success(return_value)

    def visit_StringNode(self, node, context):
        res = RTResult()
        return res.success(
            String(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = [
            res.register(self.visit(ele, context)) for ele in node.element_nodes
        ]

        return res.success(
            List(elements)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )


