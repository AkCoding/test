from src import app, db
from src import models
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


# def add_super_admin():
#     user = db.session.query(User).get(1)
#     if user != None:
#         print(user.email)
#     else:
#         print("No super admin exits")
        # user = User()


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


if __name__ == '__main__':
    manager.run()
