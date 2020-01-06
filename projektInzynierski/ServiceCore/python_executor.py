
import logging

from ServiceCore.solution_executor import *

class PythonExecutor(SolutionExecutor):
    def __init__(self):
        SolutionExecutor.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.testCommand = self.testCommand = ['python', '-m', 'unittest', 'discover', '-v', '-s']

    def configureRuntime(self):
        self.solutionType = SolutionType.objects.get(name=self.solutionData['solutionType'])
        
        if self.solutionType.name == 'File':
            # rozwiazanie nadeslane przez plik
            self.solutionsToRun = self.solutionData['file']

            if self.solutionsToRun is None:
                self.logger.info("Nie podano zadnego pliku")
                return

             # sprawdzanie czy przyslany plik ma poprawne rozszerzenie
            extensionToCheck = self.task.exercise.language.allowed_extension
            
            if not self.solutionsToRun.name.endswith(extensionToCheck):
                self.logger.info("Niepoprawny format pliku")
                return
            
            # iterowanie po wszystkich grupach mimo ze powinna byc tylko jedna
            for group in self.task.assignedTo.all():
                self.fs.location = getUserSolutionPath(self.task, group, self.user)
                self.solutionsToRun.name = 'Solution' + extensionToCheck
                
                destinatedPath = os.path.join(self.fs.location, self.solutionsToRun.name)

                if os.path.isfile(destinatedPath):
                    os.remove(destinatedPath)
                
                self.fs.save(destinatedPath, self.solutionsToRun)
        
        elif self.solutionType.name == 'Editor':
            # rozwiazanie nadeslane przez edytor
            self.solutionsToRun = self.solutionData['solution']

            if self.solutionsToRun is None:
                self.logger.info("Nie przyslano rozwiazania")
                return
            
            solutionExtension = None

            if self.task.taskType.name == 'Exercise':
                solutionExtension = self.task.exercise.language.allowed_extension
            else:
                solutionExtension = self.task.test.exercises.get(pk=self.solutionData['exercisePk']).language.allowed_extension
            
            # tworze plik z rozwiazaniem
            for group in self.task.assignedTo.all():
                if self.task.taskType.name == 'Exercise':
                    self.fs.location = getUserSolutionPath(self.task, group, self.user)
                else:
                    self.fs.location = getUserSolutionPath(self.task, group, self.user, self.task.test.exercises.get(pk=self.solutionData['exercisePk']))
                
                print(self.fs.location)
                solutionFileName = 'Solution' + solutionExtension
                
                destinatedPath = os.path.join(self.fs.location, solutionFileName)                

                try:
                    with open(destinatedPath, 'w+') as solution_file:
                        solution_file.write(self.solutionsToRun)
                except Exception as e:
                    self.logger.info("Nie udalo sie zapisac rozwiazania - " + str(e))

        elif self.solutionType.name == 'GitHub-Repository':
            '''
                zmiana katalogu - chdir
                git init
                git add remote origin repository
                git pull origin master
                git get first py file
                rename to Solution.py
                zmiana katalogu na katalog glowny
            '''
            solution_path = getUserSolutionPath(self.task, self.task.assignedTo.first(), self.user)
            self.fs.location = solution_path
            self.logger.info("Zmiana katalogu roboczego na " + solution_path)
            os.chdir(solution_path)

            git_commands = [
                ['git', 'init'],
                ['git', 'remote', 'add', 'origin', self.solutionData['repository']],
                ['git', 'pull', 'origin', 'master']
            ]

            for git_command in git_commands:
                process = subprocess.run(git_command, capture_output=True, shell=True)
                self.logger.info("Wynik wykonania instrukcji " + \
                                " ".join(git_command) + \
                                " - " + str(process.stdout.decode("utf-8")) + \
                                str(process.stderr.decode("utf-8")))
            
            # jezeli w folderze nie ma pliku o 'nazwie Solution.py'
            # to bierzemy 1 plik o rozszerzeniu allowed extension (.py) i zmieniamy 
            # jego nazwe na Solution.py
            files = os.listdir(path=os.getcwd())

            if "Solution.py" not in files:
                for f in files:
                    if f.endswith(self.task.exercise.language.allowed_extension):
                        old_filename_path = os.path.join(os.getcwd(), f)
                        new_filename_path = os.path.join(os.getcwd(), "Solution.py")
                        
                        if os.path.isfile(new_filename_path):
                            os.remove(new_filename_path)
                        
                        os.rename(old_filename_path, new_filename_path)
                        break

            self.logger.info("Powrot do katalogu glownego")
            os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        else:
            self.logger.info("Niepoprawny rodzaj rozwiazania - " + self.solutionType.name)
            self.readyToRunSolution = False
            return

        # update command - dodanie lokalizacji self.fs.location do polecenia 
        self.testCommand.append(self.fs.location)

        # pobranie sciezki do glownego katalogu cwiczenia i przekopiowanie z niego unit testow
        exercisePath = None

        if self.task.taskType.name == 'Exercise':
            exercisePath = getExerciseDirectoryRootPath(self.task.exercise)
        else:
            exercisePath = getExerciseDirectoryRootPath(self.task.test.exercises.get(pk=self.solutionData['exercisePk']))

        self.copyUnitTestsToSolutionDir(exercisePath)

        self.readyToRunSolution = True
    
    def copyUnitTestsToSolutionDir(self, exercisePath):
        # kopiowanie unit testow z katalogu Root Exercise do Root Solution
        if os.path.isdir(exercisePath):
            for subdir, dirs, files in os.walk(exercisePath):
                for file in files:
                    if os.path.isfile(os.path.join(subdir, file)):
                        # skopiowanie unit testow
                        copyCommand = 'copy ' + str(os.path.join(subdir, file)) + ' ' + str(os.path.join(self.fs.location, file))
                        print(copyCommand)
                        os.popen(copyCommand)
    
    def run(self):
        if not self.isReady():
            self.logger.info("Executor nie jest gotowy do uruchomienia")

        newSolution = None

        try:
            with open(os.path.join(self.fs.location, "result.txt"), "w") as result_file:
                self.logger.info(os.getcwd())
                self.logger.info(self.testCommand)
                process = subprocess.run(self.testCommand, capture_output=True, shell=True)
                            
                result_file.write(process.stdout.decode("utf-8"))                           
                result_file.write(process.stderr.decode("utf-8"))

                print(process.stdout.decode("utf-8"))
                print(process.stderr.decode("utf-8"))

                newSolution, created = Solution.objects.update_or_create(task=self.task,
                                                                        user=self.user,
                                                                        pathToFile=self.fs.location,
                                                                        rate=2)
                if self.solutionType.name == 'GitHub-Repository':
                    newSolution.github_link = self.solutionData['repository']
                
                newSolution.save()
        except Exception as e:
            self.logger.info("Nie udalo sie przetestowac kodu - " + str(e))
            return (False, "Nie udalo sie przetestowac kodu")

        try:
            with open(os.path.join(self.fs.location, "result.txt"), "r") as result_file:            
                for line in result_file.readlines():
                    if len(line) == 1:
                        continue
                    self.testsResult.append(line) 
                
        except Exception as e:
            self.logger.info("Nie udalo sie odczytac wynikow testowania")
            return (False, "Nie udalo sie zapisac wynikow")

        self.logger.info("Testowanie rozwiazania pk=" + str(newSolution.pk) + " zakonczone pomyslnie")
        return (True, "Testowanie zakonczone")  