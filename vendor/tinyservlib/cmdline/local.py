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

def _get_current_project_name():
    # This is semi-fragile and always assumes the last part of the URL
    # is the project name.
    
    return get_push_url(remote='tinyserv').split('/')[-1]

def cmd_apps__destroy(args):
    """
    Destroy an existing app.
    """
    
    if args.name is None:
        args.name = _get_current_project_name()

    print "Destroying project %s..." % args.name
    remote.destroy_project(args.name)
    print "Project %s destroyed." % args.name
    git(None, 'remote', 'rm', 'tinyserv')

cmd_apps__destroy_args = cmd_apps__create_args

def cmd_ps(args):
    """
    Show process status for app.
    """

    remote.show_status(_get_current_project_name())

def cmd_logs(args):
    """
    Show log for app.
    """

    remote.show_log(_get_current_project_name(), num=args.num, tail=args.tail)

def cmd_logs_args(parser):
    parser.add_argument('-n', '--num', type=int, default=5,
                        help='number of lines to display')
    parser.add_argument('-t', '--tail', action='store_true',
                        help='continually stream logs')

def run():
    global remote
    
    remote = TinyservClient(os.environ['TINYSERV_REMOTE'])
    make_run(globals())()
