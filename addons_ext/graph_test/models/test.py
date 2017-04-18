from openerp import models, api, fields
# import serial
import time

class Test_graph(models.Model):
    _name = 'xiao.test.graph'

    # def _get_data_scale(self):
    #     ser = serial.Serial(
    #         # port='COM1',
    #         baudrate=9600,
    #         parity=serial.PARITY_ODD,
    #         stopbits=serial.STOPBITS_TWO,
    #         bytesize=serial.SEVENBITS
    #     )
    #     data = ''
    #     while ser.inWaiting() > 0:
    #         data += ser.read(1)
    #     if data != '':
    #         print data
    #     return data



    name=fields.Char(string='name')
    user_id = fields.Many2one('res.users', string='User')
    # datas = fields.Char(string='Weight', default=_get_data_scale)
    price = fields.Float(string='price')

    @api.model
    def get_bi_data(self):
        res = []
        users = []
        orders = self.env['xiao.test.graph']
        for i in orders.search([]):
            user = i.user_id
            if user not in users:
                users.append(user)
        for user in users:
            dict = {}
            dict['key'] = user.name
            # dict['color'] = '#ff7f0e'
            dict['strokeWidth'] = 3.5
            dict['values'] = []
            for order in orders.search([('user_id', '=', user.id)]):
                value = {}
                ordertime = order.create_date
                value['x'] = time.mktime(time.strptime(ordertime, "%Y-%m-%d %H:%M:%S")) * 1000
                # value['x'] = order.id
                value['y'] = order.price
                dict['values'].append(value)
            res.append(dict)
        return res
