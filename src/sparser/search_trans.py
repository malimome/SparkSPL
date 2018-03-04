from src.sparser.parser import MQL


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


def transform_search(search):
    subsearches = split_pipes(search)
    subqueries = []
    mql = MQL(earliest="now-d", latest="now")
    for subs in subsearches:
        subq = mql.build_line(mql.run(subs))
        subqueries.append(subq)
    subqueries.append(mql.gen_output())
    spark_query = "\n".join(subqueries) #build_query(subqueries)
    end_query = build_end_query(spark_query, mql.meta, mql.imports, mql.udfs)
    #print(end_query)
    return end_query


"""
source=a 
| stats count by p 
| join p [source=b | table p, t | join [source=c | table p, c]]
"""
"""
val df = source(A)
val df1 = df.stats
val dfnew = source(b)
val dfnew1 = dfnew.table
val dfl = source(c)
val dfl1 = dfl.table
val dfnew2 = dfnew1.join(dfl1).on(p)
val df2 = df1.join(dfnew2).one(p)
"""

"""
only do gen_output if not subquery and is main
also have modified end query
"""



