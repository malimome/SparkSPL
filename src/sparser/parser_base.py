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
