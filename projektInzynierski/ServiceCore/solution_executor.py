
import subprocess

from ServiceCore.models import Task, TaskType, SolutionType, Solution, Language
from ServiceCore.utils import *
from django.core.files.storage import FileSystemStorage

class SolutionExecutor():
    def __init__(self):
        self.user = None
        self.task = None
        self.solutionData = None
        self.solutionType = None
        self.readyToRunSolution = False
        self.solutionsToRun = None
        self.testCommand = []
        self.testsResult = []
        self.fs = FileSystemStorage()

    def configure(self, user, task, solutionData):
        self.user = user
        self.task = task
        self.solutionData = solutionData

        if task.taskType == TaskType.objects.get(name="Exercise"):
            self.configureForExercise()
            self.configureRuntime(task.exercise.language) 
   

    def configureForExercise(self):
        self.solutionType = SolutionType.objects.get(name=self.solutionData['solutionType'])

        if self.solutionType.name == 'File':
            # rozwiazanie nadeslane przez plik
            self.solutionsToRun = self.solutionData['file']
            
            if self.solutionsToRun is None:
                print("Nie podano zadnego pliku")
                return

            # sprawdzanie czy przyslany plik ma poprawne rozszerzenie
            extensionToCheck = self.task.exercise.language.allowed_extension

            if not self.solutionsToRun.name.endswith(extensionToCheck):
                print("Niepoprawny format pliku")
                return

            for group in self.task.assignedTo.all():
                self.fs.location = getUserSolutionPath(self.task, group, self.user)
                self.solutionsToRun.name = 'solution' + extensionToCheck
                destinatedPath = os.path.join(self.fs.location, self.solutionsToRun.name)

                if os.path.isfile(destinatedPath):
                    os.remove(destinatedPath)
                
                self.fs.save(self.solutionsToRun.name, self.solutionsToRun)
            
            exercisePath = getExerciseDirectoryRootPath(self.task.exercise)

            # kopiowanie unit testow z katalogu Root Exercise do Root Solution
            if os.path.isdir(exercisePath):
                for subdir, dirs, files in os.walk(exercisePath):
                    for file in files:
                        if os.path.isfile(os.path.join(subdir, file)):
                            # skopiowanie unit testow 
                            copyCommand = 'copy ' + str(os.path.join(subdir, file)) + ' ' + str(os.path.join(self.fs.location, file))
                            os.popen(copyCommand)
                           


    def configureRuntime(self, language):
        if language.name == "Python":
            self.testCommand = ['python', '-m', 'unittest', 'discover', '-v', '-s', self.fs.location]
            self.readyToRunSolution = True
        else:
            self.testCommand = None
            self.readyToRunSolution = False

    def isReadyToRunSolution(self):
        return self.readyToRunSolution

    def run(self):
        if not self.isReadyToRunSolution():
            return (False, "Executor nie jest gotowy do uruchomienia")
        
        with open(os.path.join(self.fs.location, "result.txt"), "w") as result_file:
            process = subprocess.run(self.testCommand, capture_output=True)
            result_file.write(process.stderr.decode("utf-8"))

            newSolution, created = Solution.objects.update_or_create(task=self.task,
                                                                    user=self.user,
                                                                    pathToFile=self.fs.location,
                                                                    rate=2)
            newSolution.save()

        solutionFile = open(os.path.join(self.fs.location, "result.txt"), "r")

        for line in solutionFile.readlines():
                if len(line) == 1:
                    continue
                self.testsResult.append(line)   

        solutionFile.close()

        return (True, "Testowanie zakonczone")                                                                        

        
