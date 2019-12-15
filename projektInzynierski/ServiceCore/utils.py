import os
from distutils.dir_util import copy_tree

EXERCISES_DIRECTORY_ROOT = "exercises"
TESTS_DIRECTORY_ROOT = "exercises_tests"
SOLUTIONS_DIRECTORY_ROOT = "solutions"

def createDirectory(pathToCreate):
    # funkcja tworzy folder w lokalizacji path/dirName
    if not os.path.exists(pathToCreate):
        os.mkdir(pathToCreate)
        return True
    else:
        return False

# ************ funkcje dla cwiczen - Exercises *******************
def getExerciseDirectoryName(exercise):
    # funkcja zwraca nazwe folderu odpowiednia dla podanego cwiczenia
    return exercise.title.replace(" ", "") + '-' + exercise.author.username.replace(" ", "") + '-' + str(exercise.pk)

def getExerciseDirectoryRootPath(exercise):
    # funkcja zwraca sciezke do folderu z konkretnym cwiczeniem w ktorym sa skladowane unit testy
    directoryName = getExerciseDirectoryName(exercise)
    cwd = os.getcwd()
    
    return os.path.join(cwd, EXERCISES_DIRECTORY_ROOT, directoryName)

def createExerciseRootDirectory(exercise):
    # funkcja tworzy folder dla konkretnego cwiczenia w folderze glownym dla cwiczen
    directoryName = getExerciseDirectoryName(exercise)
    cwd = os.getcwd()
    
    pathToExercise = os.path.join(cwd, EXERCISES_DIRECTORY_ROOT, directoryName)

    return createDirectory(pathToExercise)

def createExerciseDirectory(exercise, relPath):
    # funkcja tworzy folder dla cwiczenia exercise w lokalizacji relPath
    directoryName = getExerciseDirectoryName(exercise)
    cwd = os.getcwd()

    pathToExercise = os.path.join(cwd, relPath, directoryName)

    return createDirectory(pathToExercise)


# ************ funkcje dla kolokwium - Tests *********************
def getTestDirectoryName(test):
    # funckja zwraca nazwe folderu dla podanego kolokwium
    return test.title.replace(" ", "") + '-' + test.author.username.replace(" ", "") + '-' + str(test.pk)

def getTestDirectoryRootPath(test):
    # Zwraca lokalizacje w ktorej zapisane jest kolokwium
    directoryName = getTestDirectoryName(test)
    cwd = os.getcwd()
    
    return os.path.join(cwd, TESTS_DIRECTORY_ROOT, directoryName)


def createTestRootDirectory(test):
    # funkcja tworzy folder dla kolokwium 'test' w folderze root dla kolokwium
    directoryName = getTestDirectoryName(test)
    cwd = os.getcwd()
    pathToTest = os.path.join(cwd, TESTS_DIRECTORY_ROOT, directoryName)

    created = createDirectory(pathToTest)

    if created:
        for exercise in test.exercises.all():
            if createExerciseDirectory(exercise, pathToTest):
                exerciseRootPath = getExerciseDirectoryRootPath(exercise)
                exerciseDirName = getExerciseDirectoryName(exercise)
                exerciseInTestDirPath = os.path.join(pathToTest, exerciseDirName)

                copy_tree(exerciseRootPath, exerciseInTestDirPath)
            else:
                return False        

        return True
    else:
        return False

def createTestDirectory(test, relPath):
    # funkcja tworzy folder dla kolokwium 'test' w lokalizacji relPath
    directoryName = getTestDirectoryName(test)
    cwd = os.getcwd()
    pathToTest = os.path.join(cwd, relPath, directoryName)

    created = createDirectory(pathToTest)

    if created:
        for exercise in test.exercises.all():
            if createExerciseDirectory(exercise, pathToTest):
                exerciseRootPath = getExerciseDirectoryRootPath(exercise)
                exerciseDirName = getExerciseDirectoryName(exercise)
                exerciseInTestDirPath = os.path.join(pathToTest, exerciseDirName)

                copy_tree(exerciseRootPath, exerciseInTestDirPath)
            else:
                return False        

        return True
    else:
        return False

# *************funkcje dla rozwiazan zadan - Tasks and Solutions *****************
def getTaskSolutionsDirectoryName(task):
    # funkcja zwraca nazwe folderu w ktorym znajduja sie rozwiazania zadania 'task'
    return task.title.replace(" ", "") + '-' + task.author.username.replace(" ", "") + '-' + str(task.pk)    


def createExerciseSolutionDirectory(task):
    # funkcja tworzy strukture katalogow dla zadania typu exercise
    # - RootDir Solutions
    #   - Task dir
    #       - GroupA dir
    #           - UserA solution
    #           - UserB solution
    #       - GroupB dir
    #           - UserC solution
    directoryName = getTaskSolutionsDirectoryName(task)

    cwd = os.getcwd()
    pathToSolution = os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName)
    
    if not createDirectory(pathToSolution):
        return False
    
    if not createExerciseDirectory(task.exercise, pathToSolution):
        return False

    for group in task.assignedTo.all():
        groupName = group.name + '-' + str(group.pk)
        pathToAssignedGroupSolution = os.path.join(pathToSolution, getExerciseDirectoryName(task.exercise), groupName)
        created = createDirectory(pathToAssignedGroupSolution)

        if not created:
            return False
        
        for member in group.users.all():
            memberName = member.username.replace(" ", "") + '-' + str(member.pk)
            pathToGroupMemberSolution = os.path.join(pathToAssignedGroupSolution, memberName)

            created = createDirectory(pathToGroupMemberSolution)

            if not created:
                return False

    return True


def createTestSolutionDirectory(task):
    # funkcja tworzy katalog z rozwiazaniem dla kolokwium w postaci:
    # - RootDir Solutions
    #   - Task dir
    #       - GroupA
    #           - UserA dir
    #               - ExerciseA dir
    #               - ExerciseB dir 
    directoryName = getTaskSolutionsDirectoryName(task)
    cwd = os.getcwd()
    pathToSolution = os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName)

    if not createDirectory(pathToSolution):
        return False
    
    for group in task.assignedTo.all():
        groupName = group.name + '-' + str(group.pk)
        pathToAssignedGroupSolution = os.path.join(pathToSolution, groupName)
        created = createDirectory(pathToAssignedGroupSolution)

        if not created:
            return False

        for member in group.users.all():
            memberName = member.username.replace(" ", "") + '-' + str(member.pk)
            pathToGroupMemberSolution = os.path.join(pathToAssignedGroupSolution, memberName)

            if not createDirectory(pathToGroupMemberSolution):
                return False

            for exercise in task.test.exercises.all():
                exerciseDirName = getExerciseDirectoryName(exercise)
                exerciseInTestPath = os.path.join(pathToGroupMemberSolution, exerciseDirName)

                if not createDirectory(exerciseInTestPath):
                    return False

    return True

def createDirectoryForTaskSolutions(task):
    # funkcja tworzy folder ktory bedzie przechowywal rozwiazania zadania 'task'
    typeOfTask = task.taskType.name
    print(typeOfTask)
    
    if typeOfTask == "Test":
        createTestSolutionDirectory(task)
    elif typeOfTask == "Exercise":
        createExerciseSolutionDirectory(task)
    else:
        return (
            "Podano niepoprawny rodzaj zadania",
            False
        )

    return True



