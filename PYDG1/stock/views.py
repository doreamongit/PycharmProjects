# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.


from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponse
import json
import tushare as ts
import pymysql
import pandas as pd
import datetime

tushareToken = '20ab835dfba819732460a06492ecc4634414b4379bafb4ff5d595340'

def handleDB():
    # db = pymysql.connect(host='localhost', user='root', password='12345678', port=3306)
    # cursor = db.cursor()
    # cursor.execute('SELECT VERSION()')
    # data = cursor.fetchone()
    # print('Database version:', data)
    # cursor.execute("CREATE DATABASE spiders DEFAULT CHARACTER SET utf8")
    # db.close()

    # change root password to yours:
    conn = pymysql.connect(host='127.0.0.1', user='root', password='12345678', database='stock')

    cursor = conn.cursor()

    # 创建user表:
    cursor.execute('create table user (id varchar(20) primary key, name varchar(20))')
    # 插入一行记录，注意MySQL的占位符是%s:
    cursor.execute('insert into user (id, name) values (%s, %s)', ('1', 'Michael'))
    print('rowcount =', cursor.rowcount)
    # 提交事务:
    conn.commit()
    cursor.close()

    # 运行查询:
    cursor = conn.cursor()
    cursor.execute('select * from user where id = %s', ('1',))
    values = cursor.fetchall()
    print(values)
    # 关闭Cursor和Connection:
    cursor.close()
    conn.close()

def index(request):

    # handleDB();

    ts.set_token(tushareToken)

    pro = ts.pro_api()
    # gplb = pro.stock_basic(list_status='L', fields ='ts_code, symbol, name, list_date, is_hs')
    #
    # print gplb

    # stock_info = ts.get_hist_data('600848')  # 一次性获取全部日k线数据
    # 默认索引升序
    stock_info = ts.get_hist_data('600848', start='2019-01-01', end='2019-08-29')
    # 索引降序排序
    stock_info = stock_info.sort_index()
    # print stock_info

    # jsonStr = json.dumps(stock_info)
    # print jsonStr



    # print stock_info.index

    # stock_info_json = stock_info.to_json(orient='records')
    stock_info_json = stock_info.to_json(orient='index')
    # print stock_info_json

    Dict = {'kData':stock_info_json}
    return render(request, 'kline.html', {
            'Dict': json.dumps(Dict) })
    # return render_to_response('kline.html')
    # return render(request, 'kline.html')

def hello(request):                          #request参数必须有，名字类似self的默认规则，可以修改，它封装了用户请求的所有内容
    return HttpResponse("abcHello world ! ")    #不能直接字符串，必须是由这个类封装，此为Django规则

def filter(request):
    return render(request, 'filter.html')

def search(request):
    request.encoding = 'utf-8'

    minPrice = request.GET['minPrice']
    maxPrice = request.GET['maxPrice']

    if minPrice and maxPrice:
        message = '你搜索的内容为: ' + request.GET['minPrice'] + request.GET['maxPrice']
    else:
        message = '你提交了空表单'

    ts.set_token(tushareToken)

    # stock_info = ts.get_stock_basics()
    stock_info = ts.get_today_all()

    code = stock_info[u'code']
    name = stock_info[u'name']
    changepercent = stock_info[u'changepercent']  # 涨跌幅
    trade = stock_info[u'trade']  # 现价
    open = stock_info[u'open']  # 开盘价
    high = stock_info[u'high']  # 最高价
    low = stock_info[u'low']  # 最低价
    settlement = stock_info[u'settlement']  # 昨日收盘价
    volume = stock_info[u'volume']  # 成交量
    turnoverratio = stock_info[u'turnoverratio']  # 换手率
    amount = stock_info[u'amount']  # 成交金额
    per = stock_info[u'per']  # 市盈率
    pb = stock_info[u'pb']  # 市净率
    mktcap = stock_info[u'mktcap']  # 总市值
    nmc = stock_info[u'nmc']  # 现价

    for index in range(len(name)):
        print (code[index])
        print (name[index])
        print (trade[index])


    # df = ts.get_today_all()

    # df = df[df['close'] >= float(minPrice)]
    # df = df[df['close'] <= float(maxPrice)]

    # df = df[df['turnoverratio'] > 10]

    # print(df)

    # print(df.head(5))

    return HttpResponse(message)


    ts.set_token(tushareToken)

    # 默认索引升序
    stock_info = ts.get_hist_data('600848', start='2019-01-01', end='2019-08-29')
    # 索引降序排序
    stock_info = stock_info.sort_index()




    Dict = {'kData': "dd"}
    return render(request, 'search.html', {
        'Dict': json.dumps(Dict)})