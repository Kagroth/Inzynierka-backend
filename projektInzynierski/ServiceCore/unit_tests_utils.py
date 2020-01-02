from ServiceCore.utils import *
from ServiceCore.models import UnitTest


def create_python_unit_tests(exercise, unit_tests_data):
    for index, unit_test in enumerate(unit_tests_data):
        print(unit_test)
        pathToExerciseDir = getExerciseDirectoryRootPath(exercise)
        fileName = "test_unit" + str(index) + ".py"
        pathToFile = os.path.join(pathToExerciseDir, fileName)

        with open(pathToFile, "w+") as unit_test_file:
            unit_test_file.write("import unittest \n\
import sys \n\
from Solution import * \n\n\
class FirstTest(unittest.TestCase):\n\t\
def test_first(self):\n")
            for line in unit_test.split("\n"):
                print(line)
                unit_test_file.write("\t\t" + line + "\n")
            
            unit_test_file.write("\nif __name__ == '__main__':\n\tunittest.main()")
            newUnitTest = UnitTest.objects.create(exercise=exercise, pathToFile=pathToFile, content=unit_test)
            newUnitTest.save()

def create_java_unit_tests(exercise, unit_tests_data):
    for index, unit_test in enumerate(unit_tests_data):
        print(unit_test)
        pathToExerciseDir = getExerciseDirectoryRootPath(exercise)
        pathToUnitTestsDir = os.path.join(pathToExerciseDir, 'src', 'test', 'java')
        unitTestFileName = "Unit" + str(index) + "Test.java"
        pathToFile = os.path.join(pathToUnitTestsDir, unitTestFileName)

        with open(pathToFile, "w+") as unit_test_file:
            unit_test_file.write(
"import static org.junit.jupiter.api.Assertions.*;\n\
import org.junit.jupiter.api.Test;\n\
public class Unit" + str(index) + "Test { \n\
    @Test \n\
    public void test1() { \n")
            for line in unit_test.split("\n"):
                print(line)
                unit_test_file.write("\t\t" + line + "\n")
            unit_test_file.write("\t} \n }")
            newUnitTest = UnitTest.objects.create(exercise=exercise, pathToFile=pathToFile, content=unit_test)
            newUnitTest.save()


def create_unit_tests(exercise, unit_tests_data):
    if exercise.language.name == 'Python':       
        create_python_unit_tests(exercise, unit_tests_data)
    elif exercise.language.name == 'Java':
        create_java_unit_tests(exercise, unit_tests_data)
    else:
        print("Nie da sie utworzyc unit testow dla podanego jezyka")

