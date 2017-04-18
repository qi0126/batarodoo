from openerp import models, api, fields
import time

class Batar_BI(models.Model):
    _name = 'batar.bi'

    @api.model
    def get_product_bi_data(self):
        res = []
        attribute_values = []
        orders = self.env['product.attribute.material.price']
        lines = orders.search([('active','=',False)]) + orders.search([])
        for i in lines:
            attribute_value = i.attribute_value_id
            if attribute_value not in attribute_values:
                attribute_values.append(attribute_value)
        for attribute_value in attribute_values:
            dict = {}
            dict['key'] = attribute_value.name
            # dict['color'] = '#ff7f0e'
            dict['strokeWidth'] = 3.5
            dict['values'] = []
            attribute_lines = orders.search([('active','=',False), ('attribute_value_id', '=', attribute_value.id)]) + orders.search([('attribute_value_id', '=', attribute_value.id)])
            for order in attribute_lines:
            # for order in lines.search([('attribute_value_id', '=', attribute_value.id)]):
                value = {}
                ordertime = order.create_date
                value['x'] = (time.mktime(time.strptime(ordertime, "%Y-%m-%d %H:%M:%S")) + 28800) * 1000
                # value['x'] = order.id
                value['y'] = order.material_price
                dict['values'].append(value)
            res.append(dict)
        return res