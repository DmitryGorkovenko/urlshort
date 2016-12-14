from flask_script import Manager
from flask_migrate import MigrateCommand

from rest import app


manager = Manager(app)
manager.add_option('-c', '--config', dest='config')
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
