import sys
from basetrans import SparkTrans

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
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" \
                      + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        # print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)#, optimize=True)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def run(self, inputg = None):
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

    literals = r'+-*/%,()<>='
    trans = SparkTrans()
    tokens = [
        'NAME', 'SEP',
        'NUMBER', 'FLOAT',
        'GE', 'LE', 'NE', 'IDENT'
    ]

    RESERVED = {
        "stats": "STATS",
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
    t_ignore = " \t"
    t_GE = r'>='
    t_LE = r'<='
    t_NE = r'!='
    t_IDENT = r'=='

    Statsfunctions = ('avg','c','count','dc','distinct_count','earliest','estdc','estdc_error','exactperc<int>','first','last','latest','list','max','median','min','mode','p<int>','perc<int>','range','stdev','stdevp','sum','sumsq','upperperc<int>','values','var','varp')

    def t_FLOAT(self,t):
        r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'
        try:
            t.value = float(t.value)
        except ValueError:
            print("Floating value problem: %s" % t.value)
            t.value = nan
        return t

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # Check for reserved words
        t.type = Calc.RESERVED.get(t.value, 'NAME')
        return t


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
        """commands : commands SEP command
                    | command """
        Calc.trans.p_commands(p)

    def p_table(self, p):
        """ command : TABLE field-list """
        Calc.trans.p_table(p)

    def p_eval(self, p):
        """ command : EVAL NAME '=' evalexpr """
        Calc.trans.p_eval(p)

    def p_evalexpr_arithmetic(self, p):
       """ evalexpr : evalexpr '+' evalexpr
                    | evalexpr '-' evalexpr
                    | evalexpr '/' evalexpr
                    | evalexpr '*' evalexpr """
       p[0] = '%s%s%s'% (p[1],p[2],p[3])

    def p_evalexpr_group(self, p):
       """ evalexpr : '(' evalexpr ')' """
       p[0] = '(%s)'%p[2]

    def p_evalexpr_terminal(self, p):
        """evalexpr : NAME 
                    | FLOAT 
                    | NUMBER """
        Calc.trans.p_evalexpr_terminal(p)

    def p_where(self, p):
        """ command : WHERE conditionalst"""
        Calc.trans.p_where(p)

    def p_condition(self, p):
        """ conditionalst : field-list """
        Calc.trans.p_condition(p)

    def p_stats(self, p):
        """command : STATS stats-agg-terms BY field-list"""
        # df.groupBy("col1").agg(sum("col2").alias("col2")
        Calc.trans.p_stats(p)

    def p_stats_clause(self, p):
        """ stats-agg-terms : stats-agg-terms ',' stats-agg-term 
                            | stats-agg-term """
        Calc.trans.p_agg(p)

    def p_stat_agg_term(self, p):
        """ stats-agg-term : NAME '(' expr ')' AS NAME
                           | NAME '(' expr ')' """
        if p[1] not in Calc.Statsfunctions:
           sys.exit('Unknow stats function >> %s <<'%p[1])  
        Calc.trans.p_stat_agg_term(p)

    def p_field_list_comma(self, p):
        """field-list : field-list ',' NAME
                      | NAME """
        Calc.trans.p_field_list_comma(p)

    def p_field_list_space(self,p):
        """ field-list : field-list NAME """
        Calc.trans.p_field_list_space(p)

    def p_expression_name(self, p):
        'expr : NAME'
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
    | eval a5 = ((r1))*(2.3+(r2)) """)
    print(ret)
