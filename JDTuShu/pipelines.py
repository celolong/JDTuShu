# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from openpyxl import Workbook

class JdtushuPipeline(object):
    def __init__(self):
        self.file = open('jdtushu.json','w',encoding='utf-8')

    def process_item(self, item, spider):
        str_data = json.dumps(dict(item),ensure_ascii=False) +',\n'
        self.file.write(str_data)
        return item

    def clse_file(self):
        self.file.close()


class ExcelPipeline(object):
    def __init__(self):
        # 创建excel对象
        self.wb = Workbook()
        # 创建一个sheet表格
        self.ws =  self.wb.active
        self.ws.append(['书名','作者','价格','简介','出版时间','出版社','销量','大分类','小分类','详情页面链接','封面链接','大分类链接','小分类链接'])

    def process_item(self, item, spider):
        line= [item['name'],item['authors'],item['prices'],item['desc'],item['pub_time'],item['publish'],item['sales'],item['big_cate'],item['small_cate'],item['detail_link'],item['cover_link'],item['big_cate_link'],item['small_cate_link']]
        # 按行添加到标题，注意顺序
        self.ws.append(line)
        self.wb.save('jdtushu.xlsx')
        return item
