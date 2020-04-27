import subprocess
import logging
import os

from subprocess import PIPE

# Pobranie repozytorium GitHub
# Pierwsza wersja nadeslania rozwiazania poprzez repozytorium GitHub
# Aktualnie nie wykorzystywane
def getRemoteRepository(repository_url, destination_path):
    '''
    zmiana katalogu - chdir
    git init
    git remote add origin repository
    git pull origin master
    powrot do glownego katalogu - chdir
    '''
    logger = logging.getLogger(os.path.basename(__file__)) 
    logger.info("Zmiana katalogu roboczego na " + destination_path)
    os.chdir(destination_path)

    git_commands = [
        ['git', 'init'],
        ['git', 'remote', 'add', 'origin', repository_url],
        ['git', 'pull', 'origin', 'master']
    ]

    for git_command in git_commands:
        process = subprocess.run(
            git_command, stdout=PIPE, stderr=PIPE, shell=False)
        logger.info("Wynik wykonania instrukcji " +
                         " ".join(git_command) +
                         " - " + str(process.stdout.decode("utf-8")) +
                         str(process.stderr.decode("utf-8")))
    
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return True
