from src.sparser.search_trans import transform_search
from src.sparser.parser import MQL


def test1():
    q = """
source=filebeat 
| eval group = offset % 20, rn = rand()
| sort group desc, @timestamp desc
| window first(rn) as c, last(rn) as g over group orderby @timestamp rows -1 to 1
| rename c as c2, g as g2 | head 1000
| save summary_test
"""
    print(transform_search(q))
    return ""


def test2():
    q = 'save summarytest'
    cl = MQL(earliest="now-d", latest="now")
    spsearch = cl.run(q)
    before = ""
    after = ""
    if "before" in cl.meta:
        before = "%s;" % cl.meta["before"]
    if "after" in cl.meta:
        after = ";%s" % cl.meta["after"]
    final = before + spsearch + after
    print(final)


def test3():
    import requests
    requests.get("http://localhost:5000/jobs/93498234", {"mode":"normal", "offset": 0, "count":30})


if __name__ == '__main__':
    test1()