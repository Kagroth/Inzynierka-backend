
class Executor:
    def __init__(self, concrete_executor):
        self.executor = concrete_executor

    def get_result(self):
        return self.executor.testsResult

    def execute(self):
        return self.executor.run()