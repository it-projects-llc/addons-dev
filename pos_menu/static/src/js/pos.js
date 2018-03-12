odoo.define('pos_menu', function(require){

    var models = require('point_of_sale.models');

    models.load_models([{
		model: 'pos.tag',
		field: [],
		domain: null,
		loaded: function(self, tags) {
		    self.tags = [];
		    // save tags of current POS
		    tags.forEach(function(tag){
                if ($.inArray(self.config.id, tag.pos_ids) !== -1) {
                    self.tags.push(tag);
                };
		    });
		    // add new domain for product
		    self.models.forEach(function(model) {
		        if (model.model === "product.product") {
                    model.domain.push(['tag_ids', 'in', self.config.tag_ids]);
		        }
		    });
		}
	}], {
	    'before': 'product.product'
	});
});
