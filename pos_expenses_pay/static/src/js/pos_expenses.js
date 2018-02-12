odoo.define('pos_orders_history', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var PosDB = require('point_of_sale.DB');
    var core = require('web.core');
    var longpolling = require('pos_longpolling');
    var PopupWidget = require('point_of_sale.popups');
    var rpc = require('web.rpc');

    var QWeb = core.qweb;
    var _t = core._t;
    

    var _super_pos_model = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function () {
            _super_pos_model.initialize.apply(this, arguments);
            this.bus.add_channel_callback("pos_expenses", this.on_expenses_updates, this);
            this.subscribers = [];
        },

        add_subscriber: function (subscriber) {
            this.subscribers.push(subscriber);
        },

        on_expenses_updates: function (message) {
            var self = this;
            message.updated_expenses.forEach(function (id) {
                self.get_expense(id).done(function(expense) {
                    self.update_expenses(expense);
                });
            });
        },

        get_expense: function (id) {
            return rpc.query({
                model: 'hr.expense.sheet',
                method: 'read',
                args: [id]
            });
        },

        update_expenses: function (expense) {
            var i,
                max = this.db.expenses.length,
                expense = expense[0],
                expenses_to_update = [];

            for (i = 0; i < max; i++) {
                if (expense.id === this.db.expenses[i].id) {
                    this.db.expenses.splice(i, 1);
                    expenses_to_update.push(expense.id);
                    break;
                }
            }
            delete this.db.expenses_by_id[expense.id];

            if (((expense.state === 'done') || (expense.state == 'approve')) && !expense.processed_by_pos) {
                this.db.expenses.unshift(expense);
                this.db.expenses_by_id[expense.id] = expense;
            }
            this.publish_db_updates(expenses_to_update);        
        },

        publish_db_updates: function (ids) {
            _.each(this.subscribers, function (subscriber) {
                var callback = subscriber.callback,
                    context = subscriber.context;
                callback.call(context, 'update', ids);
            });
        },

    });

    models.load_models({
        model: 'hr.expense.sheet',
        fields: [],
        domain: function (self) {
            var domain = [
                ['payment_mode','=','own_account'],
                ['state', 'in', ['post', 'approve']],
            ];
            console.log("domain", domain);
            return domain;
        },

        loaded: function (self, expenses) {
            self.db.expenses = expenses;
            expenses.forEach(function (expense) {
                self.db.expenses_by_id[expense.id] = expense;                
            });
        },
    });

    PosDB.include({
        init: function (options) {
            this.expenses = [];
            this.expenses_by_id = {};
            this._super.apply(this, arguments);
        },
    });

    var ExpensesButton = screens.ActionButtonWidget.extend({
        template: 'ExpensesButton',
        button_click: function () {
            if (this.pos.db.expenses.length) {
                this.gui.show_screen('expenses_screen');
            }
        },
    });

    screens.define_action_button({
        'name': 'expenses_button',
        'widget': ExpensesButton,
        'condition': function () {
            return this.pos.config.pay_expenses;
        },
    });

    var ExpensesScreenWidget = screens.ScreenWidget.extend({
        template: 'ExpensesScreenWidget',

        init: function(parent, options){
            this._super(parent, options);
            this.selected_expense = false;
            this.subscribe();

        },
        auto_back: true,

        subscribe: function () {
            var subscriber = {
                context: this,
                callback: this.recieve_updates
            };
            this.pos.add_subscriber(subscriber);
        },

        show: function () {
            var self = this;
            this._super();
            this.clear_list_widget();

            this.$('.back').click(function () {
                self.gui.show_screen('products');
            });

            var expenses = this.pos.db.expenses;
            this.render_list(expenses);

            this.$('.expenses-list-contents').delegate('.order-line', 'click', function (event) {
                event.stopImmediatePropagation();
                self.line_select(event, $(this), parseInt($(this).data('id')));
            });

            this.$('.next').click(function () {
                if (!self.selected_expense) {
                    return;
                }
                self.process_expense(self.selected_expense);
            });
        },

        clear_list_widget: function () {
            this.$(".order-line").removeClass('active');
            this.$(".order-line").removeClass('highlight');
            this.selected_expense = false;
            this.hide_select_button();
        },

        render_list: function (orders) {
            var self = this,
                contents = this.$el[0].querySelector('.expenses-list-contents');
            contents.innerHTML = "";
            for (var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                var order = orders[i],
                    orderline = false;
                var orderline_html = QWeb.render('ExpensesList',{widget: this, order:orders[i]});
                orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                contents.appendChild(orderline);
            }
        },

        line_select: function (event, $line, id) {
            this.$(".order-line").not($line).removeClass('active');
            this.$(".order-line").not($line).removeClass('highlight');
            if ($line.hasClass('active')) {
                $line.removeClass('active');
                $line.removeClass('highlight');
                this.hide_select_button();                
                this.selected_expense = false;
            } else {
                $line.addClass('active');
                $line.addClass('highlight');
                this.show_select_button();                
                var y = event.pageY - $line.parent().offset().top;
                this.selected_expense = this.pos.db.expenses_by_id[id];
            }
        },

        process_expense: function (expense) {
            this.gui.show_popup('expenses-popup', {
                title: _t('Pay Expense'),
                expense_id: expense.id,
                body: _t('Pay expense in ' +  expense.total_amount + ' to ' + expense.employee_id[1])
            });
        },

        hide_select_button: function () {
            this.$('.next').addClass('line-element-hidden');
        },

        show_select_button: function () {
            this.$('.next').removeClass('line-element-hidden');
        },

        recieve_updates: function (action, ids) {
            switch (action) {
                case 'update':
                    if (this.gui.current_screen == this) {
                        this.show();                        
                    }
                    // this.update_list_items(ids);
                    break;
                default:
                    break;
            }
        },
    });

    gui.define_screen({name:'expenses_screen', widget: ExpensesScreenWidget});

    var ExpensesWidget = PopupWidget.extend({
        template: 'ExpensesWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },

        click_confirm: function () {
            var self = this,
                id = this.options.expense_id,
                cashier = this.pos.get_cashier();
            rpc.query({
                model: 'hr.expense.sheet',
                method: 'process_expense_from_pos',
                args: [id, cashier.name],
            }).then(function (res) {
                self.gui.close_popup();
            }).fail(function (type, error) {
                self.gui.show_popup('error', {
                    'title': _t(error.message),
                    'body': _t(error.data.arguments[0])
                });
                event.preventDefault();
            });
        },
    });

    gui.define_popup({name:'expenses-popup', widget: ExpensesWidget});    

});
