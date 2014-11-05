FROM lorin/iptyhon-base

MAINTAINER Lorin Hochstein <lorin.hochstein@sendgrid.com>

VOLUME /notebooks
WORKDIR /notebooks

EXPOSE 8888

ADD notebook.sh /
RUN chmod u+x /notebook.sh
CMD ["/notebook.sh"]
