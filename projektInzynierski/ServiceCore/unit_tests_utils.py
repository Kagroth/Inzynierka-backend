from ServiceCore.utils import *
from ServiceCore.models import UnitTest


def create_python_unit_tests(exercise, unit_tests_data, save_model=True):
    print(unit_tests_data)
    pathToExerciseDir = getExerciseDirectoryRootPath(exercise)
    fileName = "test_unit.py"
    
    pathToFile = os.path.join(pathToExerciseDir, fileName)

    lines_to_write = ['import unittest\n', 'import sys\n',
                      'class FirstTest(unittest.TestCase):\n']

    with open(pathToFile, "w+") as unit_test_file:
        unit_test_file.writelines(lines_to_write)

        if not unit_tests_data:
            unit_test_file.write("\tpass\n")
            unit_test_file.write("\nif __name__ == '__main__':\n\tunittest.main()")
            return

        for index, unit_test in enumerate(unit_tests_data):
            unit_test_file.write(
                "\tdef test_" + str(index) + "(self):\n")

            for index_i, line in enumerate(unit_test.split("\n")):
                unit_test_file.write("\t\t" + line + "\n")

            if save_model:
                newUnitTest = UnitTest.objects.create(
                    exercise=exercise, pathToFile=pathToFile, content=unit_test)
                newUnitTest.save()

        unit_test_file.write("\nif __name__ == '__main__':\n\tunittest.main()")


def create_java_unit_tests(exercise, unit_tests_data, save_model=True):
    print(unit_tests_data)
    pathToExerciseDir = getExerciseDirectoryRootPath(exercise)
    pathToUnitTestsDir = os.path.join(pathToExerciseDir, 'src', 'test', 'java')
    unitTestFileName = "UnitTest.java"
    pathToFile = os.path.join(pathToUnitTestsDir, unitTestFileName)

    lines_to_write = ['import static org.junit.jupiter.api.Assertions.*;\n',
                      'import org.junit.jupiter.api.Test;\n\n',
                      'public class UnitTest {\n']

    with open(pathToFile, "w+") as unit_test_file:
        unit_test_file.writelines(lines_to_write)

        for index, unit_test in enumerate(unit_tests_data):
            unit_test_file.writelines(['\t@Test \n',
                                           '\tpublic void test' + str(index) + '() { \n'])

            for index_i, line in enumerate(unit_test.split('\n')):
                unit_test_file.write('\t\t' + line + '\n')
            
            unit_test_file.write('\t} \n')
                
            if save_model:    
                newUnitTest = UnitTest.objects.create(
                    exercise=exercise, pathToFile=pathToFile, content=unit_test)
                newUnitTest.save()
        
        unit_test_file.write('\n}')
        

def create_unit_tests(exercise, unit_tests_data, save_model=True):
    if exercise.language.name == 'Python':
        create_python_unit_tests(exercise, unit_tests_data, save_model)
    elif exercise.language.name == 'Java':
        create_java_unit_tests(exercise, unit_tests_data, save_model)
    else:
        print("Nie da sie utworzyc unit testow dla podanego jezyka")


def insert_python_import_instruction(path_to_unit_test, filename):
    unit_test_file_content_tmp = ""
    (filename_without_extension, extension) = filename.split(".")

    if extension != "py":
        return False

    try:
        with open(path_to_unit_test, 'r') as unit_test_file:
            unit_test_file_content_tmp = unit_test_file.read()

        with open(path_to_unit_test, 'w') as unit_test_file:
            import_instruction = "from " + filename_without_extension + " import * \n"
            unit_test_file.write(import_instruction)

        with open(path_to_unit_test, 'a') as unit_test_file:
            unit_test_file.write(unit_test_file_content_tmp)
    except Exception as e:
        print(str(e))
        return False

    return True


def insert_java_package_instruction(path_to_unit_test, package_name):
    unit_test_file_content_tmp = ""

    try:
        with open(path_to_unit_test, 'r') as unit_test_file:
            unit_test_file_content_tmp = unit_test_file.read()

        with open(path_to_unit_test, 'w') as unit_test_file:
            import_instruction = "import " + package_name + ".*; \n"
            unit_test_file.write(import_instruction)

        with open(path_to_unit_test, 'a') as unit_test_file:
            unit_test_file.write(unit_test_file_content_tmp)
    except Exception as e:
        print(str(e))
        return False

    return True


def get_java_package_name_from_file(path_to_file):
    package_line = ""

    with open(path_to_file, "r") as solution_file:
        for line in solution_file.readlines():
            if "package" in line:
                package_line = line
                break

    if package_line == "":
        return ""

    (package_keyword, package_name) = package_line.split()
    package_name = package_name.rstrip()
    package_name = package_name[:-1]  # usuniecie znaku ';'

    return package_name
