import os
import sys
import subprocess

from .run import make_run
from ..client import TinyservClient
from ..git_utils import git, get_push_url, in_git_repo

remote = None

def cmd_apps(args):
    """
    List existing apps.
    """
    
    remote.show_apps()

def cmd_apps__create(args):
    """
    Create a new app.
    """
    
    if args.name is None:
        args.name = os.path.basename(os.getcwd())

    url = remote.create_project(args.name)
    
    if in_git_repo():
        if get_push_url('tinyserv') is None:
            git(None, 'remote', 'add', 'tinyserv', url)
            print "Added remote 'tinyserv'."
        else:
            print "This repository is already configured for app '%s'." % \
                  _get_current_project_name()
    
    print "Remote repository URL is %s." % url

def cmd_apps__create_args(parser):
    parser.add_argument('name', nargs='?', default=None)

def _get_current_project_name():
    # This is semi-fragile and always assumes the last part of the URL
    # is the project name.
    
    push_url = get_push_url(remote='tinyserv')
    if push_url is not None:
        return push_url.split('/')[-1]

def cmd_apps__destroy(args):
    """
    Destroy an existing app.
    """
    
    if args.name is None and in_git_repo():
        args.name = _get_current_project_name()

    if args.name is None:
        print "Please provide a project name."
        sys.exit(1)

    print "Destroying project %s..." % args.name
    remote.destroy_project(args.name)
    print "Project %s destroyed." % args.name
    if in_git_repo() and _get_current_project_name() == args.name:
        git(None, 'remote', 'rm', 'tinyserv')
        print "Removed remote '%s'." % args.name

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

def cmd_config(args):
    """
    Show app environment settings.
    """
    
    remote.show_config(_get_current_project_name())

def cmd_config__set(args):
    """
    Set environment keys and values.
    """

    settings = {}
    for pair in args.keyvalues:
        key, value = pair.split("=", 1)
        settings[key] = value
    remote.update_config(_get_current_project_name(), settings)

def cmd_config__set_args(parser):
    parser.add_argument('keyvalues', nargs='*',
                        help='KEY=VALUE pairs to set')

def run():
    global remote
    
    remote = TinyservClient(os.environ['TINYSERV_REMOTE'])
    make_run(globals())()
