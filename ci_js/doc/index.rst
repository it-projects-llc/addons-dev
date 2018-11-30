========
 CI JS
========


Configuration
=============


Usage
=====

Creating a new tour
--------------------

* Open ``[[ CI JS ]] >> CI JS >> [Tours]``
* Press ``[Create]``
* In the opened window fill in the following fields:
    * **Tour name** - current tour name
    * **Start URL** - URL address to start the tour
    * **Wait for** - specify the condition under which the tour can be started (e.g. base.ready())
    * **Skip enabled** - check the box if you want to add the "Skip" button in the tips
    * **Using assets** - choose assets which you use (assets_frontend, assets_backend, pos_assets)
* In the ``Sets`` tab press ``[Add an item]``
* In the field **Set name** enter the name of the current tour
* In the field **Template** press on the drop-down menu and select the appropriate template
* If the list does not have a suitable template, then click on the ``[Create and Edit]`` button:
    * In the field **Template name** fill in the name of the creating template
    * In the ``Steps`` tab press ``[Add an item]`` button and fill in the following fields in the window that appears:
        * **content** - will be displayed in tips.
        * **trigger** - where to place tip. In js tests: where to click (mandatory)
        * **extra_trigger** - when this becomes visible, the tip is appeared. In js tests: when to click
        * **timeout** - max time to wait for conditions
        * **position** - how to show tip (left, rigth, top, bottom), default right
        * **width** - width in px of the tip when opened, default 270
        * **edition** - specify to execute in “community” or in “enterprise” only. By default empty – execute at any edition
        * **run** - what to do when tour runs automatically (e.g. in tests)
        * **auto** - step is skipped in non-auto running
    * If you need to add another step - click ``[Save & New]`` button or ``[Save & Close]`` button if steps are over
    * Press ``[Save]`` button if all work is done with current template
* Когда шаблон выбран, то под полем ``[Template]`` появляются поля с названиями переменных, которые принимает шаблон(если он их принимает), нужно заполнить эти поля, в соответствии с контекстом
* Когда все необходимые поля заполнены, можно нажать ``[Save & New]``, если нужно добавить еще один set. Если составление сетов для тура закончено можно нажать ``[Save & Close]``
* Чтобы сохранить получившийся тур нужно нажать ``[Save]``, после этого увидим наш тур во вкладке ``Tours``

Отладка и быстрый запуск тура
-----------------------------

* Открыть ``[[ CI JS ]] >> CI JS >> [Tours]``
* В списке туров найти необходимый и открыть его
* Нажать на ``[Start tour]``, после чего тур запустится


Генерация файла тура
--------------------

* Открыть ``[[ CI JS ]] >> CI JS >> [Tours]``
* В списке туров найти необходимый и открыть его
* Нажать на ``[Download tour]``

Генерация XML-кода для экспорта шаблонов
-----------------------------------------
* Открыть ``[[ CI JS ]] >> CI JS >> [Templates]``
* Нажать ``[Generate XML]``, после код можно будет скопировать из формы

Генерация JS-кода отдельного сета в туре для отладки
----------------------------------------------------

* Открыть ``[[ CI JS ]] >> CI JS >> [Tours]``
* Открыть необходимый тур
* Открыть интересующий сет и нажать ``[Generate JS]``, после чего код можно скопировать из формы.
