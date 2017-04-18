# -*- coding: utf-8 -*-
'''
Created on 2016年6月2日

@author: cloudy
'''

from openerp.http import Controller,route,request
from werkzeug import exceptions


class ProductLabel(Controller):
    @route(['/report/barcode', '/report/barcode/<type>/<path:value>'], type='http', auth="user")
    def report_barcode(self, type, value, width=600, height=100, humanreadable=0):
        """Contoller able to render barcode images thanks to reportlab.
        Samples: 
            <img t-att-src="'/report/barcode/QR/%s' % o.name"/>
            <img t-att-src="'/report/barcode/?type=%s&amp;value=%s&amp;width=%s&amp;height=%s' % 
                ('QR', o.name, 200, 200)"/>

        :param type: Accepted types: 'Codabar', 'Code11', 'Code128', 'EAN13', 'EAN8', 'Extended39',
        'Extended93', 'FIM', 'I2of5', 'MSI', 'POSTNET', 'QR', 'Standard39', 'Standard93',
        'UPCA', 'USPS_4State'
        :param humanreadable: Accepted values: 0 (default) or 1. 1 will insert the readable value
        at the bottom of the output image
        """
        try:
            barcode = request.registry['report'].barcode(type, value, width=width, height=height, humanreadable=humanreadable)
        except (ValueError, AttributeError):
            raise exceptions.HTTPException(description=u'不能转换为条形码.')
        return request.make_response(barcode, headers=[('Content-Type', 'image/png')])