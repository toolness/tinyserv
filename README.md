tinyserv and tinyserv-remote scripts must be on path.

note that they might need to be in ~/.bashrc for server-side, since ssh
uses non-interactive shell.

TINYSERV_ROOT - root directory for tinyserv-remote
TINYSERV_START_PORT - starting port for tinyserv automatic port assignment
TINYSERV_REMOTE - ssh-compatible host for tinyserv

TINYSERV_ROOT directory structure:

  TINYSERV_ROOT/
    repositories/
      foo/
      bar/
    builds/
      foo/
      bar/
    releases/
      foo.json
      bar.json
    logs/
      foo.log
      bar.log
    pids/
      foo.pid
      bar.pid
    exports/
      proxy-map.json
