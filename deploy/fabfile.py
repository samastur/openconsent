from fabric.api import *
from fabric import utils
from fabric.decorators import hosts

# this is our common file that can be copied across projects
# we deliberately import all of this to get all the commands it
# provides as fabric commands
from fablib import *
import fablib
import project_settings

env.home = '/var/django/'
env.project = project_settings.project_name
# the top level directory on the server
env.project_dir = env.project

# repository type can be "svn" or "git"
env.repo_type = "git"
env.repository = 'git://github.com/aptivate/openconsent.git'

env.django_dir = os.path.join('django', env.project)
env.django_apps = ['publicweb', ]
env.test_cmd = ' manage.py test -v0 ' + ' '.join(env.django_apps)


# put "django" here if you want django specific stuff to run
# put "plain" here for a basic apache app
env.project_type = "django"

# does this virtualenv for python packages
env.use_virtualenv = True

# valid environments - used for require statements in fablib
env.valid_non_prod_envs = ('dev_server', 'staging_test', 'staging')
env.valid_envs = ('dev_server', 'staging_test', 'staging', 'production')

# does this use apache - mostly for staging_test
env.use_apache = True


# this function can just call the fablib _setup_path function
# or you can use it to override the defaults
def _local_setup():
    # put your own defaults here
    fablib._setup_path()
    # override settings here
    # if you have an ssh key and particular user you need to use
    # then uncomment the next 2 lines
    #env.user = "root" 
    #env.key_filename = ["/home/shared/keypair.rsa"]


#
# These commands set up the environment variables
# to be used by later commands
#

def dev_server():
    """ use dev environment on remote host to play with code in production-like env"""
    utils.abort('remove this line when dev server setup')
    env.environment = 'dev_server'
    env.hosts = ['fen-vz-' + project_settings.project_name + '-dev']
    _local_setup()


def staging_test():
    """ use staging environment on remote host to run tests"""
    # this is on the same server as the customer facing stage site
    # so we need project_root to be different ...
    env.project_dir = env.project + '_test'
    env.environment = 'staging_test'
    env.use_apache = False
    env.hosts = ['fen-vz-' + project_settings.project_name]
    _local_setup()


def staging():
    """ use staging environment on remote host to demo to client"""
    env.environment = 'staging'
    env.hosts = ['fen-vz-' + project_settings.project_name]
    _local_setup()


def production_sandbox():
    """ use staging environment on remote host to run tests"""
    # this is on the same server as the customer facing stage site
    # so we need project_root to be different ...
    env.project_dir = env.project + '_sandbox'
    env.environment = 'production_sandbox'
    env.hosts = ['lin-openconsent.aptivate.org:48001']
    _local_setup()


def production():
    """ use production environment on remote host"""
    env.environment = 'production'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    _local_setup()
    
def production_test1():
    """ use production environment on remote host"""
    env.project_dir = env.project + '_test1'
    env.environment = 'production_test1'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    _local_setup()

def production_test2():
    """ use production environment on remote host"""
    env.project_dir = env.project + '_test2'
    env.environment = 'production_test2'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    _local_setup()

def deploy(revision=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('project_root', provided_by=env.valid_envs)
    with settings(warn_only=True):
        apache_cmd('stop')
    if not files.exists(env.project_root):
        sudo('mkdir -p %(project_root)s' % env)
    checkout_or_update(revision)
    update_requirements()
    create_private_settings()
    link_local_settings()
    rm_pyc_files()
    update_db()
    if env.environment == 'production':
        setup_db_dumps()
    # only link the apache conf once on the production server, not for all the sub-sites
    if not env.environment.startswith('production_'):
        link_apache_conf()
    load_fixtures()
    
    apache_cmd('start')
    
def load_fixtures():
    """load fixtures for this environment"""
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' load_fixtures')
