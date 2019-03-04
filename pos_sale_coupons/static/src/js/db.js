//  Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
//  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
odoo.define('pos_sale_coupons.db', function (require) {
    'use_strict';

    var PosDb = require('point_of_sale.DB');

    PosDb.include({
        init: function (options) {
            this._super(options);
            this.sale_coupons = [];
            this.sale_coupons_by_id = {};
            this.sale_coupon_programs = [];
            this.sale_coupon_programs_by_id = {};
        },
        add_sale_coupons: function (coupons) {
            var self = this;
            _.each(coupons, function (coupon) {
                self.sale_coupons.push(coupon);
                self.sale_coupons_by_id[coupon.id] = coupon;
            });
        },
        update_sale_coupons: function(coupons) {
            var self = this;
            _.each(coupons, function (coupon) {
                self.sale_coupons_by_id[coupon.id] = coupon;
                // Search old coupon by id
                var old_coupon = self.sale_coupons.find(function(record) {
                    return record.id === coupon.id;
                });
                var index = self.sale_coupons.indexOf(old_coupon);
                // Update old coupon to new
                self.sale_coupons[index] = coupon;
            });
        },
        get_sale_coupon_by_id: function(id) {
            return this.sale_coupons_by_id[id];
        },
        get_sale_coupon_by_code: function(code) {
            return this.sale_coupons.find(function(coupon) {
                return coupon.code === code;
            });
        },
        add_sale_coupon_programs: function(programs) {
            var self = this;
            _.each(programs, function (program) {
                self.sale_coupon_programs.push(program);
                self.sale_coupon_programs_by_id[program.id] = program;
            });
        },
        get_sale_coupon_program_by_id: function(id) {
            return this.sale_coupon_programs_by_id[id];
        },
    });

    return PosDb;
});
