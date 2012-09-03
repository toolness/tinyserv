import os

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

cmd_apps__destroy_args = cmd_apps__create_args

def run():
    global tinyserv
    
    tinyserv = TinyservManager(os.environ['TINYSERV_ROOT'],
                               int(os.environ['TINYSERV_START_PORT']))
    make_run(globals())()
