import os

def createSubdirectoryForUsersInGroup(group, groupSolutionsPath):
    for member in group.users.all():
        memberName = member.username + '-' + str(member.pk)
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


def createDirectoryForTaskSolutions(task):
    directoryName = task.title + '-' + task.author.username + '-' + str(task.pk)

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


def createExerciseDirectory(exercise):
    directoryName = exercise.title + '-' + exercise.author.username + '-' + str(exercise.pk)
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

def getExerciseDirectoryPath(exercise):
    directoryName = exercise.title + '-' + exercise.author.username + '-' + str(exercise.pk)
    cwd = os.getcwd()
    
    return os.path.join(cwd, 'exercises', directoryName)