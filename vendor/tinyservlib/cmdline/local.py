import os
import subprocess

from .run import make_run
from ..client import TinyservClient

remote = None

def cmd_apps__create(args):
    """
    Create a new app.
    """
    
    if args.name is None:
        args.name = os.path.basename(os.getcwd())
    
    url = remote.create_project(args.name)
    subprocess.check_call(['git', 'remote', 'add', 'tinyserv', url],
                          cwd=os.getcwd())

def cmd_apps__create_args(parser):
    parser.add_argument('name', nargs='?', default=None)

def cmd_apps__destroy(args):
    """
    Destroy an existing app.
    """
    
    if args.name is None:
        output = subprocess.check_output(['git', 'remote', 'show', '-n', 
                                          'tinyserv'])
        # This is fragile and assumes the "Push URL" is always on the second
        # line of the output.
        url = output.splitlines()[2].split("URL:")[1].strip()
        
        # This is semi-fragile and always assumes the last part of the URL
        # is the project name.
        args.name = url.split('/')[-1]

    print "Destroying project %s..." % args.name
    remote.destroy_project(args.name)
    print "Project %s destroyed." % args.name
    subprocess.check_call(['git', 'remote', 'rm', 'tinyserv'],
                          cwd=os.getcwd())

cmd_apps__destroy_args = cmd_apps__create_args

def run():
    global remote
    
    remote = TinyservClient(os.environ['TINYSERV_REMOTE'])
    make_run(globals())()
