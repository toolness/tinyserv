import sys
import subprocess

class TinyservClient(object):
    def __init__(self, host):
        self.host = host
    
    def _ssh(self, cmd, ignore_errors=False):
        fullcmd = ['ssh', self.host, cmd]
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

    def show_status(self, name):
        self._ssh('tinyserv-remote ps %s' % name)

    def show_log(self, name, num, tail):
        try:
            logfile = "-n %d $TINYSERV_ROOT/logs/%s.log" % (num, name)
            if tail:
                logfile = "-f " + logfile
            ssh_cmd = "tail %s" % logfile
            subprocess.call(['ssh', self.host, ssh_cmd])
        except KeyboardInterrupt:
            if not tail:
                raise

    def destroy_project(self, name):
        self._ssh('tinyserv-remote apps:destroy %s' % name)

    def create_project(self, name):
        result = self._ssh('tinyserv-remote apps:create %s' % name)
        repodir = result.splitlines()[-1].split()[-1].strip()
        return '%s:%s' % (self.host, repodir)
