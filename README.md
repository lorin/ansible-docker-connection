# Docker connection plugin for Ansible

This repo contains a connection plugin for Ansible that lets you configure
Docker containers without needing to install an SSH server or Ansible itself
into the container.

This is a work-in-progress.

## How to install

1. Create a `connection_plugins` directory next to your playbooks.
2. Copy the `connection_plugins/docker.py` file to the directory.

## How to use it

In your plays, add `connection: docker`. For example:

```
- name: configure my container
  connection: docker
  hosts: webcontainer

  tasks:
    - ...
```

Check out the [ipython.yml](ipython.yml) playbook for an example that builds a
container that runs an IPython notebook.

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

Q: What's with the `pre_image` and `final_image` and the playbook.

A: The playbook creates the pre-image by starting a container from a base
ubuntu image, configuring it with ansible, and then committing it. The playbook
creates the final image from the pre-image using a Dockerfile to set things like
the working directory, exposed ports, and command to run.

If you know how to do this one step, please let me know.

Q: Why do you have custom `docker` and `docker_image` modules.

A: The upstream modules don't have support for boot2docker yet. I've submitted a
[pull request](https://github.com/ansible/ansible-modules-core/pull/272) to get
these added.

