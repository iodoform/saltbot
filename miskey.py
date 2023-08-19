import asyncio
from misskey import Misskey
import random
import re
import datetime
import websockets
import json

def SpreadSalt():
    offset = ""
    salt = ""
    particleList = [" "," "," ","★","☆",".",".",".","。","。","。","゜","゜","゜","゜","*","*","*","°","°","°","・","・","・"]
    for i in range(10):
        for j in range(random.randint(5,10)):
            salt+=(particleList[random.randint(0,23)])
        for k in range(random.randint(-1,2)):
            offset+=" "
        salt+=("\n"+offset)
    return salt

def Kanji2Hiragana(string:str):
    return string.replace("撒","ま").replace("塩","しお")

#トークンを準備
with open("./TOKEN.txt","r") as f:
    TOKEN = f.read()
msk = Misskey('misskey.io', i=TOKEN)
MY_ID = msk.i()['id']
WS_URL='wss://misskey.io/streaming?i='+TOKEN
#定期投稿用の変数
hasSendMin = False
#noteの送受信
async def runner():
    global hasSendMin
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({
            "type": "connect",
            "body": 
            {
                "channel": "main",
                "id": "test"
            }
        }))
        
        while True:
            dt_now = datetime.datetime.now()
            #定期投稿
            if(dt_now.minute==0 and not hasSendMin):
                #塩撒きノートを投稿
                msk.notes_create(text=f"タイムラインに塩を撒いておきますね．\n{SpreadSalt()}")
                hasSendMin = True
            if(dt_now.minute==1):
                hasSendMin = False

            data = json.loads(await ws.recv())
            #通知をチェックして投稿
            try:
                type =data['body']['type']
            except KeyError as e:
                continue
            if type== "mention":
                print(f"メンションが来ました．{dt_now}")
                await on_note(data['body']['body'])

async def on_note(note):
    if(bool(re.search(Kanji2Hiragana('塩.*((撒いとけ)|(撒いておけ)|(撒いてください)|(撒いておいてください)|(撒け)|(撒いて))'),Kanji2Hiragana(note["text"])))):
        print("塩をまきます")
        msk.notes_create(text=f"タイムラインに塩を撒いておきますね．\n{SpreadSalt()}",reply_id=note['id'],visible_user_ids=[note['userId']])
        #ログ
        with open("./log.txt","a") as f:
            f.write(f"username:{note['user']['username']} noteid:{note['id']} date time:{datetime.datetime.now()}\n")

asyncio.get_event_loop().run_until_complete(runner())