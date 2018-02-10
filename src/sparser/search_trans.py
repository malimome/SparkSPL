from src.sparser.parser import MQL
import random
import string


def split_pipes(query):
    outbo = query.split('[')
    current_open = 0
    total_closed = 0
    outer = []
    for p in outbo:
        outbc = p.split("]")
        inner = []
        for q in outbc:
            if total_closed == current_open:
                q = q.replace('|', '#')
            inner.append(q)
            total_closed += 1
        total_closed -= 1
        p = "]".join(inner)
        outer.append(p)
        current_open += 1
    result = "[".join(outer)
    subqueries = result.split("#")
    return subqueries


def build_end_query(query, meta, imports, udfs):
    search_template = """
val sqlContext = new org.apache.spark.sql.SQLContext(sc)
{imports}
{udfs}
{query}
"""
    imports_string = ""
    udfs_string = ""
    for im in imports:
        imports_string += "%s\n" % im
    for udf in udfs:
        udfs_string += "%s\n" % udf
    search_str = search_template.format(imports=imports_string, udfs=udfs_string, query=query)
    return search_str


def get_varname(var, vardict):
    if var is None:
        varname = 'df' + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(7))
    else:
        varname = var
    return varname


def gen_output(prev_var):
    output = "{prev_var}.toJSON.collect().foreach(println)".format(prev_var=prev_var)
    return output


def build_query(subqueries):
    query = ""
    prev_var = None
    for [subq, varname] in subqueries:
        if prev_var is None:
            query += "val {varname} = {subq}\n".format(varname=varname, subq=subq)
        else:
            query += "val {varname} = {prev_var}.{subq}\n".format(varname=varname, prev_var=prev_var, subq=subq)
        prev_var = varname
    query += gen_output(prev_var)
    return query


def transform_search(search):
    subsearches = split_pipes(search)
    subqueries = []
    mql = MQL(earliest="now-d", latest="now")
    vardict = dict()
    for subs in subsearches:
        subq = mql.run(subs)
        var = mql.meta["var"] if "var" in mql.meta else None
        varname = get_varname(var, vardict)
        subqueries.append([subq, varname])
    spark_query = build_query(subqueries)
    end_query = build_end_query(spark_query, mql.meta, mql.imports, mql.udfs)
    print(end_query)
    return end_query


