#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import re
import datetime
from itertools import cycle
from collections import Counter
import pymorphy2

with open("./static/stop_words.txt", "r") as f:
     stop_words = f.read().splitlines()

with open("./static/stopmat.txt", "r") as f:
     stop_mat = f.read().splitlines() 

def extdata():
    data_msg_list = []
    set_of_senders = set()
    service_words = ['изменил', 'добавил', 'удалил', '\n']
    serv_commands_list = []
    with open(datafile, 'r') as f:
        for i in f:
            msg_date, sep, msg = i.partition(" - ")
            raw_date, sep, time = msg_date.partition(", ")
            
            try:
                dt = datetime.datetime.strptime(raw_date, "%d.%m.%Y").date()
            except:
                dt = ("no date") # check date - if not date then it is a copypaste sequence
            if dt != "no date":
                sender, sep, content = msg.partition(": ")
                if  any(word in sender for word in service_words): 
                    serv_commands_list.append(sender) # service messages
                else:
                    set_of_senders.add(sender.strip('\u202a \u202c+'))
                    data_msg_list.append([sender.strip('\u202a \u202c+'), content.strip(), dt, time]) #.replace(u'\xa0', u' ')

    mesage_data = {}
    for sender in set_of_senders:
        sh = {
           "Night": 0,
           "Morning": 0,
           "Afternoon": 0,
           "Evening": 0
                  }        
        posts_by_dt =[]
        msg_shifts =[]
        sentences =[]
        shifts = []
       
        for mesage in data_msg_list:
            if sender == mesage[0]:
                posts_by_dt.append(mesage[2])
                sentences.append(mesage[1])
                # shifts
                hour = int(mesage[3].split(":")[0])
                if hour >= 0 and hour <= 6:
                    sh["Night"] += 1
                
                elif hour > 6 and hour <= 11:
                    sh["Morning"] += 1
                
                elif hour > 11 and hour <= 17:
                    sh["Afternoon"] += 1
                
                elif hour > 17 and hour <= 23:
                    sh["Evening"] += 1 
        mesage_data[sender] = sorted(Counter(posts_by_dt).items()), sentences, list(sh.items())  
       
    return mesage_data                        

def new_dir(sender):

    path = ("./static/data_by_senders/%s" % (sender))
    if os.path.exists(path):    
        for (p,d,f) in os.walk(path, False):
            (os.remove(os.path.join(p, file_name)) for file_name in f)
            (os.rmdir(os.path.join(p,dir_name)) for dir_name in d)
    else:
        os.mkdir(path)

#def count_messages_per_weekday(data_msg_list):
    
    #senders_days = [(i[0]+";"+i[2].strftime("%A")) for i in data_msg_list[0]]  
 
     
    #all_days = Counter(senders_days)
    #for i in all_days:
        #print(i)
    #print(all_days)
    #nnn = all_days.most_common()
    #for i in nnn:
        #string1 = (" ".join(i[0].split(";")), str(i[1]))
        #string2 = " ".join(string1)

#---------WORDS-STATS---------------------------------------------------
def words_stats(sender, f_content):

    morph = pymorphy2.MorphAnalyzer()
  
         
    servs_words  = {
        'media_files':0,
        'links':0
                  }
    for sent in f_content: # count mediafiles amd http(s) hrefs
        if sent == '<Файл пропущен>':
            servs_words["media_files"] += 1
        if 'http' in sent:
            servs_words["links"] += 1
    f_clear = [x.replace(u'\xa0', u' ') for x in f_content if x !='<Файл пропущен>' and 'http' not in x ]   

    sents_with_bad = [s for x in stop_mat for s in f_clear if x in s] # bad words in stentence
    bad_sent_ind = round(100*len(sents_with_bad)/len(f_clear))

    all_strings = "".join(f_clear)
    all_symbols = str(len(all_strings))
    words_list_raw = (" ".join(f_clear).split(" ")) 
    
    words_with_bad = [s for x in stop_mat for s in words_list_raw if x in s] # bad words in all words
    bad_word_ind = round(100*len(words_with_bad)/len(words_list_raw))
    bad_index = bad_sent_ind + bad_word_ind
    
    
    words_list = [re.sub('[\W\d]', '', x.lower().rstrip(".")) for x in words_list_raw if len(x) >= 3] # clear from symbols and cut 1-2 len words
    words_list = list(filter(None, words_list)) # delete empty elements
    
    w_list = [x for x in words_list if x not in stop_words] # clear_stop_words

    w_list_10 = [[ x, len(x)] for x in sorted(w_list, key=len, reverse=True)][0:10]
    words_avg_len = round(len(all_strings)/len(words_list))
    
    normalize_words = [morph.parse(x)[0].normal_form for x in  w_list] # Get normal form for words
    count_words = list(Counter(w_list).most_common())
    
    return servs_words, [str(len(all_strings)), str(len(words_list)),\
                         str(words_avg_len), bad_index],\
                         w_list_10, count_words[0:20] 

def json_writer(sender, filename, data_list):
    
    date_handler = lambda obj: (  
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else obj
    ) 
 
    path = ("./static/data_by_senders/%s" % (sender))
    with open("%s/%s" % (path, filename), "w") as file_to_write:
        file_to_write.write(json.dumps(data_list, default=date_handler, ensure_ascii=False))
    file_to_write.close()

def create_sender_files(message_data):
    
    sender_mesg_data = {}
    for sender, content in message_data.items():
        new_dir(sender)
        json_writer(sender,"all_data.json", content)
        json_writer(sender,"posts_by_date.json", content[0]) 
        json_writer(sender,"posts_by_shifts.json", content[2])     
        json_writer(sender,"sentences.json", content[1])
        
        word_stats_list = words_stats(sender, content[1])
        
        sender_mesg_data[sender] = word_stats_list[0],\
                                   word_stats_list[1],\
                                   word_stats_list[2],\
                                   word_stats_list[3]

    return sender_mesg_data

def stats_in_one(arr):
    import operator
    trash = {}
    bad = {}
    freq = {}
    all_symbols = 0
    data = arr.items()
    
    for sender, content in data:
        all_symbols += int(content[1][0])
    
    for sender, content in data:
        trash[sender] =  int(sum(content[0].values()))
        freq[sender] = round(100*int(content[1][0])/all_symbols, 2)
        bad[sender] = int(content[1][3])
        
    sorted_x = sorted(trash.items(), key=operator.itemgetter(1), reverse=True)
    sorted_y = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
    sorted_z = sorted(bad.items(), key=operator.itemgetter(1), reverse=True)
    all_user_data = [sorted_x, sorted_y, sorted_z]     
    #print(sorted(trash.values(), reverse=True), trash.keys())     
   #newlist = sorted(trash, key=lambda k: k['name']) 
    return arr, all_user_data

#logname = "WP_FEBR.txt" 
 
def main(logname):
    global datafile
    datafile = "./uploads/%s" % logname

    return (stats_in_one(create_sender_files(extdata())))
       
    os.remove(datafile)
          
if __name__ == '__main__':
    import sys
    sys.exit(main(logname))
