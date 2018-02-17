from src.sparser.parser_base import Parser
from src.sparser.parse_source import source_query


class MQL(Parser):
    literals = r'+-*/%,()<>='
    tokens = [
        'NAME', 'LITERAL',
        'NUMBER', 'FLOAT',
        'GE', 'LE', 'NE', 'IDENT', 'AND', 'OR', 'XOR'
    ]

    evalNoArgsList = [
        "rand", "randn", "current_date", "current_timestamp"
    ]
    evalNoArgFuncs = {
    }
    evalNoArgFuncs.update({f: f for f in evalNoArgsList})

    evalOneArgList = [
        "abs", "sin", "sinh", "cos", "cosh", "tan", "tanh", "exp", "log", "acos", "asin",
        "atan", "sqrt", "cbrt", "expm1", "factorial", "degrees",
        "ceil", "floor", "bround", "round",
        "log10", "log2", "log1p", "quarter", "radians"

        "md5", "sha1", "sha2", "crc32", "hash", "hex", "unhex", "base64", "unbase64",
        "ascii", "signum",
        "tonumber", "tostring" "typeof", "isnan", "isnull",
        "rand", "randn", "trim", "ltrim", "rtrim", "upper", "lower",
        "hour", "minute", "month", "second", "year",
        "dayofmonth", "dayofyear", "from_unixtime", "weekofyear",
        "to_date", "to_json", "to_tiemstamp",
        "explode", "length",
        "initcap", "reverse",
    ]
    evalOneArgFuncs = {
        "binary": "bin",
        "len": "length",
        #bitwiseNot, max, min, isbool, isint, isnotnull, isnull, isnum, isstr, ln, log,
    }
    evalOneArgFuncs.update({f: f for f in evalOneArgList})

    evalTwoArgList = [
        "log", "pow", "hypot", "pmod",
        "format_number", "format_string", "nanvl",
        "add_months", "date_add", "date_sub", "date_diff", "date_format", "from_unixtime",
        "last_day", "months_between", "next_day", "trunc",

        "instr", "levenshtein", "repeat", "shiftLeft", "shiftRight", "split",
        #"locate"
    ]
    evalTwoArgFuncs = {
        "strpos": "instr",

    }
    evalTwoArgFuncs.update({f: f for f in evalTwoArgList})

    #"lpad", "rpad", "substring(_index), "translate",
    evalManyList = [
        "coalesce", "concat", "concat_ws", "greatest", "least",
    ]
    evalManyFuncs = {
        "join": "concat_ws",
        "max": "greatest",
        "min": "least"
    }
    evalManyFuncs.update({f: f for f in evalManyList})

    evalSpecialList = [
        "if", "case", "rex_replace", "rex_extract", "rex_match", "contains", "like", "in",
    ]
    evalSpecialFuncs ={
        # "rlike": "RLIKE",
        #"convert": "CONVERT",
    }
    evalSpecialFuncs.update({f: f.upper() for f in evalSpecialList})

    # greatest, least, hypot, log, log10, log2, md5, pmod, rint, round, sha1,
    # sha2, shiftRight, shiftLeft, sin, sinh, tanh,
    # concat, concat_ws (join), conv (base conversion)
    # decode, encode, expr, from_json, format_string, get_json_object, hash, hex,
    # instr, isnan, isnull, length, locate, lpad,
    # nanvl, repeat, reverse, rpad, to_json, trim, unbase64,
    # datediff, dayofmonth, dayofyear, from_unixtime, hour, minute, month,
    # months_between, next_day, second, to_date, to_timestamp, unix_timestamp
    # monthofyear, weekofyear, year,
    # array_contains, coalesce, corr (correlation two col), levenshtein,
    # explode(_outer), posexplode(_outer),

    #cidrmatch, commands, exact,
    #ifnull, max, md5, min, mvappend, mvcount, mvindex, mvfilter, mvjoin, mvrange, mvzip, null, nullif, pi, round, sha1, sha256, sha512, sigfig, spath, sqrt, validate

    """
    evalNumFunctions = {
        #"correlation": "CORELATION", # df.stat.corr(NAME, NAME)
        #approxQuantile
        #crosstab
        #freqItems
        #"entropy": "ENTROPY",
    }

    evalStrFunctions = {
        #"replace": "REPLACE",
        #"urlencode": "URLENCODE",
        #"split": "SPLIT",
        #"match": "MATCH",
        # "substr": "SUBSTR",
        # "searchmatch": "SEARCHMATCH",
        # translate - a version of replace
        #"len": "LEN",
        #initcap

    }

    evalDTFunctions = {
        "strptime": "STRPTIME",
        "strftime": "STRFTIME",
        "time": "TIME",
        "now": "NOW",
        # datediff, to_date, months_between
        # to_date(unix_timestamp(lit("2017-12-11"), dateFormat).cast("timestamp"))
        # to_timestamp(date, ‘yyyy-dd-MM’),
        "relative_time": "RELATIVE_TIME",
    }
    """

    RESERVED = {
        "stats": "STATS",
        "window": "WINDOW",
        "by": "BY",
        "over": "OVER",
        "as": "AS",
        "sort": "SORT",
        "orderby": "ORDERBY",
        "desc": "DESC",
        "asc": "ASC",
        "range": "RANGE",
        "rows": "ROWS",
        "to": "TO",
        "count": "COUNT",
        "table": "TABLE",
        "drop": "DROP",
        "where": "WHERE",
        "source": "SOURCE",
        "rename": "RENAME",
        "head": "HEAD",
        "top": "TOP",
        "eval": "EVAL",
        #"describe": "DESCRIBE", #df,describe calcs stats on numbers
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

    RESERVED.update(evalSpecialFuncs)

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

    statsFuncList = [
        "avg", "count", "countDistinct", "approx_count_distinct", "first", "last",
        "max", "min", "mean", "mode", "median", "stdev", "skewness", "sum", "kurtosis",
        "covar_samp", "covar_pop",
    ]
    Statsfunctions = {
        'c': 'count', #
        'dc': 'countDistinct',
        'estdc': 'approx_count_distinct',
        'distinct_count': 'countDistinct',
        #'earliest': 'min', #
        #'exactperc<int>': 'perc', #
        'grouping_id': 'grouping_id',
        #'latest': 'max', #
        'list': 'collect_list',
        #'p<int>': 'p',
        #'perc<int>': 'perc',
        #'range': 'range',
        'sumdc': 'sumDistinct',
        'sumDistinct': 'sumDistinct',
        'stdevp': 'stddev_pop',
        #'upperperc<int>': 'perc',
        'values': 'collect_set',
        'var': 'var_samp',
        'varp': 'var_pop',
        'corr': 'corr', #correlation for two columns
    }
    Statsfunctions.update({f: f for f in statsFuncList})

    def __init__(self, earliest, latest, **kw):
        super(MQL, self).__init__(**kw)
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
        r'-?\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        return t

    def t_NAME(self, t):
        r'@?[a-zA-Z_][a-zA-Z_0-9]*'
        # Check for reserved words
        t.type = MQL.RESERVED.get(t.value, 'NAME')
        return t

    def t_LITERAL(self, t):
        r'["][a-zA-Z_0-9\-\=\,\.\:\;\(\)\[\]\{\}\*\+\|\%\$\^\#\@\!\~\>\<\?]*["]'
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

    def p_table(self, p):
        """ statement : TABLE field-list """
        # TODO can rename be done here as well
        p[0] = "select({2})".format(*p)

    def p_drop(self, p):
        """ statement : DROP field-list """
        p[0] = "drop({2})".format(*p)

    #def p_join(self, p):
    #    """ command : JOIN 'type' = NAME NAME [statement]"""
    #    pass
    # How to stop it DF here? Should it go to top?

    def p_rename(self, p):
        """ statement : RENAME field-list-rename """
        p[0] = p[2]

    def p_cache(self, p):
        """ statement : CACHE NAME """
        self.var = p[2]
        p[0] = ""

    def p_fillnull(self, p):
        """ statement : FILLNULL VALUE '=' evalexpr field-list """
        # TODO fillnull - should accept both string and numbers
        raise NotImplemented

    def p_head(self, p):
        """ statement : HEAD NUMBER
                    | TOP NUMBER """
        p[0] = "limit({2})".format(*p)

    def p_sort(self, p):
        """ statement : SORT field-list-order
                      | ORDERBY field-list-order """
        p[0] = "sort({2})".format(*p)

    def p_eval(self, p):
        """ statement : EVAL eval-state """
        p[0] = p[2]

    def p_eval_statement(self, p):
        """ eval-state : eval-state ',' eval-term
                       | eval-term """
        stmts = {
            2: "{1}",
            4: "{1}.{3}"
        }
        p[0] = stmts[len(p)].format(*p)

    def p_eval_term(self, p):
        """ eval-term : NAME '=' evalexpr """
        p[0] = "withColumn(\"{1}\",{3})".format(*p)

    def p_evalexpr_arithmetic(self, p):
       """ evalexpr : evalexpr '+' evalexpr
                    | evalexpr '-' evalexpr
                    | evalexpr '/' evalexpr
                    | evalexpr '*' evalexpr 
                    | evalexpr '%' evalexpr """
       p[0] = '{1}{2}{3}'.format(*p)

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
       p[0] = '{1} {2} {3}'.format(*p)

    def p_evalexpr_func_if(self, p):
        """ evalexpr : IF '(' evalexpr ',' evalexpr ',' evalexpr ')' """
        p[0] = "when({3}, {5}).otherwise({7})".format(*p)

    def p_evalexpr_func_case(self, p):
        """ evalexpr : CASE '(' evalexpr ',' evalexpr ')' """
        p[0] = 1
        raise NotImplemented

    def p_evalexpr_func_in(self, p):
        """ evalexpr : NAME IN '(' func-args ')' """
        # TODO check spark syntax
        p[0] = ".in({1}, {4})".format(*p)

    def p_evalexpr_rex_extract(self, p):
        """ evalexpr : REX_EXTRACT '(' NAME ',' LITERAL ')' """
        p[0] = 'regexp_extract({3}, """{5}""", 1)'.format(*p)

    def p_evalexpr_rex_replace(self, p):
        """ evalexpr : REX_REPLACE '(' NAME ',' LITERAL ',' LITERAL ')' """
        p[0] = 'regexp_replace({3}, ""{5}"", {7})'.format(*p)

    def p_evalexpr_rex_match(self, p):
        """ evalexpr : NAME REX_MATCH LITERAL
                     | NAME LIKE LITERAL
                     | NAME CONTAINS LITERAL """
        map_func = {
            "rex_match": "rlike",
            "like": "like",
            "contains": "contains"
        }
        func = map_func[p[2]]
        p[0] = "{field} {func} {regex}".format(field=p[1], func=func, regex=p[3])

    def p_evalexpr_func_012arg(self, p):
        """ evalexpr : NAME '(' evalexpr ',' evalexpr ')'
                     | NAME '(' evalexpr ')'
                     | NAME '(' ')' """
        functions = {
            7: MQL.evalTwoArgFuncs,
            5: MQL.evalOneArgFuncs,
            4: MQL.evalNoArgFuncs
        }
        if p[1] not in functions[len(p)]:
            raise Exception("function %s not defined" % p[1])
        stmts = {
            7: "{1}({3}, {5})",
            5: "{1}({3})",
            4: "{1}()"
        }
        p[0] = stmts[len(p)].format(*p)

    def p_evalexpr_func_manyargs(self, p):
        """ evalexpr : NAME '(' func-args ')' """
        if p[1] not in MQL.evalManyFuncs:
            raise Exception("function %s not defined" % p[1])
        stmts = {
            5: "{1}({3})"
        }
        p[0] = stmts[len(p)].format(*p)

    def p_evalexpr_func_args(self, p):
        """ func-args : func-args ',' evalexpr
                     | evalexpr
                     | """
        stmts = {
            4: "{1},{3}",
            2: "{1}",
            1: ""
        }
        p[0] = stmts[len(p)].format(*p)

    def p_evalexpr_group(self, p):
        """ evalexpr : '(' evalexpr ')' """
        p[0] = '({2})'.format(*p)

    def p_evalexpr_terminal(self, p):
        """ evalexpr : LITERAL
                    | FLOAT 
                    | NUMBER """
        p[0] = "lit({1})".format(*p)

    def p_evalexpr_terminal_name(self, p):
        """ evalexpr : NAME """
        p[0] = "$\"{1}\"".format(*p)

    def p_where(self, p):
        """ statement : WHERE evalexpr """
        p[0] = "filter({2})".format(*p)

    def p_stats(self, p):
        """ statement : STATS stats-agg-terms BY field-list"""
        # df.groupBy("col1").agg(sum("col2").alias("col2")
        p[0] = "groupBy({4}).agg({2})".format(*p)

    def p_stats_clause(self, p):
        """ stats-agg-terms : stats-agg-terms ',' stats-agg-term
                            | stats-agg-term """
        stmts = {
            4: "{1}, {3}",
            2: "{1}"
        }
        p[0] = stmts[len(p)].format(*p)

    def p_stat_agg_term(self, p):
        """ stats-agg-term : NAME '(' expr ')' AS NAME
                           | NAME '(' expr ')'
                           | COUNT AS NAME
                           | COUNT"""
        if p[1] not in MQL.Statsfunctions:
           raise Exception('Unknow stats function >> %s <<'%p[1])
        stmts = {
            7: "{1}({3}).alias(\"{6}\")",
            5: "{1}({3})",
            4: "count(lit(1)).alias(\"{3}\"",
            2: "count(lit(1))"
        }
        p[0] = stmts[len(p)].format(*p)

    def build_window_agg(self, stmts, p):
        wSpecName = "wS" + Parser.get_rand_string(7)
        wSpecStr = "val {wSpec}=Window.".format(wSpec=wSpecName)
        wSpecStr += stmts[len(p)].format(*p)
        self.meta["before"] = wSpecStr
        return p[2].format(wSpec=wSpecName)

    def p_window(self, p):
        """ statement : WINDOW window-agg-terms OVER field-list ORDERBY field-list-order RANGE NUMBER TO NUMBER
                      | WINDOW window-agg-terms OVER field-list RANGE NUMBER TO NUMBER
                      | WINDOW window-agg-terms OVER field-list ORDERBY field-list-order
                      | WINDOW window-agg-terms OVER field-list """
        stmts = {
            11: "partitionBy({4}).orderBy({6}).rangeBetween({8}, {10})",
            9: "partitionBy({4}).rangeBetween({7}, {9})",
            7: "partitionBy({4}).orderBy({6})",
            5: "partitionBy({4})"
        }
        p[0] = self.build_window_agg(stmts, p)

    def p_window_1(self, p):
        """ statement : WINDOW window-agg-terms OVER field-list ORDERBY field-list-order ROWS NUMBER TO NUMBER
                      | WINDOW window-agg-terms OVER field-list ROWS NUMBER TO NUMBER
                      | WINDOW window-agg-terms ORDERBY field-list-order """
        stmts = {
            11: "partitionBy({4}).orderBy({6}).rowsBetween({8}, {10})",
            9: "partitionBy({4}).rowsBetween({7}, {9})",
            5: "orderBy({4})"
        }
        p[0] = self.build_window_agg(stmts, p)

    def p_window_clause(self, p):
        """ window-agg-terms : window-agg-terms ',' win-agg-term
                            | win-agg-term """
        stmts = {
            4: "{1}.{3}",
            2: "{1}"
        }
        p[0] = stmts[len(p)].format(*p)

    def p_win_agg_term(self, p):
        """ win-agg-term : NAME '(' expr ')' AS NAME
                         | NAME AS NAME """
        if p[1] not in MQL.Statsfunctions:
           raise Exception('Unknow window function >> %s <<'%p[1])
        stmts = {
            7: "withColumn(\"{6}\", {1}({3})",
            4: "withColumn(\"{3}\", {1}()"
        }
        # TODO count is not working, other funcs
        p[0] = stmts[len(p)].format(*p) + ".over({wSpec}))"

    def p_field_list_comma(self, p):
        """ field-list : field-list ',' NAME
                      | NAME """
        stmts = {
            4: "{1}, \"{3}\"",
            2: "\"{1}\""
        }
        p[0] = stmts[len(p)].format(*p)

    def p_field_list_order(self, p):
        """ field-list-order : field-list-order ',' field-order
                             | field-order """
        stmts = {
            4: "{1}, {3}",
            2: "{1}"
        }
        p[0] = stmts[len(p)].format(*p)

    def p_field_order(self, p):
        """ field-order : NAME DESC
                        | NAME ASC
                        | '-' NAME
                        | '+' NAME
                        | NAME """
        if len(p) == 2:
            p[0] = "$\"{1}\".desc"
        elif p[2].lower() == "desc":
            p[0] = "$\"{1}\".desc"
        elif p[2].lower() == "asc":
            p[0] = "$\"{1}\".asc"
        elif p[1] == "+":
            p[0] = "$\"{2}\".asc"
        elif p[1] == "-":
            p[0] = "$\"{2}\".desc"
        p[0] = p[0].format(*p)

    def p_field_list_rename(self, p):
        """ field-list-rename : field-list-rename ',' NAME AS NAME
                      | field-list-rename NAME AS NAME
                      | NAME AS NAME """
        stmts = {
            6: "{1}.withColumnRenamed(\"{3}\", \"{5}\")",
            5: "{1}.withColumnRenamed(\"{2}\", \"{4}\")",
            4: "withColumnRenamed(\"{1}\", \"{3}\")"
        }
        p[0] = stmts[len(p)].format(*p)

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

    def p_expression_name(self, p):
        ' expr : NAME '
        try:
            p[0] = "\"{1}\"".format(*p)
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
            if ind < len(caches) - 1:
                cache = caches[ind + 1]
            else:
                cache = "df_out"
            ret = rets[ind].replace(".{%s}" % cache, "")
            newret += 'val {cache} = {df}{ret}\n'.format(cache=cache,
                                                         ret=ret, df=caches[ind])
        self.meta["caches"] = ["df"]
        return newret

if __name__ == '__main__':
    calc = MQL(earliest="now-d", latest="now")
    # calc.run("stats min(f1) as mf1 max(f2) as mf2, values(f3) as f3s by f4, f5")
    ret = calc.run("""index 
    | table a1, a2
    | stats max(a1) as a11, avg(a2) as a21 by a5, a6 
    | eval a5 = ((r1))*(2.3+(r2)+if(1, if(10<1, 100+1, 8), 3)) """)
    print(ret)
