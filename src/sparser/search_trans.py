from src.sparser.parser import *


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
    imports_string = "\n".join(imports)
    udfs_string = "\n".join(udfs)
    search_str = search_template.format(imports=imports_string, udfs=udfs_string, query=query)
    return search_str


def buildCP(cparray, sub=False):
    prev_var = ""
    subqueries = []
    for cpa in cparray:
        cp = cpa["command"]
        if cp.command_type != "CPCompound":
            varname = cp.build(prev_var, subqueries)
        else:
            cpsub = cpa["sub"]
            bcsub = buildCP(cpsub, sub=True)
            subqueries.extend(bcsub[0])
            cp.parent_var = bcsub[1]
            varname = cp.build(prev_var, subqueries)
        prev_var = varname
    ret = ""
    if sub:
        ret = prev_var
    return subqueries, ret


def handle_subsearch(mql, subs):
    bopos = subs.find('[')
    # change to check if type is compound
    if bopos > 0:
        bepos = subs.rfind(']')
        subsearch = subs[bopos+1: bepos]
        subcom = trans(mql, subsearch)
        mql.run(subs[:bopos])
        subcommands =[{"command": mql.command, "sub": subcom}]
    else:
        mql.run(subs)
        subcommands = [{"command": mql.command, "sub": []}]
    return subcommands


def trans(mql, search):
    subsearches = split_pipes(search)
    cparray = []
    for subs in subsearches:
        subqs = handle_subsearch(mql, subs)
        cparray.extend(subqs)
    return cparray


def transform_search(search):
    mql = MQL(earliest="now-d", latest="now")
    cparray = trans(mql, search)
    #cparray.append(mql.json_cp())
    cparray.append(mql.csv_cp())
    subqueries = buildCP(cparray)[0]
    #cparray.append(mql.gen_output())
    spark_query = "\n".join(subqueries)
    end_query = build_end_query(spark_query, mql.meta, mql.imports, mql.udfs)
    #print(end_query)
    return end_query


"""
source=filebeat 
| stats count by p 
| eval test=rand()
| window first(rn) as c, last(rn) as g over group orderby @timestamp rows -1 to 1
| join p,q [source=filebeat | eval t=rand() 
| table p, t | join t [source=filebeat | table t, a] 
| where t>5 ]
| table p, q, t, a
"""
q = """source=filebeat | table offset, @timestamp
| eval group = offset % 10, rn = rand() % 20, rn2=rand() % 25
| sort @timestamp desc"""
#e = transform_search(q)
#print(e)
