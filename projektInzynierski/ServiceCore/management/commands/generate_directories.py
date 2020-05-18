from django.core.management.base import BaseCommand, CommandError
from ServiceCore.models import Task, Exercise, Test, UnitTest
from ServiceCore.utils import createExerciseRootDirectory, createTestRootDirectory, createDirectoryForTaskSolutions
from ServiceCore.unit_tests_utils import create_unit_tests

class Command(BaseCommand):
    def handle(self, *args, **options):
        # tworzenie cwiczen (w folderze exercises)
        exercises = Exercise.objects.all()

        for exercise in exercises:
            try:
                unit_tests = UnitTest.objects.filter(exercise=exercise)

                if createExerciseRootDirectory(exercise):
                    unit_tests_list = [unit_test.content for unit_test in unit_tests]
                    create_unit_tests(exercise, unit_tests_list, save_model=False)
                    self.stdout.write("Katalog dla ćwiczenia {} utworzony\n".format(exercise.title))
                else:
                    raise CommandError("Nie udało się utworzyć katalogu dla ćwiczenia {}".format(exercise.title))                    
            except Exception as e:
                self.stdout.write("Nie udalo sie utworzyc struktury katalogowej dla ćwiczeń (obiektów Exercise)")
                return

        # tworzenie katalogów kolokwium (w folderze exercises_tests)
        tests = Test.objects.all()

        for test in tests:
            try:
                if createTestRootDirectory(test):
                    self.stdout.write("Katalog dla kolokwium {} utworzony\n".format(test.title))
                else:
                    raise CommandError("Nie udało się utworzyć katalogu dla kolokwium {}".format(test.title))                    
            except Exception as e:
                self.stdout.write("Nie udalo sie utworzyc struktury katalogowej dla kolokwium (obiektów Test)")
                return



        # tworzenie katalogów zadan (w folderze solutions)
        tasks = Task.objects.all()

        for task in tasks:
            try:
                if createDirectoryForTaskSolutions(task):
                    self.stdout.write("Katalog dla zadania {} utworzony".format(task.title))
                else:
                    raise CommandError("Nie udało się utworzyć katalogu dla zadania {}".format(task.title))

            except Exception as e:
                self.stdout.write("Nie udalo sie utworzyc struktury katalogowej dla zadań (obiektów Task)")
                return
        
        self.stdout.write("Pomyślnie utworzono strukturę katalogów dla zadań")


