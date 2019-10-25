import random
from odoo import models, fields, api, _

class Game(models.Model):

    _name = 'game'
    _description = 'Simple game'

    name = fields.Text(default='pos_durak')
    id = fields.Integer(default=-1)
    players = fields.One2many('game.player', 'game', ondelete="cascade", delegate=True)
    extra_cards = fields.One2many('game.cards', 'game_extra_cards', ondelete="cascade")
    trump = fields.Integer(default=-1)
    who_steps = fields.Integer(default=-1, help='Holds user id')
    on_table_cards = fields.One2many('game.cards', 'on_table_cards', ondelete="cascade")

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

    @api.model
    def who_should_step(self, game_id):
        cur_game = self.sudo().search([('id', '=', game_id)])
        players_num = len(cur_game.players)
        if cur_game.who_steps + 1 < players_num:
            cur_game.who_steps += 1
        else:
            cur_game.who_steps = 0

        second_stepper = cur_game.who_steps
        if players_num > 2:
            if cur_game.who_steps + 2 < players_num:
                second_stepper = cur_game.who_steps + 2
            else:
                second_stepper = players_num - cur_game.who_steps - 1

        for player in cur_game.players:
            data = {'first': cur_game.who_steps, 'second': second_stepper,
                    'command': 'Who_steps'}
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                          player.pos_id, cur_game.name)
            self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def make_step(self, game_id, uid, card_num):
        cur_game = self.sudo().search([('id', '=', game_id)])
        stepper = cur_game.players.sudo().search([('uid', '=', uid)])
        card = stepper.cards.sudo().search([('num', '=', card_num)])[0]
        cur_game.on_table_cards += card

        for player in cur_game.players - stepper:
            data = {'uid': uid, 'num': card.num, 'command': 'Move'}
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                          player.pos_id, cur_game.name)
            self.env['bus.bus'].sendmany([[channel, data]])
        card.unlink()
        return 1

    @api.model
    def defence(self, game_id, uid, card1, card2, x, y):
        cur_game = self.sudo().search([('id', '=', game_id)])
        cur_game.make_step(game_id, uid, card1)
        first = cur_game.on_table_cards.sudo().search([('num', '=', card1)])[0]
        second = cur_game.on_table_cards.sudo().search([('num', '=', card2)])[0]
        fpow = first.power
        spow = second.power
        winner = -1
        loser = -1
        if first.suit == cur_game.trump:
            fpow = first.power + 100
        if second.suit == cur_game.trump:
            spow = first.power + 100
        if spow > fpow:
            winner = card1
            loser = card2
        else:
            loser = card1
            winner = card2
        for player in cur_game.players:
            data = {'uid': uid, 'winner': winner, 'loser': loser, 'command': 'Move'}
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                          player.pos_id, cur_game.name)
            self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def cards_are_beated(self, game_id):
        cur_game = self.sudo().search([('id', '=', game_id)])
        extra_cards_length = len(cur_game.extra_cards)
        try:
            for player in cur_game.players:
                while len(player.cards) < 6:
                    if len(cur_game.extra_cards) == 0:
                        break
                    player.add_new_card(player.uid, cur_game.extra_cards[extra_cards_length - 1])
                    cur_game.extra_cards[extra_cards_length - 1].unlink()
                    extra_cards_length -= 1
        except Exception:
            print('Extra cards sending error!!!')
        cur_game.on_table_cards.unlink()
        cur_game.who_should_step(game_id)

        for player in cur_game.players:
            data = {'command': 'Move_done'}
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                          player.pos_id, cur_game.name)
            self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def defender_took_cards(self, game_id, uid):
        cur_game = self.sudo().search([('id', '=', game_id)])
        player = cur_game.players.sudo().search([('uid', '=', uid)])
        for card in cur_game.on_table_cards:
            player.cards += card
        cur_game.on_table_cards.unlink()
        cur_game.who_should_step(game_id)

        data = {'command': 'Move_done'}
        for player in cur_game.players:
            channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                          player.pos_id, cur_game.name)
            self.env['bus.bus'].sendmany([[channel, data]])
        return 1

    @api.model
    def cards_number(self, game_id, uid, my_uid):
        cur_game = self.sudo().search([('id', '=', game_id)])
        ask_player = cur_game.players.sudo().search([('uid', '=', uid)])
        player = cur_game.players.sudo().search([('uid', '=', my_uid)])

        data = {'number': len(ask_player.cards)}
        channel = self.env['pos.config']._get_full_channel_name_by_id(self.env.cr.dbname,
                                                                      player.pos_id, cur_game.name)
        self.env['bus.bus'].sendmany([[channel, data]])
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
            card = player.cards.card_power(num)
            card.write({'in_game': False})
            card.unlink()
        except Exception:
            print('Card deletion error!!!')
        return 1

class Card(models.Model):
    _name = 'game.cards'
    _description = 'Gaming cards'

    cards_holder = fields.Many2one('game.player', string='Player', ondelete="cascade")
    game_extra_cards = fields.Many2one('game', string='Game', ondelete="cascade")
    on_table_cards = fields.Many2one('game', string='Game', ondelete="cascade")

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
