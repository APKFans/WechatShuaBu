import json
import logging
import time

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters
from wxcloudrun.shuabu.xiaomi import main_handler

logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'bushu.html', {"error": ""})


def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                           json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """

    try:
        data = Counters.objects.get(id=1)
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0},
                            json_dumps_params={'ensure_ascii': False})
    return JsonResponse({'code': 0, 'data': data.count},
                        json_dumps_params={'ensure_ascii': False})


def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if 'action' not in body:
        return JsonResponse({'code': -1, 'errorMsg': '缺少action参数'},
                            json_dumps_params={'ensure_ascii': False})

    if body['action'] == 'inc':
        try:
            data = Counters.objects.get(id=1)
        except Counters.DoesNotExist:
            data = Counters()
        data.id = 1
        data.count += 1
        data.save()
        return JsonResponse({'code': 0, "data": data.count},
                            json_dumps_params={'ensure_ascii': False})
    elif body['action'] == 'clear':
        try:
            data = Counters.objects.get(id=1)
            data.delete()
        except Counters.DoesNotExist:
            logger.info('record not exist')
        return JsonResponse({'code': 0, 'data': 0},
                            json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': -1, 'errorMsg': 'action参数错误'},
                            json_dumps_params={'ensure_ascii': False})


def shua_bu(request):
    """
    刷步
    """
    if request.method == 'POST':
        logger.info('shua_bu req: {}'.format(request.body))
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        step = request.POST.get('step', 0)

        if not username or not password or not step:
            return JsonResponse({'code': -1, 'errorMsg': '账号、密码和步数不能为空'}, json_dumps_params={'ensure_ascii': False})

        try:
            step = int(step)
            if step <= 0:
                # return render(request, "bushu.html", {"error": "step需要大于等于0"})
                return JsonResponse({'code': -1, 'errorMsg': '步数需要大于等于0'}, json_dumps_params={'ensure_ascii': False})
        except:
            # return render(request, "bushu.html", {"error": "step输入错误，需正整数"})
            return JsonResponse({'code': -1, 'errorMsg': '步数输入错误，需是正整数'}, json_dumps_params={'ensure_ascii': False})

        event = {"queryString": {"user": username.strip(), "password": password.strip(), "step": step}}
        result = main_handler(event)
        # return render(request, "bushu.html", {"error": result.get('data')})
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    else:
        # return render(request, "bushu.html", {"error": "method错误"})
        return JsonResponse({'code': -1, 'errorMsg': 'method错误'}, json_dumps_params={'ensure_ascii': False})


def reply(request):
    """
    用户刷步消息处理
    """
    logger.info('shua_bu req: {}'.format(request.body))
    reply = json.loads(request.body)
    msg_type = reply['MsgType']
    if msg_type == 'text':
        to_user = reply['ToUserName']
        from_user = reply['FromUserName']
        msg = reply['content']
        m = msg.split('#')
        create_time = int(time.time())

        if len(m) == 3:
            username = m[0]
            password = m[1]
            step = m[2]

            if not username or not password or not step:
                return f"""<xml>
                          <ToUserName><![CDATA[{to_user}]]></ToUserName>
                          <FromUserName><![CDATA[{from_user}]]></FromUserName>
                          <CreateTime>{create_time}</CreateTime>
                          <MsgType><![CDATA[text]]></MsgType>
                          <Content><![CDATA[{'账号、密码和步数不能为空'}]]></Content>
                        </xml>"""

            try:
                step = int(step)
                if step <= 0:
                    return f"""<xml>
                                  <ToUserName><![CDATA[{to_user}]]></ToUserName>
                                  <FromUserName><![CDATA[{from_user}]]></FromUserName>
                                  <CreateTime>{create_time}</CreateTime>
                                  <MsgType><![CDATA[text]]></MsgType>
                                  <Content><![CDATA[{'步数需要大于等于0'}]]></Content>
                                </xml>"""
            except:
                return f"""<xml>
                              <ToUserName><![CDATA[{to_user}]]></ToUserName>
                              <FromUserName><![CDATA[{from_user}]]></FromUserName>
                              <CreateTime>{create_time}</CreateTime>
                              <MsgType><![CDATA[text]]></MsgType>
                              <Content><![CDATA[{'步数输入错误，需是正整数'}]]></Content>
                            </xml>"""

            event = {"queryString": {"user": username.strip(), "password": password.strip(), "step": step}}
            result = main_handler(event)
            return f"""<xml>
                          <ToUserName><![CDATA[{to_user}]]></ToUserName>
                          <FromUserName><![CDATA[{from_user}]]></FromUserName>
                          <CreateTime>{create_time}</CreateTime>
                          <MsgType><![CDATA[text]]></MsgType>
                          <Content><![CDATA[{result.get('data')}]]></Content>
                        </xml>"""


