import subprocess
import os

def _realrepo(cwd):
    gitdir = os.path.join(cwd, '.git')
    if os.path.exists(gitdir):
        return gitdir
    return cwd

def _mkenv(cwd):
    env = {}
    env.update(os.environ)
    if cwd:
        # Not really sure why we have to do this, perhaps it has
        # something to do w/ the fact that we're calling git from
        # a non-terminal session or something.
        env['GIT_DIR'] = _realrepo(cwd)
    return env

def in_git_repo():
    return os.path.exists('.git')

def git(cwd, *args):
    subprocess.check_call(['git'] + list(args), cwd=cwd, env=_mkenv(cwd))

def get_git_output(args, cwd=None):
    return subprocess.check_output(['git'] + list(args), cwd=cwd,
                                   env=_mkenv(cwd))

def get_heads(cwd):
    return os.listdir(os.path.join(_realrepo(cwd), 'refs', 'heads'))

def get_head_ref(cwd):
    cwd = _realrepo(cwd)
    path = open(os.path.join(cwd, 'HEAD')).read()
    if not path.startswith('ref:'):
        raise Exception("expected HEAD to be a symbolic reference")
    headfile = os.path.join(cwd, path.split("ref:")[1].strip())
    open(headfile).read().strip()
    
def get_push_url(remote, cwd=None):
    output = get_git_output(['remote', 'show', '-n', remote], cwd=cwd)

    # This is fragile and assumes the "Push URL" is always on the second
    # line of the output.
    url = output.splitlines()[2].split("URL:")[1].strip()
    
    if url == remote:
        # No remote defined..
        return None

    return url
