====================
 Web Widget HeatMap
====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

In the view declaration, put widget='heatmap' attribute in the field tag::

    ...
    <field name="arch" type="xml">
        <form string="View name">
            ...
            <field name="field_name_ids" widget="heatmap"/>
            ...
        </form>
    </field>
    ...

All options of the widget available `here <https://cal-heatmap.com/>`__

To use the options in the view declaration, specify 'options' attribute in the field tag::

    ...
    <field name="arch" type="xml">
        <form string="View name">
            ...
            <field name="field_name_ids" widget="heatmap" options="{'domain: 'day', subDomain: 'hour'}"/>
            ...
        </form>
    </field>
    ...

