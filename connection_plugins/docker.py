import os
import subprocess

from ansible import errors
from ansible.callbacks import vvv


class Connection(object):
    def __init__(self, runner, host, port, *args, **kwargs):
        self.host = host
        self.runner = runner
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
            local_cmd = ["docker", "exec", self.host, executable, '-c', cmd]
        else:
            local_cmd = 'docker exec "%s" %s' % (self.host, cmd)

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
        args = ["docker", "exec", "-i", self.host, "bash", "-c",
                "cat > %s" % format(out_path)]

        vvv("PUT %s TO %s" % (in_path, out_path), host=self.host)

        if not os.path.exists(in_path):
            raise errors.AnsibleFileNotFound(
                "file or module does not exist: %s" % in_path)
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.stdin.write(open(in_path).read())
        p.stdin.close()

    def fetch_file(self, in_path, out_path):
        ''' fetch a file from container to local '''
        args = ["docker", "cp", "%s:%s" % (self.host, in_path),
                out_path]

        vvv("FETCH %s TO %s" % (in_path, out_path), host=self.chroot)
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

    def close(self):
        ''' terminate the connection. Nothing to do '''
        pass
