import random, string


class CommandParam(object):
    def __init__(self, **kargs):
        self.command = self._set("command", **kargs)
        self.command_name = self._set("command_name", **kargs)
        self.command_type = self.__class__.__name__
        self.meta = self._set("meta", **kargs)
        self.prefix = self._set("prefix", **kargs)
        self.postfix = self._set("postfix", **kargs)
        self.parent_var = None

    @staticmethod
    def _set(var, **kargs):
        return kargs[var] if var in kargs else None

    @staticmethod
    def get_rand_string(n):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))

    @staticmethod
    def get_varname(var, pref="df"):
        if var is None:
            varname = pref + CommandParam.get_rand_string(7)
        else:
            varname = var
        return varname


class CPSource(CommandParam):
    def __init__(self, **kargs):
        super(CPSource, self).__init__(**kargs)

    def build(self, prev_var, subqueries):
        varname = self.get_varname(None)
        subq = "val {varname} = {sub}".format(varname=varname,
                                              sub=self.command)
        subqueries.append(subq)
        return varname


class CPSingle(CommandParam):
    def __init__(self, **kargs):
        super(CPSingle, self).__init__(**kargs)

    def build(self, prev_var, subqueries):
        varname = self.get_varname(None)
        subq = "val {varname} = {prev_var}.{sub}".format(
            varname=varname, prev_var=prev_var, sub=self.command)
        subqueries.append(subq)
        return varname


class CPMulti(CommandParam):
    def __init__(self, **kargs):
        super(CPMulti, self).__init__(**kargs)

    def build(self, prev_var, subqueries):
        varws = self.get_varname(None, "wS")
        subq = "val {wSpec} = {prefix}".format(wSpec=varws, prefix=self.prefix)
        subqueries.append(subq)
        varname = self.get_varname(None)
        subq = "val {varname} = {prev_var}.{sub}".format(
            varname=varname, prev_var=prev_var,
            sub=self.command.format(wSpec=varws))
        subqueries.append(subq)
        return varname


class CPCompound(CommandParam):
    def __init__(self, **kargs):
        super(CPCompound, self).__init__(**kargs)

    def build(self, prev_var, subqueries):
        varname = self.get_varname(None)
        subq = "val {varname} = {prev_var}.{sub}".format(
            varname = varname, prev_var=prev_var,
            sub=self.command.format(parent_var=self.parent_var)
        )
        subqueries.append(subq)
        return varname


class CPInline(CommandParam):
    def __init__(self, **kargs):
        super(CPInline, self).__init__(**kargs)

    def build(self, prev_var, subqueries):
        pass


class CPTerminal(CommandParam):
    def __init__(self, **kargs):
        super(CPTerminal, self).__init__(**kargs)

    def build(self, prev_var, subqueries):
        #"toJSON.collect().foreach(println)"
        if self.prefix is not None:
            subq = self.prefix.format(prev_var=prev_var)
            subqueries.append(subq)
        subq = self.command.format(prev_var=prev_var)
        subqueries.append(subq)
        return None
