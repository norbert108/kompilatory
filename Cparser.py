from scanner import Scanner
import ast


class Cparser(object):
    def __init__(self):
        self.scanner = Scanner()

    tokens = Scanner.tokens

    precedence = (
        ("nonassoc", 'IFX'),
        ("nonassoc", 'ELSE'),
        ("right", '='),
        ("left", 'OR'),
        ("left", 'AND'),
        ("left", '|'),
        ("left", '^'),
        ("left", '&'),
        ("nonassoc", '<', '>', 'EQ', 'NEQ', 'LE', 'GE'),
        ("left", 'SHL', 'SHR'),
        ("left", '+', '-'),
        ("left", '*', '/', '%'),
    )

    # check const type
    def is_int(self, arg):
        print "isiint {0}".format(arg)
        try:
            int(arg)
        except (ValueError, TypeError) as e:
            print e
            print "ni  chuja"
            return False
        print "taaa"
        return True

    def is_float(self, arg):
        try:
            float(arg)
        except (ValueError, TypeError):
            return False
        return True

    # error catching rule
    def p_error(self, p):
        if p:
            print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')"
                  .format(p.lineno, self.scanner.find_tok_column(p), p.type, p.value))
        else:
            print('At end of input')

    start = 'program'

    # root
    def p_program(self, p):
        """program : declarations fundefs instructions"""
        p[0] = ast.Program(p[1], p[2], p[3])

    # declarations
    def p_declarations(self, p):
        """declarations : declarations declaration
                        | """
        if len(p) == 1:  # if declarations is epsilon production
            p[0] = ast.Declarations()
        else:
            p[0] = ast.Declarations(p[1], p[2])

    def p_declaration(self, p):
        """declaration : TYPE inits ';'
                       | error ';' """
        if len(p) > 2:
            p[0] = ast.Declaration(type=p[1], inits=p[2])
        else:
            p[0] = ast.Declaration(error=p[1])

    def p_inits(self, p):
        """inits : inits ',' init
                 | init """
        if len(p) > 2:
            p[0] = ast.Inits(inits=p[1], init=p[3])
        else:
            p[0] = ast.Inits(init=p[1])

    def p_init(self, p):
        """init : ID '=' expression
                | ID """
        if len(p) == 2:
            p[0] = ast.Init(id=p[1], line_no=p.lineno(1))
        else:
            p[0] = ast.Init(p[1], p[3], line_no=p.lineno(2))

    def p_instructions(self, p):
        """instructions : instructions instruction
                        | instruction """
        if len(p) == 2:
            p[0] = ast.Instructions(instruction=p[1])
        else:
            p[0] = ast.Instructions(p[1], p[2])

    def p_instruction(self, p):
        """instruction : print_instr
                       | labeled_instr
                       | assignment
                       | choice_instr
                       | while_instr
                       | repeat_instr
                       | return_instr
                       | break_instr
                       | continue_instr
                       | compound_instr"""
        p[0] = p[1]

    def p_print_instr(self, p):
        """print_instr : PRINT expression ';'
                       | PRINT error ';' """
        p[0] = ast.PrintInstr(p[2])
        #error

    def p_labeled_instr(self, p):
        """labeled_instr : ID ':' instruction """
        p[0] = ast.LabeledInstr(p[1], p[3], p.lineno(1))

    def p_assignment(self, p):
        """assignment : ID '=' expression ';' """
        id = ast.IdExpression(p[1], p.lineno(1))
        p[0] = ast.Assignment(id, p[3])

    def p_choice_instr(self, p):
        """choice_instr : IF '(' condition ')' instruction  %prec IFX
                        | IF '(' condition ')' instruction ELSE instruction
                        | IF '(' error ')' instruction  %prec IFX
                        | IF '(' error ')' instruction ELSE instruction """
        if len(p) == 7:
            p[0] = ast.ChoiceInstr(condition=p[3], instruction=p[5])
        else:
            p[0] = ast.ChoiceInstr(condition=p[3], instruction=p[5], else_instruction=p[7])
        #error

    def p_while_instr(self, p):
        """while_instr : WHILE '(' condition ')' instruction
                       | WHILE '(' error ')' instruction """
        p[0] = ast.WhileInstr(condition=p[3], instruction=p[5])

    def p_repeat_instr(self, p):
        """repeat_instr : REPEAT instructions UNTIL condition ';' """
        p[0] = ast.RepeatInstr(instructions=p[2], condition=p[4])

    def p_return_instr(self, p):
        """return_instr : RETURN expression ';' """
        p[0] = ast.ReturnInstr(p[2])

    def p_continue_instr(self, p):
        """continue_instr : CONTINUE ';' """
        p[0] = ast.ContinueInstr()

    def p_break_instr(self, p):
        """break_instr : BREAK ';' """
        p[0] = ast.BreakInstr()

    def p_compound_instr(self, p):
        """compound_instr : '{' declarations instructions '}' """
        p[0] = ast.CompoundInstr(p[2], p[3])

    def p_condition(self, p):
        """condition : expression"""
        p[0] = p[1]

    def p_const(self, p):
        """const : INTEGER
                 | FLOAT
                 | STRING """
        if self.is_int(p[1]):
            p[0] = ast.Integer(p[1])
        elif self.is_float(p[1]):
            p[0] = ast.Float(p[1])
        else:
            p[0] = ast.String(p[1])

    def p_expression(self, p):
        """expression : const
                      | ID
                      | expression '+' expression
                      | expression '-' expression
                      | expression '*' expression
                      | expression '/' expression
                      | expression '%' expression
                      | expression '|' expression
                      | expression '&' expression
                      | expression '^' expression
                      | expression AND expression
                      | expression OR expression
                      | expression SHL expression
                      | expression SHR expression
                      | expression EQ expression
                      | expression NEQ expression
                      | expression '>' expression
                      | expression '<' expression
                      | expression LE expression
                      | expression GE expression
                      | '(' expression ')'
                      | '(' error ')'
                      | ID '(' expr_list_or_empty ')'
                      | ID '(' error ')' """
        if len(p) == 2:
            if not isinstance(p[1], str):

                # if self.is_int(p[1]):
                #     const = ast.Integer(p[1])
                # elif self.is_float(p[1]):
                #     const = ast.Float(p[1])
                # else:
                #     const = ast.String(p[1])
                p[0] = ast.ConstExpression(p[1], type(p[1]))
                # print "GFGFG: {0}, {1}, {2}".format(type(const), const.value, p[1])
            else:
                p[0] = ast.IdExpression(p[1], p.lineno(1))
        elif len(p) == 4:
            if p[1] == '(':
                p[0] = ast.InsideExpression(p[2])
            else:
                p[0] = ast.BinaryExpression(p[1], p[2], p[3], p.lineno(2))
        else:
            p[0] = ast.FunctionExpression(p[1], p[3])

    def p_expr_list_or_empty(self, p):
        """expr_list_or_empty : expr_list
                              | """
        if len(p) == 1:
            p[0] = ast.Node()
        else:
            p[0] = p[1]

    def p_expr_list(self, p):
        """expr_list : expr_list ',' expression
                     | expression """
        if len(p) > 2:
            p[0] = ast.ExpressionList(p[1], p[3])
        else:
            p[0] = ast.ExpressionList(expression=p[1])

    # fundefs
    def p_fundefs(self, p):
        """fundefs : fundef fundefs
                   |  """
        if len(p) == 1:
            p[0] = ast.Fundefs()
        else:
            p[0] = ast.Fundefs(p[1], p[2])

    def p_fundef(self, p):
        """fundef : TYPE ID '(' args_list_or_empty ')' compound_instr """
        p[0] = ast.Fundef(type=p[1], id=p[2], args_list_or_empty=p[4], compound_instr=p[6], line_no=p.lineno(1))


    def p_args_list_or_empty(self, p):
        """args_list_or_empty : args_list
                              | """
        if len(p) == 1:
            p[0] = ast.Node()
        else:
            p[0] = p[1]

    def p_args_list(self, p):
        """args_list : args_list ',' arg
                     | arg """
        if len(p) > 2:
            p[0] = ast.ArgsList(p[1], p[3], line_no=p.lineno(1))
        else:
            p[0] = ast.ArgsList(arg=p[1], line_no=p.lineno(1))

    def p_arg(self, p):
        """arg : TYPE ID """
        p[0] = ast.Arg(p[1], p[2])