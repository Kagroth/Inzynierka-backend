import requests
import logging

from subprocess import PIPE
from shutil import copy

from ServiceCore.models import Solution, SolutionExercise, SolutionTest
from ServiceCore.solution_executor import *
from ServiceCore.unit_tests_utils import get_java_package_name_from_file, insert_java_package_instruction

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
                self.solutionData['filename'] = self.solutionsToRun.name
                # self.solutionsToRun.name = self.solutionData['filename'] = 'Solution' + extensionToCheck
                
                destinatedPath = os.path.join(self.fs.location, 'src', 'main', 'java', self.solutionsToRun.name)

                if os.path.isfile(destinatedPath):
                    os.remove(destinatedPath)
                
                self.fs.save(destinatedPath, self.solutionsToRun)
            
        elif self.solutionType.name == 'Editor':
            # rozwiazanie nadeslane przez edytor
            # Rzutowanie QueryDict na dict
            self.solutionData = dict(self.solutionData)
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
                
                print(self.fs.location, "b")
                self.solutionData['filename'] = 'Solution' + solutionExtension

                destinatedPath = os.path.join(self.fs.location, 'src', 'main', 'java', self.solutionData['filename'])
                
                try:
                    with open(destinatedPath, 'w') as solution_file:
                        solution_file.write("package solution; \n")

                    with open(destinatedPath, 'a') as solution_file:
                        solution_file.write(self.solutionsToRun[0])
                except Exception as e:
                    self.logger.info("Nie udalo sie zapisac rozwiazania - " + str(e))

        elif self.solutionType.name == 'GitHub-Repository':
            solution_path = getUserSolutionPath(self.task, self.task.assignedTo.first(), self.user)            
            self.fs.location = solution_path
            solution_path = os.path.join(solution_path, 'src', 'main', 'java')
            self.logger.info("Zmiana katalogu roboczego na " + solution_path)
            os.chdir(solution_path)
            
            # pobieranie pliku z repozytorium
            try:
                solution_file_binary = requests.get(self.solutionData['fileDownloadURL'])

                with open(self.solutionData['filename'], 'wb') as solution_file:
                    solution_file.write(solution_file_binary.content)
                
                self.logger.info("Pobrano " +  self.solutionData['fileDownloadURL'] + " i zapisano plik: " + self.solutionData['filename'] )
                os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
            except Exception as e:
                self.logger.info("Nastapil blad pobierania pliku z GitHub i jego zapisania: " + str(e))
                self.readyToRunSolution = False
                os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                return
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
        self.readyToRunSolution = True

    def copyUnitTestsToSolutionDir(self, exercisePath):
        # kopiowanie unit testow z katalogu Root Exercise do Root Solution
        if os.path.isdir(exercisePath):
            for subdir, dirs, files in os.walk(exercisePath):
                for file in files:
                    if os.path.isfile(os.path.join(subdir, file)):
                        # skopiowanie unit testow
                        if not file.endswith(".java"):
                            continue

                        solution_file_path = os.path.join(self.fs.location, 'src', 'main', 'java', self.solutionData['filename'])
                        package_name = get_java_package_name_from_file(solution_file_path)
                        
                        if not package_name:
                            # brak instrukcji package, trzeba ja dodac
                            package_name = "solution"
                            solution_file_tmp = ""
                            
                            with open(solution_file_path, "r") as solution_file:
                                solution_file_tmp = solution_file.read()
                            
                            with open(solution_file_path, "w") as solution_file:
                                solution_file.write("package " + package_name + "; \n")
                            
                            with open(solution_file_path, "a") as solution_file:
                                solution_file.write(solution_file_tmp)

                        source_path = os.path.join(subdir, file)
                        destination_path = os.path.join(self.fs.location, 'src', 'test', 'java', file)
                        
                        copy(source_path, destination_path)

                        result = insert_java_package_instruction(destination_path, package_name)
                        
                        if not result:
                            self.readyToRunSolution = False
                            return

            self.readyToRunSolution = True

    def run(self):
        if not self.isReady():
            self.logger.info("Executor nie jest gotowy do uruchomienia")
            return (False, False, "Executor nie jest gotowy do uruchomienia")

        solution_exercise = None
        
        try:
            os.chdir(self.fs.location) # zmiana folderu roboczego w celu uruchomienia testowania mavena
            process = subprocess.run(self.testCommand, stdout=PIPE, stderr=PIPE, shell=True) # uruchomienie testow

            process_out = process.stdout.decode("utf-8")           
            process_err = process.stderr.decode("utf-8")

            print(process_out)
            print(process_err)

            with open(os.path.join(self.fs.location, "result.txt"), "w") as result_file:                
                result_file.write(process_out)                       
                result_file.write(process_err)

                main_solution_object = Solution.objects.get(task=self.task, user=self.user)

                solution_exercise, create = SolutionExercise.objects.update_or_create(solution=main_solution_object,
                                                                        pathToFile=os.path.join(self.fs.location, 'src', 'main', 'java', self.solutionData['filename']))
                
                if solution_exercise.exercise is None:
                    if self.task.taskType.name == 'Exercise':
                        solution_exercise.exercise = self.task.exercise
                    else:
                        solution_exercise.exercise = self.task.test.exercises.get(pk=self.solutionData['exercisePk'])
                
                solution_exercise.save()
                
                if self.task.taskType.name == 'Test':
                    test_solution, created = SolutionTest.objects.update_or_create(solution=main_solution_object)
                    solution_exercise.test = test_solution
                    test_solution.save()
                    solution_exercise.save()
                
                if self.solutionType.name == 'GitHub-Repository':
                    solution_exercise.github_link = self.solutionData['repositoryURL']
                  
                solution_exercise.save()
        except Exception as e:
            os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))            
            self.logger.info("Nie udalo sie przetestowac kodu - " + str(e))
            return (False, False, "Nie udalo sie przetestowac kodu")

        
        unit_tests_passed = False

        try:            
            with open(os.path.join(self.fs.location, 'target', 'surefire-reports', 'UnitTest.txt'), "r") as result_file:
                file_lines = result_file.readlines()

                file_lines_without_newline_chars = [line for line in file_lines if line != '\n']

                # pobranie liczby testow FAILURES
                fail_number = file_lines_without_newline_chars[-1].split(',')[1].split(':')[-1]
                fail_number = int(fail_number)

                if fail_number > 0:
                    unit_tests_passed = False
                else:
                    unit_tests_passed = True

                for line in file_lines_without_newline_chars:
                    if len(line) == 1:
                        continue
                    self.testsResult.append(line) 

        except Exception as e:
            self.logger.info("Nie udalo sie odczytac wynikow testowania z surefire_reports - " + str(e))
            result_message = ""

            try:
                with open(os.path.join(self.fs.location, 'result.txt')) as result_file:
                    for line in result_file.readlines():
                        if len(line) == 1:
                            continue
                        self.testsResult.append(line)
                result_message = "Testy niezaliczone"
            except Exception as ex:
                self.logger.info("Nie udalo sie odczytac wynikow testowania z result.txt - " + str(ex))
                result_message = "Nie udalo sie odczytac wynikow testowania"
            finally:
                # powrot do glownego folderu
                os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))           
            
            return (False, False, result_message)
        
        # powrot do glownego folderu
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        return (True, unit_tests_passed, "Testowanie zakonczone pomyslnie")      