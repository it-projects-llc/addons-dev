odoo.define('pos_chat_button', function (require){
      'use_strict';

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var session = require('web.session');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');

//-------------------- Variables -----------------------

    var game_started = false;
    // Information about every user
    var chat_users = [];
    // Are user in chat room right now
    var in_chat = false;
    // Full channel name
    var channel = "pos_durak";
    // Donald Trump
    var trump = -1;
    // who moves
    var who_moves = [0,0];
    // Game mode
    var attacking = false;
    var W = 0;
    var H = 0;
    // On table cards
    var on_table_cards = [];
    var complete_move = 0;
    // How much cards on the table
    var moves_cnt = 0;
    // Cards max count
    var max_cards = 6;
    // Defender counter
    var choose_and_beat = 0;
    var def_cards = [0,0];
    var all_cards = [];
    var card_suits = ['Heart', 'Diamond', 'Clubs', 'Spade'];
    var my_game_id = -1;

//------------------------------------------------------

//--------------- Game table actions -------------------

    function Tip(str, how_long_to_hold){
        var text = document.getElementById('for-inscriptions');
        text.innerHTML = str;
        $(".tips").fadeIn(500);

        text.style.setProperty('transform','translate3d(0px,'+(H/2 - text.offsetTop)+'px,0px)');
        setTimeout(function () {
        text.style.setProperty('transform','translate3d(0px,'+(H*3 - text.offsetTop)+'px,0px)');
        },how_long_to_hold);

        setTimeout(function () {
            $(".tips").fadeOut(500);
            text.style.setProperty('top', '0');
        },how_long_to_hold + 1000);
    }

    function Comp(card_num1, card_num2){
        var card1 = Card_power(card_num1);
        var card2 = Card_power(card_num2);
        card1[0] = (card1[1] === trump) ? (card1[0] + 100) : card1[0];
        card2[0] = (card2[1] === trump) ? (card2[0] + 100) : card2[0];
        if (card1[1] === card2[1] || card1[1] === trump || card2[1] === trump){
            return card1[0] > card2[0] ? 1 : 2;
        }
        return -1;
    }

    function Defendence(x, y) {
        var ans = Comp(def_cards[0], def_cards[1]);
        if(ans === 2){
            alert('Your card is weaker!');
        }
        else if(ans === -1){
            alert('This cards are different suits!');
        }
        else if(ans === 1){
            self._rpc({
                model: "pos.session",
                method: "defend",
                args: [session.uid, def_cards[0], def_cards[1], x, y]
            });
        }

        def_cards = [0,0];
    }

    function Take_Cards() {
        // Need to finish
        var temp_cards = '';
        for(var i = 0; i < on_table_cards.length; i++){
            temp_cards += on_table_cards[i] + ' ';
        }
        self._rpc({
            model: "pos.session",
            method: "take_cards",
            args: [session.uid, temp_cards]
        });
    }

    function Ask_who_steps() {
        if(NumInQueue(session.uid) === 0) {
            self._rpc({
                model: "game",
                method: "who_should_step",
                args: [my_game_id]
            });
        }
    }

//------------------------------------------------------

//-------------Help functions part----------------------
    // Checks out which num user has
    function NumInQueue(uid){
        for(var i = 0; i < chat_users.length; i++){
            if(chat_users[i].uid === uid) {
                return i;
            }
        }
    }

    function OnTable(n) {
        for(var i = 0; i < on_table_cards.length; i++){
            if(on_table_cards[i] === n) {
                return true;
            }
        }
        return false;
    }

    function Is_card_moved(card_power) {
        for(var i = 0; i < moved_cards.length; i++){
            if(moved_cards[i] === card_power[0]){
                return true;
            }
        }
        return false;
    }

    var triangle_button_pushed = false;
    function ControlOnClick(e) {
        var elem = e ? e.target : window.event.srcElement;
        var num = '';
        if(elem.id[0]+elem.id[1]+elem.id[2]+elem.id[3] === 'card'){
           if(elem.id[elem.id.length - 2] !== '-') num = elem.id[elem.id.length - 2];
           num += elem.id[elem.id.length - 1];
           // Checking who is player - defender or attacker
           if(session.uid === next_to(who_moves[0], true)){
               if(!OnTable(num) && choose_and_beat > 0){
                   return;
               }
               choose_and_beat++;
               def_cards[choose_and_beat - 1] = num;
               if(choose_and_beat === 2){
                   choose_and_beat = 0;
                   Defendence(e.pageX/W, e.pageY/H);
               }
           }
           else{
               Move(num);
           }
        }
        else if(elem.id === "ready-button"){
            self._rpc({
                model: "game",
                method: "player_is_ready",
                args: [my_game_id, session.uid]
            });
        }
        else if(elem.id === "step-button"){
            self._rpc({
               model: 'game',
               method: 'cards_are_beated',
               args: [my_game_id]
            });
        }
        else if(elem.id === "take-button"){
            Take_Cards();
        }
        else if(elem.id === "check-button"){
            self._rpc({
               model: 'game',
               method: 'start_the_game',
                args: [my_game_id]
            });
        }
        else if(elem.id === "triangle"){
            var menu = document.getElementsByClassName('game-tools')[0];
            var chat = document.getElementsByClassName('chat-tools')[0];
            if(!triangle_button_pushed){
                menu.style.setProperty('transform','scaleX(1)');
                menu.style.setProperty('-webkit-transform','scaleX(1)');
                menu.style.setProperty('-ms-transform','scaleX(1)');
                chat.style.setProperty('transform','scaleX(1)');
                chat.style.setProperty('-webkit-transform','scaleX(1)');
                chat.style.setProperty('-ms-transform','scaleX(1)');
                triangle_button_pushed = true;
            }
            else{
                triangle_button_pushed = false;
                menu.style.setProperty('transform','scaleX(0)');
                menu.style.setProperty('-webkit-transform','scaleX(0)');
                menu.style.setProperty('-ms-transform','scaleX(0)');
                chat.style.setProperty('transform','scaleX(0)');
                chat.style.setProperty('-webkit-transform','scaleX(0)');
                chat.style.setProperty('-ms-transform','scaleX(0)');
            }
        }
        else if(elem.id[0]+elem.id[1]+elem.id[2] === "ava" && game_started){
            num = (elem.id[elem.id.length - 2] !== '-' ? elem.id[elem.id.length - 2] : '')
                + elem.id[elem.id.length - 1];
            HowMuchCards(chat_users[Number(num)].uid);
        }
        else{
            // If you missed
            if (choose_and_beat === 1){
                choose_and_beat--;
                Tip("Firstly - choose card, then - beat another one", 4000);
            }
        }
    }
//------------------------------------------------------

//-------------- New screen defenition -----------------
    var ChatButton = screens.ActionButtonWidget.extend({
        template: 'ChatButton',
        button_click: function () {
            self = this;
            this.gui.show_screen('custom_screen');
            // User in to the chat room
            in_chat = true;
            W = document.getElementById('main-window').offsetWidth;
            H = document.getElementById('main-window').offsetHeight;
            // Current users says that he connected to other users
            self._rpc({
                model: "game",
                method: "create_the_game",
                args: [channel, session.uid]
            });
        }
    });

//------------------------------------------------------

//---------- Text insertion buttons control ------------
    var CustomScreenWidget = screens.ScreenWidget.extend({
        template: 'CustomScreenWidget',
        show: function () {
          var self = this;
          this._super();
            // Returning to POS main screen
            this.$('.back').off().click(function () {
                self.gui.show_screen('products');

                self._rpc({
                    model: "game",
                    method: "delete_player",
                    args: [my_game_id, session.uid]
                });

                DeleteMyData();
            });
            // Send new messages using button
            this.$('.next').off().click(function () {
                TakeNewMessage(false);
            });
            // Send new messages using 'Enter' key on keyboard
            this.$("#text-line").off().keyup(function(event){
                if(event.keyCode === 13){
                    TakeNewMessage(true);
                }
            });

            window.onclick=function(e){
                ControlOnClick(e);
            }
        }
    });

    // Defining new screen
    gui.define_screen({name:'custom_screen', widget: CustomScreenWidget});

    screens.define_action_button({
        'name': 'durak_button',
        'widget': ChatButton,
    });

//------------------------------------------------------

//---------Help functions part----------------------

    function message_view(message_id, display){
        var single_message = document.getElementById(message_id);
        single_message.style.setProperty('border-radius', '20%');
        single_message.style.setProperty('background','white');
        single_message.style.setProperty('top','10px');
        single_message.style.setProperty('width','100px');
        single_message.style.setProperty('font','14pt sans-serif');
        if(display){
            single_message.style.setProperty('display', 'none');
        }
    }

    function CheckUserExists(uid){
        for(var i = 0; i < chat_users.length; i++){
            if(uid === chat_users[i].uid) return true;
        }
        return false;
    }

    function DeleteMyData(){
        chat_users = [];
        in_chat = false;
        game_started = false;
        try {
            document.getElementById('cards').innerHTML = '';
            document.getElementById('cards').innerHTML = '';
            var check_button = document.getElementById('check-button');
            check_button.style.setProperty('opacity', '0');
            document.getElementById('enemy-cards').innerHTML = '';
            document.getElementById('suit').style.display = 'none';
        }
        catch (error) {
            // Nothing to do
        }
    }
    // Is this string the tag checking
    function is_it_tag(str, send)
    {
        var left = 0, right = 0, slash = 0;
        var text = '';
        for(var i = 0; i < str.length; i++){
            if(left + right === 2 && str[i] !== '<'){
                text += str[i];
            }
            if(str[i] === '<')left++;
            if(str[i] === '>')right++;
            if(str[i] === '/') slash++;
        }
        // If send mode is active
        if(send) {
            return text;
        }

        return left === 2 && right === 2 && slash === 1 ? true : false;
    }

    function next_to(num, already_converted){
        var i = already_converted ? num : NumInQueue(num);
        return i === chat_users.length - 1 ?
            chat_users[0].uid : chat_users[i + 1].uid;
    }
//--------------------------------------------------

//--------------- Game table actions -------------------

    function PutOn(card) {
        var sign = (moves_cnt + 1)%2 === 0 ? 1 : -1;
        var cw = card.offsetWidth, ch = card.offsetHeight;

        var put_w = ((W - cw)/2) + (moves_cnt*cw)*(sign*0.5), put_h = (H - ch)/2;
        var x = card.offsetLeft, y = card.offsetTop;
        card.style.setProperty('opacity','1');
        card.style.setProperty('transform','translate3d('
            +(put_w - x)+'px,'+(put_h - y)+'px,0px)');
        card.style.left = x;card.style.top = y;
    }

    function Cover(card, x2, y2) {
        var card1 = document.getElementById('card-'+card);
        var x1 = card1.offsetLeft, y1 = card1.offsetTop;
        var w = card1.offsetWidth, h = card1.offsetHeight;
        card1.style.setProperty('transform','translate3d('+
            (((x2*W) - w/2) - x1)+'px,'+(((y2*H) - h/2) - y1)+'px,0px)');
    }

    function Move(card_num){
        // Need to check suit of card, and make a decide
        // Can player make a step or no
        if(OnTable(card_num)){
            return;
        }
        if(moves_cnt >= max_cards){
            alert('You can step only '+max_cards+' times!');
            return;
        }
        var stepper = [chat_users[who_moves[0]].uid,
            next_to(next_to(who_moves[0], true),false)];
        if(stepper[0] === session.uid){
            self._rpc({
                model: "pos.session",
                method: "moved",
                args: [session.uid, card_num]
            });
        }
        else if(stepper[1] === session.uid && attacking){
            self._rpc({
                model: "pos.session",
                method: "moved",
                args: [session.uid, card_num]
            });
        }
        else{
            alert('Not so fast, its not your turn!');
        }
    }

    function HowMuchCards(uid){
        self._rpc({
            model: "game",
            method: 'cards_number',
            args: [my_game_id, uid, session.uid]
        });
    }

    function ShowHowMuchCards(num){
        Tip(num, 1500);
    }

    function DownloadEnemyCards(n, user){
        for(var i = 0; i < all_cards.length; i++){
            if(n === all_cards[i]){
                return;
            }
        }
        all_cards.push(n);
        chat_users[NumInQueue(user)].cards.push(n);
        var out ='<img type="button" src="/pos_durak/static/src/img/kards/'+
                n+'.png" id="card-'+n+'" class="enemy-card"/>';
        document.getElementById('enemy-cards').innerHTML += out;
    }

    function DeleteCard(n, who){
        for(var i = 0; i < chat_users[who].cards.length; i++){
            if(n === chat_users[who].cards[i].num){
                chat_users[who].cards.splice(i,1);
            }
        }
        on_table_cards.push(n);
        if(session.uid === chat_users[who].uid){
            self._rpc({
                model: "pos.session",
                method: "send_field_updates",
                args: ['', '', 'DeleteExtraCard', chat_users[who].uid]
            });
        }
    }

    function AddExtraCards(temp) {
        for(var i = 0; i < temp_extra_cards.length; i++){
            chat_users[temp].cards.push(temp_extra_cards[i]);
        }
        while(temp_extra_cards.length > 0){
            temp_extra_cards.shift();
        }
    }

    function First_scene(){
        var i = 0;
        attacking = false;
        complete_move = 0;
        moves_cnt = 0;
        // Take new cards
        AddExtraCards(NumInQueue(session.uid));
        for(i = 0; i < on_table_cards.length; i++){
            var card = document.getElementById('card-'+on_table_cards[i]);
            card.style.setProperty('opacity', '0');
        }
        while(on_table_cards.length > 0){
            on_table_cards.shift();
        }
        while(moved_cards.length > 0){
            moved_cards.shift();
        }
        for(i = 0; i < chat_users.length; i++){
            document.getElementById('picture-'+i).
            style.setProperty('opacity','1');
        }
        document.getElementById('step-button').style.setProperty('opacity', '0');
        document.getElementById('take-button').style.setProperty('opacity','0');
        Ask_who_steps();
        if(in_chat){
            ShowUsers();
            ShowCards();
        }
    }

    function Second_scene(data){
        document.getElementById('ready-button').style.setProperty('display', 'none');
        var who_attacks = [chat_users[who_moves[0]].uid,chat_users[who_moves[1]].uid];
        var who_defends = next_to(who_attacks[0], false);
        if(who_attacks[0] === session.uid || who_attacks[1] === session.uid){
            document.getElementById('step-button').style.setProperty('opacity', '1');
        }
        // Hode other players
        for(var i = 0; i < chat_users.length; i++){
            var temp = chat_users[i].uid;
            if(temp !== who_attacks[0] && temp !== who_attacks[1]
            && temp !== who_defends){
                document.getElementById('picture-'+i).
                style.setProperty('opacity','0');
            }
        }
        var attacker_id_1 = document.getElementById('picture-'+NumInQueue(who_attacks[0]));
        var attacker_id_2 = document.getElementById('picture-'+NumInQueue(who_attacks[1]));
        var defender_id = document.getElementById('picture-'+NumInQueue(who_defends));
        // Inscription showing
        if(session.uid === who_attacks[0] || session.uid === who_attacks[1]){
            Tip('Attack'+String(chat_users[NumInQueue(who_defends)].name), 2000);
        }
        if(session.uid === who_defends){
            var button = document.getElementById('take-button');
            button.style.setProperty('opacity','1');
            Tip('Defend yourself', 2000);
        }

        var x, y, bias, bias_top;
        if(attacker_id_1 !== null){
            x = attacker_id_1.offsetLeft, y = attacker_id_1.offsetTop, bias = attacker_id_1.offsetWidth;
            bias_top = session.uid === who_defends ? -(y+H*0.05) : (H*0.75 - y);
            attacker_id_1.style.setProperty('transform','translate3d('
                +(W/2 - x - bias)+'px,'+(bias_top)+'px,0px)');
            attacker_id_1.style.setProperty('transition','transform .3s ease-in-out');
        }
        if(attacker_id_2 !== null && who_attacks[0] !== who_attacks[1]){
            x = attacker_id_2.offsetLeft, y = attacker_id_2.offsetTop, bias = attacker_id_2.offsetWidth;
            bias_top = session.uid === who_defends ? -(y+H*0.05) : (H*0.75 - y);
            attacker_id_2.style.setProperty('transform','translate3d('
                +(W/2 - x + bias)+'px,'+(bias_top)+'px,0px)');
            attacker_id_2.style.setProperty('transition','transform .3s ease-in-out');
        }
        if(defender_id !== null){
            x = defender_id.offsetLeft, y = defender_id.offsetTop;
            bias_top = session.uid === who_defends ? ((H*0.75) - y) : -(y+(H*0.05));
            defender_id.style.setProperty('transform','translate3d('
                +(W/2 - x)+'px,'+bias_top+'px,0px)');
            defender_id.style.setProperty('transition','transform .3s ease-in-out');
        }
    }
//------------------------------------------------------

//---------- Set avatar and animation part -------------
    function ShowCards(){
        var block = document.getElementById('cards');
        var me = NumInQueue(session.uid);
        var out = '', w = (60/chat_users[me].cards.length)/2;
        for(var i = 0; i < chat_users[me].cards.length; i++){
            var num = chat_users[me].cards[i].num;
            out+='<img type="button" src="/pos_durak/static/src/img/kards/'+
            num+'.png" id="card-'+num+'" class="card" style="right: '+(30 - i*w)+'%"/>';
        }
        block.innerHTML = out;
    }

    function ShowUsers(){
        var window = document.getElementById('main-window');
        var out = '';
        chat_users.forEach(function (item){
            var i = NumInQueue(item.uid);
            var str_uid = String(item.uid);
            out += '<div class="chat-user" id="picture-'+i+'">';
            out += '<div class="user-name" id="user-name-'+str_uid+'">'+chat_users[i].name+'</div>';
            out += '<img src="/web/image/res.users/' +
            item.uid + '/image_small" id="ava-' + i +'" class="avatar" style="border-radius:50%;"/>';

            out += '<ul class="game-message" id="messages-'+str_uid+'"></ul>';
            out += '</div>';
        });
        window.innerHTML = out;

        chat_users.forEach(function(item){
            SetPos(document.getElementById('picture-'+NumInQueue(item.uid)), item.uid);
        });
    }

    function SetPos(avatar, uid){
        var cnt = NumInQueue(uid) + 1;
        var angle = (2 * 3.1415 / chat_users.length) * cnt;
        var radius = Math.min(W*0.7,H*0.7)/2;
        var x = Math.trunc(radius*Math.cos(angle));
        var y = Math.trunc(radius*Math.sin(angle));

        avatar.style.setProperty('left', W/2 - (avatar.offsetWidth / 2) + 'px');
        avatar.style.setProperty('top', H*0.4 - (avatar.offsetHeight / 2) + 'px');
        avatar.style.setProperty('transform','translate3d('+x+'px,'+y+'px,0px)');
    }
//------------------------------------------------------

//------ Message taking and showing functions ----------

    function TakeNewMessage(delete_last_char){
        var i = NumInQueue(session.uid);

        var newMessage = document.getElementById('text-line');

        if(newMessage.value === ''){
            newMessage.value = '';
            return;
        }

        var text = newMessage.value;
        if(delete_last_char) {
            text.substring(0, text.length - 2);
        }

        if(is_it_tag(newMessage.value, false)){
            text = is_it_tag(newMessage.value, true);
        }

        self._rpc({
            model: "game",
            method: "send_message",
            args: [my_game_id, text, session.uid]
        });

        if(text === '/deletemygame'){
            self._rpc({
                model: "game",
                method: "delete_my_game",
                args: [my_game_id]
            });
        }

        newMessage.value = '';
    }

    function showMessage(uid, message){
        var i = NumInQueue(uid);
        var messages = document.getElementById('messages-'+String(uid));
        var out = '<div id="msg-'+chat_users[i].msg_cnt+'-'+uid+'">';
        out += '<p style="background: white;transition:' +
            ' all .3s ease-in-out;border-radius: 20%;margin-top: 5px;' +
            'margin-bottom: 0px;">'+message+'</p>';
        out += '<audio src="/pos_durak/static/src/sound/msg.wav" autoplay="true"></audio>';
        out += '</div>';
        messages.innerHTML += out;
        setTimeout(delete_message,15000, chat_users[i].msg_cnt, uid);
        chat_users[i].msg_cnt++;
    }

    function delete_message(msg, uid) {
        var old_message = document.getElementById('msg-'+String(msg)+'-'+uid);
        old_message.style.setProperty('display','none');
    }
//--------------------------------------------------

//--------------- Users relations part -----------------

    function AddNewUser(user_data) {
        var i = 0
        // If user connected too late
        if(game_started) return;

        if(chat_users.length === 0){
            chat_users = new Array(user_data.num + 1)
            for(i = 0; i < user_data.num; i++){
                chat_users[i] = ({
                    name : '',
                    uid : -1,
                    msg_cnt: 0,
                    cards : []
                });
            }
        }

        if(user_data.num < chat_users.length){
            chat_users[user_data.num] = ({
                name : user_data.name,
                uid : user_data.uid,
                msg_cnt: 0,
                cards : []
            });
        }
        else{
            chat_users.push({
                name : user_data.name,
                uid : user_data.uid,
                msg_cnt: 0,
                cards : []
            });
        }


        if(chat_users[0].uid === session.uid){
            // alert("If players are ready, push 'Start the game' button." +
            //     "Then game will begin.")
            var check_button = document.getElementById('check-button');
            check_button.style.setProperty('opacity', '1');
        }
        else{
            var ready_button = document.getElementById('ready-button');
            ready_button.style.setProperty('opacity', '1');
        }
        // Don't show players till they all become setted
        // Return even if one of players didn't throw response
        for(i = 0; i < chat_users.length; i++){
            if(chat_users[i].uid === -1 ) return;
        }

        ShowUsers();
    }

    function DeleteUser(user_id){
        var exist = false;
        chat_users.forEach(function (item) {
           if(item.uid === user_id) {
               exist = true;
           }
        });
        if(!exist) {
            return;
        }
        chat_users.splice(NumInQueue(user_id),1);
        if(user_id !== session.uid){
            ShowUsers();
        }
    }

    function Distribute_cards(data, took_cards){
        var ses = NumInQueue(session.uid);
        while(chat_users[ses].cards.length > 0){
            chat_users[ses].cards.shift();
        }
        if(took_cards){
            var str = data.message;
            for(var i = 0; i < str.length - 1; i++){
                var num = '';
                if(str[i] !== ' '){
                    if(str[i + 1] !== ' '){
                        chat_users[ses].cards.push(str[i] + str[i + 1]);
                        i++;
                    }
                    else
                        chat_users[ses].cards.push(str[i]);
                }
            }
            ShowCards();
        }
        else if(session.uid === chat_users[0].uid){
            self._rpc({
                model: "pos.session",
                method: "cards_distribution"
            });
        }
    }

    function CreatePlayer() {
        self._rpc({
            model: "game",
            method: "add_new_user",
            args: [my_game_id, session.name, session.uid]
        });
    }

//------------------------------------------------------
//-------------- Longpooling functions -----------------

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({

        initialize: function () {
            PosModelSuper.prototype.initialize.apply(this, arguments);
            var self = this;
            // Listen to 'pos_durak' channel
            self.bus.add_channel_callback(channel, self.catch_server_response, self);
        },

        catch_server_response: function(data){
            if(!in_chat){
                return;
            }
            var self = this;
            // If someone connected to the chat
            if(data.command === 'Connect'){
                if(!CheckUserExists(data.uid)){
                    AddNewUser(data);
                }
            }
            else if(data.command === 'Disconnect'){
                DeleteUser(data.uid);

                if(chat_users[0].uid === session.uid){
                    // alert("If players are ready, push 'Start the game' button." +
                    //     "Then game will begin.")
                    var check_button = document.getElementById('check-button');
                    check_button.style.setProperty('opacity', '1');
                    var ready_button = document.getElementById('ready-button');
                    ready_button.style.setProperty('opacity', '0');
                }
            }
            else if(data.command === 'Message'){ // If someone throwed a message
                showMessage(data.uid, data.message);
            }
                else if(data.command === 'Cards'){
                game_started = true;
                var temp_i = NumInQueue(session.uid);
                chat_users[temp_i].cards.push({
                   power: data.power,
                   suit: data.suit,
                   num: data.num
                });
                ShowCards();
            }
            else if(data.command === 'Trump'){
                trump = data.trump;
                // Remove 'Start the game' button
                if(NumInQueue(session.uid) === 0){
                    var start = document.getElementById('check-button');
                    start.style.setProperty('opacity', '0');
                }
                else{
                    var ready = document.getElementById('ready-button');
                    ready.style.setProperty('opacity', '0');
                }
                // Show suit
                var temp_window = document.getElementById('card-suit');
                temp_window.innerHTML = '<img type="button" src="/pos_durak/static/src/img/'+
                    card_suits[trump]+'.png" id="suit" ' +
                    'style="position:absolute;left:30%;top:30%;opacity: 0.2;"/>';
                Ask_who_steps();
            }
            else if(data.command === 'Move'){
                moves_cnt++;
                if(!attacking){
                    Second_scene();
                    Tip('If defender beated cards, press "Complete move" button)', 4000);
                }
                attacking = true;
                var attack_card = data.num;
                if(who_attacks !== session.uid){
                    DownloadEnemyCards(attack_card, who_moves[0]);
                }
                var card = document.getElementById('card-'+attack_card);
                PutOn(card);
                DeleteCard(attack_card, who_moves[0]);
            }
            else if(data.command === 'HowMuchCards'){
                ShowHowMuchCards(data.number)
            }
            else if(data.command === 'Move_done'){
                complete_move++;
                if((complete_move === 2 && chat_users.length > 2) ||
                    (complete_move === 1 && chat_users.length === 2)){
                    First_scene();
                }
            }
            else if(data.command === 'Defense'){
                var card1 = data.first, card2 = data.second;
                if(data.uid !== session.uid){
                    DownloadEnemyCards(card1, data.uid);
                    DownloadEnemyCards(card2, data.uid);
                }
                if(!OnTable(card1)){
                    on_table_cards.push(card1);
                    moved_cards.push(Card_power(card1)[0]);
                }
                if(!OnTable(card2)){
                    on_table_cards.push(card2);
                    moved_cards.push(Card_power(card2)[0]);
                }
                Cover(card1, data.x, data.y);
                beated.push(card1, card2);
                DeleteCard(card1, NumInQueue(data.uid));
            }
            else if(data.command === 'my_game_id'){
                my_game_id = data.id;
                // When game id is recieved, then adding new user
                CreatePlayer();
            }
            else if(data.command === 'ready'){
                var sign = document.getElementById('user-name-'+String(data.uid));
                sign.style.setProperty('background', 'green');
            }
            else if(data.command === 'Who_steps'){
                if(chat_users[data.first].uid === session.uid){
                    Tip("Your turn to step", 5000);
                }
                who_moves = [data.first, data.second];
            }
        },
    });
//------------------------------------------------------
    return ChatButton;
});
