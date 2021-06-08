import os
from src import config
import shutil

MIGRATION_PATH = os.path.join(os.path.curdir, "migrations")
try:

    if not os.path.exists(MIGRATION_PATH):

        if os.path.exists(config.DATABASE_PATH):
            os.system("python3 manager.py db migrate")
            os.system("python3 manager.py db upgrade")
        else:
            os.system("python3 manager.py db init")
            os.system("python3 manager.py db migrate")
            os.system("python3 manager.py db upgrade")
    else:
        os.system("python3 manager.py db migrate")
        os.system("python3 manager.py db upgrade")
except Exception as err:
    print(err)
    print("MIGRATION FAILED")
    shutil.rmtree(MIGRATION_PATH)
    os.remove(config.DATABASE_PATH)
    os.system("python3 manager.py db init")
    os.system("python3 manager.py db migrate")
    os.system("python3 manager.py db upgrade")

os.system("python3 -m nltk.downloader wordnet")
os.system("python3 -m nltk.downloader punkt")