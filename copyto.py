#!/usr/bin/env python
# Copy into a docker container
import subprocess

name = "docktest"
dest = "/tmp/file.txt"
srcdata = "Hello, my name is computer\n"

args = ["docker", "exec", "-i", name, "bash", "-c", "cat > {}".format(dest)]

p = subprocess.Popen(args, stdin=subprocess.PIPE)
p.stdin.write(srcdata)
p.stdin.close()

# This blocks forever, unfortunately
p.wait()
