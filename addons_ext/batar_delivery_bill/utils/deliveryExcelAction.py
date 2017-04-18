# -*- coding: utf-8 -*-
'''
Created on 2016年5月4日

@author: cloudy
'''
import xlrd
import xlwt
import base64
import cStringIO

class deliveryExcelFile(object):
    '''读取送货单excel文件'''
    def __init__(self,file_contents,line,sheet=0,filename=None):
        self.filename = filename
        self.file_contents =  base64.decodestring(file_contents)
        self.line = line
        self.sheet = sheet
    def readFile(self):
        '''excel文件读取'''
        data_dict = {}
        try:
            book = xlrd.open_workbook(filename=self.filename,file_contents=self.file_contents)
            sheet = book.sheet_by_index(self.sheet)
            nrows = sheet.nrows
       
            data_dict['name']=  str(sheet.row_values(0)[1])
            #送货方负责人信息
            data_dict['partner_name'] = sheet.row_values(1)[1]
            data_dict['partner_person'] = sheet.row_values(2)[1]
            data_dict['partner_mobile'] = str(sheet.row_values(3)[1])
            #物流信息
            data_dict['delivery_method'] = sheet.row_values(1)[3]
            data_dict['delivery_man'] = sheet.row_values(2)[3]
            data_dict['delivery_mobile'] = str(sheet.row_values(3)[3]) 
            #包装明细头
            tmp = sheet.row_values(self.line-1)
            titles =[]
            #去掉第一行的空格
            for v in tmp:
                titles.append(v.strip())
            data_dict['data']=[]
            for line in range(self.line,nrows):
                data_dict['data'].append(dict(zip(titles,sheet.row_values(line))))
        except Exception,e:
            return None
        return data_dict