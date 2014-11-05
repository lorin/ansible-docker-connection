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

## Start the IPython notebook

This will start the notebook and mount /notebooks to your current directory on
the host.

```
docker run -d -p 8888:8888 -v `pwd`:/notebooks -w /notebooks lorin/ipython:v2 /notebook.sh
```

## Access the notebook

Browse to <http://192.168.59.103:8888>


