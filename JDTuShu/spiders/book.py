# -*- coding: utf-8 -*-
import scrapy,json
from JDTuShu.items import JdtushuItem
from scrapy_redis.spiders import RedisSpider

class BookSpider(RedisSpider):
    name = 'book'
    # 修改域名----->分布式注销允许的域和起始地url
    # allowed_domains = ['jd.com','p.3.cn','ad.3.cn','club.jd.com']
    # # 修改起始url
    # start_urls = ['https://book.jd.com/booksort.html']

    # 动态获取允许的域
    def __init__(self,*args,**kwargs):
        domain =  kwargs.pop('domain','')
        self.allowed_domains = list(filter(None,domain.split(',')))
        super(BookSpider,self).__init__(*args,**kwargs)

    # 加入redis_key值
    redis_key = 'book'

    def parse(self, response):
        data_list = response.xpath('//*[@id="booksort"]/div[2]/dl/dt')
        for data in data_list:
            temp = {}
            temp['big_cate'] = data.xpath('./a/text()').extract()[0]
            temp['big_cate_link'] ='https:' + data.xpath('./a/@href').extract()[0]
            node_list = data.xpath('./following-sibling::dd[1]/em')
            for node in node_list:
                temp['small_cate'] = node.xpath('./a/text()').extract()[0]
                temp['small_cate_link']='https:' + node.xpath('./a/@href').extract()[0]
                yield scrapy.Request(temp['small_cate_link'],callback=self.parse_detail,meta={'mymeta':temp})

    def parse_detail(self,response):
        temp = response.meta['mymeta']
        data_list = response.xpath('//*[@id="plist"]/ul/li')
        for data in data_list:
            item = JdtushuItem()
            item['big_cate'] = temp['big_cate']
            item['big_cate_link'] = temp['big_cate_link']
            item['small_cate']= temp['small_cate']
            item['small_cate_link']= temp['small_cate_link']
            # 注意有单件和套装的定位不同
            item['name']=data.xpath('./div/div[3]/a/em/text() | ./div/div/div[2]/div[1]/div[3]/a/em/text()').extract()[0].strip()
            if len(data.xpath('./div/div[1]/a/img/@src | ./div/div[1]/a/img/@data-lazy-img').extract()) !=0:
                item['cover_link'] ='https:'+ data.xpath('./div/div[1]/a/img/@src | ./div/div[1]/a/img/@data-lazy-img').extract()[0]
            else:
                item['cover_link']= 'https:' + data.xpath('./div/div/div[2]/div[1]/div[1]/a/img/@src | ./div/div/div[2]/div[1]/div[1]/a/img/@data-lazy-img').extract()[0]
            item['detail_link']  = 'https:' + data.xpath('./div/div[1]/a/@href | ./div/div/div[2]/div[1]/div[1]/a/@href').extract()[0]
            # 注意有多个作者和出版社的情况
            item['authors'] =''.join(data.xpath('./div/div[4]/span[1]/span[1]/a/text() | ./div/div/div[2]/div[1]/div[4]/span[1]/span[1]/a/text()').extract())
            item['publish'] =''.join(data.xpath('./div/div[4]/span[2]/a/text() | ./div/div/div[2]/div[2]/div[4]/span[2]/a/text()').extract())
            item['pub_time'] = data.xpath('./div/div[4]/span[3]/text() | ./div/div/div[2]/div[2]/div[4]/span[3]/text()').extract()[0].replace('\n','').strip()
            bid = data.xpath('./div/div/div[2]/div[1]/@data-sku | ./div/@data-sku').extract()[0]
            url = 'https://p.3.cn/prices/mgets?skuIds=J_'+ bid +'&pduid=93872252'
            yield scrapy.Request(url,callback=self.price_detail,meta={'mymeta':item,'bid':bid})

    def price_detail(self,response):
        item = response.meta['mymeta']
        bid = response.meta['bid']
        item['prices'] = json.loads(response.text,encoding='utf-8')[0]['p']
        # print(item)
        url = 'https://ad.3.cn/ads/mgets?&skuids=AD_'+bid
        yield scrapy.Request(url, callback=self.ad_detail, meta={'mymeta': item,'bid':bid})

    def ad_detail(self,response):
        item = response.meta['mymeta']
        bid = response.meta['bid']
        item['desc'] = json.loads(response.text,encoding='utf-8')[0]['ad']
        url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=' + bid
        yield scrapy.Request(url, callback=self.sales_detail, meta={'mymeta': item})

    def sales_detail(self,response):
        item = response.meta['mymeta']
        item['sales'] = json.loads(response.text, encoding='utf-8')['CommentsCount'][0]['CommentCountStr']
        print(item)
        yield item