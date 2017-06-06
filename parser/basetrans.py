#from hunter.parser.lazy import lazy


#@lazy
#def pi(p, i):
#    return p[i]


class BaseTrans(object):
    def __init__(self):
        self.functions = None
        self.metadata = None

    @staticmethod
    def arg_check(cls, p, thresh, iftrue, iffalse):
        if len(p) < thresh:
            p[0] = iftrue
        else:
            p[0] = iffalse

    def each_p(self):
        pass


class SparkTrans(BaseTrans):
    def __init__(self):
        super(SparkTrans).__init__()

    def p_statement(self, p):
        #self.arg_check(p, 3, "df", "df.%s" % pi(p, 3))
        if len(p) < 3:
            p[0] = "df"
        else:
            p[0] = "df.%s" % p[3]

    def p_commands(self, p):
        #self.arg_check(p, 3, p[1], "%s.%s" % (p[1], pi(p, 3)))
        if len(p) < 3:
            p[0] = p[1]
        else:
            p[0] = "%s.%s" % (p[1], p[3])

    def p_statement_table(self, p):
        p[0] = "select(%s)" % p[2]

    def p_statement_eval(self, p):
        p[0] = "withColumn(%s)" % p[2]

    def p_statement_evalst(self, p):
        p[0] = "%s" % p[1]

    def p_statement_where(self, p):
        p[0] = "filter(%s)" % p[2]

    def p_statement_condition(self, p):
        p[0] = "%s" % p[1]

    def p_statement_stats(self, p):
        p[0] = "groupBy(%s).agg(%s)" % (p[4], p[2])

    def p_statement_agg(self, p):
        if len(p) < 3:
            p[0] = p[1]
        else:
            p[0] = "%s,%s" % (p[1], p[3])
        #self.arg_check(p, 3, p[1], "%s,%s" % (p[1], pi(p, 3)))

    def p_statement_aggfuncexpr(self, p):
        if len(p) < 6:
            p[0] = "%s(%s)" % (p[1], p[3])
        else:
            p[0] = "%s(%s).alias(%s)" % (p[1], p[3], p[6])
        #self.arg_check(p, 6, "%s(%s)" % (p[1], p[3]), "%s(%s).alias(%s)" % (p[1], p[3], pi(p, 6)))

    def p_statement_aggfunc(self, p):
        p[0] = p[1]

    def p_statement_argstats(self, p):
        p[0] = ",".join([p[i] for i in range(1, len(p), 2)])

    def p_expression_name(self, p):
        try:
            p[0] = '"' + p[1] + '"'
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0