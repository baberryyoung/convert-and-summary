#!/usr/bin
# -*- coding=utf-8 -*-
#将入院记录，病理报告，放射报告，出院小结分开来。
#定位集中记录在原始文本中的位置，然后分割，接着将标注文件中的各个实体标记按照结束位置排序，对应各个报告的开始位置，然后计算相对位置，分别输出到文件中。
import operator
import  os,sys
import argparse
#import jieba
import math
dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)

filepath = os.path.join(dir,'data', 'rawdata')
raw_data_file = 'hjh-annotation'
#jieba.load_userdict(os.path.join(dir, 'dict','mydict.txt'))
def read_txt(path):
    text = ""
    try:
        with open(os.path.join(path, 'record.txt'), encoding='utf-8') as f:
            text = f.read()
            f.close()
    except Exception:
        return None
    return text

def read_ann(path):
    with open(os.path.join(path,'record.ann'), encoding='utf-8') as f:
        lines = f.readlines()
        entity = dict()
        rela = dict()
        for line in lines:
            #
            if line[0] == 'T':
                [id, annotation, content] = line.strip().split('\t')
                if ';' in annotation or '，' in content:
                    continue
                else:
                    [entity_type, start_index, end_index] = annotation.split(' ')
                    if ('占位' in content or '强化' in content or '影' in content or '结节' in content) and content != 'image_feature':
                        entity_type = 'image_feature'
                    entity[id] = [entity_type, int(start_index), int(end_index), content, id]
            elif line[0] =='R':
                [id, annotation] = line.strip().split('\t')
                rela_type = annotation.split(' ')[0]
                try:
                    start_entity = entity[annotation.split(' ')[1].split(':')[1]]
                    end_entity = entity[annotation.split(' ')[2].split(':')[1]]
                except Exception:
                    print('start',annotation.split(' ')[1].split(':')[1])
                    print('end',annotation.split(' ')[2].split(':')[1])
                rela[id] = [rela_type]+ start_entity + end_entity
        f.close()
        entity_list = list(entity.values())
        entity_list.sort(key=operator.itemgetter(1))#對標注的實體位置的索引從小到大排序
        return entity_list, rela

def merge_ann(data_file):
    rawtext = read_txt(data_file)
    if rawtext is None:
        return None

    try:
        dcn_index = rawtext.index('出院小结：')
    except Exception:
        dcn_index = len(rawtext)
    try:
        adn_index = rawtext.index('入院记录：')
    except Exception:
        adn_index = len(rawtext)
    try:
        ris_index = rawtext.index('数字化放射检查记录：')
    except Exception:
        ris_index = len(rawtext)

    try:
        ult_index = rawtext.index('超声检查记录：')
    except Exception:
        ult_index = len(rawtext)
    foldername = os.path.split(data_file)[1]



    entities, rela = read_ann(data_file)
    adn_entity_start_index = len(entities)
    ris_entity_start_index = len(entities)
    ult_entity_start_index = len(entities)
    dcn_entity_start_index = len(entities)

    for i in range(len(entities)):
        if ris_entity_start_index == len(entities) and entities[i][1]>=ris_index and entities[i][1]<ult_index and entities[i][1]<dcn_index:
            ris_entity_start_index = i
        elif ult_entity_start_index == len(entities) and entities[i][1]>=ult_index and entities[i][1]<dcn_index:
            ult_entity_start_index = i
        elif dcn_entity_start_index == len(entities) and entities[i][1]>=dcn_index:
            dcn_entity_start_index = i
            break
    adn_text = ''
    for entity in entities[0:min(ris_entity_start_index,ult_entity_start_index,dcn_entity_start_index)]:
        if entity:
            adn_text += entity[4]+'\t'+entity[0]+' '+str(entity[1])+' '+str(entity[2])+'\t'+entity[3]+'\n'

    ris_text=''
    for entity in entities[ris_entity_start_index:min(ult_entity_start_index,dcn_entity_start_index)]:
        if entity:
            ris_text += entity[4]+'\t'+entity[0]+' '+str(entity[1]-ris_index)+' '+str(entity[2]-ris_index)+'\t'+entity[3]+'\n'

    ult_text = ''
    for entity in entities[ult_entity_start_index:dcn_entity_start_index]:
        if entity:
            ult_text += entity[4] + '\t' + entity[0] + ' ' + str(entity[1]-ult_index) + ' ' + str(entity[2]-ult_index) + '\t' + entity[3] + '\n'

    dcn_text = ''
    for entity in entities[dcn_entity_start_index:]:
        if entity:
            dcn_text += entity[4] + '\t' + entity[0] + ' ' + str(entity[1]-dcn_index) + ' ' + str(entity[2]-dcn_index) + '\t' + entity[3] + '\n'

    try:
        if len(rawtext[0:min(ris_index, ult_index, dcn_index)]) > 5:
            write_train_file(rawtext[0:min(ris_index, ult_index, dcn_index)].strip(),
                             os.path.join(filepath, '入院记录'+raw_data_file, foldername + '.txt'))
            write_train_file(adn_text.strip(), os.path.join(filepath, '入院记录'+raw_data_file, foldername + '.ann'))
    except Exception:
        print('write error')
    try:
        if len(rawtext[ris_index:min(ult_index, dcn_index)]) > 0:
            write_train_file(rawtext[ris_index:min(ult_index, dcn_index)].strip(),
                             os.path.join(filepath, '放射报告'+raw_data_file, foldername + '.txt'))
            write_train_file(ris_text.strip(), os.path.join(filepath, '放射报告'+raw_data_file, foldername + '.ann'))

    except Exception:
        print('write error')
    try:
        if len(rawtext[ult_index:dcn_index]) > 0:
            write_train_file(rawtext[ult_index:dcn_index].strip(), os.path.join(filepath, '超声报告'+raw_data_file, foldername + '.txt'))
            write_train_file(ult_text.strip(), os.path.join(filepath, '超声报告'+raw_data_file, foldername + '.ann'))
    except Exception:
        print('write error')
    try:
        if len(rawtext[dcn_index:]) > 5:
            write_train_file(rawtext[dcn_index:].strip(), os.path.join(filepath, '出院小结'+raw_data_file, foldername + '.txt'))
            write_train_file(dcn_text.strip(), os.path.join(filepath, '出院小结'+raw_data_file, foldername + '.ann'))
    except Exception:
        print('write error')

def rela_extract(rela, gened_relas):
    reall_relas = list(rela.values())
    count = 0
    for item in gened_relas:
        if item not in reall_relas:
            item[0]='others'
        else:
            count+=1
    relas = gened_relas
    relas.sort(key=operator.itemgetter(2))
    text = ""
    print(count)
    for i in range(len(relas)):
        text += relas[i][0]+'\t' #关系类型
        text += str(relas[i][1]) + '\t' + str(relas[i][4]) + '\t'+ str(relas[i][2]) + '\t'+ str(relas[i][3]) + '\t' #源实体1类型，源实体1单词
        text += str(relas[i][5]) + '\t' + str(relas[i][8]) + '\t'+ str(relas[i][6]) + '\t'+ str(relas[i][7]) + '\t'#源实体2类型，源实体2单词
        text += str(abs(int(relas[i][2]) - int(relas[i][6]))) + '\n'#两实体开始位置的相对间隔
    write_train_file(text, os.path.join(filepath,'rela_train.txt'))
    return relas

def write_train_file(text,path):
    if os.path.isdir(os.path.split(path)[0])== False:
        os.mkdir(os.path.split(path)[0])
    with open(path,'w') as f:
            f.write(text)
            f.close()

if __name__ == '__main__':
    #if os.path.isdir(raw_data_file):
    folders = os.listdir(os.path.join(filepath,raw_data_file))
    for folder in folders:
        if '.' not in folder:
            print("The folder-%s is converting..." % folder)
            merge_ann(os.path.join(filepath,raw_data_file,folder))    #train,dev,test
            print("Converting folder-%s is done!" % folder)
