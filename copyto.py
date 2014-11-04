#!/usr/bin/env python
# Copy into a docker container
import subprocess

name = "mytest"
dest = "/tmp/file.txt"
srcdata = "Hello, my name is computer"

args = ["docker", "exec", "-i", name, "bash", "-c", "cat > {}".format(dest)]

p = subprocess.Popen(args, stdin=subprocess.PIPE)
p.communicate()
