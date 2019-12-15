import os

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
    directoryName = task.title.replace(" ", "") + '-' + task.author.username.replace(" ", "") + '-' + str(task.pk)

    cwd = os.getcwd()
    pathToTaskSolutions = os.path.join(cwd, 'solutions', directoryName)

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
    directoryName = exercise.title.replace(" ", "") + '-' + exercise.author.username.replace(" ", "") + '-' + str(exercise.pk)
    cwd = os.getcwd()
    pathToExercise = os.path.join(cwd, 'exercises', directoryName)

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

# funkcja zwraca sciezke do folderu z konkretnym cwiczeniem w ktorym sa skladowane unit testy
def getExerciseDirectoryPath(exercise):
    directoryName = exercise.title.replace(" ", "") + '-' + exercise.author.username.replace(" ", "") + '-' + str(exercise.pk)
    cwd = os.getcwd()
    
    return os.path.join(cwd, 'exercises', directoryName)

# funkcja zwraca sciezke do rozwiazania zadania przez uzytkownika
def getUserSolutionPath(task, group, user):
    directoryName = task.title.replace(" ", "") + '-' + task.author.username.replace(" ", "") + '-' + str(task.pk)
    groupName = group.name.replace(" ", "") + '-' + str(group.pk)
    memberName = user.username.replace(" ", "") + '-' + str(user.pk)

    cwd = os.getcwd()

    return os.path.join(cwd, 'solutions', directoryName, groupName, memberName)