#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time   : 2019/7/2 11:02 AM
# @Author : mayra.zhao
# @File   : ExcelHandler.py
import xlwt
import xlrd

def set_style(name, height, bold=False):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = name
    font.bold = bold
    font.color_index = 4
    font.height = height
    style.font = font
    return style

class ExcelHandler(object):
    def __init__(self, fileName):
        self.fileName = fileName
        self.f = xlwt.Workbook(encoding="utf-8")

    def addSheet(self, sheetName, row0):
        self.sheetName = sheetName
        self.sheet1 = self.f.add_sheet(sheetName, cell_overwrite_ok=True)
        self.row0 = row0
        for i in range(0, len(self.row0)):
            self.sheet1.write(0, i, row0[i] ,set_style('Regular', 220, True))
        self.row = 1

    def writeToExcel(self, data):
        self.data = data
        if len(data) > 1:
            for i in range(len(data)):
                value = data[i]
                self.sheet1.write(self.row, i , value)
            self.f.save(self.fileName)
            self.row = self.row + 1

