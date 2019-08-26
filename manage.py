from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import create_app, db, models

app = create_app("dev")
manager = Manager(app)
Migrate(app, db)  # 关联APP和db
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
