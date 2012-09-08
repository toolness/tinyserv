#! /usr/bin/env python

import os
import argparse
import subprocess
import json
import urllib2

from os import path, environ

ROOT = path.abspath(path.dirname(path.realpath(__file__)))

PACKAGE_JSON = {
  "name": "tinyserv-smoketest",
  "version": "0.0.1",
  "author": "Foo <foo@foo.org>",
  "description": "smoke test for tinyserv.",
  "dependencies": {},
  "engines": {
    "node": "0.8.x",
    "npm": "1.1.x"
  },
  "license": "MIT"
}

APP_JS = """\
var port = process.env['PORT'];
var http = require('http');

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('foo is ' + process.env['foo']);
}).listen(port, function() {
  console.log("listening on port " + port);
});
"""

PROCFILE = "web: node app.js"

def chdir(path):
    print "  $ cd %s" % path
    os.chdir(path)

def mkdir(path):
    print "  $ mkdir %s" % path
    os.mkdir(path)

def run(cmd, silent=False):
    if not silent:
        print "  $ %s" % cmd
    try:
        contents = subprocess.check_output(cmd, shell=True,
                                           stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        if e.output:
            prefixed_print("  ", e.output)
        raise
    if contents:
        prefixed_print("  ", contents)
    return contents

def writefile(filename, contents):
    print "  $ cat <<EOF > %s" % filename
    prefixed_print("  > ", contents)
    print "  > EOF"
    f = open(filename, 'w')
    f.write(contents)
    f.close()

def readurl(url):
    print "  $ curl %s" % url
    output = urllib2.urlopen(url).read()
    prefixed_print("  ", output)
    return output

def prefixed_print(prefix, msg):
    for line in msg.splitlines():
        print prefix + line

def equals(a, b):
    if a != b:
        raise AssertionError("%s != %s" % (repr(a), repr(b)))

def contains(a, b):
    if not b in a:
        raise AssertionError("%s is not in %s" % (repr(b), repr(a)))

def describe(msg):
    print
    print msg
    print

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
      '--use-env',
      action='store_true',
      help='Use existing TINYSERV_* environment variables.'
      )
    args = parser.parse_args()
    
    if not args.use_env:
        tinyserv_bin_path = path.normpath(path.join(ROOT, '..'))
        environ.update({
            'TINYSERV_REMOTE': 'localhost',
            'TINYSERV_ROOT': path.join(ROOT, '.tinyserv'),
            'TINYSERV_START_PORT': '5000',
            'PATH': tinyserv_bin_path + path.pathsep + os.environ['PATH']
            })

    remote = environ['TINYSERV_REMOTE']
    host = remote.split('@')[-1]

    print "Running smoke test on %s." % host
    
    describe("Setting up sample 'tinysmoke' repository.")
    
    chdir(ROOT)
    if path.exists("tinysmoke"):
        run("rm -rf tinysmoke")
    try:
        run("tinyserv apps:destroy tinysmoke", silent=True)
    except subprocess.CalledProcessError, e:
        if "invalid choice: 'tinysmoke'" not in e.output:
            print "Failed process output follows."
            print e.output
            raise
    mkdir("tinysmoke")
    chdir("tinysmoke")
    run("git init")
    writefile("package.json", json.dumps(PACKAGE_JSON, indent=2))
    writefile("Procfile", PROCFILE)
    writefile("app.js", APP_JS)
    run("git add package.json Procfile app.js")
    run("git commit -m 'origination'")

    describe("Creating tinyserv app on %s." % remote)

    run("tinyserv apps:create")
    
    describe("Ensuring app exists.")
    
    contains(run("tinyserv apps").split(), "tinysmoke")
    
    describe("Deploying app by pushing to %s." % remote)
    
    run("git push tinyserv master")

    describe("Ensuring app is now running.")

    equals(run("tinyserv ps").strip().split(), ["tinysmoke", "running"])

    describe("Obtaining app configuration.")

    config = json.loads(run("tinyserv config"))
    url = "http://%s:%d" % (host, config['port'])

    describe("Accessing app at %s." % url)

    equals(readurl(url), "foo is undefined")

    describe("Changing app environment.")

    run("tinyserv config:set foo=blargey")
    equals(readurl(url), "foo is blargey")

    describe("Undoing app environment changes.")

    run("tinyserv config:unset foo")
    equals(readurl(url), "foo is undefined")

    describe("Checking app log.")

    contains(run("tinyserv logs"), "listening on port %d\n" % config['port'])
    
    describe("Shutting down app.")
    
    run("tinyserv apps:destroy")
    chdir("..")
    run("rm -rf tinysmoke")

    describe("Smoke test successful.")

if __name__ == "__main__":
    main()
