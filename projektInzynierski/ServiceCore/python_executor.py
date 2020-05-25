
import logging
import requests

from subprocess import PIPE
from shutil import copy

from ServiceCore.models import Solution, SolutionExercise, SolutionTest, Exercise
from ServiceCore.solution_executor import *
from ServiceCore.unit_tests_utils import insert_python_import_instruction

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
            
            group = self.task.assigned_to

            self.fs.location = getUserSolutionPath(self.task, group, self.user)
            self.solutionsToRun.name = self.solutionData['filename'] = 'solution' + extensionToCheck
                
            destinatedPath = os.path.join(self.fs.location, self.solutionsToRun.name)

            if os.path.isfile(destinatedPath):
                os.remove(destinatedPath)
                
            self.fs.save(destinatedPath, self.solutionsToRun)
        
        elif self.solutionType.name == 'Editor':
            # rozwiazanie nadeslane przez edytor
            # Rzutowanie QueryDict na dict
            self.solutionData = dict(self.solutionData)
            print(self.solutionData['solution'])
            self.solutionsToRun = self.solutionData['solution']
            
            if self.solutionsToRun is None:
                self.logger.info("Nie przyslano rozwiazania")
                return
            
            solutionExtension = None

            if self.task.taskType.name == 'Exercise':
                solutionExtension = self.task.exercise.language.allowed_extension
            else:
                exercise_pk = str(self.solutionData['exercisePk'][0])
                solutionExtension = self.task.test.exercises.get(pk=exercise_pk).language.allowed_extension
            
            # tworze plik z rozwiazaniem
            group = self.task.assigned_to
                
            if self.task.taskType.name == 'Exercise':
                self.fs.location = getUserSolutionPath(self.task, group, self.user)
            else:
                exercise_pk = str(self.solutionData['exercisePk'][0])
                self.fs.location = getUserSolutionPath(self.task, group, self.user, self.task.test.exercises.get(pk=exercise_pk))
                
            print(self.fs.location)
            self.solutionData['filename'] = 'solution' + solutionExtension
                
            destinatedPath = os.path.join(self.fs.location, self.solutionData['filename'])                

            try:
                with open(destinatedPath, 'w+') as solution_file:
                    solution_file.write(self.solutionData['solution'][0])
            except Exception as e:
                self.logger.info("Nie udalo sie zapisac rozwiazania - " + str(e))

        elif self.solutionType.name == 'GitHub-Repository':
            solution_path = getUserSolutionPath(self.task, self.task.assigned_to, self.user)
            self.fs.location = solution_path
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
        
        # update command - dodanie lokalizacji self.fs.location do polecenia 
        self.testCommand.append(self.fs.location)

        # pobranie sciezki do glownego katalogu cwiczenia i przekopiowanie z niego unit testow
        exercisePath = None

        if self.task.taskType.name == 'Exercise':
            exercisePath = getExerciseDirectoryRootPath(self.task.exercise)
        else:
            exercise_pk = str(self.solutionData['exercisePk'][0])
            exercisePath = getExerciseDirectoryRootPath(self.task.test.exercises.get(pk=exercise_pk))

        self.copyUnitTestsToSolutionDir(exercisePath)

        self.readyToRunSolution = True
    
    def copyUnitTestsToSolutionDir(self, exercisePath):
        # kopiowanie unit testow z katalogu Root Exercise do Root Solution
        # oraz dodanie do kazdego testu instrukcji import
        if os.path.isdir(exercisePath):
            for subdir, dirs, files in os.walk(exercisePath):
                for file in files:
                    if os.path.isfile(os.path.join(subdir, file)):
                        # skopiowanie unit testow
                        source_path = os.path.join(subdir, file)
                        destination_path = os.path.join(self.fs.location, file)
                        copy(source_path, destination_path)

                        result = insert_python_import_instruction(destination_path, self.solutionData['filename'])
                        
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
            with open(os.path.join(self.fs.location, "result.txt"), "w") as result_file:
                self.logger.info(os.getcwd())
                self.logger.info(self.testCommand)
                process = subprocess.run(self.testCommand, stdout=PIPE, stderr=PIPE, shell=False)
                            
                result_file.write(process.stdout.decode("utf-8"))                           
                result_file.write(process.stderr.decode("utf-8"))

                print(process.stdout.decode("utf-8"))
                print(process.stderr.decode("utf-8"))

                main_solution_object = Solution.objects.get(task=self.task, user=self.user)
                solution_exercise, created = SolutionExercise.objects.update_or_create(solution=main_solution_object,
                                                        pathToFile=os.path.join(self.fs.location, self.solutionData['filename']))
                
                if solution_exercise.exercise is None:
                    if self.task.taskType.name == 'Exercise':
                        solution_exercise.exercise = self.task.exercise
                    else:
                        exercise_pk = str(self.solutionData['exercisePk'][0])
                        solution_exercise.exercise = self.task.test.exercises.get(pk=exercise_pk)
                
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
            self.logger.info("Nie udalo sie przetestowac kodu - " + str(e))
            return (False, False, "Nie udalo sie przetestowac kodu")

        unit_tests_passed = False

        try:
            with open(os.path.join(self.fs.location, "result.txt"), "r") as result_file:            
                file_lines = result_file.readlines()
                
                file_lines_without_newline_chars = [line for line in file_lines if line != '\n']

                if "OK" in file_lines_without_newline_chars[-1]:
                    unit_tests_passed = True
                else:
                    unit_tests_passed = False

                for line in file_lines:
                    if len(line) == 1:
                        continue
                    self.testsResult.append(line) 
                
        except Exception as e:
            self.logger.info("Nie udalo sie odczytac wynikow testowania")
            return (True, False, "Nie udalo sie zapisac wynikow")

        self.logger.info("Testowanie rozwiazania pk=" + str(solution_exercise.pk) + " zakonczone pomyslnie")
        return (True, unit_tests_passed, "Testowanie zakonczone")  