import core.constant as cc
from core.nodes import (
    NumberNode,
    BinOpNode,
    UnaryOpNode,
    VarAssignNode,
    VarAccessNode,
    IfNode,
    ForNode,
    ProcNode,
    CallNode,
    StringNode,
    ListNode,
)
from core.error import InvalidSyntaxError, FeatureInProgress

class ParseResult:
    """to add errors if any to Parser this would link to the Error class"""

    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error

        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def reverse(self, rev_amount = 1):
        self.tok_idx -= rev_amount
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.stmts()
        if not res.error and self.current_tok.value in cc.WORK_IN_PROGRESS:
            return res.failure(
                FeatureInProgress(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Will shortly be available for you ;)",
                )
            )
        if not res.error and self.current_tok.type not in (
            cc.TT_EOF,
            # cc.TT_RPAREN,
        ): 
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected '+', '-', '*', or '/'",
                )
            )
        return res

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (cc.TT_INT, cc.TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == cc.TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.type == cc.TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == cc.TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == cc.TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ')'",
                    )
                )

        elif tok.type == cc.TT_LCURLY:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)
            
        elif tok.matches(cc.TT_KEYWORD, "IF"):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(cc.TT_KEYWORD, "LOOP"):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(cc.TT_KEYWORD, "PROC"):
            proc_def = res.register(self.proc_def())
            if res.error:
                return res
            return res.success(proc_def)

        res.failure(
            InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-',or '('",
            )
        )

    def power(self):
        return self.bin_op(self.call, (cc.TT_POW), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())

        if res.error:
            return res

        if self.current_tok.type == cc.TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == cc.TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected ')', 'BUCKET', int, float, identifier",
                        )
                    )

                while self.current_tok.type == cc.TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))

                    if res.error:
                        return res

                if self.current_tok.type != cc.TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()

            return res.success(CallNode(atom, arg_nodes))

        return res.success(atom)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (cc.TT_PLUS, cc.TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())

            if res.error:
                return res

            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (cc.TT_MUL, cc.TT_DIV))

    def stmts(self):  # sourcery skip
        res = ParseResult()
        stmts = []
        pos_start = self.current_tok.pos_start.copy()
        while self.current_tok.type == cc.TT_NEWLINE:
            res.register_advancement()
            self.advance()
        
        stmt = res.register(self.expr())
        if res.error:
            return res
        stmts.append(stmt)

        more_stmts = True

        while True:
            newline_count = 0
            while self.current_tok.type == cc.TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count +=1
            
            if newline_count == 0:
                more_stmts = False

            if not more_stmts:
                break

            stmt = res.try_register(self.expr())
            if not stmt:
                self.reverse(res.to_reverse_count)
                more_stmts = False
                continue
            stmts.append(stmt)
        return res.success(ListNode(stmts, pos_start, self.current_tok.pos_end.copy()))

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(cc.TT_KEYWORD, "BUCKET"):
            res.register_advancement()
            self.advance()
            if self.current_tok.type != cc.TT_IDENTIFIER:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected 'identifier'",
                    )
                )

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != cc.TT_EQ:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '='",
                    )
                )

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())

            if res.error:
                return res

            return res.success(VarAssignNode(var_name, expr))

        node = res.register(
            self.bin_op(
                self.comp_expr,
                ((cc.TT_KEYWORD, "AND"), (cc.TT_KEYWORD, "OR"), (cc.TT_KEYWORD, "XOR")),
            )
        )

        if res.error:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'BUCKET', int, float, identifier, '+', '-', 'NOT',or '('",
                )
            )

        return res.success(node)

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()
        
        if self.current_tok.type != cc.TT_LCURLY:
            return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '{'",
                    )
                )
        res.register_advancement()
        self.advance()

        if self.current_tok.type == cc.TT_RCURLY:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '}', 'BUCKET', int, float, identifier",
                    )
                )

            while self.current_tok.type == cc.TT_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))

                if res.error:
                    return res

            if self.current_tok.type != cc.TT_RCURLY:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ',' or '}'",
                    )
                )
            res.register_advancement()
            self.advance()

        return res.success(ListNode(element_nodes, pos_start, self.current_tok.pos_end.copy()))

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(cc.TT_KEYWORD, "NOT"):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(
            self.bin_op(
                self.arth_expr,
                (cc.TT_EE, cc.TT_NE, cc.TT_GT, cc.TT_GTE, cc.TT_LT, cc.TT_LTE),
            )
        )

        if res.error:
            res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected int, float, identifier, '+', '-','NOT', '('",
                )
            )

        return res.success(node)

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases("IF"))

        if res.error: return res
        cases, else_case = all_cases

        return res.success(IfNode(cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(cc.TT_KEYWORD, case_keyword):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected '{case_keyword}'",
                )
            )
        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(cc.TT_KEYWORD, "THEN"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'THEN'",
                )
            )

        res.register_advancement()
        self.advance()

        #newline in if cases
        if self.current_tok.type == cc.TT_NEWLINE:
            res.register_advancement()
            self.advance()

            stmts = res.register(self.stmts())  # append to cases list
            if res.error:
                return res
            cases.append((condition, stmts, True))

            if self.current_tok.matches(cc.TT_KEYWORD, "END"):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: 
                    return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.expr())
            if res.error: 
                return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: 
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases("ALTER")

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(cc.TT_KEYWORD, "ELSE"):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == cc.TT_NEWLINE:
                res.register_advancement()
                self.advance()

                stmts = res.register(self.stmts())

                if res.error:
                    return res

                else_case = (stmts, True)

                if not self.current_tok.matches(cc.TT_KEYWORD, "END"):
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected 'THEN'",
                        )
                    )

                res.register_advancement()
                self.advance()
            else:
                expr = res.register(self.expr())
                if res.error:
                    return res
                else_case = (expr, False)

        return res.success(else_case)
    
    def if_expr_b_or_c(self):
        res = ParseResult()

        cases = []
        else_case = None

        if self.current_tok.matches(cc.TT_KEYWORD, "ALTER"):
            all_cases = res.register(self.if_expr_b())

            if res.error: 
                return res
            
            cases, else_case = all_cases

        else:
            else_case = res.register(self.if_expr_c())

            if res.error: return res
        
        return res.success((cases, else_case))


    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(cc.TT_KEYWORD, "LOOP"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'LOOP'",
                )
            )
        res.register_advancement()
        self.advance()

        if self.current_tok.type != cc.TT_IDENTIFIER:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'identifier'",
                )
            )

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != cc.TT_EQ:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected '='",
                )
            )

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(cc.TT_KEYWORD, "TILL"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'TILL'",
                )
            )
        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(cc.TT_KEYWORD, "STEP"):
            res.register_advancement()
            self.advance()
            step_value = res.register(self.expr())
        else:
            step_value = None

        if not self.current_tok.matches(cc.TT_KEYWORD, "DO"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'DO'",
                )
            )
        res.register_advancement()
        self.advance()

        #newline in loop
        if self.current_tok.type == cc.TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.stmts())
            if res.error:
                return res

            if not self.current_tok.matches(cc.TT_KEYWORD, "END"):
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected 'THEN'",
                    )
                )

            res.register_advancement()
            self.advance()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))
        
        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def arth_expr(self):
        return self.bin_op(self.term, (cc.TT_PLUS, cc.TT_MINUS))

    def proc_def(self):
        res = ParseResult()
        if not self.current_tok.matches(cc.TT_KEYWORD, "PROC"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'PROC'",
                )
            )
        res.register_advancement()
        self.advance()
        if self.current_tok.type == cc.TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != cc.TT_LPAREN:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '('",
                    )
                )
        else:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'identifier'",
                )
            )

        res.register_advancement()
        self.advance()

        arg_name_tok = []
        if self.current_tok.type == cc.TT_IDENTIFIER:
            arg_name_tok.append(self.current_tok)
            res.register_advancement()
            self.advance()
            while self.current_tok.type == cc.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_tok.type != cc.TT_IDENTIFIER:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected 'identifier'",
                        )
                    )

                arg_name_tok.append(self.current_tok)
                res.register_advancement()
                self.advance()
            if self.current_tok.type != cc.TT_RPAREN:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ')'",
                    )
                )
        else:
            if self.current_tok.type != cc.TT_RPAREN:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected identifier or ')'",
                    )
                )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == cc.TT_COLON:
            res.register_advancement()
            self.advance()
            node_to_return = res.register(self.expr())
            if res.error:
                return res

            return res.success(ProcNode(var_name_tok, arg_name_tok, node_to_return, False))

        if self.current_tok.type != cc.TT_NEWLINE:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ':' or NEWLINE",
                    )
                )

        res.register_advancement()
        self.advance()

        body = res.register(self.stmts())
        if res.error:
            return res

        if not self.current_tok.matches(cc.TT_KEYWORD, "END"):
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected 'THEN'",
                    )
                )

        res.register_advancement()
        self.advance()

        return res.success(ProcNode(var_name_tok, arg_name_tok, body, True))

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res
        # TODO: Ops Operation as TUPLE - Breaking my head over below line in ep5
        # while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
