Install Python3.5 + Jupyter + PLY (python lex, yacc)

# PLY
homepage: http://www.dabeaz.com/ply/index.html
examples: https://github.com/dabeaz/ply/tree/master/example

# Test cases for the language
From: STATS (stats-function(field) [AS fieldnew])... [BY field-list] 
stats-function: avg() | c() | count() | dc() | distinct_count() | earliest() | estdc() | estdc_error() | exactperc<int>() | first() | last() | latest() | list() | max() | median() | min() | mode() | p<int>() | perc<int>() | range() | stdev() | stdevp() | sum() | sumsq() | upperperc<int>() | values() | var() | varp()
TO: df.groupBy(field-list).aggr(stats-function(field).alias(fieldnew), ...)

example: stats min(f) as f1 -> df.aggr(min(f).alias(f1))
http://docs.splunk.com/Documentation/Splunk/6.6.0/SearchReference/Stats
example: stats perc80(n) as nn, estdc(b) by part -> df.groupBy(part).aggr(perc80(n).alias(nn), estdc(b))


From: eval <field>=<expression>["," <field>=<expression>]... 
http://docs.splunk.com/Documentation/Splunk/6.6.0/SearchReference/Eval
TO: df.withColumn(<field>, <expression>).withColumn(...

From: expression
Arithmetic 	+ - * / %
Concatenation 	.
Boolean 	AND OR NOT XOR < > <= >= != = == LIKE
functions: abs, case, ceil, ceiling, cidrmatch, coalesce, commands, exact, exp, floor, if, ifnull, isbool, isint, isnotnull, isnull, isnum, isstr, len, like, ln, log, lower, ltrim, match, max, md5, min, mvappend, mvcount, mvindex, mvfilter, mvjoin, mvrange, mvzip, now, null, nullif, pi, pow, random, relative_time, replace, round, rtrim, searchmatch, sha1, sha256, sha512, sigfig, spath, split, sqrt, strftime, strptime, substr, time, tonumber, tostring, trim, typeof, upper, urldecode, validate
To: Syntax or function name may change. TBD
