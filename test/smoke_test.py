import os
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
  "dependencies": {
    "express": "2.5.x"
  },
  "engines": {
    "node": "0.8.x",
    "npm": "1.1.x"
  },
  "license": "MIT"
}

APP_JS = """\
var server = require('express').createServer();
var port = process.env['PORT'];

server.get('/', function(req, res) {
  res.send('foo is ' + process.env['foo']);
});

server.listen(port, function() {
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

def shorten(contents, maxlen=20):
    short_contents = contents
    if len(contents) > maxlen:
        short_contents = contents[:maxlen] + '...'
    return short_contents

def run(cmd, silent=False):
    if not silent:
        print "  $ %s" % cmd
    contents = subprocess.check_output(cmd, shell=True,
                                       stderr=subprocess.STDOUT)
    if contents:
        print "    -> %s" % repr(shorten(contents, maxlen=40))
    return contents

def writefile(filename, contents):
    print "  $ echo %s > %s" % (repr(shorten(contents)), filename)
    f = open(filename, 'w')
    f.write(contents)
    f.close()

def readurl(url):
    print "  $ curl %s" % url
    output = urllib2.urlopen(url).read()
    print "    -> %s" % repr(output)
    return output

def equals(a, b):
    if a != b:
        raise AssertionError("%s != %s" % (repr(a), repr(b)))

def describe(msg):
    print
    print msg
    print

def main():
    remote = environ['TINYSERV_REMOTE']
    host = remote.split('@')[-1]

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
    writefile("package.json", json.dumps(PACKAGE_JSON))
    writefile("Procfile", PROCFILE)
    writefile("app.js", APP_JS)
    run("git add package.json Procfile app.js")
    run("git commit -m 'origination'")

    describe("Creating tinyserv app on %s." % remote)

    run("tinyserv apps:create")
    
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

    describe("Shutting down app.")
    
    run("tinyserv apps:destroy")
    chdir("..")
    run("rm -rf tinysmoke")

    describe("Smoke test successful.")

if __name__ == "__main__":
    main()
