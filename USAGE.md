README
======


REQUIREMENTS
============

   $ sudo pip install -r requirements.txt


TESTS
=====
    $ python-coverage run --source='core' ./manage.py runserver 8001 --pythonpath=$PWD/../python-gooclientlib --noreload

    $ cd core; python -munittest tests; cd -

    $ python-coverage html -d docs/coverage

    $ xdg-open docs/coverage/index.html 
