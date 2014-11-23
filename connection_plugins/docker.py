# Author: Lorin Hochstein
# Based on the chroot connection plugin by Maykel Moya
import os
import subprocess
import time

from ansible import errors
from ansible.callbacks import vvv


class DockerExecConnection(object):
    def __init__(self, runner, host, port, *args, **kwargs):
        self.host = host
        self.runner = runner
        self.has_pipelining = False
        self.docker_cmd = "docker"
        pass

    def connect(self, port=None):
        """ Connect to the container. Nothing to do """
        return self

    def exec_command(self, cmd, tmp_path, sudo_user=None, sudoable=False,
                     executable='/bin/sh', in_data=None, su=None,
                     su_user=None):

        ''' run a command on the local host '''

        # su requires to be run from a terminal, and therefore isn't
        # supported here (yet?)
        if su or su_user:
            raise errors.AnsibleError("Internal Error: this module does not "
                                      "support running commands via su")

        if in_data:
            raise errors.AnsibleError("Internal Error: this module does not "
                                      "support optimized module pipelining")

        # We enter container as root so sudo stuff can be ignored

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

    def put_file(self, in_path, out_path):
        ''' transfer a file from local to container '''
        args = [self.docker_cmd, "exec", "-i", self.host, "bash", "-c",
                "cat > %s" % format(out_path)]

        vvv("PUT %s TO %s" % (in_path, out_path), host=self.host)

        if not os.path.exists(in_path):
            raise errors.AnsibleFileNotFound(
                "file or module does not exist: %s" % in_path)
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.stdin.write(open(in_path).read())
        p.stdin.close()

        # HACK because of https://github.com/boot2docker/boot2docker/issues/583
        # This is only a problem with boot2docker
        time.sleep(1)
        p.terminate()

    def fetch_file(self, in_path, out_path):
        ''' fetch a file from container to local '''
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
        ''' terminate the connection. Nothing to do '''
        pass

Connection = DockerExecConnection
