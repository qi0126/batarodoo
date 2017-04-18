# -*- coding: utf-8 -*-

import xlrd
import xlwt
import base64
import cStringIO

class ImportExcelFile(object):
    '''读取excel文件中的内容'''
    def __init__(self,file_contents,filename=None):
        self.filename = filename
        self.file_contents =  base64.decodestring(file_contents)
    def readFile(self):
        '''excel或者csv文件中的内容'''
        #保存结构
        res = {}
        try:
            book = xlrd.open_workbook(filename=self.filename, file_contents=self.file_contents)
            sheet = book.sheet_by_index(0)
            tmp = sheet.row_values(0)
            titles =[]
            #去掉第一行的空格
            for v in tmp:
                titles.append(v.strip())
            #可以在此处增加对标题的检测
            datas = []
            nrows = sheet.nrows
            for i in range(1,nrows):
                dic = dict(zip(titles,sheet.row_values(i)))
                datas.append(dic)
                res.update({'titles':titles,'data':datas})
        except Exception,e:
            pass
        return res
class ExportExcelFile(object):
    def __init__(self,titles,datas,sheetname):
        self.titles = titles
        self.datas = datas
        self.sheetname = sheetname
    def writeFile(self):
        book = xlwt.Workbook()
        sheet = book.add_sheet(self.sheetname)
        row = 0
        col = 0
        keys = self.titles.keys()
        write_title = []
        #写标题
        for key in keys:
            sheet.write(row,col,self.titles[key])
            write_title.append(key)
            col += 1
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(row+1)
        sheet.set_remove_splits(True)
        #写内容
        for line in self.datas:
            row += 1
            for i in range(len(write_title)):
                sheet.write(row, i, line.get(self.titles.get(write_title[i],''),''))                
        buf = cStringIO.StringIO()
        book.save(buf)
        out = base64.encodestring(buf.getvalue())
        buf.close()
        return out
        
                
            
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: