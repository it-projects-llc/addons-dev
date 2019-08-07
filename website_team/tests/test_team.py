# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/fedoranvar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def main(self, test_login):
        test_model = self.env['res.users']
        youtube_urls = [
            'somelink.elsewhere',
            'youtube.com',
        ]
        twitter_urls = [
            'twitter.com/!johnny',
            '@johnny',
            ' johnny',
            'twitter.com/_@johnny',
            'twitter.com/_@johnnY',
        ]
        upwork_urls = [
            'gregory',
            'upwork.com/gregory'
        ]
        github_names = [
            '-ec',
            'UsEr',
            'ey.d',
            ' sds'
        ]
        for url in youtube_urls:
            self.assertEqual(test_model.youtube_url_validation(url), None)
        for url in twitter_urls:
            self.assertEqual(test_model.twitter_url_validation(url), False)
        for url in upwork_urls:
            self.assertEqual(test_model.upwork_url_validation(url), False)
        for name in github_names:
            self.assertEqual(test_model.github_name_validation(url), False)

    def test_01_team(self):
        self.main("admin")
