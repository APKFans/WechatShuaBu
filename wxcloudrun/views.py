import json
import logging
import time

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
# from wxcloudrun.models import Counters
from wxcloudrun.shuabu.xiaomi import main_handler

logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'bushu.html', {"error": ""})


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
    xml = 'success'
    logger.info('shua_bu req: {}'.format(request.body))
    reply = json.loads(request.body)
    logger.info(reply)
    msg_type = reply['MsgType']
    if msg_type == 'text':
        from_user = reply['ToUserName']
        to_user = reply['FromUserName']
        msg = reply['Content']
        m = msg.split('#')
        create_time = int(time.time())

        if len(m) == 3:
            username = m[0]
            password = m[1]
            step = m[2]

            xml_from = """
                <xml>
                    <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
                    <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
                    <CreateTime>{CreateTime}</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[{Content}]]></Content>
                </xml>
                """

            if not username or not password or not step:
                xml = xml_from.format(ToUserName=to_user, FromUserName=from_user, CreateTime=create_time,
                                      Content='账号、密码和步数不能为空')
            else:
                try:
                    step = int(step)
                    if step <= 0:
                        xml = xml_from.format(ToUserName=to_user, FromUserName=from_user, CreateTime=create_time,
                                              Content='步数需要大于等于0')
                    else:
                        event = {"queryString": {"user": username.strip(), "password": password.strip(), "step": step}}
                        result = main_handler(event)
                        if result['code'] == 0:
                            xml = xml_from.format(ToUserName=to_user, FromUserName=from_user, CreateTime=create_time,
                                                  Content=result.get('data'))
                        else:
                            xml = xml_from.format(ToUserName=to_user, FromUserName=from_user, CreateTime=create_time,
                                                  Content=result.get('errorMsg'))

                except:
                    xml = xml_from.format(ToUserName=to_user, FromUserName=from_user, CreateTime=create_time,
                                          Content='步数输入错误，需是正整数')
    logger.info(xml)
    return HttpResponse(xml, content_type='application/xml')
