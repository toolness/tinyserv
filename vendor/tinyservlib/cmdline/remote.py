import os
import sys
import json

from ..manager import TinyservManager
from .run import make_run

tinyserv = None

def cmd_git__post_update(args):
    """
    Called by git post-update hooks to push a new deployment.
    """

    # This is called in the context of the remote server, by the post-update
    # hook in tinyserv/repositories/name.
    
    gitdir = os.path.join(os.getcwd(), os.environ['GIT_DIR'])
    gitdir = os.path.normpath(gitdir)
    name = os.path.basename(gitdir)
    rootdir = os.path.normpath(os.path.join(gitdir, '..', '..'))
    
    if rootdir != tinyserv.rootdir:
        raise Exception("roots do not match: %s, %s" % (rootdir,
                                                        tinyserv.rootdir))
    
    tinyserv.projects[name].update_build()

def cmd_apps__create(args):
    """
    Create an app.
    """

    project = tinyserv.create_project(args.name)
    
    print "repository: %s" % project.repodir

def cmd_apps__create_args(parser):
    parser.add_argument('name')

def cmd_apps__destroy(args):
    """
    Destroy an app.
    """

    project = tinyserv.destroy_project(args.name)

def cmd_apps__destroy_args(parser):
    parser.add_argument('name', choices=tinyserv.projects.keys())

def cmd_ps(args):
    """
    Show process status for an app.
    """
    
    tinyserv.projects[args.name].process.status()

cmd_ps_args = cmd_apps__destroy_args

def cmd_config__set(args):
    """
    Update environment via stdin JSON blob.
    """
    
    settings = json.load(sys.stdin)
    tinyserv.projects[args.name].update_config(settings)

cmd_config__set_args = cmd_apps__destroy_args

def cmd_config(args):
    """
    Show app environment settings.
    """
    
    print json.dumps(tinyserv.projects[args.name].release, 
                     sort_keys=True,
                     indent=2)

cmd_config_args = cmd_apps__destroy_args

def all_processes():
    for name in tinyserv.projects:
        process = tinyserv.projects[name].process
        if process:
            yield process

def cmd_startup(args):
    """
    Start all apps.
    """
    
    for process in all_processes():
        process.start()

def cmd_shutdown(args):
    """
    Stop all apps.
    """

    for process in all_processes():
        process.stop()

def run():
    global tinyserv
    
    tinyserv = TinyservManager(os.environ['TINYSERV_ROOT'],
                               int(os.environ['TINYSERV_START_PORT']))
    make_run(globals())()
