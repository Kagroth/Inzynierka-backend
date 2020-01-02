
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
        else:
            self.configureForTest()
            self.configureRuntime(task.test.exercises.get(pk=self.solutionData['exercisePk']).language)         
   

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
                print("A" + self.fs.location)
                self.solutionsToRun.name = 'Solution' + extensionToCheck
                destinatedPath = None

                if self.task.exercise.language.name == 'Java':
                    destinatedPath = os.path.join(self.fs.location, 'src', 'main', 'java', self.solutionsToRun.name)
                else:
                    destinatedPath = os.path.join(self.fs.location, self.solutionsToRun.name)

                print("B" + self.fs.location)

                if os.path.isfile(destinatedPath):
                    os.remove(destinatedPath)
                
                self.fs.save(destinatedPath, self.solutionsToRun)
            
            
                           
        elif self.solutionType.name == 'Editor':
            # rozwiazanie nadeslane przez edytor
            self.solutionsToRun = self.solutionData['solution']
            
            if self.solutionsToRun is None:
                print("Nie przyslano rozwiazania")
                return
            
            solutionExtension = self.task.exercise.language.allowed_extension

            # tworze plik z rozwiazaniem
            for group in self.task.assignedTo.all():
                self.fs.location = getUserSolutionPath(self.task, group, self.user)
                print(self.fs.location)
                solutionFileName = 'solution' + solutionExtension
                destinatedPath = os.path.join(self.fs.location, solutionFileName)

                with open(destinatedPath, 'w+') as solution_file:
                    solution_file.write(self.solutionsToRun)
            

        # pobranie sciezki do glownego katalogu cwiczenia i przekopiowanie z niego unit testow
        exercisePath = getExerciseDirectoryRootPath(self.task.exercise)
        dest = None

        if self.task.exercise.language.name == 'Java':
            exercisePath = os.path.join(exercisePath, 'src', 'test', 'java')
            dest = os.path.join(self.fs.location, 'src', 'test', 'java')

        self.copyUnitTestsToSolutionDir(exercisePath, dest)
        

    def configureForTest(self):
        self.solutionType = SolutionType.objects.get(name=self.solutionData['solutionType'])

        if self.solutionType.name == 'Editor':
            # rozwiazanie nadeslane przez edytor
            self.solutionsToRun = self.solutionData['solution']
            
            if self.solutionsToRun is None:
                print("Nie przyslano rozwiazania")
                return
            
            # solutionExtension = self.task.exercise.language.allowed_extension
            solutionExtension = self.task.test.exercises.get(pk=self.solutionData['exercisePk']).language.allowed_extension

            # tworze plik z rozwiazaniem
            for group in self.task.assignedTo.all():
                self.fs.location = getUserSolutionPath(self.task, group, self.user, self.task.test.exercises.get(pk=self.solutionData['exercisePk']))
                print(self.fs.location)
                solutionFileName = 'solution' + solutionExtension
                destinatedPath = os.path.join(self.fs.location, solutionFileName)

                with open(destinatedPath, 'w+') as solution_file:
                    solution_file.write(self.solutionsToRun)

            # pobranie sciezki do glownego katalogu cwiczenia i przekopiowanie z niego unit testow
            exercisePath = getExerciseDirectoryRootPath(self.task.test.exercises.get(pk=self.solutionData['exercisePk']))
            self.copyUnitTestsToSolutionDir(exercisePath)
   
    def configureRuntime(self, language):
        if language.name == "Python":
            self.testCommand = ['python', '-m', 'unittest', 'discover', '-v', '-s', self.fs.location]
            self.readyToRunSolution = True
        elif language.name == "Java":
            self.testCommand = ['mvn', 'clean', 'test']
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
            if self.task.taskType.name == 'Exercise':
                if self.task.exercise.language.name == 'Java':
                    os.chdir(self.fs.location) # zmiana folderu roboczego w celu uruchomienia testowania mavena

            process = subprocess.run(self.testCommand, capture_output=True, shell=True)

                          
            result_file.write(process.stdout.decode("utf-8"))                           
            result_file.write(process.stderr.decode("utf-8"))

            print(process.stdout.decode("utf-8"))
            print(process.stderr.decode("utf-8"))
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
        
        # powrot do glownego folderu
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        return (True, "Testowanie zakonczone")                                                                        


    def copyUnitTestsToSolutionDir(self, exercisePath, destination=None):
        # kopiowanie unit testow z katalogu Root Exercise do Root Solution
        if os.path.isdir(exercisePath):
            for subdir, dirs, files in os.walk(exercisePath):
                for file in files:
                    if os.path.isfile(os.path.join(subdir, file)):
                        # skopiowanie unit testow
                        copyCommand = ""
                        if destination is not None:
                            copyCommand = 'copy ' + str(os.path.join(subdir, file)) + ' ' + destination
                        else:
                            copyCommand = 'copy ' + str(os.path.join(subdir, file)) + ' ' + str(os.path.join(self.fs.location, file))
                        print(destination)
                        print(copyCommand)
                        os.popen(copyCommand)