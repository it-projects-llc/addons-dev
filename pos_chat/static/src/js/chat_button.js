//odoo.define('pos_chat_button', function (require){
//      'use_strict';
//
//    var gui = require('point_of_sale.gui');
//    var PopupWidget = require('point_of_sale.popups');
//    var screens = require('point_of_sale.screens');
//    var rpc = require('web.rpc');
//    var session = require('web.session');
//
//    var models = require('point_of_sale.models');
//    //declare a new variable and inherit ActionButtonWidget
//
//    var ChatButton = screens.ActionButtonWidget.extend({
//        template: 'ChatButton',
//        button_click: function () {
//            this.gui.show_popup('chat',{
//              'title': 'Chat',
//              'value': false,
//            });
//            if(messages.length == 0)
//            {
//                var messageList = document.getElementById('message-list');
//                messageList.innerHTML = '<li class="text-right small"><em>Welcome to chat!</em></li>';
//                loadComments();
//            }
//            else showMessages();
//        }
//    });
//
//
//    // Messages are stored here
//    var messages = [];
//    var user = session.name;
//
//    var PosModelSuper = models.PosModel;
//    models.PosModel = models.PosModel.extend({
//
//        initialize: function () {
//
//          PosModelSuper.prototype.initialize.apply(this, arguments);
//          var self = this;
//
//          self.bus.add_channel_callback("pos_chat_228", self.on_barcode_updates, self);
//        },
//
//        on_barcode_updates: function(data){
//
//            var self = this;
//
//            var tempMessage = {
//                text : data.message,
//                time : data.date,
//                name : data.name
//            }
//
//            AddNewMessage(tempMessage);
//        },
//    });
//
//    var ChatPopupWidget = PopupWidget.extend({
//        template: 'ChatPopupWidget',
//        show: function () {
//          var self = this;
//          this._super();
//
//            this.$('.back').click(function () {
//                self.gui.show_screen('products');
//            });
//
//            this.$('.next').click(function () {
//                var newMessage = document.getElementById('text-line');
//                var tempMessage = {
//                    text : newMessage.value,
//                    time : Math.floor(Date.now()/1000),
//                    name : session.name
//                }
//
//                newMessage.value = '';
//
//                self._rpc({
//                    model: "pos.chat",
//                    method: "send_field_updates",
//                    args: [tempMessage.text, tempMessage.time, tempMessage.name]
//                })
//            });
//        },
//    });
//
//    function AddNewMessage(message)
//    {
//        messages.push(message);
//        saveMessages();
//        showMessages();
//    }
//
//    gui.define_popup({name:'chat', widget: ChatPopupWidget});
//
//    screens.define_action_button({
//        'name': 'chat_button',
//        'widget': ChatButton,
//    });
//
//    function saveMessages()
//    {
//        localStorage.setItem('messages', JSON.stringify(messages));
//    }
//
//    function showMessages()
//    {
//        var messageList = document.getElementById('message-list');
//        var out = '';
//        messages.forEach(function (item)
//        {
//        out += '<li class="text-right small"><em>' + timeConverter(item.time) + ' (' + item.name +'):</em></li>';
//        out += '<li class="text-right small"><em>' + item.text + '</em></li>';
//        });
//        messageList.innerHTML = out;
//    }
//
//    function loadComments()
//    {
//        localStorage.setItem('messages', JSON.stringify(messages));
//    }
//
////     Time converter function
//    function timeConverter(UNIX_timestamp)
//    {
//        var a = new Date(UNIX_timestamp * 1000);
//        var months = ['Jan', 'Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
//        var year = a.getFullYear();
//        var month = months[a.getMonth()];
//        var date = a.getDate();
//        var hour = a.getHours();
//        var min = a.getMinutes();
//        var sec = a.getSeconds();
//        var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec;
//        return time;
//    }
//
//    return ChatButton;
//});

odoo.define('pos_chat_button', function (require){
      'use_strict';

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var session = require('web.session');
    var PopupWidget = require('point_of_sale.popups');
    var models = require('point_of_sale.models');

    var current_message = '';
    var last_key_pressed = 0;
    var messages = [];

    var ChatButton = screens.ActionButtonWidget.extend({
        template: 'ChatButton',
        button_click: function () {
            this.gui.show_screen('custom_screen');
            SetPos();
        }
    });

    var CustomScreenWidget = screens.ScreenWidget.extend({
        template: 'CustomScreenWidget',
        show: function () {
          var self = this;
          this._super();

            this.$('.back').click(function () {
                self.gui.show_screen('products');
            });

            this.$('.next').click(function () {
                SendMessage()
            });

            this.$("#text-line").keyup(function(event){

                if(event.keyCode == 13){
                    SendMessage();
                }
            });
        }
    });

    gui.define_screen({name:'custom_screen', widget: CustomScreenWidget});

    screens.define_action_button({
        'name': 'chat_button',
        'widget': ChatButton,
    });


    // Users number
    var user_num = 1;
    var radius = 200;
    var messages = [];
    var timeOut = [];

    function SendMessage()
    {
        if(messages.length == 2)
        {
            var text = messages[1].text;
            messages[1] = messages[0];
            clearTimeout(timeOut[0]);
            Disappear();
            messages[0].text = text;
        }

        var newMessage = document.getElementById('text-line');
        current_message = {
            text : newMessage.value,
            time : Math.floor(Date.now()/1000),
            name : session.name,
            class : 'new-message-' + messages.length + '',
            id : 'message-id-' + messages.length + '',
            appeared : false
        }


        if(messages.length == 1 && messages[0].class == 'new-message-1')
        {
            messages[0].class = 'new-message-0';
            messages[0].id = 'message-id-0';
        }

        messages.push(current_message);

        showMessages(messages.length - 1);
        newMessage.value = '';
    }

    function showMessages(num)
    {
        message = document.getElementById('message-id');
        var out ='';
        if(num == 1)
            out += '<div class="' + messages[num - 1].class + '" id="' + messages[num - 1].id + '"><em>' + messages[num - 1].text + '</em></div>';
        out += '<div class="' + messages[num].class + '" id="' + messages[num].id + '"><em>' + messages[num].text + '</em></div>';
        message.innerHTML = out;

        if(messages[num].appeared == false)
        {
            $("."+ messages[num].class +"").fadeIn();
            messages[num].appeared = true;
            timeOut.push(window.setTimeout(Disappear,5000));
        }
    }

    function Disappear()
    {
        $("."+ messages[0].class +"").fadeOut();
        messages.shift();
        timeOut.shift();
    }

    function SetPos()
    {
        var action_window = document.getElementById('main-window');
        var avatar = document.getElementById('picture');
        var angle = 2 * 3.1415 / (session.uid - 1);
        var circle_x = action_window.offsetWidth / 2;
        var circle_y = action_window.offsetHeight / 2;
        var x = circle_x + radius*Math.cos(angle);
        var y = circle_y + radius*Math.sin(angle);
        avatar.style.setProperty('--pos-X', x - (avatar.offsetWidth / 2) + 'px');
        avatar.style.setProperty('--pos-Y', y - (avatar.offsetHeight / 2) + 'px');

    }

//    $("." + message_class + "").fadeIn();
//    var disappear_bool_timer = window.setTimeout(function(){disappeared_first = true;},5000);

    return ChatButton;
});
