from src.sparser.parser_base import Parser
from src.sparser.parse_source import source_query
from src.sparser.command_param import *
import re


class MQL(Parser):
    timepat = re.compile("(\d*)\s*(\w*)")
    literals = r'+-*/%,()<>=[]'
    tokens = [
        'NAME', 'LITERAL', 'NUMBER', 'FLOAT',
        'GE', 'LE', 'NE', 'IDENT', 'AND', 'OR', 'XOR'
    ]

    evalNoArgsList = [
        "rand", "randn", "current_date", "current_timestamp", "now"
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
        "last_day", "months_between", "next_day", "trunc", "date_trunc",
        "instr", "levenshtein", "repeat", "shiftLeft", "shiftRight", "split",
        "substr"
        #"locate", "relative_time"
    ]
    evalTwoArgFuncs = {
        "strpos": "instr",
    }
    evalTwoArgFuncs.update({f: f for f in evalTwoArgList})

    evalThreeArgList = [
        "replace"
    ]
    evalThreeArgFuncs = {
    }
    evalThreeArgFuncs.update({f: f for f in evalThreeArgList})

    #"lpad", "rpad", "substring(_index), "translate",
    evalManyList = [
        "coalesce", "concat", "concat_ws", "greatest", "least",
    ]
    evalManyFuncs = {
        "max": "greatest",
        "min": "least"
    }
    evalManyFuncs.update({f: f for f in evalManyList})

    evalSpecialList = [
        "if", "case", "rex_replace", "rex_extract", "rex_match", "contains", "like", "in", "interval_round"
    ]
    evalSpecialFuncs ={
        # "rlike": "RLIKE",
        #"convert": "CONVERT",
    }
    evalSpecialFuncs.update({f: f.upper() for f in evalSpecialList})

    # pmod, rint, nanvl, to_json, unix_timestamp, monthofyear,
    # concat, concat_ws (join), conv (base conversion)
    # decode, encode, expr, from_json, format_string, get_json_object,
    #  array_contains, coalesce, corr (correlation two col), levenshtein,
    # explode(_outer), posexplode(_outer),
    #cidrmatch, commands, exact, sha1, sha256, sha512, sigfig, spath, sqrt, validate
    #ifnull, max, min, mvappend, mvcount, mvindex, mvfilter, mvjoin, mvrange, mvzip, null, nullif, pi
    """
    evalNumFunctions = {
        #"correlation": "CORELATION", # df.stat.corr(NAME, NAME)
        #approxQuantile
        #crosstab
    }
    """

    RESERVED = {
        "stats": "STATS",
        "timechart": "TIMECHART",
        "interval": "INTERVAL",
        "bin": "BIN",
        "join": "JOIN",
        "window": "WINDOW",
        "by": "BY",
        "over": "OVER",
        "save": "SAVE",
        "as": "AS",
        "sort": "SORT",
        "orderby": "ORDERBY",
        "desc": "DESC",
        "asc": "ASC",
        "range": "RANGE",
        "rows": "ROWS",
        "to": "TO",
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
        "max", "min", "mean", "mode", "median", "stddev", "skewness", "sum", "kurtosis",
        "sumDistinct", "var_samp", "var_pop"
    ]
    Statsfunctions = {
        'c': 'count',
        'dc': 'countDistinct',
        'estdc': 'approx_count_distinct',
        'distinct_count': 'countDistinct',
        'grouping_id': 'grouping_id',
        'list': 'collect_list',
        'set': 'collect_set',
        'sumdc': 'sumDistinct',
        'dcsum': 'sumDistinct',
        'stdevp': 'stddev_pop',
        'stdevs': 'stddev_samp',
        'std': 'stddev',
        'values': 'collect_set',
        'var': 'var_samp',
        'varp': 'var_pop',
        #'latest': 'max', #
        #'earliest': 'min', #
        #'exactperc<int>': 'perc', #
        #'upperperc<int>': 'perc',
        #'p<int>': 'p',
        #'perc<int>': 'perc',
        #'range': 'range',
    }
    Statsfunctions.update({f: f for f in statsFuncList})
    statsFuncList2 = [
        "covar_samp", "covar_pop", "corr"
    ]
    Statsfunctions2 = {}
    Statsfunctions2.update({f: f for f in statsFuncList2})
    WindowFuncList = [
        "percent_rank", "rank", "row_number", "currentRow", "cume_dist", "dense_rank",
        "unboundedFollowing", "unboundedPreceding",
    ]
    Windowfunctions = {}
    Windowfunctions.update({f: f for f in WindowFuncList})
    WindowFuncList1 = [ "ntile" ]
    Windowfunctions1 = {}
    Windowfunctions1.update({f: f for f in WindowFuncList1})
    WindowFuncList2 = [ "lag", "lead" ]
    Windowfunctions2 = {}
    Windowfunctions2.update({f: f for f in WindowFuncList2})

    def __init__(self, earliest, latest, **kw):
        super(MQL, self).__init__(**kw)
        self.imports = set()
        self.udfs = set()
        self.earliest = earliest
        self.latest = latest
        self.command = None

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

    def t_LITERAL(self, t):
        r'"[^"]*"'
        t.type = MQL.RESERVED.get(t.value, 'LITERAL')
        return t

    def t_NAME(self, t):
        r'@?[a-zA-Z_][a-zA-Z_0-9]*'
        # Check for reserved words
        t.type = MQL.RESERVED.get(t.value, 'NAME')
        return t

    """
    TODO:
    Separate source name, commands, fields, literals, etc
    """

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        t.lexer.skip(1)
        raise Exception("Illegal character '%s'" % t.value[0])

    def update_command(self, p, CmType, prefix=None, postfix=None):
        self.command = CmType(
            command=p[0],
            command_name=p[1].lower(),
            meta=self.meta,
            prefix=prefix,
            postfix=postfix,
        )

    def json_cp(self):
        self.command = {"command": CPTerminal(
            command="toJSON.collect().foreach(println)",
            command_name=None,
            meta=self.meta,
            prefix=None,
            postfix=None
        ), "sub": None}
        return self.command

    def csv_cp(self):
        pref = """var vartypes0001 = ""; for (f <- {prev_var}.schema.fields) vartypes0001 = vartypes0001 + "\\"" + f.name + "\\": \\"" + f.dataType.typeName + "\\", "; vartypes0001 = "{{" + vartypes0001.dropRight(2) + "}}" """
        self.command = {"command": CPTerminal(
            command="(vartypes0001 +: {prev_var}.toJSON.collect()).foreach(println)",
            command_name=None,
            meta=self.meta,
            prefix=pref,
            postfix=None
        ), "sub": None}
        return self.command

    start = "statement"

    def p_source(self, p):
        """ statement : SOURCE '=' NAME
                     | SOURCE '=' NAME command-args """
        p[0] = source_query(p[3], self.earliest, self.latest)
        self.update_command(p, CPSource)
        if len(p) == 5:
            self.meta["src_param"] = p[4]

    def p_command_args(self, p):
        """ command-args : NAME
                          | LITERAL
                          | NAME '=' nlnftypes
                          | NAME command-args
                          | LITERAL command-args empty
                          | NAME '=' nlnftypes command-args"""

        self.meta["commands-args"] = {}
        #p[0] = p[1]

    def p_nlnf_types(self, p):
        """ nlnftypes : NAME
                       | LITERAL
                       | FLOAT
                       | NUMBER """
        p[0] = p[1]

    def p_empty(self, p):
        """empty :"""
        pass

    def p_table(self, p):
        """ statement : TABLE field-list
                      | TABLE '-' field-list"""
        # TODO can rename be done here as well
        if len(p) == 3:
            p[0] = "select({2})".format(*p)
        else:
            p[0] = "drop({2})".format(*p)
        self.update_command(p, CPSingle)

    def p_join(self, p):
        """ statement : JOIN field-list-novar """
        # '[' statement ']'
        p[0] = "join({parent_var}, Seq(%s))" % p[2]
        self.update_command(p, CPCompound)

    def p_rename(self, p):
        """ statement : RENAME field-list-rename """
        p[0] = p[2]
        self.update_command(p, CPSingle)

    def p_cache(self, p):
        """ statement : CACHE NAME """
        self.var = p[2]
        p[0] = ""
        self.update_command(p, CPSingle)

#    def p_inline(self, p):
#        """ statement : INLINE '[' subquery ']' """
#        # TODO store var here, do calcs and add it back to var.
#        p[0] = ""
    # do union command to append
    #   self.update_meta(p, type=INLINE)

    def p_save(self, p):
        """ statement : SAVE NAME """
        print(self.prev_var)
        self.meta["before"] = """{var}.write.format("org.elasticsearch.spark.sql")
.option("es.nodes" , "localhost")
.option("es.port","9200")
.option("es.index.auto.create","true")
.option("es.nodes.wan.only","true")
.option("es.resouce.auto.create", "{res}")
.mode("Append")
.save("{res}")
        """.format(var=self.prev_var, res="%s-/summary" % p[2])
        p[0] = ""
        self.update_command(p, CPTerminal)
        #.mode("Overwrite")

    def p_drop(self, p):
        """ statement : DROP NAME """
        #TODO fix the variable before write, should be empty variable
        self.meta["before"] = """write.format("org.elasticsearch.spark.sql")
        .option("es.nodes" , "localhost")
        .option("es.port","9200")
        .option("es.index.auto.create","true")
        .option("es.nodes.wan.only","true")
        .option("es.resouce.auto.create", "{res}")
        .mode("Overwrite")
        .save("{res}")
                """.format(var=self.prev_var, res=p[2])
        p[0] = ""

    def p_fillnull(self, p):
        """ statement : FILLNULL VALUE '=' nlnftypes field-list-novar
                      | FILLNULL VALUE '=' nlnftypes """
        stmts = {
            5: "na.fill({4})",
            6: "na.fill({4}, Seq({5}))"
        }
        p[0] = stmts[len(p)].format(*p)
        self.update_command(p, CPSingle)

    def p_head(self, p):
        """ statement : HEAD NUMBER
                    | TOP NUMBER """
        p[0] = "limit({2}).toDF".format(*p)
        self.update_command(p, CPSingle)

    def p_bin(self, p):
        """ statement : BIN INTERVAL '=' LITERAL NAME """
        p[0] = "withColumn(\"{5}\",window($\"{5}\", {4}).getItem(\"start\"))".format(*p)
        self.update_command(p, CPSingle)

    def p_sort(self, p):
        """ statement : SORT field-list-order
                      | ORDERBY field-list-order """
        p[0] = "sort({2}).toDF".format(*p)
        self.update_command(p, CPSingle)

    def p_eval(self, p):
        """ statement : EVAL eval-state """
        p[0] = p[2]
        self.update_command(p, CPSingle)

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
        p[5] = p[5].replace("\\", "\\\\")
        p[0] = 'regexp_extract($"{3}", {5}, 1)'.format(*p)

    def p_evalexpr_rex_replace(self, p):
        """ evalexpr : REX_REPLACE '(' NAME ',' LITERAL ',' LITERAL ')' """
        p[0] = 'regexp_replace("${3}", {5}, {7})'.format(*p)

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

    def p_evalexpr_interval_round(self, p):
        """ evalexpr : INTERVAL_ROUND '(' NAME ',' LITERAL ')' """
        map = {
           "s": 1, "second": 1, "seconds": 1,
           "m": 60, "min": 60, "minute": 60, "minutes": 60,
           "h": 60*60, "hour": 60*60, "hours": 60*60,
           "d": 60*60*24, "day": 60*60*24, "days": 60*60*24,
           "w": 60*60*24*7, "week": 60*60*24*7, "weeks": 60*60*24*7,
           "M": 60*60*24*30, "month": 60*60*24*30, "months": 60*60*24*30,
           "y": 60*60*24*365, "year": 60*60*24*365, "years": 60*60*24*365
        }
        g = MQL.timepat.match(p[5].strip("\""))
        num_modifier = g.group(1)
        time_modifier = g.group(2)
        if time_modifier == '' and num_modifier == '':
            raise Exception("bin value not defined!")
        num_bin = 1
        if num_modifier != '':
            num_bin = int(num_modifier)
        if time_modifier != '':
            if time_modifier not in map:
                raise Exception("time modifier not defined!")
            num_bin = num_bin * map[time_modifier]
            p[5] = num_bin
            p[0] = "(floor($\"{3}\".cast(\"timestamp\").cast(\"long\") / {5}) * {5}).cast(\"timestamp\")".format(*p)
        else:
            p[5] = num_bin
            p[0] = "floor(${3} / {5})*{5}".format(*p)

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
        self.update_command(p, CPSingle)

    def p_timechart(self, p):
        """ statement : TIMECHART INTERVAL '=' LITERAL stats-agg-terms BY NAME
                      | TIMECHART INTERVAL '=' LITERAL stats-agg-terms """
        stmts = {
            6: "groupBy(window($\"@timestamp\", {4}).getItem(\"start\").alias(\"@timestamp\")).agg({5})",
            8: "groupBy(window($\"@timestamp\", {4}).getItem(\"start\").alias(\"@timestamp\")).pivot(\"{7}\").agg({5})",
        }
        p[0] = stmts[len(p)].format(*p)
        self.update_command(p, CPSingle)

    def p_stats(self, p):
        """ statement : STATS stats-agg-terms BY field-list"""
        # df.groupBy("col1").agg(sum("col2").alias("col2")
        p[0] = "groupBy({4}).agg({2})".format(*p)
        self.update_command(p, CPSingle)

    def p_stats_clause(self, p):
        """ stats-agg-terms : stats-agg-terms ',' stats-agg-term
                            | stats-agg-term """
        stmts = {
            4: "{1}, {3}",
            2: "{1}"
        }
        p[0] = stmts[len(p)].format(*p)

    def p_stat_agg_term(self, p):
        """ stats-agg-term : NAME '(' stat-arg ',' stat-arg ')' AS NAME
                           | NAME '(' stat-arg ',' stat-arg ')'
                           | NAME '(' stat-arg ')' AS NAME
                           | NAME '(' stat-arg ')'
                           | NAME AS NAME
                           | NAME """
        if len(p) >= 7 and p[4] == ',' and p[1] not in MQL.Statsfunctions2:
            raise Exception("Unknown stats function with 2 args: %s" % p[1])
        elif p[1] not in MQL.Statsfunctions:
            raise Exception('Unknow stats function: %s' % p[1])
        if len(p)<=4 and p[1].lower() != "count":
            raise Exception('Stats function %s missing arguments!' % p[1])
        stmts = {
            9: "{1}({3}, {5}).alias(\"{8}\")",
            7: "{1}({3}).alias(\"{6}\")",
            5: "{1}({3})",
            4: "count(lit(1)).alias(\"{3}\")",
            2: "count(lit(1)).alias(\"count\")"
        }
        if len(p) == 7 and p[4] == ",":
            stmts[7] = "{1}({3}, {5})"
        p[1] = MQL.Statsfunctions.get(p[1], p[1])
        p[0] = stmts[len(p)].format(*p)

    def build_window_agg(self, stmts, p):
        self.imports.add("import org.apache.spark.sql.expressions.Window")
        self.imports.add("import org.apache.spark.sql.functions._")
        #wSpecName = "wS" + Parser.get_rand_string(7)
        #wSpecStr = "val {wSpec}=Window.".format(wSpec=wSpecName)
        wSpecStr = "Window." + stmts[len(p)].format(*p)
        #self.meta["before"] = wSpecStr
        return wSpecStr

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
        p[0] = p[2]
        wSpecStr = self.build_window_agg(stmts, p)
        self.update_command(p, CPMulti, prefix=wSpecStr)

    def p_window_1(self, p):
        """ statement : WINDOW window-agg-terms OVER field-list ORDERBY field-list-order ROWS NUMBER TO NUMBER
                      | WINDOW window-agg-terms OVER field-list ROWS NUMBER TO NUMBER
                      | WINDOW window-agg-terms ORDERBY field-list-order """
        stmts = {
            11: "partitionBy({4}).orderBy({6}).rowsBetween({8}, {10})",
            9: "partitionBy({4}).rowsBetween({7}, {9})",
            5: "orderBy({4})"
        }
        p[0] = p[2]
        wSpecStr = self.build_window_agg(stmts, p)
        self.update_command(p, CPMulti, prefix=wSpecStr)

    def p_window_clause(self, p):
        """ window-agg-terms : window-agg-terms ',' win-agg-term
                            | win-agg-term """
        stmts = {
            4: "{1}.{3}",
            2: "{1}"
        }
        p[0] = stmts[len(p)].format(*p)

    def p_win_agg_term(self, p):
        """ win-agg-term : NAME '(' stat-arg ')' AS NAME
                         | NAME AS NAME
                         | NAME
        """
        if p[1] not in MQL.Statsfunctions:
           raise Exception('Unknow window function >> %s <<'%p[1])
        if len(p)<=4 and p[1].lower() != "count":
            raise Exception('Stats function %s missing arguments!' % p[1])
        if len(p) <= 4:
            p1 = "(lit(1))" if p[1].lower() == "count" else "()"
            p[1] += p1
        stmts = {
            7: "withColumn(\"{6}\", {1}({3})",
            4: "withColumn(\"{3}\", {1}",
            2: "withColumn(\"{1}\", {1}"
        }
        p[0] = stmts[len(p)].format(*p) + ".over({wSpec}))"

    def p_field_list_comma(self, p):
        """ field-list : field-list ',' NAME
                      | NAME """
        stmts = {
            4: "{1}, $\"{3}\"",
            2: "$\"{1}\""
        }
        p[0] = stmts[len(p)].format(*p)

    def p_field_list_comma_novar(self, p):
        """ field-list-novar : field-list-novar ',' NAME
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
        self.update_command(p, CPSingle)
        raise NotImplemented

    def p_iploc(self, p):
        """ statement : IPLOC NAME """
        p[0] = 1
        self.update_command(p, CPSingle)
        raise NotImplemented

    def p_geoloc(self, p):
        """ statement : GEOLOC NAME """
        p[0] = 1
        self.update_command(p, CPSingle)
        raise NotImplemented

    def p_fit(self, p):
        """ statement : FIT NAME """
        p[0] = 1
        self.update_command(p, CPSingle)
        raise NotImplemented

    def p_apply(self, p):
        """ statement : APPLY NAME """
        p[0] = 1
        self.update_command(p, CPSingle)
        raise NotImplemented

    def p_expression_name(self, p):
        ' stat-arg : NAME '
        try:
            p[0] = "\"{1}\"".format(*p)
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0

    def p_expression_literal(self, p):
        ' stat-arg : LITERAL '
        p[0] = p[1]

    def p_error(self, p):
        if p:
            raise Exception("Syntax error at '%s'" % p.value)
        else:
            raise Exception("Syntax error!")


if __name__ == '__main__':
    calc = MQL(earliest="now-d", latest="now")
    # calc.run("stats min(f1) as mf1 max(f2) as mf2, values(f3) as f3s by f4, f5")
    ret = calc.run("""index 
    | table a1, a2
    | stats max(a1) as a11, avg(a2) as a21 by a5, a6 
    | eval a5 = ((r1))*(2.3+(r2)+if(1, if(10<1, 100+1, 8), 3)) """)
    print(ret)
