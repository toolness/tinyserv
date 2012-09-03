import os
import subprocess

from .run import make_run
from ..client import TinyservClient
from ..git_utils import git, get_push_url

remote = None

def cmd_apps__create(args):
    """
    Create a new app.
    """
    
    if args.name is None:
        args.name = os.path.basename(os.getcwd())
    
    url = remote.create_project(args.name)
    git(None, 'remote', 'add', 'tinyserv', url)

def cmd_apps__create_args(parser):
    parser.add_argument('name', nargs='?', default=None)

def cmd_apps__destroy(args):
    """
    Destroy an existing app.
    """
    
    if args.name is None:
        # This is semi-fragile and always assumes the last part of the URL
        # is the project name.
        args.name = get_push_url(remote='tinyserv').split('/')[-1]

    print "Destroying project %s..." % args.name
    remote.destroy_project(args.name)
    print "Project %s destroyed." % args.name
    git(None, 'remote', 'rm', 'tinyserv')

cmd_apps__destroy_args = cmd_apps__create_args

def run():
    global remote
    
    remote = TinyservClient(os.environ['TINYSERV_REMOTE'])
    make_run(globals())()
