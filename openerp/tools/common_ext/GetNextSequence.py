# -*- coding: utf-8 -*-
'''
Created on 2016年5月13日

@author: cloudy
'''

def GetNextSequence(sequence):
    ''''''
  
    str = "%s"%sequence
    if str.find("0")==1:   
        str=str.replace("0", "1")
        return int(str)
    else: 
        sequence = sequence + 1
        str = "%s"%sequence
        if str.find("0")==1:
            str=str.replace("0", "1")
            return int(str)  
       
        return sequence