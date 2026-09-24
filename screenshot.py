import requests
import time
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import os


def load_data():
    """从JSON文件加载历史数据"""
    try:
        with open('water_level_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_data(data):
    """保存数据到JSON文件"""
    with open('water_level_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_html_report(data):
    """生成HTML可视化报告"""
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水位数据可视化报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1350px;
            min-width: 1350px;
            margin: 0 auto;
            background-color: white;
            padding: 5px 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 3px 3px rgba(0,0,0,0.3);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin: 0px;
        }}
        .chart-section {{
            margin-bottom: 0px;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 0px;
        }}
        .table-section {{
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: center;
        }}
        th {{
            background-color: #3a71cb;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .timestamp {{
            text-align: right;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }}
        .status-section {{
            background-color: #f8f9fa;
            padding: 10px 10px;
            border-radius: 10px;
            margin: 10px 0;
            border: 2px solid #ddd;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .status-item {{
            align-items: self-end;
        }}
        .status-label {{
            font-size: 20px;
            color: #666;
            font-weight: bold;
        }}
        .status-value {{
            font-size: 40px;
            font-weight: bold;
        }}
        .warningStatus-value {{
            font-size: 25px;
            font-weight: bold;
            line-height: 32px;
        }}
        .status-red {{
            color: red;
        }}
        .status-blue {{
            color: #007bff;
        }}
        .status-green {{
            color: #03ed08;
        }}
        .status-orange {{
            color: #f3a533;
        }}
        .image-section {{
            max-width: 90%;
            margin: 0px auto;
            text-align: center;
            position: relative;
            border-radius: 10px;
            box-shadow: 2px 2px 2px 2px rgba(0,0,0,0.3);
        }}
        .image-section img {{
            max-width: 100%;
            height: auto;
            display: block;
            border-radius: 10px;
            margin: 0 auto;
        }}
        .image-overlay-text {{
            transform: translateX(-50%);
            font-size: 250%;
            font-weight: bold;
            z-index: 10;
            white-space: nowrap;
        }}
        .wz {{
            position: absolute;
            top: 52%;
            left: 92.5%;
        }}
        .jk {{
            position: absolute;
            top: 52%;
            left: 68%;  
        }}
        .wx {{
            position: absolute;
            top: 10%;
            left: 40%;
        }}
        .lb {{
            position: absolute;
            top: 10%;
            left: 11%;
        }}
        .lc {{
            position: absolute;
            top: 54.5%;
            left: 13%;
        }}
        .gg {{
            position: absolute;
            top: 54.5%;
            left: 46%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>西江流域水位数据可视化报告</h1>
        
        <div class="chart-section">
            <div class="chart-container">
                <canvas id="waterLevelChart"></canvas>
            </div>
        </div>
"""

    # 按时间排序数据
    sorted_data = sorted(data, key=lambda x: x['时间'])

    # 测试输出
    #print(sorted_data)

    # 获取最新数据的上游状态、所有站点状态
    if sorted_data:
        latest_upstream_color = sorted_data[-1].get('上游情况', {}).get('颜色', 'blue')
        latest_upstream_desc = sorted_data[-1].get('上游情况', {}).get('描述', '-')
        latest_upstream_change = sorted_data[-1].get('上游情况', {}).get('总变化和', '0')

        latest_wuzhou_color = sorted_data[-1].get('站点数据',{}).get('梧州', {}).get('颜色', 'blue')
        latest_wuzhou_desc = sorted_data[-1].get('站点数据',{}).get('梧州', {}).get('情况', '-')
        latest_wuzhou_data = sorted_data[-1].get('站点数据',{}).get('梧州', {}).get('水位', '0')
        latest_wuzhou_change = sorted_data[-1].get('站点数据',{}).get('梧州', {}).get('变化值', '0')

        latest_jiangkou_color = sorted_data[-1].get('站点数据',{}).get('濛江', {}).get('颜色', 'blue')
        latest_jiangkou_desc = sorted_data[-1].get('站点数据',{}).get('濛江', {}).get('情况', '-')
        latest_jiangkou_data = sorted_data[-1].get('站点数据',{}).get('濛江', {}).get('水位', '0')
        latest_jiangkou_change = sorted_data[-1].get('站点数据',{}).get('濛江', {}).get('变化值', '0')

        latest_wuxuan_color = sorted_data[-1].get('站点数据',{}).get('武宣', {}).get('颜色', 'blue')
        latest_wuxuan_desc = sorted_data[-1].get('站点数据',{}).get('武宣', {}).get('情况', '-')
        latest_wuxuan_data = sorted_data[-1].get('站点数据',{}).get('武宣', {}).get('水位', '0')
        latest_wuxuan_change = sorted_data[-1].get('站点数据',{}).get('武宣', {}).get('变化值', '0')

        latest_laibing_color = sorted_data[-1].get('站点数据',{}).get('来宾', {}).get('颜色', 'blue')
        latest_laibing_desc = sorted_data[-1].get('站点数据',{}).get('来宾', {}).get('情况', '-')
        latest_laibing_data = sorted_data[-1].get('站点数据',{}).get('来宾', {}).get('水位', '0')
        latest_laibing_change = sorted_data[-1].get('站点数据',{}).get('来宾', {}).get('变化值', '0')

        latest_luancheng_color = sorted_data[-1].get('站点数据',{}).get('峦城', {}).get('颜色', 'blue')
        latest_luancheng_desc = sorted_data[-1].get('站点数据',{}).get('峦城', {}).get('情况', '-')
        latest_luancheng_data = sorted_data[-1].get('站点数据',{}).get('峦城', {}).get('水位', '0')
        latest_luancheng_change = sorted_data[-1].get('站点数据',{}).get('峦城', {}).get('变化值', '0')

        latest_guigang_color = sorted_data[-1].get('站点数据',{}).get('贵港', {}).get('颜色', 'blue')
        latest_guigang_desc = sorted_data[-1].get('站点数据',{}).get('贵港', {}).get('情况', '-')
        latest_guigang_data = sorted_data[-1].get('站点数据',{}).get('贵港', {}).get('水位', '0')
        latest_guigang_change = sorted_data[-1].get('站点数据',{}).get('贵港', {}).get('变化值', '0')

        latest_datengxia_data = sorted_data[-1].get('枢纽数据',{}).get('大藤峡枢纽', {}).get('上游水位', '0')
        latest_datengxia_fs = sorted_data[-1].get('枢纽数据',{}).get('大藤峡枢纽', {}).get('是否放水', '0')
        latest_datengxia_ckll = sorted_data[-1].get('枢纽数据',{}).get('大藤峡枢纽', {}).get('出库流量', '0')

        latest_guiping_data = sorted_data[-1].get('枢纽数据',{}).get('贵港枢纽', {}).get('上游水位', '0')
        latest_guiping_fs = sorted_data[-1].get('枢纽数据',{}).get('贵港枢纽', {}).get('是否放水', '0')
        latest_guiping_ckll = sorted_data[-1].get('枢纽数据',{}).get('贵港枢纽', {}).get('出库流量', '0')

        latest_changzhou_data = sorted_data[-1].get('枢纽数据',{}).get('长洲船闸', {}).get('上游水位', '0')
        latest_changzhou_fs = sorted_data[-1].get('枢纽数据',{}).get('长洲船闸', {}).get('是否放水', '0')
        latest_changzhou_ckll = sorted_data[-1].get('枢纽数据',{}).get('长洲船闸', {}).get('出库流量', '0')

    latest_upstream_change_value = ''
    if latest_upstream_change >= 0:
        latest_upstream_change_value += '上升'
    else:
        latest_upstream_change_value += '下降'
    latest_upstream_change_value += str(format(abs(latest_upstream_change), '.2f'))
    
    #上游变化和加权水库放水信息！
    latest_upstream_change += latest_datengxia_fs*0.4+latest_guiping_fs*0.4+latest_changzhou_fs*0.6

    #计算预报值 如果变化幅度过小就上下略微波动 否则梧州预计变化值在上游最新总变化值0.35到0.65之间
    latest_wuzhou_data_float = float(latest_wuzhou_data)  # 转换为浮点数
    if latest_upstream_change <= 0.5 and latest_upstream_change >= -0.5:
        latest_wuzhou_p1 = format(latest_wuzhou_data_float - latest_upstream_change*0.7, '.2f')
        latest_wuzhou_p2 = format(latest_wuzhou_data_float + latest_upstream_change*0.7, '.2f')
    else:
        latest_wuzhou_p1 = format(latest_wuzhou_data_float + latest_upstream_change*0.4, '.2f')
        latest_wuzhou_p2 = format(latest_wuzhou_data_float + latest_upstream_change*0.7, '.2f')

    lp3 = 0 #互换一下
    if latest_wuzhou_p1 > latest_wuzhou_p2:
        lp3 = latest_wuzhou_p2
        latest_wuzhou_p2 = latest_wuzhou_p1
        latest_wuzhou_p1 = lp3

    # 计算预报颜色样式 如果上游变化幅度过小或水位下降就用蓝色 否则用红色
    if latest_upstream_change <= 0.5:
        latest_wuzhou_pColor = 'blue'
    else:
        latest_wuzhou_pColor = 'red'

    #计算预报程度描述 如果上游变化幅度绝对值小于0.5为“变化不大”，绝对值在0.5和2直接为“略微”，绝对值在2和4直接为“明显”，绝对值大于4为“大幅”
    if abs(latest_upstream_change) < 0.5:
        latest_wuzhou_pDesc = '变化不大 '
        latest_upstream_des = ''
    elif abs(latest_upstream_change) < 2:
        latest_wuzhou_pDesc = '略微'
        if latest_upstream_desc == '较平稳':
            latest_upstream_des = ''
        else:
            latest_upstream_des = '略微'
    elif abs(latest_upstream_change) < 4:
        latest_wuzhou_pDesc = '明显'
        latest_upstream_des = '明显'
    else:
        latest_wuzhou_pDesc = '大幅'
        latest_upstream_des = '大幅'

    #计算预报上升或下降，如果上游变化幅度大于0.5为“上升”，小于-0.5为“下降”，否则为“小幅波动”
    if latest_upstream_change > 0.5:
        latest_wuzhou_pDirection = '上升'
    elif latest_upstream_change < -0.5:
        latest_wuzhou_pDirection = '下降'
    else:
        latest_wuzhou_pDirection = '上下小幅波动'

    #计算预报情况符号，如果上游变化幅度在0.5和2之间用↗︎，在2和4之间用▲，在4以上用⏫︎；如果上游变化幅度在-0.5和-2之间用↘︎，在-2和-4之间用▼，在-4以上用⏬︎，否则用〰︎
    if latest_upstream_change > 0.5 and latest_upstream_change < 2:
        latest_wuzhou_pSymbol = '↗︎'
        latest_upstream_Symbol = '↗︎'
    elif latest_upstream_change > 2 and latest_upstream_change < 4:
        latest_wuzhou_pSymbol = '▲'
        latest_upstream_Symbol = '▲'
    elif latest_upstream_change > 4:
        latest_wuzhou_pSymbol = '⏫︎'
        latest_upstream_Symbol = '⏫︎'
    elif latest_upstream_change < -0.5 and latest_upstream_change > -2:
        latest_wuzhou_pSymbol = '↘︎'
        latest_upstream_Symbol = '↘︎'
    elif latest_upstream_change < -2 and latest_upstream_change > -4:
        latest_wuzhou_pSymbol = '▼'
        latest_upstream_Symbol = '▼'
    elif latest_upstream_change < -4:
        latest_wuzhou_pSymbol = '⏬︎'
        latest_upstream_Symbol = '⏬︎'
    elif latest_upstream_change > 0 and latest_upstream_change <= 0.5:
        latest_upstream_Symbol = '↗︎'
        latest_wuzhou_pSymbol = '  '
    elif latest_upstream_change < 0 and latest_upstream_change >= -0.5:
        latest_upstream_Symbol = '↘︎'
        latest_wuzhou_pSymbol = '  '
    else:
        latest_wuzhou_pSymbol = '  '

    #站点告警文字
    station_warning = ' '

    #站点是否需要警告符号
    latest_wuzhou_wSymbol = ' '
    latest_jiangkou_wSymbol = ' '
    latest_wuxuan_wSymbol = ' '
    latest_laibing_wSymbol = ' '
    latest_luancheng_wSymbol = ' '
    latest_guigang_wSymbol = ' '

    #站点是否需要超警戒线警告
    s1 = 0
    if float(latest_wuzhou_data) >= 18.5:
        latest_wuzhou_wSymbol = '🚨'
        station_warning += '<br> &nbsp;'
        station_warning += '梧州（已超警'
        station_warning += str(format(float(latest_wuzhou_data)-18.5), '.2f')
        station_warning += '米）'
        s1 = 1

    if float(latest_jiangkou_data) >= 25:
        latest_jiangkou_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '濛江（已超警'
        station_warning += str(format(float(latest_jiangkou_data)-31.7), '.2f')
        station_warning += '米）'
        s1 = 1

    if float(latest_guigang_data) >= 44:
        latest_guigang_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '贵港（已超警'
        station_warning += str(format(float(latest_guigang_data)-44), '.2f')
        station_warning += '米）'
        s1 = 1

    if float(latest_luancheng_data) >= 64.2:
        latest_luancheng_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '峦城（已超警'
        station_warning += str(format(float(latest_luancheng_data)-64.2), '.2f')
        station_warning += '米）'
        s1 = 1

    if float(latest_wuxuan_data) >= 61.4:
        latest_wuxuan_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '武宣（已超警'
        station_warning += str(format(float(latest_wuxuan_data)-61.4), '.2f')
        station_warning += '米）'
        s1 = 1

    if float(latest_laibing_data) >= 62:
        latest_laibing_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '来宾（已超警'
        station_warning += str(format(float(latest_laibing_data)-62), '.2f')
        station_warning += '米）'
        s1 = 1

    if s1 != 0:
        station_warning += '站点水位已超警！请紧密关注水位变化！'

    s2 = 0
    if float(latest_wuzhou_data) >= 13 and float(latest_wuzhou_data) < 18.5:
        latest_wuzhou_wSymbol = '⚠️'
        station_warning += '<br> &nbsp;'
        station_warning += '梧州（水位已超过13米）'

    if float(latest_jiangkou_data) >= 23.5 and float(latest_jiangkou_data) < 25:
        latest_jiangkou_wSymbol = '⚠️'
        if s2 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '濛江（水位已超过24米）'

    if s2 != 0:
        station_warning += '水位较高，注意警戒！'

    #站点是否需要水位快速上涨警告
    s3 = 0
    if float(latest_wuzhou_change) > 2:
        latest_wuzhou_wSymbol = '🚨'
        station_warning += '<br> &nbsp;'
        station_warning += '梧州'
        s3 = 1

    if float(latest_jiangkou_change) > 2:
        latest_jiangkou_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '濛江'
        s3 = 1

    if float(latest_wuxuan_change) > 2:
        latest_wuxuan_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '武宣'
        s3 = 1

    if float(latest_laibing_change) > 2:
        latest_laibing_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '来宾'
        s3 = 1

    if float(latest_luancheng_change) > 2:
        latest_luancheng_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '峦城'
        s3 = 1

    if float(latest_guigang_change) > 2:
        latest_guigang_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        else:
            station_warning += '<br> &nbsp;'
        station_warning += '贵港'
        s3 = 1

    if s3 != 0:
        station_warning += '水位快速上涨（日涨幅已超2米）！请密切关注水位变化！'

    #梧州是否需要水位过低警告
    if float(latest_wuzhou_data) < 4:
        latest_wuzhou_wSymbol = '⚠️'
        station_warning += '<br> &nbsp;'
        station_warning += '梧州水位过低，可能影响船舶通航！'

    swC = "green"
    
    if station_warning != ' ':
        #station_warning += '加强船舶调度！'
        swC = "red"
    else:
        station_warning += '无预警信息'

    #水库预警文字
    reservoir_warning = ' '

    latest_datengxia_wSymbol = ' '
    latest_guiping_wSymbol = ' '
    latest_changzhou_wSymbol = ' '
    latest_datengxia_color = 'blue'
    latest_guiping_color = 'blue'
    latest_changzhou_color = 'blue'
 
    #水库是否需要开闸预警
    r2 = 0
    if float(latest_datengxia_fs) == 1 or float(latest_datengxia_ckll) >= 12000:
        latest_datengxia_color = 'orange'
        latest_datengxia_wSymbol += '🌊'
        reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '大藤峡枢纽'
        if float(latest_datengxia_ckll) >= 12000:
            reservoir_warning += '(出库流量达'
            reservoir_warning += latest_datengxia_ckll
            reservoir_warning += 'm³/秒，较大)'
        r2 = 1
    if float(latest_guiping_fs) == 1 or float(latest_guiping_ckll) >= 12000:
        latest_guiping_color = 'orange'
        latest_guiping_wSymbol += '🌊'
        if r2 != 0:
            reservoir_warning += '、'
        else:
            reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '贵港枢纽'
        if float(latest_guiping_ckll) >= 12000:
            reservoir_warning += '(出库流量达'
            reservoir_warning += latest_guiping_ckll
            reservoir_warning += 'm³/秒，较大)'
        r2 = 1
    if float(latest_changzhou_fs) == 1 or float(latest_changzhou_ckll) >= 15000:
        latest_changzhou_color = 'orange'
        latest_changzhou_wSymbol += '🌊'
        if r2 != 0:
            reservoir_warning += '、'
        else:
            reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '长洲枢纽'
        if float(latest_changzhou_ckll) >= 15000:
            reservoir_warning += '(出库流量达'
            reservoir_warning += latest_changzhou_ckll
            reservoir_warning += 'm³/秒，较大)'
        r2 = 1
    if r2 != 0:
        reservoir_warning += '出库流量更大，可能正在放水，对下游水位会有额外影响。'

    #水库是否需要水位超过正常水位警告
    r3 = 0
    if float(latest_datengxia_data) >= 61:
        latest_datengxia_wSymbol += '🚨'
        reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '大藤峡枢纽（已超'
        resevoir_warning += str(format((float(latest_datengxia_data)-61), '.2f'))
        resevoir_warning += '米）'
        latest_datengxia_color = 'red'
        r3 = 1
    if float(latest_guiping_data) >= 43.1:
        latest_guiping_wSymbol += '🚨'
        if r3 != 0:
            reservoir_warning += '、'
        else:
            reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '贵港枢纽(已超'
        reservoir_warning += str(format((float(latest_guiping_data)-43.1), '.2f'))
        reservoir_warning += '米）'
        latest_guiping_color = 'red'
        r3 = 1
    if float(latest_changzhou_data) >= 20.6:
        latest_changzhou_wSymbol += '🚨'
        if r3 != 0:
            reservoir_warning += '、'
        else:
            reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '长洲枢纽(已超'
        reservoir_warning += str(format((float(latest_changzhou_data)-20.6), '.2f'))
        reservoir_warning += '米）'
        latest_changzhou_color = 'red'
        r3 = 1
    if r3 != 0:
        reservoir_warning += '水位达到或已超过正常蓄水位，可能进行泄洪放水！'
     #水库是否需要水位高警告符号
    r1 = 0
    if float(latest_datengxia_data) >= 60 and float(latest_datengxia_data) < 61:
        latest_datengxia_wSymbol += '⚠️'
        reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '大藤峡枢纽(还差'
        reservoir_warning += str(format(61-float(latest_datengxia_data), '.2f'))
        reservoir_warning += '米）'
        latest_datengxia_color = 'orange'
        r1 = 1
    if float(latest_guiping_data) >= 42 and float(latest_guiping_data) < 43.1:
        latest_guiping_wSymbol += '⚠️'
        if r1 != 0:
            reservoir_warning += '、'
        else:
            reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '贵港枢纽(还差'
        reservoir_warning += str(format(43.1-float(latest_guiping_data), '.2f'))
        reservoir_warning += '米）'
        latest_guiping_color = 'orange'
        r1 = 1
    if float(latest_changzhou_data) >= 19.6 and float(latest_changzhou_data) < 20.6:
        latest_changzhou_wSymbol += '⚠️'
        if r1 != 0:
            reservoir_warning += '、'
        else:
            reservoir_warning += '<br> &nbsp;'
        reservoir_warning += '长洲枢纽(还差'
        reservoir_warning += str(format(20.6-float(latest_changzhou_data), '.2f'))
        reservoir_warning += '米）'
        latest_changzhou_color = 'orange'
        r1 = 1
    if r1 != 0:
        reservoir_warning += '接近正常蓄水位，请留意开闸放水信息！'

    if latest_datengxia_wSymbol == ' ':
        latest_datengxia_wSymbol += '正常'

    if latest_guiping_wSymbol == ' ':
        latest_guiping_wSymbol += '正常'

    if latest_changzhou_wSymbol == ' ':
        latest_changzhou_wSymbol += '正常'

    rwC = "green"
    
    if reservoir_warning != ' ':
        #reservoir_warning += '请及时注意水位变化，加强船舶调度！'
        rwC = "red"
    else:
        reservoir_warning += '无预警信息'
    
    # 添加状态显示区域
    html_content += f"""
        
        <div class="status-section">
            <div class="status-item">
                <span class="status-label">上游整体情况：</span>
                <span class="status-value status-{latest_upstream_color}" style="font-size:35px">
                    水位{latest_upstream_des}{latest_upstream_desc} &nbsp;整体{latest_upstream_change_value}m &nbsp;&nbsp;
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">今早八点梧州水位：</span>
                <span class="status-value status-{latest_wuzhou_color}">
                    {latest_wuzhou_data}m&nbsp;
                </span>
                <span class="status-label">较昨日变化：</span>
                <span class="status-value status-{latest_wuzhou_color}">
                    {latest_wuzhou_change}m{latest_wuzhou_desc}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">近2天梧州水位预报：</span>
                <span class="status-value status-{latest_wuzhou_pColor}">
                    {latest_wuzhou_p1}m~{latest_wuzhou_p2}m      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   预计水位{latest_wuzhou_pDesc}{latest_wuzhou_pDirection}{latest_wuzhou_pSymbol}  
                </span>
            </div>
        </div>
        <div class="status-section" style="gap: 0px">
            <div class="status-item" style="min-width:1300px">
                <span class="status-label">🚨水库预警：</span>
                <span class="warningStatus-value status-{rwC}">
                    {reservoir_warning}
                </span>
            </div>
            <div class="status-item" style="min-width:1300px">
                <span class="status-label">🚨站点预警：</span>
                <span class="warningStatus-value status-{swC}">
                    {station_warning}
                </span>
            </div>
        </div>
        
        <div class="image-section">
            <div class="image-overlay-text status-{latest_wuzhou_color}" style="position: absolute; top: 52%; left: 92.5%; font-size:200%;">{latest_wuzhou_data}m</div>
            <div class="image-overlay-text status-{latest_wuzhou_color}" style="position: absolute; top: 62%; left: 92.5%; font-size:150%;">{latest_wuzhou_change}m{latest_wuzhou_desc}</div>
            <div class="image-overlay-text status-{latest_wuzhou_color}" style="position: absolute;top: 41.25%;left: 86%;">====</div>
            <div class="image-overlay-text status-{latest_jiangkou_color}" style="position: absolute; top: 52%; left: 68%; font-size:200%;">{latest_jiangkou_data}m</div>
            <div class="image-overlay-text status-{latest_jiangkou_color}" style="position: absolute; top: 62%; left: 68%; font-size:150%;">{latest_jiangkou_change}m{latest_jiangkou_desc}</div>
            <div class="image-overlay-text status-{latest_jiangkou_color}" style="position: absolute; top: 41.4%; left: 63.85%;">==</div>
            <div class="image-overlay-text status-{latest_wuxuan_color}" style="position: absolute; top: 12%; left: 39%; font-size:200%;">{latest_wuxuan_data}m</div>
            <div class="image-overlay-text status-{latest_wuxuan_color}" style="position: absolute; top: 6%; left: 39%; font-size:150%;">{latest_wuxuan_change}m{latest_wuxuan_desc}</div>
            <div class="image-overlay-text status-{latest_wuxuan_color}" style="position: absolute; top: 18.9%; left: 23.2%;">===========</div>
            <div class="image-overlay-text status-{latest_laibing_color}" style="position: absolute; top: 12%; left: 9%; font-size:200%;">{latest_laibing_data}m</div>
            <div class="image-overlay-text status-{latest_laibing_color}" style="position: absolute; top: 6%; left: 9%; font-size:150%;">{latest_laibing_change}m{latest_laibing_desc}</div>
            <div class="image-overlay-text status-{latest_laibing_color}" style="position: absolute; top: 18.9%; left: 4%;">===</div>
            <div class="image-overlay-text status-{latest_luancheng_color}" style="position: absolute; top: 57%; left: 13%; font-size:200%;">{latest_luancheng_data}m</div>
            <div class="image-overlay-text status-{latest_luancheng_color}" style="position: absolute; top: 51%; left: 13%; font-size:150%;">{latest_luancheng_change}m{latest_luancheng_desc}</div>
            <div class="image-overlay-text status-{latest_luancheng_color}" style="position: absolute; top: 63.8%; left: 6%;">====</div>
            <div class="image-overlay-text status-{latest_guigang_color}" style="position: absolute; top: 57%; left: 46%; font-size:200%;">{latest_guigang_data}m</div>
            <div class="image-overlay-text status-{latest_guigang_color}" style="position: absolute; top: 51%; left: 46%; font-size:150%;">{latest_guigang_change}m{latest_guigang_desc}</div>
            <div class="image-overlay-text status-{latest_guigang_color}" style="position: absolute; top: 63.8%; left: 28.5%;">============</div>
            <div class="image-overlay-text" style="position: absolute; top: 42.4%; left: 92.2%;font-size:200%">{latest_wuzhou_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 42.4%; left: 66.9%;font-size:200%">{latest_jiangkou_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 20%; left: 37.9%;font-size:200%">{latest_wuxuan_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 20%; left: 8.6%;font-size:200%">{latest_laibing_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 65%; left: 12%;font-size:200%">{latest_luancheng_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 65%; left: 45%;font-size:200%">{latest_guigang_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute;top: 17%;left: 53.75%;font-size: 180%;writing-mode: vertical-rl;text-orientation: mixed;justify-content: center;align-items: center;display: flex;height: 20%;color:blue">{latest_datengxia_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 59.9%;left: 56.1%;font-size: 180%;writing-mode: vertical-rl;text-orientation: mixed;justify-content: center;align-items: center;display: flex;height: 20%;color:blue">{latest_guiping_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 39%; left: 79%;font-size: 180%;writing-mode: vertical-rl;text-orientation: mixed;justify-content: center;align-items: center;display: flex; height: 20%;color:blue">{latest_changzhou_wSymbol}</div>
            <div class="image-overlay-text status-{latest_datengxia_color}" style="position: absolute;top: -0.5%;left: 53.8%;font-size: 180%;">{latest_datengxia_data}m</div>
            <div class="image-overlay-text status-{latest_guiping_color}" style="position: absolute;top: 88%;left: 56%;font-size: 180%;">{latest_guiping_data}m</div>
            <div class="image-overlay-text status-{latest_changzhou_color}" style="position: absolute;top: 3%;left: 79%;font-size: 180%;">{latest_changzhou_data}m</div>
            <img src="river.jpg" alt="西江流域图">
        </div>
        
        <div class="table-section">
            <h2>历史数据总表</h2>
            <table>
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>梧州</th>
                        <th>濛江</th>
                        <th>贵港</th>
                        <th>武宣</th>
                        <th>来宾</th>
                        <th>峦城</th>
                    </tr>
                </thead>
                <tbody>
"""

    # 添加表格数据
    for record in sorted_data:
        station_data = record.get('站点数据', {})
        html_content += f"""
                    <tr>
                        <td>{record['时间']}</td>
                        <td>{station_data.get('梧州', {}).get('水位', '-')} {station_data.get('梧州', {}).get('情况', ' ')} ({station_data.get('梧州', {}).get('变化值', '-')})</td>
                        <td>{station_data.get('濛江', {}).get('水位', '-')} {station_data.get('濛江', {}).get('情况', ' ')} ({station_data.get('濛江', {}).get('变化值', '-')})</td>
                        <td>{station_data.get('贵港', {}).get('水位', '-')} {station_data.get('贵港', {}).get('情况', ' ')} ({station_data.get('贵港', {}).get('变化值', '-')})</td>
                        <td>{station_data.get('武宣', {}).get('水位', '-')} {station_data.get('武宣', {}).get('情况', ' ')} ({station_data.get('武宣', {}).get('变化值', '-')})</td>
                        <td>{station_data.get('来宾', {}).get('水位', '-')} {station_data.get('来宾', {}).get('情况', ' ')} ({station_data.get('来宾', {}).get('变化值', '-')})</td>
                        <td>{station_data.get('峦城', {}).get('水位', '-')} {station_data.get('峦城', {}).get('情况', ' ')} ({station_data.get('峦城', {}).get('变化值', '-')})</td>
                    </tr>
"""

    # 准备图表数据 - 只显示最新的14条记录
    chart_data = sorted_data[-14:] if len(sorted_data) > 14 else sorted_data
    labels = [record['时间'] for record in chart_data]
    stations = ['梧州', '濛江', '贵港', '武宣', '来宾', '峦城']
    colors = [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)',
        'rgb(153, 102, 255)',
        'rgb(255, 159, 64)'
    ]

    datasets = []
    for i, station in enumerate(stations):
        water_levels = []
        for record in chart_data:
            station_data = record.get('站点数据', {})
            water_level = station_data.get(station, {}).get('水位', 0)
            # 尝试转换为浮点数，如果失败则使用0
            try:
                water_levels.append(float(water_level))
            except (ValueError, TypeError):
                water_levels.append(0)

        datasets.append(f"""
                {{
                    label: '{station}',
                    data: {water_levels},
                    borderColor: '{colors[i]}',
                    backgroundColor: '{colors[i]}',
                    tension: 0.1,
                    fill: false
                }}""")

    html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="timestamp">
            报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            数据记录数: {len(data)} 条
        </div>
    </div>

    <script>
        const ctx = document.getElementById('waterLevelChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{','.join(datasets)}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '各站点水位变化趋势图 (最近{len(chart_data)}天)',
                        font: {{
                            size: 18
                        }}
                    }},
                    legend: {{
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        title: {{
                            display: true,
                            text: '水位 (米)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: '时间'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    with open('water_level_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


def parse_water_level_data(html_content, publish_date):
    """解析水位数据"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 目标站点
    target_stations = ['梧州', '濛江', '贵港', '武宣', '来宾', '峦城']

    # 查找所有表格
    tables = soup.find_all('table')

    results = {}

    for table in tables:
        rows = table.find_all('tr')

        # 跳过表头行
        for row in rows[3:]:  # 前3行是表头
            cells = row.find_all('td')
            if len(cells) >= 4:
                station_name = cells[0].get_text(strip=True)

                # 检查是否为目标站点
                if station_name in target_stations:
                    observation_time = cells[1].get_text(strip=True)
                    water_level = cells[2].get_text(strip=True)
                    change_value = cells[3].get_text(strip=True)

                    # 如果变化值大于0且不以+开头，则添加+号
                    try:
                        if float(change_value) > 0 and not change_value.startswith('+'):
                            change_value = '+' + change_value
                    except (ValueError, TypeError):
                        pass

                    # 将变化值转换为数字：1表示上升，0表示持平或下降
                    try:
                        change_num = float(change_value)
                        if change_num > 0 and change_num < 2:
                            change_value_num = 1  # 上升
                            change_des = "▲"
                            color = "red"
                        elif change_num >= 2:
                            change_value_num = 0  # 大幅上升
                            change_des = "⏫︎"
                            color = "red"
                        elif change_num <= 0 and change_num > -2:
                            change_value_num = 0  # 持平或下降
                            change_des = "▼"
                            color = "blue"
                        else:
                            change_value_num = 0  # 大幅下降
                            change_des = "⏬︎"
                            color = "blue"
                    except (ValueError, TypeError):
                        change_value_num = 0  # 无法解析时默认为0
                        change_des = "▼"
                        color = "blue"

                    # 组合完整日期时间
                    full_datetime = f"{publish_date} {observation_time}"

                    # 使用字典存储，站名为键，重复的会自动覆盖
                    results[station_name] = {
                        '站名': station_name,
                        '水位': water_level,
                        '变化值': change_value,
                        '变化': change_value_num,
                        '情况': change_des,
                        '颜色': color,
                        '时间': full_datetime
                    }

    return results


def parse_reservoir_data(html_content, publish_date):
    """解析水库/船闸数据"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 目标枢纽
    target_reservoirs = ['大藤峡枢纽', '贵港枢纽', '长洲船闸']
    
    # 查找所有表格
    tables = soup.find_all('table')
    
    results = {}
    
    for table in tables:
        rows = table.find_all('tr')
        
        # 寻找通航建筑物流量信息表
        table_found = False
        for row_index, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 1 and '通航建筑物流量信息表' in cells[0].get_text():
                # 找到了正确的表格，从该行开始解析数据（跳过表头行）
                table_found = True
                # 从表头之后开始解析数据行
                for data_row in rows[row_index + 1:]:  # 跳过表头和可能的第二行表头
                    data_cells = data_row.find_all('td')
                    if len(data_cells) >= 6:
                        reservoir_name = data_cells[0].get_text(strip=True)
                        
                        # 检查是否为目标枢纽
                        if reservoir_name in target_reservoirs:
                            observation_time = data_cells[1].get_text(strip=True)
                            upstream_level = data_cells[2].get_text(strip=True)
                            downstream_level = data_cells[3].get_text(strip=True)
                            inflow = data_cells[4].get_text(strip=True)
                            outflow = data_cells[5].get_text(strip=True)
                            
                            # 计算是否放水：出库流量 >= 入库流量则为1，否则为0
                            try:
                                inflow_float = float(inflow)
                                outflow_float = float(outflow)
                                is_releasing = 1 if outflow_float >= inflow_float else 0
                            except (ValueError, TypeError):
                                is_releasing = 0
                            
                            # 组合完整日期时间
                            full_datetime = f"{publish_date} {observation_time}"
                            
                            # 使用字典存储，站名为键，重复的会自动覆盖
                            results[reservoir_name] = {
                                '站名': reservoir_name,
                                '时间': full_datetime,
                                '上游水位': upstream_level,
                                '入库流量': inflow,
                                '出库流量': outflow,
                                '是否放水': is_releasing
                            }
                break
        if table_found:
            break  # 找到表格后就停止搜索其他表格
    
    return results


def main():
    import sys
    import os

    # 设置标准输出编码为 UTF-8，避免 Windows 终端 GBK 编码问题
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 访问目标网站
    print("正在打开网站...")
    base_url = "https://www.gxghj.cn/c/fw/slcx"
    try:
        response = requests.get(base_url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        print(f"网站访问成功，状态码: {response.status_code}")
    except Exception as e:
        print(f"访问网站失败: {e}")
        return

    # 解析列表页HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取前6条新闻链接
    news_items = soup.select('.newsList li')
    num_links = min(6, len(news_items))

    print(f"找到 {len(news_items)} 条新闻，将处理前 {num_links} 条")

    # 使用字典存储所有数据，站名为键
    all_water_data = {}

    # 使用字典存储水库数据，枢纽名为键
    all_reservoir_data = {}

    for i in range(num_links):
        news_item = news_items[i]

        # 获取链接标题和URL
        title_tag = news_item.select_one('.newsTitle')
        link_tag = news_item.select_one('a')

        if not title_tag or not link_tag:
            continue

        link_title = title_tag.get_text(strip=True)
        link_url = link_tag.get('href')

        # 处理相对URL
        if link_url.startswith('/'):
            link_url = f"https://www.gxghj.cn{link_url}"
        elif not link_url.startswith('http'):
            link_url = f"https://www.gxghj.cn/c/fw/slcx/{link_url}"

        print(f"\n{'='*50}")
        print(f"正在处理第 {i+1} 条链接: {link_title}")
        print(f"{'='*50}")

        # 访问详情页
        try:
            detail_response = requests.get(link_url, headers=headers, timeout=30)
            detail_response.encoding = 'utf-8'
            print(f"详情页访问成功，状态码: {detail_response.status_code}")
        except Exception as e:
            print(f"访问详情页失败: {e}")
            continue

        # 解析详情页HTML
        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

        # 获取发布日期
        info_tag = detail_soup.select_one('.info')
        if info_tag:
            publish_date_info = info_tag.get_text()
            date_match = re.search(r'发布日期：(\d{4}-\d{2}-\d{2})', publish_date_info)
            if date_match:
                publish_date = date_match.group(1)
            else:
                publish_date = "未知日期"
        else:
            publish_date = "未知日期"

        print(f"发布日期: {publish_date}")

        # 解析水位数据
        water_data = parse_water_level_data(detail_response.text, publish_date)
        # 合并到总数据中，重复站点会自动覆盖
        all_water_data.update(water_data)

        # 解析水库/船闸数据
        reservoir_data = parse_reservoir_data(detail_response.text, publish_date)
        # 合并到水库数据中，重复枢纽会自动覆盖
        all_reservoir_data.update(reservoir_data)

        print(f"本次获取水位数据: {len(water_data)} 个站点")
        print(f"本次获取水库数据: {len(reservoir_data)} 个枢纽")

        # 短暂延迟，避免请求过快
        time.sleep(1)

    # 输出所有爬取的数据
    print("\n\n")
    print("=" * 60)
    print("所有水位数据汇总")
    print("=" * 60)

    for station_name in sorted(all_water_data.keys()):
        data = all_water_data[station_name]
        change_desc = "上升" if data['变化'] == 1 else "持平或下降"
        print(f"站名: {data['站名']}")
        print(f"水位: {data['水位']} 米")
        print(f"变化: {data['变化']} ({change_desc})")
        print(f"变化值: {data['变化值']}")
        print(f"情况: {data['情况']}")
        print(f"颜色: {data['颜色']}")
        print(f"时间: {data['时间']}")
        print("-" * 60)

    # 输出所有爬取的水库数据
    print("\n\n")
    print("=" * 60)
    print("水库/船闸数据汇总")
    print("=" * 60)

    for reservoir_name in sorted(all_reservoir_data.keys()):
        data = all_reservoir_data[reservoir_name]
        releasing_status = "放水中" if data['是否放水'] == 1 else "未放水"
        print(f"站名: {data['站名']}")
        print(f"时间: {data['时间']}")
        print(f"上游水位: {data['上游水位']} 米")
        print(f"入库流量: {data['入库流量']} m³/s")
        print(f"出库流量: {data['出库流量']} m³/s")
        print(f"是否放水: {data['是否放水']} ({releasing_status})")
        print("-" * 60)

    # 加载历史数据
    print("\n正在加载历史数据...")
    historical_data = load_data()

    # 检查是否已存在相同时间的数据
    new_data_time = list(all_water_data.values())[0]['时间'] if all_water_data else None
    existing_index = -1
    if new_data_time:
        for i, record in enumerate(historical_data):
            if record['时间'] == new_data_time:
                existing_index = i
                break

    # 添加或更新数据
    if new_data_time:
        # 计算上游整体情况（来宾、武宣、贵港、峦城、濛江）
        upstream_stations = ['来宾', '武宣', '贵港', '峦城', '濛江']
        upstream_change_sum = 0
        up_change_value_sum = 0
        for station in upstream_stations:
            if station in all_water_data:
                upstream_change_sum += all_water_data[station]['变化']
                up_change_value_sum += float(all_water_data[station]['变化值'])


        # 根据上游变化和值决定整体情况
        if upstream_change_sum == 0:
            upstream_status = "下降⏬︎"
            upstream_color = "blue"
        elif upstream_change_sum == 1:
            upstream_status = "下降▼"
            upstream_color = "blue"
        elif upstream_change_sum == 2:
            upstream_status = "较平稳"
            upstream_color = "blue"
        elif upstream_change_sum == 3:
            upstream_status = "上升▲"
            upstream_color = "red"
        else:  # 4或5
            upstream_status = "上升⏫︎"
            upstream_color = "red"

        record_data = {
            '时间': new_data_time,
            '站点数据': all_water_data,
            '枢纽数据': all_reservoir_data,
            '上游情况': {
                '描述': upstream_status,
                '颜色': upstream_color,
                '变化和': upstream_change_sum,
                '总变化和': up_change_value_sum
            }
        }

        print(f"\n上游整体情况: {upstream_status} 变化和: {upstream_change_sum} 总变化和: {up_change_value_sum}")

        if existing_index >= 0:
            print(f"更新时间 {new_data_time} 的数据")
            historical_data[existing_index] = record_data
        else:
            print(f"添加新的时间数据: {new_data_time}")
            historical_data.append(record_data)

    # 保存数据
    save_data(historical_data)
    print(f"数据已保存，当前共有 {len(historical_data)} 条记录")

    # 生成HTML报告
    print("\n正在生成HTML可视化报告...")
    generate_html_report(historical_data)
    print("报告已生成: water_level_report.html")

    print("\n数据爬取完成！")


if __name__ == "__main__":
    main()
