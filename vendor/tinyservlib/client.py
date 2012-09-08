import sys
import json
import subprocess

class TinyservClient(object):
    def __init__(self, host):
        self.host = host
    
    def make_remote_url(self, repodir):
        if self.host == 'localhost':
            return repodir
        else:
            return '%s:%s' % (self.host, repodir)

    def make_remote_cmd(self, cmd):
        if self.host == 'localhost':
            return ['bash', '-c', cmd]
        else:
            return ['ssh', self.host, cmd]

    def _remote(self, cmd, ignore_errors=False):
        fullcmd = self.make_remote_cmd(cmd)
        popen = subprocess.Popen(
          fullcmd,
          stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT
          )
        chars = []
        while True:
            data = popen.stdout.read(1)
            if len(data):
                chars.append(data)
                sys.stdout.write(data)
            elif popen.poll() is not None:
                break
        output = ''.join(chars)
        if popen.returncode and not ignore_errors:
            raise subprocess.CalledProcessError(
                returncode=popen.returncode,
                cmd=' '.join(fullcmd),
                output=output
                )
        return output

    def update_config(self, name, settings):
        fullcmd = self.make_remote_cmd('tinyserv-remote config:set %s' % name)
        popen = subprocess.Popen(fullcmd, stdin=subprocess.PIPE)
        popen.communicate(json.dumps(settings))
        if popen.wait():
            raise subprocess.CalledProcessError(
                returncode=popen.returncode,
                cmd=' '.join(fullcmd)
                )

    def show_config(self, name):
        self._remote('tinyserv-remote config %s' % name)

    def show_status(self, name):
        self._remote('tinyserv-remote ps %s' % name)

    def show_apps(self):
        self._remote('tinyserv-remote apps')

    def show_log(self, name, num, tail):
        try:
            logfile = "-n %d $TINYSERV_ROOT/logs/%s.log" % (num, name)
            if tail:
                logfile = "-f " + logfile
            subprocess.call(self.make_remote_cmd("tail %s" % logfile))
        except KeyboardInterrupt:
            if not tail:
                raise

    def destroy_project(self, name):
        self._remote('tinyserv-remote apps:destroy %s' % name)

    def create_project(self, name):
        result = self._remote('tinyserv-remote apps:create %s' % name)
        repodir = result.splitlines()[-1].split()[-1].strip()
        return self.make_remote_url(repodir)
