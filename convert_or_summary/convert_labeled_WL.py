#!/usr/bin
# -*- coding=utf-8 -*-
import operator
import  os,sys
import argparse
import jieba
dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)
parser = argparse.ArgumentParser()
parser.add_argument('-o','--operation',default='出院小结hjh-annotation')
args = parser.parse_args()
raw_data_file = os.path.join(dir,'data','rawdata',args.operation)
filepath = os.path.join(dir,'data')

def read_ann(path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
        entity = dict()

        for line in lines:
            #
            if line[0] == 'T':
                [id, annotation, content] = line.strip().split('\t')
                if ';' in annotation or ';' in content or '、' in content or '，' in content:
                    continue
                else:
                    [entity_type, start_index, end_index] = annotation.split(' ')
                    #if entity_type not in ['number','size','person','time_point','period']:
                        #entity_type = 'others'
                    entity[id] = [entity_type, int(start_index), int(end_index), content]

        f.close()
        entity_list = list(entity.values())
        entity_list.sort(key=operator.itemgetter(1))#對標注的實體位置的索引從小到大排序
        return entity_list

def read_txt(path):
    text = ""
    try:
        with open(path , encoding='utf-8') as f:
            text = f.read()
            f.close()
    except Exception:
        return None
    return text

def merge_ann(data_file, operation = args.operation):
    rawtext = read_txt(data_file+'.txt')
    if rawtext is None:
        return None
    entities = read_ann(data_file+'.ann')
    annote = list()
    last_end_index = 0
    interval_text=''
    for i in range(len(entities)):
        interval_text = rawtext[last_end_index:entities[i][1]].replace('\n','。')
        if len(interval_text)>1:
            words = " ".join(jieba.cut(interval_text, HMM=True))
            print(words)
            for word in words.split(" "):
                annote.append(word+'\tothers')
        elif len(interval_text)== 1 and interval_text not in ['\n','\t']:
            annote.append(interval_text + '\tothers')
        else:
            print(interval_text)
        #annote.extend((int(entities[i][1]) - last_end_index) * ['others'])
        #word_len = int(entities[i][2]) - int(entities[i][1])
        if entities[i][0]:# in ['disorder','body_location','test','drug','operation','test_result']:
            annote.append(entities[i][3]+'\t'+entities[i][0])
        else:
            annote.append(entities[i][3] + '\tothers')
        last_end_index = int(entities[i][2])

    #rela_extract(rela, gened_rela)
    interval_text = rawtext[last_end_index:len(interval_text)].replace('\n','。')
    if len(interval_text) > 1:
        words = " ".join(jieba.cut(interval_text, HMM=True))
        print(words)
        for word in words.split(" "):
            annote.append(word + '\tothers')
    elif len(interval_text) == 1:
        annote.append(interval_text + '\tothers')
    else:
        print(interval_text)
    text=''
    for i in range(len(annote)):
        text+=annote[i]+'\n'
    write_train_file(text, operation)
    return text

def Load_data(data_file, operation='train'):
    entities = read_ann(data_file)
    #entities.extend(read_ann(folderdir))
    if entities:
        text=''
        for i in range(len(entities)):
            text+=entities[i]['text']+'\t'+entities[i]['label']+'\n'
        write_train_file(text, operation)


def write_train_file(text,operation):
    if len(text)>0:
        with open(os.path.join(filepath, operation+'.txt'),'a') as f:
            f.write(text)	
            f.close()

if __name__ == '__main__':
    #if os.path.isdir(raw_data_file):
    for _,_,files in os.walk(raw_data_file):
        for file in files:
            print("The file-%s is converting..." % file)
            merge_ann(os.path.join(raw_data_file,file.split('.')[0]))#train,dev,test
            print("Converting file-%s is done!" % file)
