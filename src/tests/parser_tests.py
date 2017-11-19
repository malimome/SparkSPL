import unittest

from src.sparser.parser import Calc


class TestParser(unittest.TestCase):

    def test_postjob(self):
        cl = Calc()
        ret = cl.run("""index 
            | table a1, a2
            | stats max(a1) as a11, avg(a2) as a21 by a5, a6 
            | eval a5 = ((r1))*(2.3+(r2)+if(1, if(10<1, 100+1, 8), 3)) """)
        print(ret)

if __name__ == '__main__':
    unittest.main()