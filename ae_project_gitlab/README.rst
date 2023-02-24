==========================
Gitlab project Integration
==========================
Authors
=======================
Ing. Yadier Abel De Quesada Ricardo

AE Project Gitlab
-----------------

Description
===========

 Allows synchronizing the information from the Gitlab repositories that your company has registered.
 With the group identifier in Gitlab, it obtains through api calls the necessary data to create a copy of
 the projects in the Odoo Project Management and convert the Gitlab issues
 into tasks
 It also allows you to register and sync the profiles of Gitlab users.

Installation and Configuration
==============================

Requirement
-----------
* Install Requests => 2.21.0 `request <https://pypi.org/project/requests/>`_
* Configure Secret token and Url in settings for access to the Gitlab-Api

    Menu => Settings =>  Connection Gitlab
    fill Gitlab Secret Token and Gitlab Base Api Url

Features
========
* Make sync data of the Groups registered in Gitlab

  Set the Group id when create a Gitlab Group, then sync

* Make sync data for projects related to one group (manual)

  You can sync the projects related to one group just pressing a button

* Make sync data for issues/tasks related to one project (manual)

  You can sync the issues/task for projects just pressing a button

TODO
====
* Make sync data for all projects registered in Gitlab (automatically) [next]
* Make sync data for all issues/tasks registered in Gitlab (automatically) [next]
* Make sync data of for gitlab user(automatically) [next]

Data Source
===========
* The module uses a request  http to the gitlab API read this `guide <https://docs.gitlab.com/ee/api/index.html>`_  for more information
