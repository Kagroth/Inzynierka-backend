
import logging

from ServiceCore.solution_executor import *

class JavaExecutor(SolutionExecutor):
    def __init__(self):
        SolutionExecutor.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.testCommand = ['mvn', 'clean', 'test']
    
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
                
                destinatedPath = os.path.join(self.fs.location, 'src', 'main', 'java', self.solutionsToRun.name)

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

                destinatedPath = os.path.join(self.fs.location, 'src', 'main', 'java', solutionFileName)
                
                try:
                    with open(destinatedPath, 'w+') as solution_file:
                        solution_file.write(self.solutionsToRun)
                except Exception as e:
                    self.logger.info("Nie udalo sie zapisac rozwiazania - " + str(e))

        elif self.solutionType.name == 'GitHub-Repository':
            '''
            zmiana katalogu - chdir
            git init
            git remote add origin repository
            git pull origin master
            get first java file
            rename to Solution.java
            zmiana katalogu na katalog glowny
            '''
            solution_path = getUserSolutionPath(self.task, self.task.assignedTo.first(), self.user)            
            self.fs.location = solution_path
            solution_path = os.path.join(solution_path, 'src', 'main', 'java')
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

            if "Solution.java" not in files:
                for f in files:
                    if f.endswith(self.task.exercise.language.allowed_extension):
                        old_filename_path = os.path.join(os.getcwd(), f)
                        new_filename_path = os.path.join(os.getcwd(), "Solution.java")
                        
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
            
        # pobranie sciezki do glownego katalogu cwiczenia i przekopiowanie z niego unit testow
        exercisePath = None
        
        if self.task.taskType.name == 'Exercise':
            exercisePath = getExerciseDirectoryRootPath(self.task.exercise)
        else:
            exercisePath = getExerciseDirectoryRootPath(self.task.test.exercises.get(pk=self.solutionData['exercisePk']))


        self.copyUnitTestsToSolutionDir(exercisePath)

    def copyUnitTestsToSolutionDir(self, exercisePath):
        # kopiowanie unit testow z katalogu Root Exercise do Root Solution
        if os.path.isdir(exercisePath):
            for subdir, dirs, files in os.walk(exercisePath):
                for file in files:
                    if os.path.isfile(os.path.join(subdir, file)):
                        # skopiowanie unit testow
                        copyCommand = 'copy ' + str(os.path.join(subdir, file)) + ' ' + str(os.path.join(self.fs.location, 'src', 'test', 'java'))
                        
                        print(copyCommand)
                        os.popen(copyCommand)

    def run(self):
        newSolution = None
        
        try:
            with open(os.path.join(self.fs.location, "result.txt"), "w") as result_file:
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
        except Exception as e:            
            self.logger.info("Nie udalo sie przetestowac kodu - " + str(e))
            return (False, "Nie udalo sie przetestowac kodu")

        try:            
            with open(os.path.join(self.fs.location, 'target', 'surefire-reports', 'Unit0Test.txt'), "r") as result_file:
                 
                for line in result_file.readlines():
                    if len(line) == 1:
                        continue
                    self.testsResult.append(line) 

        except Exception as e:
            self.logger.info("Nie udalo sie odczytac wynikow testowania - " + str(e))
            # powrot do glownego folderu
            os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return (False, "Nie udalo sie odczytac wynikow")
        
        # powrot do glownego folderu
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        return (True, "Testowanie zakonczone")      