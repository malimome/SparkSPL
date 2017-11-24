import sys

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
        self.meta = {}
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


class MQL(Parser):

    literals = r'+-*/%,()<>='
    tokens = [
        'NAME', 'SEP',
        'NUMBER', 'FLOAT',
        'GE', 'LE', 'NE', 'IDENT', 'AND', 'OR', 'XOR'
    ]
    
    evalGenFunctions = {
        "coalesce": "COALESCE",
        "tonumber": "TONUMBER",
        "tostring": "TOSTRING",
        "typeof": "typeof",
    }

    #cidrmatch, commands, exact, exp, 
    #ifnull, isbool, isint, isnotnull, isnull, isnum, isstr, ln, log, max, md5, min, mvappend, mvcount, mvindex, mvfilter, mvjoin, mvrange, mvzip, null, nullif, pi, round, sha1, sha256, sha512, sigfig, spath, sqrt, validate
    evalBinFunctions = {
        "if": "IF",
        "case": "CASE",
    }

    evalNumFunctions = {
        "pow": "POW",
        "log": "LOG",
        "abs": "ABS",
        "floor": "FLOOR",
        "random": "RANDOM",
        #"ceil": "CEIL",
        #"ceiling": "CEILING",
        #"substr": "SUBSTR",
        #"entropy": "ENTROPY",
        #"searchmatch": "SEARCHMATCH",
    }

    evalStrFunctions = {
        "trim": "TRIM",
        #"ltrim": "LTRIM",
        #"rtrim": "RTRIM",
        "upper": "UPPER",
        #"lower": "LOWER",
        #"like": "LIKE",
        #"replace": "REPLACE",
        #"urlencode": "URLENCODE",
        #"split": "SPLIT",
        #"match": "MATCH",
        #"len": "LEN",
    }

    evalDTFunctions = {
        "strptime": "STRPTIME",
        "strftime": "STRFTIME",
        "time": "TIME",
        "now": "NOW",
        "relative_time": "RELATIVE_TIME",
    }

    evalMVFunctions = {
    }

    evalCrptFunctions = {
    }


    evalFunctions = {}
    #evalFunctions.update(evalGenFunctions)
    evalFunctions.update(evalBinFunctions)
    evalFunctions.update(evalNumFunctions)
    evalFunctions.update(evalStrFunctions)
    #evalFunctions.update(evalDTFunctions)
    #evalFunctions.update(evalMVFunctions)
    #evalFunctions.update(evalCrptFunctions)


    RESERVED = {
        "stats": "STATS",
        "by": "BY",
        "as": "AS",
        "table": "TABLE",
        "where": "WHERE",
        "source": "SOURCE",
        "eval": "EVAL",
        "lookup": "LOOKUP",
        "fit": "FIT",
        "apply": "APPLY",
        #"models": "MODELS",
        #"summary": "SUMMARY",
        "iploc": "IPLOC",
        "geoloc": "GEOLOC",
    }

    RESERVED.update(evalFunctions)

    tokens += RESERVED.values()

    # Tokens
    t_SEP = r'\|'
    t_ignore = " \t"
    t_GE = r'>='
    t_LE = r'<='
    t_NE = r'!='
    t_IDENT = r'=='
    t_AND = r'and'
    t_OR = r'or'
    t_XOR = r'xor'

    Statsfunctions = ('avg', 'c', 'count', 'dc', 'distinct_count', 'earliest', 'estdc', 'estdc_error',
                      'exactperc<int>', 'first', 'last', 'latest', 'list', 'max', 'median', 'min', 'mode', 'p<int>',
                      'perc<int>', 'range', 'stdev', 'stdevp', 'sum', 'sumsq', 'upperperc<int>', 'values', 'var', 'varp')

    def t_FLOAT(self,t):
        r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'
        try:
            t.value = float(t.value)
        except ValueError:
            print("Floating value problem: %s" % t.value)
            t.value = 0
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
        t.type = MQL.RESERVED.get(t.value, 'NAME')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    start = "statement"

    def p_statement(self, p):
        """statement : SOURCE '=' NAME SEP commands
                     | SOURCE '=' NAME """
        if len(p) < 5:
            p[0] = ""
        else:
            p[0] = ".%s" % p[5]
        self.meta["source"] = p[3]

    def p_commands(self, p):
        """commands : commands SEP command
                    | command """
        if len(p) < 3:
            p[0] = p[1]
        else:
            p[0] = "%s.%s" % (p[1], p[3])

    def p_table(self, p):
        """ command : TABLE field-list """
        p[0] = "select(%s)" % p[2]

    def p_eval(self, p):
        """ command : EVAL NAME '=' evalexpr """
        p[0] = "withColumn(\"%s\",%s)" % (p[2],p[4])

    def p_lookup(self, p):
        """ command : LOOKUP NAME """
        p[0] = 1
        raise NotImplemented

    def p_iploc(self, p):
        """ command : IPLOC NAME """
        p[0] = 1
        raise NotImplemented

    def p_geoloc(self, p):
        """ command : GEOLOC NAME """
        p[0] = 1
        raise NotImplemented

    def p_fit(self, p):
        """ command : FIT NAME """
        p[0] = 1
        raise NotImplemented

    def p_apply(self, p):
        """ command : APPLY NAME """
        p[0] = 1
        raise NotImplemented

    def p_evalexpr_arithmetic(self, p):
       """ evalexpr : evalexpr '+' evalexpr
                    | evalexpr '-' evalexpr
                    | evalexpr '/' evalexpr
                    | evalexpr '*' evalexpr 
                    | evalexpr '%' evalexpr """
       p[0] = '%s%s%s' % (p[1], p[2], p[3])

    def p_evalexpr_binary(self, p):
       """ evalexpr : evalexpr GE evalexpr 
                    | evalexpr LE evalexpr
                    | evalexpr '<' evalexpr
                    | evalexpr '>' evalexpr
                    | evalexpr NE evalexpr 
                    | evalexpr IDENT evalexpr 
                    | evalexpr AND evalexpr 
                    | evalexpr OR evalexpr 
                    | evalexpr XOR evalexpr """
       p[0] = '%s %s %s' % (p[1], p[2], p[3])

    def p_evalexpr_func_if(self, p):
        """ evalexpr : IF '(' evalexpr ',' evalexpr ',' evalexpr ')' """
        p[0] = p[5] if p[3] else p[7]

    def p_evalexpr_func_case(self, p):
        """ evalexpr : CASE '(' evalexpr ',' evalexpr ')' """
        p[0] = 1
        raise NotImplemented

    def p_evalexpr_func_1arg(self, p):
        """ evalexpr : POW '(' evalexpr ')' 
                     | LOG '(' evalexpr ')' 
                     | ABS '(' evalexpr ')' 
                     | FLOOR '(' evalexpr ')' 
                     | RANDOM '(' evalexpr ')' 
                     | TRIM '(' evalexpr ')' 
                     | UPPER '(' evalexpr ')' """
        if p[0] not in MQL.evalFunctions:
            raise Exception("function not defined")
        raise NotImplemented

    def p_evalexpr_group(self, p):
       """ evalexpr : '(' evalexpr ')' """
       p[0] = '(%s)'%p[2]

    def p_evalexpr_terminal(self, p):
        """evalexpr : NAME 
                    | FLOAT 
                    | NUMBER """
        #TODO check NAME and add double qoute
        if type(p[1]) == type(""):
            p[0] = "col(" + p[1] + ")"
        else:
            p[0] = p[1]

    def p_where(self, p):
        """ command : WHERE evalexpr """
        p[0] = "filter(%s)" % p[2]

    def p_stats(self, p):
        """command : STATS stats-agg-terms BY field-list"""
        # df.groupBy("col1").agg(sum("col2").alias("col2")
        p[0] = "groupBy(%s).agg(%s)" % (p[4], p[2])

    def p_stats_clause(self, p):
        """ stats-agg-terms : stats-agg-terms ',' stats-agg-term 
                            | stats-agg-term """
        if len(p) < 3:
            p[0] = p[1]
        else:
            p[0] = "%s,%s" % (p[1], p[3])

    def p_stat_agg_term(self, p):
        """ stats-agg-term : NAME '(' expr ')' AS NAME
                           | NAME '(' expr ')' """
        if p[1] not in MQL.Statsfunctions:
           sys.exit('Unknow stats function >> %s <<'%p[1])  
        if len(p) < 6:
            p[0] = "%s(\"%s\")"%(p[1], p[3])
        else:
            p[0] = "%s(\"%s\").alias(\"%s\")"%(p[1], p[3], p[6])

    def p_field_list_comma(self, p):
        """field-list : field-list ',' NAME
                      | NAME """
        if len(p) < 3:
            p[0] = "\"%s\"" % p[1]
        else:
            p[0] = p[1] + ", \"%s\"" % p[3]
        #p[0] = ",".join([p[i] for i in range(1, len(p), 2)])

    def p_field_list_space(self,p):
        """ field-list : field-list NAME """
        p[0] = '%s,\"%s\"'%(p[2],p[1])

    def p_expression_name(self, p):
        'expr : NAME'
        try:
            p[0] = p[1]
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

if __name__ == '__main__':
    calc = MQL()
    # calc.run("stats min(f1) as mf1 max(f2) as mf2, values(f3) as f3s by f4, f5")
    ret = calc.run("""index 
    | table a1, a2
    | stats max(a1) as a11, avg(a2) as a21 by a5, a6 
    | eval a5 = ((r1))*(2.3+(r2)+if(1, if(10<1, 100+1, 8), 3)) """)
    print(ret)
