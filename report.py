import os
import yaml
import hoshino
from hoshino import Service, R, priv
from hoshino.typing import *
from hoshino.util import FreqLimiter, concat_pic, pic2b64, silence
from .util import report


sv = Service('health-report', enable_on_default=False, bundle='打卡初始化')


def getYmlConfig() -> dict:
    current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    file = open(current_dir, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


def writeDataToYaml(data):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    with open(current_dir, "w", encoding="UTF-8") as f:
        yaml.dump(data, f, allow_unicode=True)


@sv.on_fullmatch("填报初始化")
async def init(bot, ev):
    # if not priv.check_priv(ev, priv.SUPERUSER):
    #     msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
    #     await bot.send(ev, msg)
    #     return
    data = {
        'Info': {
            'author': 'kcqnly',
            'info': '武汉理工健康填报'
        }
    }
    writeDataToYaml(data)
    msg = '初始化成功'
    await bot.send(ev, msg)


@sv.on_prefix('添加用户')
async def addinfo(bot, ev):
    await _addinfo(bot, ev)

# 为多用户模式添加额外用户

# 添加填报用户 012xx passwd nickname


async def _addinfo(bot, ev: CQEvent):
    # 处理输入数据
    allText: str = ev.message.extract_plain_text()
    strList = allText.split(' ')
    if len(strList) < 3:
        msg = '缺少参数'
        await bot.send(ev, msg)
        return
    qq = str(ev.user_id)
    sn = strList[0]
    idCard = strList[1]
    nickName = strList[2]
    config = getYmlConfig()
    if 'users' not in config.keys():
        usersData = {
            'users': [{'user': {'sn': sn,
                                'idCard': idCard,
                                'nickName': nickName,
                                'qq': qq}}]
        }
        writeDataToYaml(usersData)
    else:
        usersData = {
            'user': {
                'sn': sn,
                'idCard': idCard,
                'nickName': nickName,
                'qq': qq
            }
        }
        config["users"].append(usersData)
        writeDataToYaml(config)
    await bot.send(ev, '添加成功')


@sv.on_fullmatch("填报用户列表")
async def allinfo(bot, ev):
    config = getYmlConfig()
    msg = '使用该打卡功能的用户有：'
    for user in config['users']:
        msg = msg + '\n' + user['user']['qq']
    await bot.send(ev, msg)


@sv.on_fullmatch("填报")
async def allinfo(bot, ev):
    qq = str(ev.user_id)
    config = getYmlConfig()
    msg = '未在用户列表中找到您'
    for user in config['users']:
        if user['user']['qq'] == qq:
            userData = user['user']
            sn = userData['sn']
            idCard = userData['idCard']
            nickName = userData['nickName']
            msg = report(sn, idCard, nickName)
            break
    await bot.send(ev, msg)


@sv.on_fullmatch("填报help")
async def allinfo(bot, ev):
    msg = """
    author：kcqnly
    [添加用户 学号 密码 微信昵称] 添加新用户
    (格式:添加用户 0121809360719 xxx kcqnly)
    """
    await bot.send(ev, msg)
