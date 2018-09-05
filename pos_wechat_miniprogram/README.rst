=========================================
 Integrate POS with WeChat mini-program
=========================================

Integrate POS with WeChat mini-program

Verification mobile number
==========================

Quick
-----

Use the mobile phone number specified in your WeChat account.::

    authByWeChat: function (e) {
        var detail = e.detail;
        var params = {
            model: 'res.users',
            method: 'wechat_mobile_number_verification',
            args: [detail],
            context: {},
            kwargs: {}
        };
        odooRpc(params).then(function (res) {
            wx.setStorageSync('telephoneNumberVerified', res.result);
        })
    }

With code confirmation
----------------------

You need to enter a phone number and confirm the number using a code from SMS message.::

    submitNumber: function(e) {
        var value = e.detail.value;
        var TemplateID = 1; # id of verification template (model 'qcloud.sms.template')
        var params = {
            model: 'res.users',
            method: 'template_sms_mobile_number_verification',
            args: [value.usrtel, TemplateID],
            context: {},
            kwargs: {}
        };
        odooRpc(params).then(function (res) {
            # your code here ...
        });
    },
    submitCode: function (e) {
        var value = e.detail.value;
        var params = {
            model: 'res.users',
            method: 'check_verification_code',
            args: [value.code],
            context: {},
            kwargs: {}
        };
        odooRpc(params).then(function (res) {
            wx.setStorageSync('telephoneNumberVerified', res.result);
        });
    }

Credits
=======

Contributors
------------
* `Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>`__

Sponsors
--------
* `Sinomate <http://sinomate.net/>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/11.0/pos_wechat_miniprogram/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/pos_addons/11.0

HTML Description: https://apps.odoo.com/apps/modules/11.0/pos_wechat_miniprogram/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 11.0 ee2b9fae3519c2494f34dacf15d0a3b5bd8fbd06
