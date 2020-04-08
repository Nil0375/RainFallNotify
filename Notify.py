#coding: utf-8
import telegram.ext
from telegram.ext import Updater, CommandHandler,MessageHandler, Filters, CallbackQueryHandler,ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import RainFallInfo as rain
#from time import sleep
import time
import json
import uuid
import logging
import datetime
#logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO ,filename='RainFall_Bot-'+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+'.log')

APIKey=''

root_logger= logging.getLogger()
root_logger.setLevel(logging.INFO) # or whatever
handler = logging.FileHandler('log/RainFall_Bot-'+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+'.log', 'w', 'utf-8') # or whatever
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')) # or whatever
root_logger.addHandler(handler)

try:
    logging.info('OPEN AlertData')
    file=open('AlertData.json',mode='r')
    
except FileNotFoundError :
    logging.warning('AlertData FileNotFound')
    alert={'list':[]}
except Exception as e:
    logging.error('Unknown Error:['+e.__class__.__name__+'] '+e.args[0])
    alert={'list':[]}
else:
    logging.info('OPEN AlertData Successful')
    alert=json.loads(open('AlertData.json',mode='r').read())
    file.close()


globalrain = rain.RainFall()


updater = Updater(APIKey, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    logging.info('Chat_id:{} Use_command:start'.format(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome!!\n感謝使用本系統 \n\n指令列表: \
                                                                        \n  /start :\n        顯示歡迎資訊及指令列表\
                                                                        \n  /search [地區名稱] :\n        搜尋該地區的鄉鎮或是觀測站\
                                                                        \n  /search_info [觀測站] :\n        搜尋觀測站的詳細資訊\
                                                                        \n  /list :\n        列出個人所有的警報\
                                                                        \n  /del [編號] :\n        刪除警報(編號可從/list中取得)\
                                                                        \n  /set_up [觀測站] [時雨量] :\n        設定警報\
                                                                        \n\n\n版本:1.1.0(Beta)")
    
def stop (update, context):
    logging.warning('Chat_id:{} Use_command:stop'.format(update.effective_chat.id))
    if(update.effective_chat.id==584142770):
        logging.warning('======Rain Fall Bot Stop======')
        updater.stop()
   
def info(update, context):
    #print(update.effective_chat.id)
    logging.info('Chat_id:{} Use_command:info'.format(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text='update_id:'+str(update.update_id)+'\nmessage_id:'+str(update.message.message_id)+'\nForm_user_id:'+str(update.message.from_user.id)+'\nChat_id:'+str(update.message.chat.id)+'\nChat_type:'+str(update.message.chat.type))
def ls(update, context):
    logging.info('Chat_id:{} Use_command:list'.format(update.effective_chat.id))
    global alert
    idcache=str(update.effective_chat.id)
    cache='個人所有警報:\n\n'
    logging.debug('Chat_id:{}\n alert:{} \n alert[idcache][list]:{}'.format(idcache,alert,alert[idcache]['list']))
    for i,j in zip(alert[idcache]['list'],range(1,len(alert[idcache]['list'])+1)):
        cache = cache+str(j)+":\n    觀測站:"+alert[idcache][i]['platform']+'\n    警報降雨量:'+str(alert[idcache][i]['alert'])+'\n'
    logging.debug('Chat_id:{}\n list_text:{} '.format(idcache,cache))
    context.bot.send_message(chat_id=update.effective_chat.id,text=cache)
def search(update, context):
    logging.info('Chat_id:{} Use_command:search'.format(update.effective_chat.id))
    region = (update.message.text).split()[1].replace('台', '臺')
    #print(update.message.text)
    #region = context.args[0]
    re,data=globalrain.FindRegion(region)
    logging.info('Chat_id:{} 查詢地區:{} 查詢結果:{}'.format(update.effective_chat.id,region,re))
    if(re):
        result ='----區 域----\t 觀測站'
        for i in range(len(data)):
            for j in range(i,len(data)):
                if(data[i]>data[j]):
                    cache = data[i]
                    data[i]=data[j]
                    data[j]=cache
        for i in data:
            result=result+'\n'+i
        #print(result)
        context.bot.send_message(chat_id=update.effective_chat.id, text=result)
    else: context.bot.send_message(chat_id=update.effective_chat.id, text="❌查詢錯誤❌")
def set_up(update, context):
    parameter = (update.message.text).split()
    logging.info('Chat_id:{} Use_command:set_up Parameter:{}'.format(update.effective_chat.id,parameter))
    if(len(parameter)==3):
        try:
            int(parameter[2])
        except  ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="❌參數錯誤❌")
            logging.warning('Chat_id:{} Parameter:{} message={}'.format(update.effective_chat.id,parameter,"❌參數錯誤❌"))
        else:
                re=globalrain.FindPlatform(parameter[1])
                #print(parameter)
                if(re==True):
                    cache = '時雨量警報設定: \n\n 觀測站:'+parameter[1] + '\n 警報時雨量:' + str(parameter[2])
                    context.bot.send_message(chat_id=update.effective_chat.id, text=cache,reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(str(ans), callback_data = '{} {} {}'.format(ans,update.effective_chat.id,' '.join(parameter[1:3])))for ans in ['Yes','No']]]))
                    #alert.append([update.effective_chat.id,parameter[0],parameter[1]])
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="❌觀測站名稱錯誤❌")
                #context.bot.send_message(chat_id=update.effective_chat.id, text=)
    else : context.bot.send_message(chat_id=update.effective_chat.id, text="❌參數錯誤❌")
    return 0
def set_up_check(update, context):
    global alert
    #print( update.callback_query.data.split())
    data=update.callback_query.data.split()
    logging.info('Chat_id:{} set_up_check Data:{}'.format(update.effective_chat.id,data))
    #print(data)
    if(data[0]=='Yes'):
        if(alert['list'].count(data[1])==0):
            alert['list'].append(data[1])
        
        alert[data[1]]=alert.setdefault(data[1],{})
        alert[data[1]]['list']=alert[data[1]].setdefault('list',[])
        uuidcache=str(uuid.uuid1())
        alert[data[1]]['list'].append(uuidcache)
        #'chat_id':data[1],
        alert[data[1]][uuidcache]={'platform':data[2],'alert':int(data[3]),'alerttime':'2020-01-01T00:00:00+08:00'}
        logging.info(json.dumps(alert, sort_keys=True, indent=4, separators=(',', ': ')))
        open('AlertData.json',mode='w').write(json.dumps(alert, sort_keys=True, indent=4, separators=(',', ': ')))
        update.callback_query.edit_message_text('✅設定成功✅!!')
    else:
        update.callback_query.edit_message_text('設定取消!!')
def search_info(update, context):
    parameter = (update.message.text).split()
    logging.info('Chat_id:{} Use_command:search_info Parameter:{}'.format(update.effective_chat.id,parameter))
    context.bot.send_message(chat_id=update.effective_chat.id, text='觀測站:'+parameter[1]+'\n'+globalrain.GetPlatformInfo(parameter[1]))
def delete(update, context):
    global alert
    parameter = (update.message.text).split()
    logging.info('Chat_id:{} Use_command:del Parameter:{}'.format(update.effective_chat.id,parameter))
    if (len(parameter)>1):
        try:
            parameter[1] = int(parameter[1])-1
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="❌參數錯誤❌")
        else :
            idcache=str(update.effective_chat.id)
            uuidcache=alert[idcache]['list'][parameter[1]]
            cache = '時雨量警報刪除: \n\n 觀測站:'+alert[idcache][uuidcache]['platform'] + '\n 警報時雨量:' + str(alert[idcache][uuidcache]['alert'])
            context.bot.send_message(chat_id=update.effective_chat.id, text=cache,reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(str(ans), callback_data = '{} {} {} {}'.format(ans,update.effective_chat.id,uuidcache,parameter[1]))for ans in ['Yes','No']]]))
            #context.bot.send_message(chat_id=update.effective_chat.id, text=cache,reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(str(ans), callback_data = '{} {} {}'.format(ans,update.effective_chat.id,' '.join(parameter[1:3])))for ans in ['Yes','No']]]))
            
    else:context.bot.send_message(chat_id=update.effective_chat.id, text="❌參數錯誤❌")
    return 1 
def del_check(update, context):
    
    global alert
    data=update.callback_query.data.split()
    logging.info('Chat_id:{} del_check Data:{}'.format(update.effective_chat.id,data))
    if(data[0]=='Yes'):
        alert[data[1]].pop(data[2])
        alert[data[1]]['list'].pop(int(data[3]))
        open('AlertData.json',mode='w').write(json.dumps(alert, sort_keys=True, indent=4, separators=(',', ': ')))
        update.callback_query.edit_message_text('✅刪除成功✅!!')
    else:
        update.callback_query.edit_message_text('刪除取消!!')
#def test(update,context):
    #print(Filters.update.message)
    #context.bot.send_message(chat_id=update.effective_chat.id, text=Filters.reply)
def nocommand(update, context):
    logging.info('Chat_id:{} Nocommand message:{}'.format(update.effective_chat.id,update.message.text))
    context.bot.send_message(chat_id=update.effective_chat.id, text="❌輸入錯誤❌")               

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('stop', stop))
dispatcher.add_handler(CommandHandler('info',info))
dispatcher.add_handler(CommandHandler('list',ls))
dispatcher.add_handler(CommandHandler('search',search))
#dispatcher.add_handler(CommandHandler('test',test))
set_up_handler = ConversationHandler(
    entry_points=[CommandHandler('set_up',set_up)],
    states={
        0:[CallbackQueryHandler(set_up_check)]
    },
    fallbacks=[CommandHandler('set_up',set_up)]
)
dispatcher.add_handler(set_up_handler)
dispatcher.add_handler(CommandHandler('search_info',search_info))
del_handler = ConversationHandler(
    entry_points=[CommandHandler('del',delete)],
    states={
        1:[CallbackQueryHandler(del_check)]
    },
    fallbacks=[CommandHandler('del',delete)]
)
dispatcher.add_handler(del_handler)

#updater.dispatcher.add_handler(CallbackQueryHandler(answer))


dispatcher.add_handler(MessageHandler(Filters.text, nocommand))

job = updater.job_queue
#-----use RainFallInfo-----
"""def alert_job(context: telegram.ext.CallbackContext):
    global alert
    logging.info('======Alert Job Start======')
    globalrain.RefreshData()
    for i in alert['list']:
        for j in alert[i]['list']:
            rainfallcache=globalrain.GetRainFallData(alert[i][j]['platform'])
            logging.info('Alert Job: alert[{}][{}]:{} GetRainFall:{} SetRainFall:{}'.format(i,j,alert[i][j],rainfallcache[2],alert[i][j]['alert']))
            if(rainfallcache[2]>=alert[i][j]['alert'] and alert[i][j]['alerttime']!=globalrain.GetRainFallUpdateTime() ):
                textcache = '⚠️警告⚠️ ⚠️警告⚠️\n\n地區: '+rainfallcache[0] + '\n觀測站: '+rainfallcache[1]+'\n時雨量: '+str(rainfallcache[2])+'\n\n雨量單位:毫米(mm)\n資料更新時間:\n'+ str(globalrain.GetRainFallUpdateTime())
                context.bot.send_message(chat_id=int(i),text=textcache)
                alert[i][j]['alerttime']=globalrain.GetRainFallUpdateTime()
                logging.info('Alert Job: chat_id:{} GetRainFall:{} SetRainFall:{} SenD Successful'.format(i,rainfallcache[2],alert[i][j]['alert']))
                time.sleep(0.03)
    open('AlertData.json',mode='w').write(json.dumps(alert, sort_keys=True, indent=4, separators=(',', ': ')))    
    logging.info('======Alert Job Stop======')"""
#-----use RainFallInfo_json
def alert_job(context: telegram.ext.CallbackContext):
    global alert
    logging.info('======Alert Job Start======')
    globalrain.RefreshData()
    for i in alert['list']:
        for j in alert[i]['list']:
            rainfallcache=globalrain.GetRainFallData(alert[i][j]['platform'])
            logging.info('Alert Job: alert[{}][{}]:{} GetRainFall:{} SetRainFall:{}'.format(i,j,alert[i][j],rainfallcache[2],alert[i][j]['alert']))
            if(rainfallcache[2]>=alert[i][j]['alert'] ):
                lastalerttime=datetime.datetime.strptime(alert[i][j]['alerttime'], "%Y-%m-%dT%H:%M:%S+08:00").replace(second=0, minute=0)
                latesttime=datetime.datetime.strptime(globalrain.GetRainFallUpdateTime() , "%Y-%m-%dT%H:%M:%S+08:00").replace(second=0, minute=0)
                if((lastalerttime-latesttime).seconds>=3600):
                    textcache = '⚠️警告⚠️ ⚠️警告⚠️\n\n地區: '+rainfallcache[0] + '\n觀測站: '+rainfallcache[1]+'\n時雨量: '+str(rainfallcache[2])+'\n\n雨量單位:毫米(mm)\n資料更新時間:\n'+ str(globalrain.GetRainFallUpdateTime())
                    context.bot.send_message(chat_id=int(i),text=textcache)
                    alert[i][j]['alerttime']=globalrain.GetRainFallUpdateTime()
                    logging.info('Alert Job: chat_id:{} GetRainFall:{} SetRainFall:{} SenD Successful'.format(i,rainfallcache[2],alert[i][j]['alert']))
                    time.sleep(0.03)
    open('AlertData.json',mode='w').write(json.dumps(alert, sort_keys=True, indent=4, separators=(',', ': ')))    
    logging.info('======Alert Job Stop======')

job_10minute_alert=job.run_repeating(alert_job,interval=540, first=0)

logging.info('======Rain Fall Bot Start======')
updater.start_polling()
updater.idle()