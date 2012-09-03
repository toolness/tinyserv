import subprocess
import os

def _mkenv(cwd):
    env = {}
    env.update(os.environ)
    if cwd:
        gitdir = os.path.join(cwd, '.git')
        if os.path.exists(gitdir):
            # Not really sure why we have to do this, perhaps it has
            # something to do w/ the fact that we're calling git from
            # a non-terminal session or something.
            env['GIT_DIR'] = gitdir
    return env

def git(cwd, *args):
    subprocess.check_call(['git'] + list(args), cwd=cwd, env=_mkenv(cwd))

def get_git_output(args, cwd=None):
    return subprocess.check_output(['git'] + list(args), cwd=cwd,
                                   env=_mkenv(cwd))

def get_push_url(remote, cwd=None):
    output = get_git_output(['remote', 'show', '-n', remote], cwd=cwd)
    
    # This is fragile and assumes the "Push URL" is always on the second
    # line of the output.
    return output.splitlines()[2].split("URL:")[1].strip()
