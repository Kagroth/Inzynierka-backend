import os
from django.conf import settings
from distutils.dir_util import copy_tree

EXERCISES_TEMPLATES_DIRECTORY_ROOT = "exercises_templates"
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
    cwd = settings.BASE_DIR
    
    return os.path.join(cwd, EXERCISES_DIRECTORY_ROOT, directoryName)

def createExerciseRootDirectory(exercise):
    # funkcja tworzy folder dla konkretnego cwiczenia w folderze glownym dla cwiczen

    directoryName = getExerciseDirectoryName(exercise)
    cwd = settings.BASE_DIR

    pathToExercise = os.path.join(cwd, EXERCISES_DIRECTORY_ROOT, directoryName)

    if exercise.language.name == 'Python':
        return createDirectory(pathToExercise)
    elif exercise.language.name == 'Java':
        rootPathCreated = createDirectory(pathToExercise)

        if rootPathCreated:
            javaTemplateDirPath = os.path.join(cwd, EXERCISES_TEMPLATES_DIRECTORY_ROOT, exercise.language.name.lower())
            print(javaTemplateDirPath)
            copy_tree(javaTemplateDirPath, pathToExercise) # skopiowanie templatki do folderu z cwiczeniem
        
        return rootPathCreated

def createExerciseDirectory(exercise, relPath):
    # funkcja tworzy folder dla cwiczenia exercise w lokalizacji relPath
    directoryName = getExerciseDirectoryName(exercise)
    cwd = settings.BASE_DIR

    pathToExercise = os.path.join(cwd, relPath, directoryName)

    return createDirectory(pathToExercise)


# ************ funkcje dla kolokwium - Tests *********************
def getTestDirectoryName(test):
    # funckja zwraca nazwe folderu dla podanego kolokwium
    return test.title.replace(" ", "") + '-' + test.author.username.replace(" ", "") + '-' + str(test.pk)

def getTestDirectoryRootPath(test):
    # Zwraca lokalizacje w ktorej zapisane jest kolokwium
    directoryName = getTestDirectoryName(test)
    cwd = settings.BASE_DIR
    
    return os.path.join(cwd, TESTS_DIRECTORY_ROOT, directoryName)


def createTestRootDirectory(test):
    # funkcja tworzy folder dla kolokwium 'test' w folderze root dla kolokwium
    directoryName = getTestDirectoryName(test)
    cwd = settings.BASE_DIR
    pathToTest = os.path.join(cwd, TESTS_DIRECTORY_ROOT, directoryName)

    created = createDirectory(pathToTest)

    if created:
        for exercise in test.exercises.all():
            if createExerciseDirectory(exercise, pathToTest):
                exerciseRootPath = getExerciseDirectoryRootPath(exercise)
                exerciseDirName = getExerciseDirectoryName(exercise)
                exerciseInTestDirPath = os.path.join(pathToTest, exerciseDirName)
                print("Bede kopiowal z: " + exerciseRootPath)
                print("Do: " + exerciseInTestDirPath)
                copy_tree(exerciseRootPath, exerciseInTestDirPath)
            else:
                return False        

        return True
    else:
        return False

def createTestDirectory(test, relPath):
    # funkcja tworzy folder dla kolokwium 'test' w lokalizacji relPath
    directoryName = getTestDirectoryName(test)
    cwd = settings.BASE_DIR
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

def getUserSolutionPath(task, group, user, exercise=None):
    if task.taskType.name == "Exercise":    
        taskDirName = getTaskSolutionsDirectoryName(task)
        groupName = group.name + '-' + str(group.pk)
        userName = user.username.replace(" ", "") + '-' + str(user.pk)
        cwd = settings.BASE_DIR

        #if task.exercise.language.name == 'Java':
        #    return os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, taskDirName, groupName, userName, 'src', 'main', 'java')
        
        return os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, taskDirName, groupName, userName)
    else:
        taskDirName = getTaskSolutionsDirectoryName(task)
        groupName = group.name + '-' + str(group.pk)
        userName = user.username.replace(" ", "") + '-' + str(user.pk)
        cwd = settings.BASE_DIR

        return os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, taskDirName, groupName, userName, getExerciseDirectoryName(exercise))   


def createExerciseSolutionDirectory(task):
    # funkcja tworzy strukture katalogow dla zadania typu exercise
    # - RootDir Solutions
    #   - Task dir
    #       - GroupA dir
    #           - UserA solution
    #           - UserB solution
    group = task.assigned_to
    
    directoryName = getTaskSolutionsDirectoryName(task)

    cwd = settings.BASE_DIR
    pathToSolution = os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName)
    
    if not createDirectory(pathToSolution):
        return False

    groupName = group.name + '-' + str(group.pk)
    pathToAssignedGroupSolution = os.path.join(pathToSolution, groupName)
    created = createDirectory(pathToAssignedGroupSolution)

    if not created:
        return False
        
    for member in group.users.all():
        memberName = member.username.replace(" ", "") + '-' + str(member.pk)
        pathToGroupMemberSolution = os.path.join(pathToAssignedGroupSolution, memberName)

        created = createDirectory(pathToGroupMemberSolution)

        if not created:
            return False

        # skopiowanie template z EXERCISES_TEMPLATES_DIRECTORY_ROOT do folderu z rozwiazaniem uzytkownika      
        if task.exercise.language.name == 'Java':
            javaTemplateDirPath = os.path.join(cwd, EXERCISES_TEMPLATES_DIRECTORY_ROOT, task.exercise.language.name.lower())
            copy_tree(javaTemplateDirPath, pathToGroupMemberSolution)

    return True


def createTestSolutionDirectory(task):
    # funkcja tworzy katalog z rozwiazaniem dla kolokwium w postaci:
    # - RootDir Solutions
    #   - Task dir
    #       - GroupA
    #           - UserA dir
    #               - ExerciseA dir
    #               - ExerciseB dir
    group = task.assigned_to 
    directoryName = getTaskSolutionsDirectoryName(task)
    cwd = settings.BASE_DIR
    pathToSolution = os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName)

    if not createDirectory(pathToSolution):
        return False
    
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
                
            if exercise.language.name == 'Java':
                exerciseRootPath = getExerciseDirectoryRootPath(exercise)
                copy_tree(exerciseRootPath, exerciseInTestPath)

    return True

def createDirectoryForTaskSolutions(task):
    # funkcja tworzy folder ktory bedzie przechowywal rozwiazania zadania 'task'
    typeOfTask = task.taskType.name
    print(typeOfTask)
    
    result = False

    if typeOfTask == "Test":
        result = createTestSolutionDirectory(task)
    elif typeOfTask == "Exercise":
        result = createExerciseSolutionDirectory(task)
    else:
        return (
            "Podano niepoprawny rodzaj zadania",
            False
        )

    return result

def createAllUserSolutionDirectory(group, user):
    # funkcja wykorzystywana w momencie dodania nowego uzytkownika do grupy
    # dla tego uzytkownika tworzone sa katalogi z rozwiazaniami w kazdym zadaniu 
    # przypisanym grupie do ktorej zostal dodany
    tasks = group.tasks.all()
    result = False

    for task in tasks:
        task_type = task.taskType.name

        if task_type == "Test":
            directoryName = getTaskSolutionsDirectoryName(task)
            cwd = settings.BASE_DIR
            pathToSolution = os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName)
            
            groupName = group.name + '-' + str(group.pk)
            pathToAssignedGroupSolution = os.path.join(pathToSolution, groupName)
            
            memberName = user.username.replace(" ", "") + '-' + str(user.pk)
            pathToGroupMemberSolution = os.path.join(pathToAssignedGroupSolution, memberName)

            if not createDirectory(pathToGroupMemberSolution):
                return False

            for exercise in task.test.exercises.all():
                exerciseDirName = getExerciseDirectoryName(exercise)
                exerciseInTestPath = os.path.join(pathToGroupMemberSolution, exerciseDirName)

                if not createDirectory(exerciseInTestPath):
                    return False
                        
                if exercise.language.name == 'Java':
                    exerciseRootPath = getExerciseDirectoryRootPath(exercise)
                    copy_tree(exerciseRootPath, exerciseInTestPath)

        elif task_type == "Exercise":            
            directoryName = getTaskSolutionsDirectoryName(task)

            cwd = settings.BASE_DIR
            pathToSolution = os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName)

            groupName = group.name + '-' + str(group.pk)
            pathToAssignedGroupSolution = os.path.join(pathToSolution, groupName)
                
            memberName = user.username.replace(" ", "") + "-" + str(user.pk)
            pathToGroupMemberSolution = os.path.join(pathToAssignedGroupSolution, memberName)

            created = createDirectory(pathToGroupMemberSolution)

            if not created:
                return False

            # skopiowanie template z EXERCISES_TEMPLATES_DIRECTORY_ROOT do folderu z rozwiazaniem uzytkownika      
            if task.exercise.language.name == 'Java':
                javaTemplateDirPath = os.path.join(cwd, EXERCISES_TEMPLATES_DIRECTORY_ROOT, task.exercise.language.name.lower())
                copy_tree(javaTemplateDirPath, pathToGroupMemberSolution)

            result = True
        else:
            return False

    return result

def changeGroupSolutionDirectoryName(group, newGroupName):
    # funkcja zmienia nazwe katalogow z rozwiazaniem 
    tasks = group.tasks.all()
    result = False

    for task in tasks:
        task_type = task.taskType.name
        directoryName = ""

        if task_type == "Test":
            directoryName = getTaskSolutionsDirectoryName(task)
        elif task_type == "Exercise":
            directoryName = getTaskSolutionsDirectoryName(task)
        else:
            return False

        cwd = settings.BASE_DIR
        pathToSolution = os.path.join(cwd, SOLUTIONS_DIRECTORY_ROOT, directoryName)
        
        groupName = group.name + '-' + str(group.pk)
        newGroupNameDir = newGroupName + '-' + str(group.pk)
        
        pathToAssignedGroupSolution = os.path.join(pathToSolution, groupName)
        pathToAssignedGroupSolutionWithNewGroupName = os.path.join(pathToSolution, newGroupNameDir)

        os.rename(pathToAssignedGroupSolution, pathToAssignedGroupSolutionWithNewGroupName)

        result = True

    return result
