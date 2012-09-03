import os
import subprocess
import json
import time
from distutils.dir_util import mkpath

import ProcessManager

def git(cwd, *args):
    env = {}
    if cwd:
        gitdir = os.path.join(cwd, '.git')
        if os.path.exists(gitdir):
            # Not really sure why we have to do this, perhaps it has
            # something to do w/ the fact that we're calling git from
            # a non-terminal session or something.
            env['GIT_DIR'] = gitdir
    subprocess.check_call(['git'] + list(args), cwd=cwd, env=env)
    
def writefile(filename, contents, mode=0644):
    f = open(filename, 'w')
    f.write(contents)
    f.close()
    os.chmod(filename, mode)

class Project(object):
    def __init__(self, tinyserv, name):
        self.tinyserv = tinyserv
        self.name = name
        self.repodir = os.path.join(tinyserv.repodir, self.name)
        self.builddir = os.path.join(tinyserv.builddir, self.name)
        self.releasefile = os.path.join(tinyserv.releasedir, 
                                        '%s.json' % self.name)
        self.release = {}
        self.process = None
        self.logfile = os.path.join(tinyserv.logdir, '%s.log' % self.name)

        if not os.path.exists(self.repodir):
            os.mkdir(self.repodir)
            git(self.repodir, 'init', '--bare')
            writefile(os.path.join(self.repodir, 'hooks', 'post-update'),
                      "exec tinyserv-remote git:post-update", 0755)

        if os.path.exists(self.releasefile):
            self.release.update(json.load(open(self.releasefile)))
            self._on_release_updated()

    def _buildpath(self, *args):
        return os.path.join(self.builddir, *args)

    def _buildcmd(self, cmd):
        subprocess.check_call(cmd, cwd=self.builddir, shell=True)

    def _on_build_updated(self):
        if not os.path.exists(self._buildpath('package.json')):
            raise Exception("package.json not found!")

        package = json.load(open(self._buildpath('package.json')))

        self._buildcmd('npm install')

        if not os.path.exists(self._buildpath('Procfile')):
            raise Exception("Procfile not found!")
        
        procfile = open(self._buildpath('Procfile'), 'r').readlines()
        
        if len(procfile) != 1:
            raise Exception("Only 1-line procfiles are currently supported.")
        
        cmdline = procfile[0].split(':')[1].strip()
        headfile = self._buildpath('.git', 'refs', 'heads', 'master')

        self.release['cmdline'] = cmdline
        self.release['id'] = time.asctime()
        self.release['commit'] = open(headfile).read().strip()
        self.release['description'] = package.get('description')

        if not self.release.get('port'):
            self.release['port'] = self.tinyserv.find_unused_port()
        
        json.dump(self.release, open(self.releasefile, 'w'))
        
        self._on_release_updated()
        
    def _on_release_updated(self):
        if not self.release.get('cmdline'):
            return
        
        args = self.release['cmdline'].split()

        self.process = ProcessManager.Process(
            name=self.name,
            desc=self.release.get('description') or "project %s" % self.name,
            program=args[0],
            args=args[1:],
            workingDir=self.builddir,
            logFile=self.logfile,
            env={'PORT': str(self.release['port'])}
            )

        ProcessManager.set(self.process)
        
        # 6. update tinyserv/exports directory.
        # 7. start processmanager task
        # 8. restart/update proxy server if necessary

    def update_build(self):
        if self.process:
            self.process.stop()
        
        if not os.path.exists(self.builddir):
            git(None, 'clone', self.repodir, self.builddir)
        
        git(self.builddir, 'pull')
        
        self._on_build_updated()

        self.process.start()

    def destroy(self):
        if self.process:
            self.process.stop()
        
        subprocess.check_call(['rm', '-rf', self.repodir])
        subprocess.check_call(['rm', '-rf', self.builddir])
        subprocess.check_call(['rm', '-f', self.releasefile])
        subprocess.check_call(['rm', '-f', self.logfile])
        
        self.release = {}
        self.process = None

class TinyservManager(object):
    def __init__(self, rootdir, start_port):
        self.rootdir = os.path.expanduser(rootdir)
        self.repodir = os.path.join(self.rootdir, 'repositories')
        self.builddir = os.path.join(self.rootdir, 'builds')
        self.releasedir = os.path.join(self.rootdir, 'releases')
        self.exportdir = os.path.join(self.rootdir, 'exports')
        self.logdir = os.path.join(self.rootdir, 'logs')
        self.piddir = os.path.join(self.rootdir, 'pids')
        self.start_port = start_port
        
        paths = [self.rootdir, self.repodir, self.builddir, self.releasedir,
                 self.exportdir, self.logdir, self.piddir]
        
        for path in paths:
            if not os.path.exists(path):
                mkpath(path)

        # Note that this means TinyservManager is a singleton for now...
        ProcessManager.init(self.piddir)
        
        self.projects = {}
        
        for reponame in os.listdir(self.repodir):
            self.projects[reponame] = Project(self, reponame)

    def find_unused_port(self):
        max_port = self.start_port
        for name in self.projects:
            port = self.projects[name].release.get('port', 0)
            if port > max_port:
                max_port = port
        return max_port + 1

    def create_project(self, name):
        if name not in self.projects:
            self.projects[name] = Project(self, name)
        return self.projects[name]

    def destroy_project(self, name):
        self.projects[name].destroy()
        del self.projects[name]
