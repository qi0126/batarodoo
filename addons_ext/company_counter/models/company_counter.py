#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo10
@author:cloudy
@site:
@file:product_counter.py
@date:2017/3/18 11:06
"""
from odoo import models, fields, api, tools, _


class CompanyCounter(models.Model):
    _name = "company.counter"

    name = fields.Char(string="counter name")
    company_id = fields.Many2one("res.company", string="affiliated company")
    counter_products = fields.One2many("counter.product", 'counter_id', string='products')
    active = fields.Boolean(default=True, string="active")
    active_counter = fields.Float()
    image = fields.Binary('Counter big size image', compute='_compute_images', inverse='_set_image')
    image_small = fields.Binary('Counter small size image', compute='_compute_images', inverse='_set_image_small')
    image_medium = fields.Binary('Counter medium size image', compute='_compute_images', inverse='_set_image_medium')

    def _compute_images(self):
        if self._context.get('bin_size'):
            self.image_medium = self.image
            self.image_small = self.image
            self.image = self.image
        else:
            resized_images = tools.image_get_resized_images(self.image, return_big=True, avoid_resize_medium=True)
            self.image_medium = resized_images['image_medium']
            self.image_small = resized_images['image_small']
            self.image = resized_images['image']

    @api.one
    def _set_image(self):
        self._set_image_value(self.image)

    @api.one
    def _set_image_medium(self):
        self._set_image_value(self.image_medium)

    @api.one
    def _set_image_small(self):
        self._set_image_value(self.image_small)

    @api.one
    def _set_image_value(self, value):
        image = tools.image_resize_image_big(value)
        self.image = image


class CounterProduct(models.Model):
    _name = "counter.product"

    counter_id = fields.Many2one("company.counter", string="counter name")
    product = fields.Many2one("product.product", string='product')
    active = fields.Boolean(default=True, string="active")



