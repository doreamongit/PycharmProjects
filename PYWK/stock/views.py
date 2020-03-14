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
import numpy as np
import pandas as pd
import math
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

import datetime
from datetime import date

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

class JsonExtendEncoder(json.JSONEncoder):
    """
        This class provide an extension to json serialization for datetime/date.
    """
    def default(self, o):
        """
            provide a interface for datetime/date
        """
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)

def filter(request):
    request.encoding = 'utf-8'

    minPrice = request.GET.get('minPrice', None)
    maxPrice = request.GET.get('maxPrice', None)

    filterDict = {}
    if minPrice:
        filterDict['minPrice'] = minPrice

    if maxPrice:
        filterDict['maxPrice'] = maxPrice
    else:
        filterDict['maxPrice'] = ''

    filterResult = filterFromDB(minPrice,maxPrice)

    filterAry = []
    if filterResult.count>0:
        filterAry = filterResult

        filterResultJson = json.dumps(filterResult, cls=JsonExtendEncoder)
        # print "筛选结果:"+str(filterResult)

    filterDict['filterAry'] = filterAry

    return render(request, 'filter.html',{
        'Dict': json.dumps(filterDict, cls=JsonExtendEncoder)})

def filterFromDB(minPrice,maxPrice):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='12345678', database='stock',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    # 插入一行记录，注意MySQL的占位符是%s:
    sql1 = """select * from stock_today_all"""

    result = cursor.execute(sql1)

    allResult = cursor.fetchall()
    while (1):
        row = cursor.fetchone()
        if row == None:
            break
        # print row
        # print (row[0], row[1], row[2])
    # 提交事务:
    # conn.commit()
    cursor.close()
    conn.close()
    return allResult


def findLastTradingDay():
    lastTradingDay = datetime.datetime.now()
    is_trading_day = False
    while(is_trading_day == False):
        is_trading_day = isTradingDay(lastTradingDay)
        if is_trading_day == False:
            yesterday = lastTradingDay - datetime.timedelta(days=1)
            lastTradingDay = yesterday

    lastTradingDayStr = lastTradingDay.strftime("%Y-%m-%d")

def isTradingDay(today):

    ts.set_token(tushareToken)

    today = today.strftime("%Y-%m-%d")

    is_trading_day_stock = ts.get_hist_data('600601', start=today, end=today)
    is_trading_day_open = is_trading_day_stock[u'open'].values  # 开盘价
    # print(is_trading_day_open)
    is_trading_day = False
    if is_trading_day_open.size>0:
        is_trading_day = True
    return is_trading_day

def search(request):
    request.encoding = 'utf-8'

    minPrice = request.GET['minPrice']
    maxPrice = request.GET['maxPrice']

    if minPrice and maxPrice:
        message = '你搜索的内容为: ' + request.GET['minPrice'] + request.GET['maxPrice']
    else:
        message = '你提交了空表单'

    ts.set_token(tushareToken)

    # is_trading_day = isTradingDay(datetime.datetime.now())
    findLastTradingDay()

    return render(request, 'filter.html')

    # if is_trading_day:
    #     print('交易日')
    # else:
    #     print('非交易日')
    #     return HttpResponse('非交易日')

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

    conn = pymysql.connect(host='127.0.0.1', user='root', password='12345678', database='stock')
    cursor = conn.cursor()

    for index in range(len(name)):
        # print (code[index])
        # print (name[index])
        # print (trade[index])

        db_code = code[index]
        db_name = name[index]
        db_changepercent = changepercent[index]
        db_trade = trade[index]
        db_open = open[index]
        db_high = high[index]
        db_low = low[low]
        db_settlement = settlement[index]
        db_volume = volume[index]
        db_turnoverratio = turnoverratio[index]
        db_amount = amount[index]
        db_per = per[index]
        db_pb = pb[index]
        db_mktcap= mktcap[index]
        db_nmc = nmc[index]



        # 插入一行记录，注意MySQL的占位符是%s:
        cursor.execute("insert into stock_today_all (date,code, name) values (%s,%s, %s)", (today,db_code, db_name))
        print('rowcount =', cursor.rowcount)
        # 提交事务:
        conn.commit()

    cursor.close()


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

def detail(request):
    request.encoding = 'utf-8'

    code = request.GET.get('code', None)

    if code is None:
        return HttpResponse("错误的代码")

    ts.set_token(tushareToken)

    # 默认索引升序
    stock_info = ts.get_hist_data(code)

    if stock_info is None:
        return HttpResponse("错误的代码")
    # 索引降序排序
    stock_info = stock_info.sort_index()

    stock_info_json = stock_info.to_json(orient='index')
    # print stock_info_json

    Dict = {'kData':stock_info_json}
    return render(request, 'detail.html', {
            'Dict': json.dumps(Dict) })

def calculate(request):
    originAry = [2, 8, 15, 3, 15]
    originAryXieLv = np.gradient(originAry)
    print originAryXieLv
    print '-------'

    df = pd.DataFrame(np.arange(24).reshape(6, 4), \
         index=pd.date_range(start= '20170101', \
                             periods = 6), columns = ['A','B','C','D'])

    diffResult = df.diff(periods=1, axis='index')

    print df
    print diffResult


    begin_time = '2019-11-01'
    end_time = '2019-11-11'
    code = "000001"
    stock = ts.get_hist_data(code, start=begin_time, end=end_time)


    stock = stock.sort_index(0)  # 将数据按照日期排序下。
    # stock.to_pickle("stock_data_000001.pickle")
    # print("finish save ...")

    print stock

    stockDiff = stock.diff(periods=1, axis='index')

    print stockDiff

    stockDiffClose = stockDiff['close']
    print stockDiffClose

    stockDiffClose.plot(figsize=(20, 10), grid=True)
    plt.show()

    for index, val in stockDiffClose.items():
        print(index, val)



    # 读取股票数据分析。不用每次网络请求数据
    # stock = pd.read_pickle("stock_data_000001.pickle")
    # 5周期、10周期、20周期和60周期
    # 周线、半月线、月线和季度线
    stock["5d"] = stock["close"].rolling(window=5).mean()  # 周线
    stock["10d"] = stock["close"].rolling(window=10).mean()  # 半月线
    stock["20d"] = stock["close"].rolling(window=20).mean()  # 月线
    stock["60d"] = stock["close"].rolling(window=60).mean()  # 季度线

    # 展示股票收盘价格信息

    stock[["close", "5d", "10d", "20d", "60d", ]].plot(figsize=(20, 10), grid=True)
    # plt.show()

    stock["5-10d"] = stock["5d"] - stock["10d"]  # 周-半月线差
    stock["5-20d"] = stock["5d"] - stock["10d"]  # 周-月线差
    # stock[["close", "5-10d", "5-20d"]].plot(subplots=True, style='b', figsize=(20, 10), grid=True)
    # plt.show()

    # 计算股票的收益价格 可以看到return 在-0.06 在 0.06 之间波动，如果为负值，说明股票下跌。
    # 如果为正值则股票上涨
    stock["return"] = np.log(stock["close"] / stock["close"].shift(1))
    # stock["return_a"] = stock["close"] / stock["close"].shift(1)
    # print(stock[["return","return_a"]].head(15))
    fig = Figure(figsize=(20, 10))
    ax = fig.add_subplot(111)
    stock[["close", "return"]].plot(subplots=True, style='b', figsize=(20, 10), grid=True)

    # print stock["date"]
    # 设置时间标签显示格式
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(pd.date_range('2014-09-01', '2014-09-30'), rotation=90)

    # plt.show()

    # 计算股票的【收益率的移动历史标准差】
    mov_day = int(len(stock) / 20)
    stock["mov_vol"] = stock["return"].rolling(window=mov_day).std() * math.sqrt(mov_day)
    # print(stock["mov_vol"].head(mov_day+1))

    stock[["close", "mov_vol", "return"]].plot(subplots=True, style='b', figsize=(20, 10), grid=True)
    # plt.show()

    # print(stock[["mov_vol","return"]].tail(30))
    # print(stock["mov_vol"].tail(5).sum())
    # print(stock["mov_vol"].tail(10).sum())
    # print(stock["mov_vol"].tail(15).sum())
    # print(stock["mov_vol"].describe())

    return HttpResponse("成功")

    # fig = Figure(figsize=(6, 6))
    # fig.autofmt_xdate()
    # canvas = FigureCanvasAgg(fig)
    # response = HttpResponse(content_type='image/png')
    # canvas.print_png(response)
    # plt.close(fig)
    # return response

    # fig = Figure(figsize=(6, 6))
    # ax = fig.add_subplot(111)
    # x = []
    # y = []
    # now = datetime.datetime.now()
    # delta = datetime.timedelta(days=1)
    # for i in range(10):
    #     x.append(now)
    #     now += delta
    #     y.append(random.randint(0, 1000))
    # ax.plot_date(x, y, '-')
    # ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    # fig.autofmt_xdate()
    # canvas = FigureCanvasAgg(fig)
    # response = HttpResponse(content_type='image/png')
    # canvas.print_png(response)
    # plt.close(fig)
    # return response

    # fig = Figure()
    # ax = fig.add_subplot(111)
    # x = []
    # y = []
    # now = datetime.datetime.now()
    # delta = datetime.timedelta(days=1)
    # for i in range(10):
    #     x.append(now)
    #     now += delta
    #     y.append(random.randint(0, 1000))
    # ax.plot_date(x, y, '-')
    # ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    # fig.autofmt_xdate()
    # canvas = FigureCanvasAgg(fig)
    # response = HttpResponse(content_type='image/png')
    # canvas.print_png(response)
    # return response