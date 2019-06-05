=========================
 Backups to Google Drive
=========================

Installation
============

* Install `Google API Client Library for Python <https://developers.google.com/api-client-library/python/>`__ ::

    pip install google-api-python-client

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Creating Service Account Key
----------------------------

Note: You need to have a Google Account

* Open the GCP Console. https://console.cloud.google.com/
* Login to Google.
* В верхнем меню нажмите "Выберете проект"
* В открывшемся окне нажмите "СОЗДАТЬ ПРОЕКТ"
* Укажите название проекта и Местоположение при необходимости
* Нажмите "создать"
* В верхнем меню выберете созданный проект из списка проектов
* Откройте меню навигации (Верхняя левая кнопка)
* Выберете API и Сервисы >> Библиотека
* В Поиске найдите Google Drive API и включите его
* Перейдите в раздел Учетные данные в меню слева
* На кнопке "Создать учетные данные" выберете "Ключ сервисного аккаунта"
* Укажите "Сервисный аккаунт" или создайте новый
  * При создании нового сервисного аккаунта укажите роль "Проект" >> "Владелец"
  * Укажите Название сервисного аккаунта
  * Start Odoo with ``--load=web,odoo_backup_sh`` or set the ``server_wide_modules`` option in the Odoo configuration file:
* Укажите тип ключа JSON
* Нажмите "Создать" (ключ автоматически скачается)
* Откроется страница "Учетные данные" нажмите на "Управление сервисными аккаунтами"
* Запомните Электронную почту Сервисного аккаунта.

Set rights to Folder in Google Drive
------------------------------------

* Откройте Google Drive https://www.google.com/drive/
* Создайте новую папку и новозите "Backups"
* Правой кнопкой мыши нажмите на эту папку и выберете "Открыть Доступ"
* В открывшемся окне укажите email Сервисного аккаунта
* Нажмите готово.

Установка закрытого ключа сервисного Аккаунта на сервер
-------------------------------------------------------

(Ниже приведен пример для сервера запущенного с помощью Docker)

* Скопируйте ключ в Docker контейнер::

  docker cp PATH_FROM/YOU_FILE_NAME.JSON CONTAINER_NAME:/PATH_TO

Настройка Сервера
-----------------

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Откройте меню Backups >> Configuration >> Settings
* Укажите Google Drive
* Нажмите Save

Usage
=====

Open the menu ``[[ Backups ]] >> Dashboard``

Top window is a general statistics of all your backups are stored on a remote server.

.. todo:: Add a description of top window when interfaces are ready.

Below are the forms for managing and controlling backups of your databases.
In addition to auto backup, you can make new backup manually at any time.
Backups taken by hand are not involved in auto rotation conditions.

.. todo:: Add the section when interfaces are ready.

{Instruction for daily usage. It should describe how to check that module works. What shall user do and what would user get.}

* Open menu ``{Menu} >> {Submenu} >> {Subsubmenu}``
* Click ``[{Button Name}]``
* RESULT: {what user gets, how the modules changes default behaviour}
