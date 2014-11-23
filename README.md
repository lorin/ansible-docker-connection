# Docker connection plugin for Ansible

This repo contains a connection plugin for Ansible that lets you configure
Docker containers without needing to install an SSH server or Ansible itself
into the container.

This is a work-in-progress.

## How to install

1. Create a `connection_plugins` directory next to your playbooks.
2. Copy the `connection_plugins/docker.py` file to the directory.

You may also need to modify the remote temporary directory (I had to do this
with the `ubuntu` base image). Add the following to your ansible.cfg:

```
[defaults]
remote_tmp = /tmp
```


### boot2docker issues

Because of a [docker
issue](https://github.com/docker/docker/issues/864://github.com/docker/docker/issues/8642),
if you are using boot2docker, you must disable TLS or the connectin plugin will
hang.

To disable TLS in boot2docker:

```
boot2docker ssh
sudo -i
/etc/init.d/docker stop
echo DOCKER_TLS="no" > /var/lib/boot2docker/profile
/etc/init.d/docker start
```

Your `DOCKER_HOST` should now point to port 2376 (the IP may not match the one
below), and the `DOCKER_TLS_VERIFY` and `DOCKER_CERT_PATH` environment variables
should not be deifned.

```
export DOCKER_HOST=tcp://192.168.59.103:2375
unset DOCKER_TLS_VERIFY
unset DOCKER_CERT_PATH
```

## How to use it

In your plays, add `connection: docker`. For example:

```
- name: configure my container
  connection: docker
  hosts: webcontainer

  tasks:
    - ...
```

You need a running container first, and you'll need to add the hostname to
Ansible's inventory. One way to do it is to write an initial play that runs a
container using the `docker` module and then uses the `add_host` module to add
to the inventory, like this:

```
- name: start up a docker container
  hosts: localhost
  vars:
    base_image: ubuntu
    docker_hostname: webcontainer

  tasks:
    - name: start up a docker container by running bash
      local_action: docker image={{ base_image }} name={{ docker_hostname }} detach=yes tty=yes command=bash
    - name: add the host
      add_host: name={{ docker_hostname }}

- name: configure the web container
  hosts: webcontainer
  connection: docker
  tasks:
   - ...
```

## Example

Check out the [ipython.yml](ipython.yml) playbook for an example that builds a
container that runs an IPython notebook.

To build the example image, just do:

```
ansible-playbook ipython.yml
```

It will build a docker image called `lorin/ipython`

## Start the IPython notebook

This will start the notebook and mount /notebooks to your current directory on
the host.

```
docker run -d -p 8888:8888 -v `pwd`:/notebooks lorin/ipython
```

## Access the notebook

If you're running docker locally on Linux, browse to <http://localhost:8888>.

If you're using boot2docker, browse to the IP address associated with the
`DOCKER_HOST` environment variable, e.g.: <http://192.168.59.104:8888>

## FAQ

Q: Does it work with boot2docker?

A: Sure does!

Q: What's with the `pre_image` and `final_image` in the
[ipython.yml](ipython.yml) playbook?

A: The playbook creates the pre-image by starting a container from a base
ubuntu image, configuring it with ansible, and then committing it. The playbook
creates the final image from the pre-image using a Dockerfile to set things like
the working directory, exposed ports, and command to run.

If you know how to do this one step, please let me know.

Q: Why does this repo contain custom [docker](library/docker) and [docker_image](library/docker_image) modules?

A: The upstream modules don't have support for boot2docker yet. I've submitted a
[pull request](https://github.com/ansible/ansible-modules-core/pull/272) to get
these added.

