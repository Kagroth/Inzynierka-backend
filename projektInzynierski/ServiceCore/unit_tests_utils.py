from ServiceCore.utils import *
from ServiceCore.models import UnitTest

def create_unit_tests(exercise, unit_tests_data):
    for index, unit_test in enumerate(unit_tests_data):
        print(unit_test)
        pathToExerciseDir = getExerciseDirectoryPath(exercise)
        fileName = "test_unit" + str(index) + ".py"
        pathToFile = os.path.join(pathToExerciseDir, fileName)

        with open(pathToFile, "w+") as unit_test_file:
            unit_test_file.write("import unittest \n\
import sys \n\
from solution import * \n\n\
class FirstTest(unittest.TestCase):\n\t\
def test_first(self):\n")
            for line in unit_test.split("\n"):
                print(line)
                unit_test_file.write("\t\t" + line + "\n")
            
            unit_test_file.write("\nif __name__ == '__main__':\n\tunittest.main()")

        # zapis sciezki w modelu nie dziala
        print(pathToFile)
        newUnitTest = UnitTest.objects.create(exercise=exercise, pathToFile=pathToFile)
        print("Zapisana sciezka: " + newUnitTest.pathToFile)
        #print(newUnitTest.pathToFile.path)
        newUnitTest.save()
        print(newUnitTest)