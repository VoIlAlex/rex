Usage
==============

.. meta::
   :description lang=en: Using requirements-txt command line tool.

In this section you can find docs on how to use requirements-txt command line tool.

Basic usage
---------------

There are two ways to use requirements-txt command line tool. The first one is:

.. code-block::

    requirements-txt <command> <options>

The second one is to use alias:

.. code-block::

    rt <command> <options>

Both commands results in the same outcome. It's just an alias.


Alias
---------------

To activate full potential of the cli you should add following lines to your
.bashrc, .zshrc or other .*rc file:

.. code-block::

    alias rt=". rt"
    alias requirements-txt=". requirements-txt"

It will allow requirements-txt cli to activate your environment and init command.
You can also achieve this by the command:

.. code-block::

    rt alias

This command will work for the following shells:

* bash
* zsh


Init
---------------

If you want to initialize virtual environment for your project use:

.. code-block::

    rt init

Or with alias:

.. code-block::

    rt i

This command will:

1. Install virtualenv package with your pip or skip this step if it's already installed.
2. Create requirements.txt file or skip this step if it already exists.
3. Install dependencies from your requirements.txt.
4. Install to-requirements.txt to your newly created environment.
5. Setup installed to-requirements.txt.

After that you can source your environment with

.. code-block::

    source venv/bin/activate

and start working on the project.


Install
---------------

To override your pip scripts and enable requirements.txt synchronization use:

.. code-block::

    rt install

This command is not required if use set up your environment with init command.

Uninstall
---------------

To restore your pip scripts to their original state and stop
requirements.txt synchronization use:

.. code-block::

    rt uninstall

Run it before ``pip uninstall rex`` (or with the virtual environment
activated, for a project set up with ``rt init``).

Help
---------------

To get more information about commands use the following command:

.. code-block::

     rt --help


Config
---------------

To use configuration util:

.. code-block::

    rt config <configuration options>


Show
---------------

If you want to see contents of your requirements.txt file type this:

.. code-block::

    rt show

Or with alias:

.. code-block::

    rt s

