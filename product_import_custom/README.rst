==============================================
 Sync products via remote csv (custom module)
==============================================

Syncs products periodically with cron. Works only with specific column names. URL source and credentials are customized.

Requires two csv files with following columns (order is important!):

* ``product_import_custom.product`` ::

     0. "primary_key"
     1. "Aktiv"
     2. "Name"
     3. "Kategorie"
     4. "Preis"
     5. "Tax"
     6. "Rabatt"
     7. "Rabattbetrag"
     8. "Visibility"
     9. "Brand"
     10. "Menge"
     11. "Kurzbeschreibung"
     12. "Beschreibung"
     13. "Tag"
     14. "Meta-Schlag"
     15. "intelli_KASSA_CAT"
     16. "Meta-Title"
     17. "TextInStock"
     18. "TextSoldOut"
     19. "URLBilder"
     20. "Bild_löschen"
     21. "Joker2"
     22. "Bestellbar"
     23. "ArtNr"
     24. "show price"
     25. "von"
     26. "bis"

* ``product_import_custom.product_variant``::

     0. "External ID"
     1. "Internal Reference"
     2. "Point of Sale Category / Datenbank ID"
        TODO: this points directly to POS Category in odoo. It may be a problem on deploying module in a new database
     3. "Name"
     4. "price"
     5. "Customer Taxes / Datenbank ID"
     6. "primary_key"

Roadmap
=======

* The module has hardcoded ids from some record (see WTF marks in the source)

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/addons-dev/misc-addons-10.0-product_import_custom

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 10.0 2aa3132d09656f90520aaa89fdb0220823c3bd46
