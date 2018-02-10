from src.sparser.parser_base import Parser
from src.sparser.parse_source import source_query


class MQL(Parser):
    literals = r'+-*/%,()<>='
    tokens = [
        'NAME', 'LITERAL',
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
        "exp": "EXP",
        "abs": "ABS",
        "sin": "SIN",
        "cos": "COS",
        "tan": "TAN",
        #"cotan": "COTAN",
        "floor": "FLOOR",
        "rand": "RAND",
        "randn": "RANDN",
        #"round": "ROUND",
        #"correlation": "CORELATION", # df.stat.corr(NAME, NAME)
        #approxQuantile
        #crosstab
        #freqItems
        #"ceil": "CEIL",
        #"ceiling": "CEILING",
        #"entropy": "ENTROPY",
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
        #"contains": "CONTAINS",
        # "substr": "SUBSTR",
        # "searchmatch": "SEARCHMATCH",
        # "regexp_replace"
        # "regexp_extract
        # translate - a version of replace
        #"len": "LEN",
        #initcap

    }

    evalDTFunctions = {
        "strptime": "STRPTIME",
        "strftime": "STRFTIME",
        "time": "TIME",
        "now": "NOW",
        #current_date() , current_timestamp()
        # date_sub date_add
        # datediff, to_date, months_between
        # to_date(unix_timestamp(lit("2017-12-11"), dateFormat).cast("timestamp"))
        # to_timestamp(date, ‘yyyy-dd-MM’),
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
        "count": "COUNT",
        "table": "TABLE",
        "where": "WHERE",
        "source": "SOURCE",
        "rename": "RENAME",
        "head": "HEAD",
        "top": "TOP",
        "eval": "EVAL",
        #"describe": "DESCRIBE", #df,describe calcs stats on numbers
        "in": "IN",
        "cache": "CACHE",
        "fillnull": "FILLNULL",
        "value": "VALUE",
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
    t_ignore = " \t"
    t_GE = r'>='
    t_LE = r'<='
    t_NE = r'!='
    t_IDENT = r'=='
    t_AND = r'and'
    t_OR = r'or'
    t_XOR = r'xor'

    Statsfunctions = {
        'avg': 'avg',
        'c': 'count',
        'count': 'count',
        'dc': 'countDistinct',
        'countDistinct': 'countDistinct',
        'approx_count_distinct': 'approx_count_distinct',
        'distinct_count': 'countDistinct',
        'earliest': 'min',
        'estdc': 'approx_count_distinct',
        #'estdc_error': 'dc',
        'exactperc<int>': 'perc',
        'first': 'first',
        'last': 'last',
        'latest': 'max',
        'list': 'collect_list',
        'max': 'max',
        'median': 'median',
        'min': 'min',
        'mean': 'mean',
        'mode': 'mode',
        'p<int>': 'p',
        'perc<int>': 'perc',
        'range': 'range',
        'stdev': 'stddev',
        'sumdc': 'sumDistinct',
        'sumDistinct': 'sumDistinct',
        'stdevp': 'stddev_pop',
        'skewness': 'skewness',
        'sum': 'sum',
        'upperperc<int>': 'perc',
        'values': 'collect_set',
        'kurtosis': 'kurtosis',
        'var': 'var_samp',
        'varp': 'var_pop',
        'corr': 'corr', #correlation for two columns
        'covar_pop': 'covar_pop',
        'covar_samp': 'covar_samp',
    }

    def __init__(self, earliest, latest, **kw):
        super(MQL, self).__init__(**kw)
        #self.state = dict()
        self.imports = set()
        self.udfs = set()
        self.earliest = earliest
        self.latest = latest

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

    def t_LITERAL(self, t):
        r'["][a-zA-Z_0-9]*["]'
        t.type = MQL.RESERVED.get(t.value, 'LITERAL')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    start = "statement"

    def p_source(self, p):
        """ statement : SOURCE '=' NAME
                     | SOURCE '=' NAME '(' LITERAL ')' """
        p[0] = source_query(p[3], self.earliest, self.latest)
        if len(p) == 7:
            self.meta["src_param"] = p[5]
        self.assign = True

    def p_table(self, p):
        """ statement : TABLE field-list """
        # TODO can rename be done here as well
        p[0] = "select(%s)" % p[2]

    #def p_join(self, p):
    #    """ command : JOIN 'type' = NAME NAME [statement]"""
    #    pass
    # How to stop it DF here? Should it go to top?

    def p_rename(self, p):
        """ statement : RENAME field-list-rename """
        p[0] = p[2]

    def p_cache(self, p):
        """ statement : CACHE NAME """
        self.meta["var"] = p[2]
        p[0] = ""

    #def p_window(self, p):
    #    """ command : WINDOW command-params NAME """
    #    # TODO similar to bin
    #    pass

    def p_fillnull(self, p):
        """ statement : FILLNULL VALUE '=' evalexpr field-list """
        # TODO fillnull - should accept both string and numbers
        raise NotImplemented

    def p_head(self, p):
        """ statement : HEAD NUMBER
                    | TOP NUMBER """
        p[0] = "limit(%d)" % p[2]

    def p_eval(self, p):
        """ statement : EVAL eval-state """
        p[0] = p[2]

    def p_eval_statement(self, p):
        """ eval-state : eval-state ',' eval-term
                       | eval-term """
        if len(p) < 3:
            p[0] = p[1]
        else:
            p[0] = "%s.%s" % (p[1], p[3])

    def p_eval_term(self, p):
        """ eval-term : NAME '=' evalexpr """
        p[0] = "withColumn(\"%s\",%s)" % (p[1], p[3])

    def p_lookup(self, p):
        """ statement : LOOKUP NAME """
        p[0] = 1
        raise NotImplemented

    def p_iploc(self, p):
        """ statement : IPLOC NAME """
        p[0] = 1
        raise NotImplemented

    def p_geoloc(self, p):
        """ statement : GEOLOC NAME """
        p[0] = 1
        raise NotImplemented

    def p_fit(self, p):
        """ statement : FIT NAME """
        p[0] = 1
        raise NotImplemented

    def p_apply(self, p):
        """ statement : APPLY NAME """
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
       if p[2] == "!=" or p[2] == "==":
           p[2] = p[2] + "="
       p[0] = '%s %s %s' % (p[1], p[2], p[3])

    def p_evalexpr_func_if(self, p):
        """ evalexpr : IF '(' evalexpr ',' evalexpr ',' evalexpr ')' """
        p[0] = "when(%s, %s).otherwise(%s)" % (p[3], p[5], p[7])

    def p_evalexpr_func_case(self, p):
        """ evalexpr : CASE '(' evalexpr ',' evalexpr ')' """
        p[0] = 1
        raise NotImplemented

    def p_evalexpr_func_in(self, p):
        """ evalexpr : NAME IN '(' func-args ')' """
        # TODO check spark syntax
        p[0] = ".in(%s, %s)" % (p[1], p[4])

    def p_evalexpr_func_1arg(self, p):
        """ evalexpr : POW '(' func-args ')'
                     | LOG '(' evalexpr ')'
                     | ABS '(' evalexpr ')'
                     | SIN '(' evalexpr ')'
                     | COS '(' evalexpr ')'
                     | TAN '(' evalexpr ')'
                     | EXP '(' evalexpr ')'
                     | FLOOR '(' evalexpr ')'
                     | RAND '(' func-args ')'
                     | RANDN '(' evalexpr ')'
                     | TRIM '(' evalexpr ')'
                     | UPPER '(' evalexpr ')' """
        if p[1] not in MQL.evalFunctions:
            raise Exception("function %s not defined" % p[1])
        p[0] = "%s(%s)" % (p[1], p[3])

    def p_evalexpr_func_args(self, p):
        """ func-args : func-args ',' evalexpr
                     | evalexpr
                     | """
        if len(p) < 2:
            p[0] = ''
        elif len(p) < 3:
            p[0] = p[1]
        else:
            p[0] = "%s,%s" % (p[1], p[3])

    def p_evalexpr_group(self, p):
        """ evalexpr : '(' evalexpr ')' """
        p[0] = '(%s)' % p[2]

    def p_evalexpr_terminal(self, p):
        """ evalexpr : LITERAL
                    | FLOAT 
                    | NUMBER """
        p[0] = "lit(%s)" % p[1]

    def p_evalexpr_terminal_name(self, p):
        """ evalexpr : NAME """
        p[0] = "$\"" + p[1] + "\""

    def p_where(self, p):
        """ statement : WHERE evalexpr """
        p[0] = "filter(%s)" % p[2]

    def p_stats(self, p):
        """ statement : STATS stats-agg-terms BY field-list"""
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
                           | NAME '(' expr ')'
                           | COUNT
                           | COUNT AS NAME """
        if p[1] not in MQL.Statsfunctions:
           raise Exception('Unknow stats function >> %s <<'%p[1])
        #TODO is this right,
        # replace the func with the right spark one
        if p[1].lower() == "count":
            p[0] = "count()"
        elif len(p) < 4:
            p[0] = "count().alias(\"%s\""%(p[3])
        elif len(p) < 6:
            p[0] = "%s(%s)"%(p[1], p[3])
        else:
            p[0] = "%s(%s).alias(\"%s\")"%(p[1], p[3], p[6])

    def p_field_list_comma(self, p):
        """ field-list : field-list ',' NAME
                      | NAME """
        if len(p) < 3:
            p[0] = "\"%s\"" % p[1]
        elif len(p) < 4:
            p[0] = p[1] + ", \"%s\"" % p[2]
        else:
            p[0] = p[1] + ", \"%s\"" % p[3]
        #p[0] = ",".join([p[i] for i in range(1, len(p), 2)])

    def p_field_list_rename(self, p):
        """ field-list-rename : field-list-rename ',' NAME AS NAME
                      | field-list-rename NAME AS NAME
                      | NAME AS NAME """
        if len(p) < 5:
            p[0] = "withColumnRename(%s, %s)"
        elif len(p) < 6:
            p[0] = "%s.withColumnRename(%s, %s)" % (p[1], p[2], p[4])
        else:
            p[0] = p[0] = "%s.withColumnRename(%s, %s)" % (p[1], p[3], p[5])

    def p_expression_name(self, p):
        ' expr : NAME '
        try:
            p[0] = "\"" + p[1] + "\""
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0

    def p_expression_literal(self, p):
        ' expr : LITERAL '
        p[0] = p[1]

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

    def post_process(self, ret):
        if len(self.meta["caches"]) == 1:
            return ret
        rets = ret.split("\n")
        caches = self.meta["caches"]
        newret = ""
        for ind in range(len(caches)):
            if ind < len(caches) -1:
                cache = caches[ind+1]
            else:
                cache = "df_out"
            ret = rets[ind].replace(".{%s}" % cache, "")
            newret += 'val {cache} = {df}{ret}\n'.format(cache=cache,
                                                         ret=ret, df=caches[ind])
        self.meta["caches"] = ["df"]
        return newret

if __name__ == '__main__':
    calc = MQL()
    # calc.run("stats min(f1) as mf1 max(f2) as mf2, values(f3) as f3s by f4, f5")
    ret = calc.run("""index 
    | table a1, a2
    | stats max(a1) as a11, avg(a2) as a21 by a5, a6 
    | eval a5 = ((r1))*(2.3+(r2)+if(1, if(10<1, 100+1, 8), 3)) """)
    print(ret)
