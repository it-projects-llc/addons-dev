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
    var W = 0;
    var H = 0;
    // On table cards
    var on_table_cards = [];
    // How much cards on the table
    var moves_cnt = 0;
    // Cards max count
    var max_cards = 6;
    // Defender counter
    var choose_and_beat = 0;
    var def_cards = [0,0];
    var card_suits = ['Heart', 'Diamond', 'Clubs', 'Spade'];
    var my_game_id = -1;
    var i = 0;

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

    function Defendence(x, y) {
        self._rpc({
            model: "game",
            method: "defence",
            args: [my_game_id, session.uid, def_cards[0], def_cards[1], x, y]
        });
        def_cards = [0,0];
    }

    function Take_Cards() {
        // Need to finish
        var temp_cards = '';
        for(i = 0; i < on_table_cards.length; i++){
            temp_cards += on_table_cards[i] + ' ';
        }
        self._rpc({
            model: "game",
            method: "defender_took_cards",
            args: [my_game_id, session.uid]
        });
    }

//------------------------------------------------------

//-------------Help functions part----------------------
    // Checks out which num user has
    function NumInQueue(uid){
        for(i = 0; i < chat_users.length; i++){
            if(chat_users[i].uid === uid) {
                return i;
            }
        }
    }

    function OnTable(n) {
        for(i = 0; i < on_table_cards.length; i++){
            if(on_table_cards[i] === Number(n)) {
                return true;
            }
        }
        return false;
    }

    function buttons_opacity(num) {
        document.getElementById('ready-button').style.setProperty('opacity', '0');
        document.getElementById('step-button').style.setProperty('opacity', '0');
        document.getElementById('take-button').style.setProperty('opacity', '0');
        document.getElementById('check-button').style.setProperty('opacity', '0');
        if(num === 1){
            document.getElementById('ready-button').style.setProperty('opacity', '1');
        }
        else if(num === 2){
            document.getElementById('step-button').style.setProperty('opacity', '1');
        }
        else if(num === 3){
            document.getElementById('take-button').style.setProperty('opacity', '1');
        }
        else if(num === 4){
            document.getElementById('check-button').style.setProperty('opacity', '1');
        }
    }

    function is_my_card(card_num){
        var me = NumInQueue(session.uid);
        for(i = 0; i < chat_users[me].cards.length; i++){
            if(chat_users[me].cards[i].num === Number(card_num)){
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
           if(Number(num) < 0 || Number(num) > 52){
               alert(elem.id);
               return;
           }
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
           else if(is_my_card(num) && !OnTable(num)){
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
               args: [my_game_id, session.uid]
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

    function CheckUserExists(uid){
        for(i = 0; i < chat_users.length; i++){
            if(uid === chat_users[i].uid) return true;
        }
        return false;
    }

    function DeleteMyData(){
        chat_users = [];
        in_chat = false;
        game_started = false;
        moves_cnt = 0;
        on_table_cards = [];
        trump = -1;
        who_moves = [-1,-1];
        try {
            chat_users.forEach(function(item){
                document.getElementById('picture-'+NumInQueue(item.uid)).style.setProperty('display', 'none');
            });
            document.getElementById('cards').innerHTML = '';
            buttons_opacity(0);
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
        for(i = 0; i < str.length; i++){
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

    function next_to(uid, already_converted){
        if(already_converted){
            i = uid;
        }
        else{
            i = NumInQueue(uid);
        }

        if(i === chat_users.length - 1){
            return chat_users[0].uid;
        }

        return chat_users[i + 1].uid;
    }

//--------------------------------------------------

//---------- Set avatar and animation part -------------
function ShowCards(){
    var block = document.getElementById('cards');
    var me = NumInQueue(session.uid);
    var out = '', w = (60/chat_users[me].cards.length)/2;
    for(i = 0; i < chat_users[me].cards.length; i++){
        var n = chat_users[me].cards[i].num;
        out+='<img type="button" src="/pos_durak/static/src/img/kards/'+
        n+'.png" id="card-'+n+'" class="card" style="right: '+String(30 - (i*w))+'%"></img>';
    }
    block.innerHTML = out;
}

function ShowUsers(){
    var window = document.getElementById('main-window');
    var out = '';
    chat_users.forEach(function (item){
        i = NumInQueue(item.uid);
        var str_uid = String(item.uid);
        out += '<div class="chat-user" id="picture-'+i+'">';
        out += '<div class="user-name" id="user-name-'+str_uid+'">'+chat_users[i].name+'</div>';
        out += '<img src="/web/image/res.users/' +
        item.uid + '/image_small" id="ava-' + i +'" class="avatar" style="border-radius:50%;margin-left:20%;"/>';

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

    avatar.style.setProperty('left', (W/2) - (avatar.offsetWidth / 2) + 'px');
    avatar.style.setProperty('top', (H*0.4) - (avatar.offsetHeight / 2) + 'px');
    avatar.style.setProperty('transform','translate3d('+x+'px,'+y+'px,0px)');
}
//------------------------------------------------------

//--------------- Game table actions -------------------

    function PutOn(puton_card) {
        var card = document.getElementById('card-'+puton_card);
        var sign = (moves_cnt + 1)%2 === 0 ? 1 : -1;
        var cw = card.offsetWidth, ch = card.offsetHeight;

        var put_w = ((W - cw)/2) + (moves_cnt*cw)*(sign*0.5), put_h = (H - ch)/2;
        var x = card.offsetLeft, y = card.offsetTop;
        card.style.setProperty('opacity','1');
        card.style.setProperty('transform','translate3d('
            +(put_w - x)+'px,'+(put_h - y)+'px,0px)');
    }

    function Cover(card, x2, y2) {
        try{
            var card1 = document.getElementById('card-'+card);
            var x1 = card1.offsetLeft, y1 = card1.offsetTop;
            var w = card1.offsetWidth, h = card1.offsetHeight;
            card1.style.setProperty('transform','translate3d('+
                (((x2*W) - w/2) - x1)+'px,'+(((y2*H) - h/2) - y1)+'px,0px)');
        }
        catch(e){
            Tip("Can't cover chosen card!", 3000);
        }
    }

    function Move(card_num){
        // Need to check suit of card, and make a decide
        // Can player make a step or no
        if(moves_cnt >= max_cards){
            alert('You can step only '+max_cards+' times!');
            return;
        }
        var stepper = [chat_users[who_moves[0]].uid, chat_users[who_moves[1]].uid];
        if(stepper[0] === session.uid){
            self._rpc({
                model: "game",
                method: "make_step",
                args: [my_game_id, session.uid, card_num]
            });
        }
        else if(stepper[1] === session.uid && on_table_cards.length > 0){
            self._rpc({
                model: "game",
                method: "make_step",
                args: [my_game_id, session.uid, card_num]
            });
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

    function DownloadEnemyCards(num, uid){
        chat_users[NumInQueue(uid)].cards.push({
           power: -1,
           suit: -1,
           num: num
        });
        var out ='<img type="button" src="/pos_durak/static/src/img/kards/'+
                num+'.png" id="card-'+num+'" class="enemy-card"/>';
        document.getElementById('enemy-cards').innerHTML += out;
    }

    function First_scene(){
        i = 0;
        moves_cnt = 0;
        try{
            var me = NumInQueue(session.uid);
            for(i = 0; i < on_table_cards.length; i++){
                for(var j = 0; j < chat_users[me].cards.length; j++){
                    if(chat_users[me].cards[j].num === on_table_cards[i]){
                        chat_users[me].cards.splice(j,1);
                    }
                }
            }

            for(i = 0; i < on_table_cards.length; i++){
                var card = document.getElementById('card-'+on_table_cards[i]);
                card.style.setProperty('opacity', '0');
            }
            on_table_cards = [];
        }
        catch(e){
            Tip('Game cards deletion error!', 3000);
        }

        buttons_opacity(0);
        try{
            for(i = 0; i < chat_users.length; i++){
                document.getElementById('picture-'+i).style.setProperty('opacity', '1');
                SetPos(document.getElementById('picture-'+i), chat_users[i].uid);
            }
        }
        catch(e){
            Tip('Transition to the first scene error!', 3000);
        }
        ShowCards();
    }

    function Second_scene(data){
        buttons_opacity(0);
        var who_attacks = [chat_users[who_moves[0]].uid,chat_users[who_moves[1]].uid];
        var who_defends = next_to(who_attacks[0], false);
        if(who_attacks[0] === session.uid || who_attacks[1] === session.uid){
            buttons_opacity(2);
        }
        // Hode other players
        for(i = 0; i < chat_users.length; i++){
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
            buttons_opacity(2);
            Tip('Attack '+String(chat_users[NumInQueue(who_defends)].name), 2000);
        }
        if(session.uid === who_defends){
            buttons_opacity(3);
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

//------ Message taking and showing functions ----------

    function TakeNewMessage(delete_last_char){
        i = NumInQueue(session.uid);

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
                args: [my_game_id, session.uid]
            });
        }

        newMessage.value = '';
    }

    function delete_message(msg, uid) {
        try{
            var old_message = document.getElementById('msg-'+String(msg)+'-'+uid);
            old_message.innerHTML = '';
            old_message.style.display = none;
        }
        catch(e){
            // Error
        }
    }
    
    function showMessage(uid, message){
        i = NumInQueue(uid);
        var time = 10000;
        var messages = document.getElementById('messages-'+String(uid));
        var audio_mes = '<audio src="/pos_durak/static/src/sound/msg.wav" autoplay="true"></audio>';
        if(message === 'sorry'){
            time = 2000;
            audio_mes = '<audio src="/pos_durak/static/src/sound/shit.wav" autoplay="true"></audio>';
        }
        else if(message === 'welcome'){
            time = 2000;
            audio_mes = '<audio src="/pos_durak/static/src/sound/welcome.wav" autoplay="true"></audio>';
        }
        else if(message === 'win'){
            time = 4400;
            audio_mes = '<audio src="/pos_durak/static/src/sound/won.wav" autoplay="true"></audio>';
        }
        var out = '<div id="msg-'+chat_users[i].msg_cnt+'-'+uid+'">';
        out += '<p style="background: white;transition:' +
            ' all .3s ease-in-out;border-radius: 20%;margin-top: 5px;' +
            'margin-bottom: 0px;">'+message+'</p>';
        out += audio_mes;
        out += '</div>';
        messages.innerHTML += out;
        setTimeout(delete_message, time, chat_users[i].msg_cnt, uid);
        chat_users[i].msg_cnt++;
    }
//--------------------------------------------------

//--------------- Users relations part -----------------

    function AddNewUser(user_data) {
        i = 0;
        // If user connected too late
        if(game_started) return;

        if(chat_users.length === 0){
            chat_users = new Array(user_data.num + 1);
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
            buttons_opacity(4);
        }
        else{
            buttons_opacity(1);
        }
        for(i = 0; i < chat_users.length; i++){
            if(chat_users[i].uid === -1 ){
                return;
            }
        }

        ShowUsers();
    }

    function DeleteUser(user_id){
        i = NumInQueue(user_id);
        try{
            var user = document.getElementById('picture-'+i);
            user.style.setProperty('display', 'none');
        }
        catch(e){
            Tip('Trying to delete undefined user!', 3000);
        }
        chat_users.splice(NumInQueue(user_id),1);
        if(session.uid !== user_id){
            ShowUsers();
        }
        if(session.uid === user_id){
            DeleteMyData();
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
            self.bus.add_channel_callback(channel, self.catch_response, self);
        },

        catch_response: function(data){
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
                if(data.uid === session.uid){
                    for(i = 0; i < chat_users.length; i++){
                        DeleteUser(chat_users[i].uid);
                    }
                }
                else{
                    DeleteUser(data.uid);
                    First_scene();
                }

                if(chat_users[0].uid === session.uid){
                    // alert("If players are ready, push 'Start the game' button." +
                    //     "Then game will begin.")
                    buttons_opacity(4);
                }
            }
            else if(data.command === 'Message'){
                showMessage(data.uid, data.message);
            }
            else if(data.command === 'Cards'){
                var me = NumInQueue(session.uid);
                if(data.pack_num === 0){
                    chat_users[me].cards = [];
                }
                chat_users[me].cards.push({
                    power: data.power,
                    suit: data.suit,
                    num: data.num
                });
                if(data.n === chat_users[me].cards.length){
                    document.getElementById('cards').innerHTML = '';
                    ShowCards();
                }
            }
            else if(data.command === 'Trump'){
                game_started = true;
                trump = data.trump;
                buttons_opacity(0);
                // Show suit
                var temp_window = document.getElementById('card-suit');
                temp_window.innerHTML = '<img type="button" src="/pos_durak/static/src/img/'+
                    card_suits[trump]+'.png" id="suit" ' +
                    'style="position:absolute;left:30%;top:30%;opacity: 0.2;"/>';
            }
            else if(data.command === 'Move'){
                moves_cnt++;
                if(on_table_cards.length === 0){
                    Second_scene();
                    Tip('If defender beated cards, press "Complete move" button)', 4000);
                }
                if(data.uid !== session.uid){
                    DownloadEnemyCards(data.num, data.uid);
                }
                PutOn(data.num);
                on_table_cards.push(data.num);
            }
            else if(data.command === 'HowMuchCards'){
                ShowHowMuchCards(data.number);
            }
            else if(data.command === 'Move_done'){
                First_scene();
            }
            else if(data.command === 'Defence'){
                if(!data.can_beat){
                    if(session.uid === data.uid){
                        Tip("You can't beat this card with chosen card", 2000);
                    }
                    Tip(chat_users[NumInQueue(data.uid)].name + ' tried to cover card, but not successfuly', 2000);
                    showMessage(data.uid, 'sorry');
                    return;
                }
                var winner = data.winner, loser = data.loser;
                if(data.uid !== session.uid){
                    DownloadEnemyCards(winner, data.uid);
                }
                on_table_cards.push(winner);
                Cover(winner, data.x, data.y);
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
                for(i = 0; i < chat_users.length; i++){
                    if(data.first !== i){
                        try{
                            var pic = document.getElementById('picture-'+String(i));
                            pic.style.setProperty('opacity','0.6');    
                        }
                        catch(e){
                            Tip('Something bad happened', 2000);
                        }
                    }
                }

                who_moves = [data.first, data.second];
            }
            else if(data.command === 'Won'){
                DeleteUser(data.uid);
                for(i = 0; i < chat_users.length; i++){
                    SetPos(document.getElementById('picture-'+String(i)), chat_users[i].uid);
                }
                if(session.uid === data.uid){
                    Tip('You won!', 3000);
                    showMessage(data.uid, 'won');
                }
            }
            else if(data.command === 'GAME_PING'){
                Tip('Catch Ping', 2000);
                self._rcp({
                    model: 'game',
                    method: 'Pong',
                    args: [my_game_id, session.uid]
                });
            }
            else if(data.command === 'Welcome'){
                showMessage(data.uid, 'welcome');
            }
        },
    });
//------------------------------------------------------
    return ChatButton;
});
