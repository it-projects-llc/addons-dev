# -*- coding: utf-8 -*-
# Part of BiztechCS. See LICENSE file for full copyright and licensing details.

import math
import werkzeug
from openerp import api, fields, models, _
from openerp.http import request
from openerp.addons.website_sale.controllers import main

PPG = 18


class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    is_megamenu = fields.Boolean(string='Is megamenu...?')
    megamenu_type = fields.Selection([('2_col', '2 Columns'),
                                      ('3_col', '3 Columns'),
                                      ('4_col', '4 Columns')],
                                     default='3_col',
                                     string="Megamenu type")
    megamenu_bg = fields.Boolean(string='Want to set megamenu background', default=False)
    megamenu_bg_img_color = fields.Selection([('bg_img', 'Background image'),
                                              ('bg_color', 'Background color')],
                                             default='bg_img',
                                             string="Megamenu background selection")
    megamenu_bg_image = fields.Binary(string="Background image for megamenu")
    megamenu_bg_color = fields.Char(string="Background color for megamenu",
                                    default='#ccc',
                                    help="Background color for megamenu, for setting background color you have to pass hexacode here.")
    category_slider = fields.Boolean(string='Want to display category slider', default=False)
    carousel_header_name = fields.Char(string="Slider label",
                                       default="Latest", translate=True,
                                       help="Header name for carousel slider in megamenu")
    category_slider_position = fields.Selection([('left', 'Left'), ('right', 'Right')],
                                                default='left', string="Category Slider Position")
    menu_icon = fields.Boolean(string='Want to display menu icon', default=False)
    menu_icon_image = fields.Binary(string="Menu Icon", help="Menu icon for your menu")

    display_menu_footer = fields.Boolean(string="Display menu footer", default=False,
                                         help="For displaying footer in megamenu")
    menu_footer = fields.Html(string="Footer content",
                              help="Footer name for megamenu")
    customize_menu_colors = fields.Boolean(string='Want to customize menu colors', default=False)
    main_category_color = fields.Char(string='Main category color',
                                      help="Set color for main category in megamenu")
    sub_category_color = fields.Char(string='Sub category color',
                                     help="Set color for sab category in megamenu")


class website(models.Model):
    _inherit = 'website'

    # For Multi image
    thumbnail_panel_position = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('bottom', 'Bottom'),
    ], default='left',
        string='Thumbnails panel position',
        help="Select the position where you want to display the thumbnail panel in multi image.")
    interval_play = fields.Char(string='Play interval of slideshow', default='5000',
                                help='With this field you can set the interval play time between two images.')
    enable_disable_text = fields.Boolean(string='Enable the text panel',
                                         default=True,
                                         help='Enable/Disable text which is visible on the image in multi image.')
    color_opt_thumbnail = fields.Selection([
        ('default', 'Default'),
        ('b_n_w', 'B/W'),
        ('sepia', 'Sepia'),
        ('blur', 'Blur'), ],
        default='default',
        string="Thumbnail overlay effects")
    no_extra_options = fields.Boolean(string='Slider effects',
                                      default=True,
                                      help="Slider with all options for next, previous, play, pause, fullscreen, hide/show thumbnail panel.")
    change_thumbnail_size = fields.Boolean(string="Change thumbnail size", default=False)
    thumb_height = fields.Char(string='Thumb height', default=50)
    thumb_width = fields.Char(string='Thumb width', default=88)

    # For Sort By
    enable_sort_by = fields.Boolean(string='Enable product sorting option',
                                    help='For enabling product sorting feature in website.',
                                    default=True)

    # For first last pager
    enable_first_last_pager = fields.Boolean(string="Enable First and Last Pager", default=True,
                                             help="Enable this checkbox to make 'First' and 'Last' button in pager on website.")
    # Product per grid
    product_display_grid = fields.Selection([('2', '2'), ('3', '3'), ('4', '4')],
                                            default='3', string='Product per grid', help="Display no. of products per line in website product grid.")

    # For first last pager
    def get_pager_selection(self):
        prod_per_page = self.env['product.per.page'].search([])
        prod_per_page_no = self.env['product.per.page.no'].search([])
        values = {
            'name': prod_per_page.name,
            'page_no': prod_per_page_no,
        }
        return values

    def get_current_pager_selection(self):
        if request.session.get('default_paging_no'):
            return int(request.session.get('default_paging_no'))
        else:
            return PPG

    @api.model
    def pager(self, url, total, page=1, step=30, scope=5, url_args=None):
        res = super(website, self). pager(url=url,
                                          total=total,
                                          page=page,
                                          step=step,
                                          scope=scope,
                                          url_args=url_args)
        # Compute Pager
        page_count = int(math.ceil(float(total) / step))

        page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
        scope -= 1

        pmin = max(page - int(math.floor(scope/2)), 1)
        pmax = min(pmin + scope, page_count)

        if pmax - pmin < scope:
            pmin = pmax - scope if pmax - scope > 0 else 1

        def get_url(page):
            _url = "%s/page/%s" % (url, page) if page > 1 else url
            if url_args and not url_args.get('tag') and not url_args.get('range1') and not url_args.get('range2') and not url_args.get('max1') and not url_args.get('min1') and not url_args.get('sort_id'):
                _url = "%s?%s" % (_url, werkzeug.url_encode(url_args))
            return _url
        res.update({
            # Overrite existing
            "page_start": {
                'url': get_url(pmin),
                'num': pmin
            },
            "page_previous": {
                'url': get_url(max(pmin, page - 1)),
                'num': max(pmin, page - 1)
            },
            "page_next": {
                'url': get_url(min(pmax, page + 1)),
                'num': min(pmax, page + 1)
            },
            "page_end": {
                'url': get_url(pmax),
                'num': pmax
            },
            'page_first': {
                'url': get_url(1),
                'num': 1
            },
            'page_last': {
                'url': get_url(int(res['page_count'])),
                'num': int(res['page_count'])
            },
            'pages': [
                {'url': get_url(page), 'num': page}
                for page in xrange(pmin, pmax+1)
            ]
        })
        return res

    # For multi image
    @api.multi
    def get_multiple_images(self, product_id=None):
        product_img_data = False
        if product_id:
            self.env.cr.execute(
                "select id from biztech_product_images where product_tmpl_id=%s and more_view_exclude IS NOT TRUE order by sequence", ([product_id]))
            product_ids = map(lambda x: x[0], self.env.cr.fetchall())
            if product_ids:
                product_img_data = self.env['biztech.product.images'].browse(
                    product_ids)
        return product_img_data

    # For brands
    def sale_product_domain(self):
        domain = super(website, self).sale_product_domain()
        if 'brand_id' in request.context:
            domain.append(
                ('product_brand_id', '=', request.context['brand_id']))
        return domain

    # For product tags feature
    def get_product_tags(self):
        product_tags = self.env['biztech.product.tags'].search([])
        return product_tags

    # For Sorting products
    def get_sort_by_data(self):
        request.session['product_sort_name'] = ''
        sort_by = self.env['biztech.product.sortby'].search([])
        return sort_by

    # For setting current sort list
    def set_current_sorting_data(self):
        sort_name = request.session.get('product_sort_name')
        return sort_name

    # For megamenu
    @api.multi
    def get_public_product_category(self, submenu):
        categories = self.env['product.public.category'].search([('parent_id', '=', False),
                                                                 ('include_in_megamenu',
                                                                  '!=', False),
                                                                 ('menu_id', '=', submenu.id)],
                                                                order="sequence")
        return categories

    def get_public_product_child_category(self, children):
        child_categories = []
        for child in children:
            categories = self.env['product.public.category'].search([
                ('id', '=', child.id),
                ('include_in_megamenu', '!=', False)], order="sequence")
            if categories:
                child_categories.append(categories)
        return child_categories


class WebsiteConfigSettings(models.TransientModel):

    _inherit = 'website.config.settings'

    # For multi image
    thumbnail_panel_position = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('bottom', 'Bottom')],
        string='Thumbnails panel position',
        related='website_id.thumbnail_panel_position',
        help="Select the position where you want to display the thumbnail panel in multi image.")
    interval_play = fields.Char(string='Play interval of slideshow',
                                related='website_id.interval_play',
                                help='With this field you can set the interval play time between two images.')
    enable_disable_text = fields.Boolean(string='Enable the text panel',
                                         related='website_id.enable_disable_text',
                                         help='Enable/Disable text which is visible on the image in multi image.')
    color_opt_thumbnail = fields.Selection([
        ('default', 'Default'),
        ('b_n_w', 'B/W'),
        ('sepia', 'Sepia'),
        ('blur', 'Blur')],
        related='website_id.color_opt_thumbnail',
        string="Thumbnail overlay effects")
    no_extra_options = fields.Boolean(string='Slider effects',
                                      # default=True,
                                      related='website_id.no_extra_options',
                                      help="Slider with all options for next, previous, play, pause, fullscreen, hide/show thumbnail panel.")
    change_thumbnail_size = fields.Boolean(string="Change thumbnail size",
                                           related="website_id.change_thumbnail_size"
                                           )
    thumb_height = fields.Char(string='Thumb height',
                               related="website_id.thumb_height"
                               )
    thumb_width = fields.Char(string='Thumb width',
                              related="website_id.thumb_width"
                              )

    # For Sort By
    enable_sort_by = fields.Boolean(related="website_id.enable_sort_by", string='Enable product sorting option',
                                    help='For enabling product sorting feature in website.',
                                    default=True)

    # For first last pager
    enable_first_last_pager = fields.Boolean(related='website_id.enable_first_last_pager',
                                             string="Enable First and Last Pager", default=True,
                                             help="Enable this checkbox to make 'First' and 'Last' button in pager on website.")
    # Product per grid
    product_display_grid = fields.Selection(related='website_id.product_display_grid',
                                            default='3', string='Product per grid', help="Display no. of products per line in website product grid.")
