************
Installation
************

.. _deployment:

===================
Standard deployment
===================

Clone the CSTrack_URJC Github repository wherever you want to deploy the application. Then access the folder where the Dash application is located.

.. code:: console

    $ git clone https://github.com/FernanSLN/CSTrack_URJC.git
    $ cd CSTrack_URJC/cstrack_dash

The application needs Python 3.9 to fully work. After installing Python, install the requirements:

.. code:: console

    $ pip install -r requirements.txt

=================
Docker deployment
=================

The cstrack_dash folder comes with a Dockerfile file that can be used to create a Docker image with everything in it. This
means that you will not need to install Python nor the dependencies. You will need to have Docker in the computer where you want to
deploy the Dash application. The first steps are the same as in :ref:`deployment`:

.. code:: console

    $ git clone https://github.com/FernanSLN/CSTrack_URJC.git
    $ cd CSTrack_URJC/cstrack_dash

Then, you need to create and run the image with the following commands:

.. code:: console

    $ docker build -t cstrack .
    $ docker run --name=cstrack_container -p 6123:6123

=======================
Running the application
=======================
Prior to starting the Dash application have check the sections :ref:`columns-inline`