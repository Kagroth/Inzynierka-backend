import os
from distutils.dir_util import copy_tree

EXERCISES_DIRECTORY_ROOT = "exercises"
TESTS_DIRECTORY_ROOT = "exercises_tests"
SOLUTIONS_DIRECTORY_ROOT = "solutions"

# funkcja dla kazdego uzytkownika w kazdej grupie tworzy folder w ktorym bedzie 
# przechowywane rozwiazanie zadania konkretnego uzytkownika
def createSubdirectoryForUsersInGroup(group, groupSolutionsPath):
    for member in group.users.all():
        memberName = member.username.replace(" ", "") + '-' + str(member.pk)
        pathToGroupMemberSolution = os.path.join(groupSolutionsPath, memberName)

        if not os.path.exists(pathToGroupMemberSolution):
            os.mkdir(pathToGroupMemberSolution)
        else:
            print("Nie udalo sie utworzyc folderu dla uzytkownika " + memberName)
            print("w grupie " + group.name)
            return (
                "Nie udalo sie utworzyc folderu dla uzytkownika " + memberName,
                False
            )

    return (
        "Pomyslnie utworzono podfoldery dla grupy " + group.name,
        True
    )    



# funkcja tworzy podfolder w folderze z rozwiazaniami zadania 'task' dla kazdej z przypisanych grup
def createSubdirectoryForAssignedGroup(task, solutionPath):
    for group in task.assignedTo.all():
        groupName = group.name + '-' + str(group.pk)
        pathToAssignedGroupSolution = os.path.join(solutionPath, groupName)

        if not os.path.exists(pathToAssignedGroupSolution):
            os.mkdir(pathToAssignedGroupSolution)
        else:
            return (
                "Podfolder dla podanej grupy juz istnieje",
                False
            )
        
        (message, result) = createSubdirectoryForUsersInGroup(group, pathToAssignedGroupSolution)

        if not result:
            print(message)
            return (
                message,
                False
            )

    return (
        "Pomyslnie utworzono podfoldery dla zadania " + task.title,
        True
    )


# funkcja tworzy folder ktory bedzie przechowywal rozwiazania zadania 'task'
def createDirectoryForTaskSolutions(task):
    typeOfTask = task.taskType.name

    if typeOfTask == "Test":
        # utworzenie katalogow dla kolokwium
        pass
    elif typeOfTask == "Exercise":
        # utworzenie katalogu dla exercise
        pass
    else:
        return (
            "Podano niepoprawny rodzaj zadania",
            False
        )

    directoryName = task.title.replace(" ", "") + '-' + task.author.username.replace(" ", "") + '-' + str(task.pk)

    cwd = os.getcwd()
    pathToTaskSolutions = os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName)

    if not os.path.exists(pathToTaskSolutions):
        os.mkdir(pathToTaskSolutions)
    else:
        print("Utworzono zadanie ale nie udalo sie utworzyc folderu")
        return (
            "Folder o podanej nazwie juz istnieje",
            False
        )

    (message, result) = createSubdirectoryForAssignedGroup(task, pathToTaskSolutions)
    print(message)
    print(result)


# funkcja tworzy folder dla konkretnego cwiczenia
def createExerciseDirectory(exercise):
    directoryName = getExerciseDirectoryName(exercise)
    cwd = os.getcwd()
    pathToExercise = os.path.join(cwd, EXERCISES_DIRECTORY_ROOT, directoryName)

    if not os.path.exists(pathToExercise):
        os.mkdir(pathToExercise)
        return (
            "Utworzono folder dla cwiczenia",
            True
        )
    else:
        print()
        return (
            "Nie udalo sie utworzyc folderu dla tego cwiczenia",
            False
        )

# funkcja tworzy folder dla kolokwium 'test'
def createTestDirectory(test):
    directoryName = getTestDirectoryName(test)
    cwd = os.getcwd()
    pathToTest = os.path.join(cwd, TESTS_DIRECTORY_ROOT, directoryName)

    if not os.path.exists(pathToTest):
        os.mkdir(pathToTest)

        for exercise in test.exercises.all():
            exercisePath = getExerciseDirectoryPath(exercise)
            exerciseDirectoryName = getExerciseDirectoryName(exercise)
            exerciseInTestPath = os.path.join(pathToTest, exerciseDirectoryName)

            copy_tree(exercisePath, exerciseInTestPath)

        return (
            "Utworzono folder dla kolokwium",
            True
        )
    else:
        print()
        return (
            "Nie udalo sie utworzyc folderu dla tego kolokwium",
            False
        )

# funkcja zwraca nazwe folderu odpowiednia dla podanego cwiczenia
def getExerciseDirectoryName(exercise):
    return exercise.title.replace(" ", "") + '-' + exercise.author.username.replace(" ", "") + '-' + str(exercise.pk)

# funckaj zwraca nazwe folderu dla podanego kolokwium
def getTestDirectoryName(test):
    return test.title.replace(" ", "") + '-' + test.author.username.replace(" ", "") + '-' + str(test.pk)

# funkcja zwraca sciezke do folderu z konkretnym cwiczeniem w ktorym sa skladowane unit testy
def getExerciseDirectoryPath(exercise):
    directoryName = getExerciseDirectoryName(exercise)
    cwd = os.getcwd()
    
    return os.path.join(cwd, EXERCISES_DIRECTORY_ROOT, directoryName)

# funkcja zwraca sciezke do rozwiazania zadania przez uzytkownika
def getUserSolutionPath(task, group, user):
    directoryName = task.title.replace(" ", "") + '-' + task.author.username.replace(" ", "") + '-' + str(task.pk)
    groupName = group.name.replace(" ", "") + '-' + str(group.pk)
    memberName = user.username.replace(" ", "") + '-' + str(user.pk)

    cwd = os.getcwd()

    return os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName, groupName, memberName)