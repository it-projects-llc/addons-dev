==============================================
 Sync products via remote csv (custom module)
==============================================

Syncs products periodically with cron. Works only with specific column names. URL source can be customized.

Requires two csv files with following columns (order is important!):

1. ``product_import_custom.product``

   * "primary_key"
   * "Aktiv"
   * "Name"
   * "Kategorie"
   * "Preis"
   * "Tax"
   * "Rabatt"
   * "Rabattbetrag"
   * "Visibility"
   * "Brand"
   * "Menge"
   * "Kurzbeschreibung"
   * "Beschreibung"
   * "Tag"
   * "Meta-Schlag"
   * "intelli_KASSA_CAT"
   * "Meta-Title"
   * "TextInStock"
   * "TextSoldOut"
   * "URLBilder"
   * "Bild_löschen"
   * "Joker2"
   * "Bestellbar"
   * "ArtNr"
   * "show price"
   * "von"
   * "bis"

2. ``product_import_custom.product_variant``

   * "External ID"
   * "Internal Reference"
   * "Point of Sale Category / Datenbank ID"
   * "Name"
   * "price"
   * "Customer Taxes / Datenbank ID"
   * "primary_key"

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
