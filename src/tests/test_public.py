#pylint: skip-file
from io import StringIO
import sys
sys.path.insert(0, './')
import src.main as project

class TestGivenExamples:

    def test_1(self):
        input_data = "3 2 3\n1 1 1\n2 1 1\n3 2 1\n1 2 1\n2 2 1\n1 1 2 3\n2 1 2 1\n3 2 1\n"
        sys.stdin = StringIO(input_data)
        sys.stdout = StringIO()
        project.main()
        output = sys.stdout.getvalue().strip()
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        assert output == "3"

    def test_2(self):
        input_data = "3 2 3\n1 1 2\n2 1 2\n3 2 2\n1 1 1\n2 1 1\n1 1 2 3\n2 2 1 2\n3 2 1 2\n"
        sys.stdin = StringIO(input_data)
        sys.stdout = StringIO()
        project.main()
        output = sys.stdout.getvalue().strip()
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        assert output == "2"

    def test_3(self):
        input_data = "3 3 5\n1 1 1\n2 2 2\n3 3 2\n1 1 1\n2 2 1\n3 2 1\n1 1 3\n2 1 1\n3 2 3\n4 3 1 2\n5 3 1\n"
        sys.stdin = StringIO(input_data)
        sys.stdout = StringIO()
        project.main()
        output = sys.stdout.getvalue().strip()
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        assert output == "4"

    def test_4(self):
        input_data = "3 3 5\n1 1 1\n2 2 2\n3 3 2\n1 1 2\n2 2 0\n3 2 2\n1 1 3\n2 1 1\n3 2 3\n4 3 1 2\n5 3 1\n"
        sys.stdin = StringIO(input_data)
        sys.stdout = StringIO()
        project.main()
        output = sys.stdout.getvalue().strip()
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        assert output == "-1"
