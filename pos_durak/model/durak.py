import random
import re
from odoo import models, fields, api, _

class Durak(models.Model):
    _inherit = 'pos.session'

    # def default_game_id(self):
    #     return self.env.ref('base_game')

    # game_id = fields.Many2one('game', default=default_game_id)

    @api.model
    def send_field_updates(self, name, message, command, uid):
        channel_name = "pos_chat"
        if command == "Disconnect":
            self.search([("user_id", "=", uid)]).write({'plays': False, 'cards': '',
                                                        'cards_num': 0})
        data = {'name': name, 'message': message, 'uid': uid, 'command': command}
        self.env['pos.config'].send_to_all_poses(channel_name, data)
        return 1

    @api.model
    def send_to_user(self, command, message, pos_id):
        data = {'command': command, 'message': message}
        channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname, pos_id, "pos_chat")
        self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def send_all_user_data_to(self, name, true_name, participate, allow, from_uid, command, to_uid):
        data = {'name': name, 'true_name': true_name, 'participate': participate, 'allow': allow,
                'uid': from_uid, 'command': command}
        pos_id = self.search([('state', '=', 'opened'), ('user_id', '=', to_uid)], limit=1).id
        channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname, pos_id, "pos_chat")
        self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def player_ready(self, uid, max_users):
        try:
            pos_id = self.search([('user_id', '=', uid)]).id
        except Exception:
            print('Excpected that pos_id only 1!')

        self.search([("id", "=", pos_id)]).write({
            'plays': True
        })
        cnt = len(self.search([("plays", "=", True)]))
        if cnt > 7:
            return 1
        if cnt >= max_users or cnt == 7:
            self.send_field_updates("", "", "game_started", -1)
        return 1

    @api.model
    def card_power(self, card_num):
        card = int(card_num)
        cnt = 0
        while card < 13:
            card -= 13
            cnt += 1
        return [card, cnt]

    @api.model
    def cards_distribution(self):
        print('STARTED TO CALCULATE!')
        players = self.search([('plays', '=', True), ('state', '=', 'opened')])
        seq = [*range(0, 52)]
        how_much_cards = 6
        random.shuffle(seq)
        card_nums = []
        i = 0
        print('START CYCLE!')
        for num in seq:
            card_nums.append(num)
            if len(card_nums) == how_much_cards:
                temp_str = ""
                for j in card_nums:
                    temp_str += str(j)
                    temp_str += ' '
                card_nums.clear()
                players[i].write({
                    'cards': temp_str,
                    'cards_num': 7
                })
                print('SENDING CARDS TO ' + str(players[i].id))
                self.send_to_user('Cards', temp_str, players[i].id)
                print('SENT CARDS TO ' + str(players[i].id))
                i += 1
            if(i >= len(players)):
                break
        temp_str = ''
        for k in range(len(players)*how_much_cards, len(seq) - 2):
            temp_str += str(seq[k]) + ' '
        print('SENDING EXTRA CARDS')
        self.send_field_updates(str(seq[len(seq) - 1]),
                                temp_str, "Extra", -1)
        print('SENT EXTRA CARDS')

        # self.game_id.trump = self.CardPower(str(seq[len(seq) - 1]))[1]
        return 1

    @api.model
    def delete_card(self, uid, card1):
        user = self.search([('user_id', '=', uid)])
        user.write({
            'cards': re.sub(card1 + " ", "", user.cards)
        })
        return 1

    @api.model
    def moved(self, from_uid, card):
        user = self.search([('user_id', '=', from_uid)])
        self.delete_card(from_uid, card)
        user.write({'cards_num': user.cards_num - 1})
        self.send_field_updates('', card + " " + str(from_uid), 'Move', from_uid)
        return 1

    @api.model
    def number_of_cards(self, uid, from_uid):
        self.send_to_user('HowMuchCards',
                          str(self.search([('user_id', '=', uid)]).cards_num),
                          self.search([('user_id', '=', from_uid)]).id)
        return 1

    @api.model
    def defend(self, uid, card1, card2, x, y):
        self.delete_card(uid, card1)
        data = {'uid': uid, 'first': card1, 'second': card2, 'command': 'Defense', 'x': x, 'y': y}
        for pos in self.search([('plays', '=', True)]):
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname, pos.id, "pos_chat")
            self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def resent_cards(self, uid):
        user = self.search([('user_id', '=', uid)])
        self.send_to_user('Cards', user.cards, user.id)
        return 1

    @api.model
    def take_cards(self, uid, cards):
        user = self.search([('user_id', '=', uid)])
        user.write({
            'cards': user.cards + cards
        })
        self.send_field_updates('', user.cards, 'Loser', user.id)
        return 1

class Game(models.Model):

    _name = 'game'
    _description = 'Simple game'

    name = fields.Text(default='pos_durak')
    id = fields.Integer(default=-1)
    players = fields.One2many('game.player', 'game', ondelete="cascade", delegate=True)
    extra_cards = fields.One2many('game.cards', 'game_extra_cards', ondelete="cascade")
    trump = fields.Integer(default=-1)

    @api.model
    def create_the_game(self, game_name, uid):
        temp_game = self.sudo().search([('name', '=', game_name)])
        pos_id = self.env['pos.session'].search([('user_id', '=', uid)])[0].id
        # If game didn't created, then create
        if len(temp_game) == 0:
            try:
                self.sudo().create({'name': game_name, 'id': len(self.sudo().search([]))})
            except Exception:
                print('Game creation error!!! Game num is -' + str(len(self)))

        temp_game = self.sudo().search([('name', '=', game_name)])
        data = {'command': 'my_game_id', 'id': temp_game.id}
        channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname, pos_id, game_name)
        self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def add_new_user(self, game_id, name, uid):
        cur_game = self.sudo().search([('id', '=', game_id)])
        new_num = len(cur_game.players)
        new_pos_id = self.env['pos.session'].search([('user_id', '=', uid)])[0].id
        if cur_game.trump != -1:
            data = {'command': 'Game_started'}
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                          new_pos_id, cur_game.name)
            return 1
        # Sending new player's data to all players
        data = {'name': name, 'uid':uid, 'num': new_num, 'command': 'Connect'}
        self.env['pos.config'].send_to_all_poses(cur_game.name, data)
        # Sending old players data to the new player
        try:
            for user in cur_game.players:
                data = {'name': user.name, 'uid': user.uid, 'num': user.num, 'command': 'Connect'}
                channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                              new_pos_id, cur_game.name)
                self.env['bus.bus'].sendmany([[channel, data]])
        except Exception:
            print('Player connected notification error!!!(add_new_user)')

        try:
            cur_game.players += cur_game.players.sudo().create({'name': name,
                                            'uid': uid, 'num': new_num,
                         'pos_id': new_pos_id})
        except Exception:
            print('Player creation error!!!')
        return 1

    @api.model
    def player_is_ready(self, game_id, uid):
        cur_game = self.sudo().search([('id', '=', game_id)])
        try:
            cur_game.players.sudo().search([('uid', '=', uid)]).write({'ready': True})
        except Exception:
            print('Error in player_is_ready method!!! (Model - game)')

        self.env['pos.config'].send_to_all_poses(cur_game.name,
                                                 {'command': 'ready', 'uid': uid})
        return 1

    @api.model
    def send_cards(self, game_name, player):
        for card in player.cards:
            data = {'num': card.num, 'power': card.power,
                    'suit': card.suit, 'command': 'Cards'}
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                          player.pos_id, game_name)
            self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def start_the_game(self, game_id):
        cur_game = self.sudo().search([('id', '=', game_id)])
        seq = [*range(0, 52)]
        cards_limit = 6
        random.shuffle(seq)

        i = 0
        cards_cnt = 0
        all_cards_cnt = 0
        cur_game.player_is_ready(cur_game.id,
                                 cur_game.players.sudo().search([('num', '=', 0)]).uid)
        player = cur_game.players.sudo().search([('ready', '=', True)])
        player[0].sudo().write({'stepping': True})
        try:
            for num in seq:
                player[i].add_new_card(player[i].uid, num)
                seq.remove(num)
                cards_cnt += 1
                all_cards_cnt += 1
                if cards_cnt == cards_limit:
                    cards_cnt = 0
                    i += 1
                if len(player) == i:
                    break
        except Exception:
            print('Cards distribution error!!!\n')

        try:
            for num in seq:
                card = cur_game.extra_cards.sudo().card_power(num)
                cur_game.extra_cards += cur_game.extra_cards.sudo().create({'power': card[0],
                                          'suit': card[1], 'num': num, 'in_game': True})
            cur_game.sudo().write({'trump': cur_game.extra_cards[0].suit})
            self.env['pos.config'].send_to_all_poses(cur_game.name, {'command': 'Trump',
                                                                     'trump': cur_game.trump})
        except Exception:
            print('Extra cards assignment error!!!')

        try:
            for player in cur_game.players:
                cur_game.send_cards(cur_game.name, player)
        except Exception:
            print('Cards sending error!!!')

        try:
            for player in cur_game.players.sudo().search([('ready', '=', False)]):
                cur_game.delete_player(cur_game.id, player.uid)
        except Exception:
            print("Can't delete not ready players!!!(start_the_game)")
        return 1

    @api.model
    def delete_player(self, game_id, uid):
        cur_game = self.sudo().search([('id', '=', game_id)])
        try:
            for user in cur_game.players:
                data = {'uid': uid, 'command': 'Disconnect'}
                channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                              user.pos_id, cur_game.name)
                self.env['bus.bus'].sendmany([[channel, data]])
        except Exception:
            print('Player disconnected notification error!!!(delete_player)')

        try:
            deleting_user = cur_game.players.sudo().search([('uid', '=', uid)])
            for user in cur_game.players:
                if user.num > deleting_user.num:
                    user.sudo().write({'num': user.num - 1})
        except Exception:
            print("Users num's shifting error!!!(delete_player)")

        try:
            deleting_user.unlink()
        except Exception:
            print('Player removing error!!!')

        try:
            if len(cur_game.players) == 0:
                cur_game.sudo().unlink()
        except Exception:
            print("Game session deleting error!!!")
        return 1

    @api.model
    def send_message(self, game_id, message, uid):
        cur_game = self.sudo().search([('id', '=', game_id)])
        for player in cur_game.players:
            data = {'uid': uid, 'message': message, 'command': 'Message'}
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                          player.pos_id, cur_game.name)
            self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def delete_my_game(self, game_id):
        self.sudo().search([('id', '=', game_id)]).unlink()
        return 1

class Player(models.Model):

    _name = 'game.player'
    _description = 'Game player'

    game = fields.Many2one('game', string='Game', ondelete="cascade")
    cards = fields.One2many('game.cards', 'cards_holder', ondelete="cascade")

    # Player name
    name = fields.Text(default='')
    # Player uid
    uid = fields.Integer(default=-1)
    # Serial number
    num = fields.Integer(default=-1)
    # Is player ready to play or alredy playing
    ready = fields.Boolean(default=False)
    pos_id = fields.Integer(default=-1)
    # Step turn
    stepping = fields.Boolean(default=False)

    @api.model
    def add_new_card(self, uid, num):
        player = self.sudo().search([('uid', '=', uid)])
        try:
            card = player.cards.sudo().card_power(num)
            player.cards += player.cards.sudo().create({'power': card[0],
                                      'suit': card[1], 'num': num, 'in_game': True})
        except Exception:
            print('New card addition error!!!')
        return 1

    @api.model
    def delete_card(self, uid, num):
        player = self.sudo().search([('uid', '=', uid)])
        try:
            card = player.cards.sudo().card_power(num)
            card.write({'in_game': False})
            player.cards.sudo().search([('power', '=', card[0]), ('suit', '=', card[1])]).unlink()
        except Exception:
            print('Card deletion error!!!')
        return 1

class Card(models.Model):
    _name = 'game.cards'
    _description = 'Gaming cards'

    cards_holder = fields.Many2one('game.player', string='Player', ondelete="cascade")
    game_extra_cards = fields.Many2one('game', string='Game', ondelete="cascade")

    suit = fields.Integer(default=-1)
    power = fields.Integer(default=-1)
    num = fields.Integer(default=-1)
    in_game = fields.Boolean(default=False)

    @api.model
    def card_power(self, num):
        temp_suit = 0
        while num >= 13:
            num -= 13
            temp_suit += 1
        # Cause tuzes is located on the first position
        if num == 0:
            num = 13
        return [num, temp_suit]
