import ply.lex as lex
import ply.yacc as yacc
import os
import random
import string


class Parser(object):
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.meta = dict()
        self.debug = kw.get('debug', 0)
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

        self.var = None
        self.prev_var = None

    @staticmethod
    def get_rand_string(n):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))

    def get_varname(self, var, vardict):
        if var is None:
            varname = 'df' + Parser.get_rand_string(7)
        else:
            varname = var
        return varname

    def build_line(self, subq):
        varname = self.get_varname(self.var, None)
        query = "" if "before" not in self.meta else "%s\n" % self.meta["before"]
        if self.prev_var is None:
            query += "val {varname} = {subq}".format(varname=varname, subq=subq)
        else:
            if len(subq) > 0:
                query += "val {varname} = {prev_var}.{subq}".format(varname=varname, prev_var=self.prev_var, subq=subq)
            else:
                query += "val {varname} = {prev_var}".format(varname=varname, prev_var=self.prev_var)
        self.prev_var = varname
        self.var = None
        return query

    def gen_output(self):
        output = "{prev_var}.toJSON.collect().foreach(println)".format(prev_var=self.prev_var)
        return output

    def run(self, inputg = None):
        self.meta = dict()
        if inputg is not None:
            ret = yacc.parse(inputg)
            return ret
        return ""

    def run_commandline(self):
        import sys
        if sys.version_info[0] >= 3:
            raw_input = input
        while 1:
            try:
                s = raw_input('calc > ')
            except EOFError:
                break
            if not s:
                continue
            return yacc.parse(s)
