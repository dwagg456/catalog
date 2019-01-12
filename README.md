# Item Catalog Project

The item catalog project consists of creating a catalog where users can add, edit, and delete item listings. I have implemented this as a resale site using Google sign-in for authentication.

The database contains two tables: 
1. Category
2. Item

This README file displays the installation steps necessary to recreate the project environment.

## Table of Contents

* [Dependencies](#dependencies)
* [Installation](#installation)
* [Usage](#usage)
* [Attribution](#attribution)

## Dependencies

Running the solution script to produce the output file assumes that the following dependencies already exist on the machine being used. If not, they need to be installed and configured before proceeding.
* Python 2.7

## Installation

1. Install VirtualBox 5.1
    * [https://www.virtualbox.org/wiki/Download_Old_Builds_5_1](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
2. Install Vagrant 1.8.5
    * [https://releases.hashicorp.com/vagrant/1.8.5/](https://releases.hashicorp.com/vagrant/1.8.5/)
3. Download the VM Configuration
    * Either download the zip file or fork and clone the repository:
        * [https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip)
        * [https://github.com/udacity/fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm)
4. Unzip the catalog folder into the vagrant subdirectory.
5. Start the virtual machine
    * Access the vagrant subdirectory in your terminal.
    ```
    $ vagrant up
    $ vagrant ssh
    ```
6. Create the database
    ```
    vagrant@vagrant:~$ cd /vagrant/catalog
    vagrant@vagrant:/vagrant$ python database_setup.py
    ```
7. Load default data
    ```
    vagrant@vagrant:/vagrant$ python database_values.py
    ```
8. Start webserver
    ```
    vagrant@vagrant:/vagrant$ python application.py
    ```

## Usage

Access the item catalog via a web browser:
* [http://localhost:8000](http://localhost:8000)

## Attribution

The following resources were used in creating this project.
* [Udacity](https://www.udacity.com) - Udacity resources were used for this project, including the instructions to set up the virtual machine and database, sample README files, and sample code.

* [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/latest/orm/tutorial.html) - This documention had tutorials and usage information for SQLAlchemy.

* [Flask Documentation](http://flask.pocoo.org/docs/1.0/) - This documentation had tutorials and usage information for Flask templates.

* [GitHub Issue Discussion](https://github.com/g2p/bedup/issues/38) - This page was used to resolve a thread error issue.
