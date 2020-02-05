from aiocqhttp import CQHttp, ApiError, Event

bot = CQHttp(
    api_root='http://127.0.0.1:5700/',  # 如果使用反向 WebSocket，这里不需要传入
    access_token='123',  # 应与 CQHTTP 配置中一致，如果没填，这里不需要传入
    secret='abc',  # 应与 CQHTTP 配置中一致，如果没填，这里不需要传入
)


@bot.on_message
# 上面这句等价于 @bot.on('message')
async def handle_msg(event: Event):
    try:
        # await bot.send_private_msg(user_id=event.user_id,
        #                            message='你好呀，下面一条是你刚刚发的：')
        # 上下两句等价
        await bot.send(event, '你好呀，下面一条是你刚刚发的：')
    except ApiError:
        pass

    # 返回给 CQHTTP 插件，走快速回复途径
    return {'reply': event.message, 'at_sender': False}


@bot.on_notice('group_increase')
# 上面这句等价于 @bot.on('notice.group_increase')
async def handle_group_increase(event: Event):
    info = await bot.get_group_member_info(group_id=event.group_id,
                                           user_id=event.user_id)
    nickname = info['nickname']
    name = nickname if nickname else '新人'
    await bot.send(event, message=f'欢迎{name}～',
                   at_sender=True, auto_escape=True)


@bot.on_request('group', 'friend')
# 上面这句等价于 @bot.on('request.group', 'request.friend')
async def handle_group_request(event: Event):
    if event.comment != 'some-secret':
        # 验证信息不符，拒绝
        return {'approve': False, 'reason': '你填写的验证信息有误'}
    return {'approve': True}


if __name__ == '__main__':
    bot.run(host='127.0.0.1', port=8080)
