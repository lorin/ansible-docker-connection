# Connection plugin for configuring docker containers
# Author: Lorin Hochstein
#
# Based on the chroot connection plugin by Maykel Moya
import os
import subprocess
import time

from ansible import errors
from ansible.callbacks import vvv


class Connection(object):
    def __init__(self, runner, host, port, *args, **kwargs):
        self.host = host
        self.runner = runner
        self.has_pipelining = False
        self.docker_cmd = "docker"

    def connect(self, port=None):
        """ Connect to the container. Nothing to do """
        return self

    def exec_command(self, cmd, tmp_path, sudo_user=None, sudoable=False,
                     executable='/bin/sh', in_data=None, su=None,
                     su_user=None):

        """ Run a command on the local host """

        # Don't currently support su
        if su or su_user:
            raise errors.AnsibleError("Internal Error: this module does not "
                                      "support running commands via su")

        if in_data:
            raise errors.AnsibleError("Internal Error: this module does not "
                                      "support optimized module pipelining")

        if sudoable and sudo_user:
            raise errors.AnsibleError("Internal Error: this module does not "
                                      "support running commands via sudo")

        if executable:
            local_cmd = [self.docker_cmd, "exec", self.host, executable,
                         '-c', cmd]
        else:
            local_cmd = '%s exec "%s" %s' % (self.docker_cmd, self.host, cmd)

        vvv("EXEC %s" % (local_cmd), host=self.host)
        p = subprocess.Popen(local_cmd,
                             shell=isinstance(local_cmd, basestring),
                             cwd=self.runner.basedir,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()
        return (p.returncode, '', stdout, stderr)

    # Docker doesn't have native support for copying files into running
    # containers, so we use docker exec to implement this
    def put_file(self, in_path, out_path):
        """ Transfer a file from local to container """
        args = [self.docker_cmd, "exec", "-i", self.host, "bash", "-c",
                "cat > %s" % format(out_path)]

        vvv("PUT %s TO %s" % (in_path, out_path), host=self.host)

        if not os.path.exists(in_path):
            raise errors.AnsibleFileNotFound(
                "file or module does not exist: %s" % in_path)
        p = subprocess.Popen(args, stdin=open(in_path),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        # HACK: Due to a race condition, this sometimes returns before
        # the file has been written to disk, so we sleep for one second
        time.sleep(1)

    def fetch_file(self, in_path, out_path):
        """ Fetch a file from container to local. """
        # out_path is the final file path, but docker takes a directory, not a
        # file path
        out_dir = os.path.dirname(out_path)
        args = [self.docker_cmd, "cp", "%s:%s" % (self.host, in_path), out_dir]

        vvv("FETCH %s TO %s" % (in_path, out_path), host=self.host)
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        # Rename if needed
        actual_out_path = os.path.join(out_dir, os.path.basename(in_path))
        if actual_out_path != out_path:
            os.rename(actual_out_path, out_path)

    def close(self):
        """ Terminate the connection. Nothing to do for Docker"""
        pass
