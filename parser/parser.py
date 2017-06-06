import sys
from basetrans import SparkTrans

#sys.path.insert(0, "../..")
if sys.version_info[0] >= 3:
    raw_input = input

import ply.lex as lex
import ply.yacc as yacc
import os


class Parser(object):
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = {}
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                          1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        # print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug, optimize=True)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def run(self, inputg=None):
        if inputg is not None:
            ret = yacc.parse(inputg)
            return ret
        while 1:
            try:
                s = raw_input('calc > ')
            except EOFError:
                break
            if not s:
                continue
            return yacc.parse(s)


class Calc(Parser):
    trans = SparkTrans()
    tokens = [
        'NAME', 'NUMBER', 'SEP',
        'LPAREN', 'RPAREN', 'COMMA'
    ]

    RESERVED = {
        "stats": "STATS",
        "min": "MIN",
        "max": "MAX",
        "avg": "AVG",
        "std": "STD",
        "by": "BY",
        "as": "AS",
        "table": "TABLE",
        "where": "WHERE",
        "index": "INDEX",
        "if": "IF",
        "case": "CASE",
        "eval": "EVAL",
    }

    tokens += RESERVED.values()

    # Tokens
    t_SEP = r'\|'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','
    t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        # print "parsed number %s" % repr(t.value)
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = Calc.RESERVED.get(t.value, 'NAME')  # Check for reserved words
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    start = "statement"

    def p_statement(self, p):
        """statement : INDEX SEP commands
                     | INDEX """
        Calc.trans.p_statement(p)

    def p_commands(self, p):
        """commands : commands SEP commandst
                   | commandst """
        Calc.trans.p_commands(p)

    def p_statement_table(self, p):
        """ commandst : TABLE argfields """
        Calc.trans.p_statement_table(p)

    def p_statement_eval(self, p):
        """commandst : EVAL evalst"""
        Calc.trans.p_statement_eval(p)

    def p_statement_evalst(self, p):
        """evalst : argfields"""
        Calc.trans.p_statement_evalst(p)

    def p_statement_where(self, p):
        """commandst : WHERE conditionalst"""
        Calc.trans.p_statement_where(p)

    def p_statement_condition(self, p):
        """conditionalst : argfields"""
        Calc.trans.p_statement_condition(p)

    def p_statement_stats(self, p):
        """commandst : STATS aggstats BY argfields"""
        # df.groupBy("col1").agg(sum("col2").alias("col2")
        Calc.trans.p_statement_stats(p)

    def p_statement_agg(self, p):
        """aggstats : aggstats COMMA aggfuncexpr 
                    | aggfuncexpr"""
        Calc.trans.p_statement_agg(p)

    def p_statement_aggfuncexpr(self, p):
        """aggfuncexpr : aggfunc LPAREN name RPAREN AS name
                        | aggfunc LPAREN name RPAREN """
        Calc.trans.p_statement_aggfuncexpr(p)

    def p_statement_aggfunc(self, p):
        """aggfunc : MIN
                    | MAX
                    | AVG
                    | STD """
        Calc.trans.p_statement_aggfunc(p)

    def p_statement_argstats(self, p):
        """argfields : argfields COMMA name
                    | name """
        Calc.trans.p_statement_argstats(p)

    def p_expression_name(self, p):
        'name : NAME'
        Calc.trans.p_expression_name(p)

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

if __name__ == '__main__':
    calc = Calc()
    # calc.run("stats min(f1) as mf1 max(f2) as mf2, values(f3) as f3s by f4, f5")
    ret = calc.run("""index 
    | table a1, a2
    | stats max(a1) as a11, avg(a2) as a21 by a5, a6 
    | eval a5""")
    print(ret)
