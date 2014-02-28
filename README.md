Goo project
===========

The goo project aim to create a user-friendly platform for batch processes in grid infrastructure (and others).

Computer simulations are used in many scientific researches, from many different fields. Batch processes are a common way of process this simulations, that are executed in HPC clusters or computing grids.

This platform creates an easy-to-use environment so a researcher without computer experience can submit simulations to large and complex computer systems.

It provides a web interface (goo-server/portal) as well command-line (goo-client) tools. It can also be extended or integrated using a REST API.

For more information visit https://submit.grid.unesp.br

This platform is been developed by NCC/UNESP in the GridUNESP project.

Architecture
============

The goo platform is composed by the following packages:

* goo-server
* goo-dataproxy (this code)
* goo-client
* python-gooclientlib

For the technical documentation visit https://submit.grid.unesp.br/portal/docs/

goo-server
----------

This is the main server, who handle job workflows, as well all data-objects metadata. It also provide a web portal. It currently execute jobs using Globus GRAM mechanisms, but other mechanisms can be easily extend.

goo-dataproxy
-------------

This is the data server. It was developed as external server to allow multiple instances and handle very large data transfers. Future versions should support Globus data mechanisms, like SRM and GridFTP. Currently only local storage is supported.

goo-client
----------

This is the command-line tool for the client to interact with the goo-server and goo-dataproxy using REST API. It allows to control jobs (submit, list, delete, ...), applications and data-objects (input, checkpoints and output files).

python-gooclientlib
-------------------

This is a Python 2.x library for goo-client and goo-dataproxy (that act as a client to retrieve metadata information).

BUGS, Suggestions and Questions
--------------------------------

Please, contact: devel AT ncc DOT unesp DOT br.

