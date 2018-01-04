#!/usr/bin
# -*- coding=utf-8 -*-
import operator
import  os,sys
import argparse
import re
dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)
parser = argparse.ArgumentParser()
parser.add_argument("-s","--source_path", help="the path of the rawdata file",default ="data/rawdata/")
parser.add_argument("-d","--dest_path", help="the path to save file",default="data/")
parser.add_argument("-o","--operation", help="the operation type of this dataset used for(train/dev/test)", default="train")
args = parser.parse_args()
filepath = os.path.join(dir,args.dest_path)
raw_data_file = os.path.join(dir,args.source_path, args.operation)
def read_txt(path):
    with open(path + '.txt', encoding='utf-8') as f:
        text = f.read()
        f.close()
        return text

def read_ann(path):
    with open(path + '.ann', encoding='utf-8') as f:
        lines = f.readlines()
        entity = list()
        for line in lines:
            #
            if line[0] == 'T':
                [id, annotation, content] = line.split('\t')
                if ';' in annotation:
                    pass
                else:
                    [entity_type, start_index, end_index] = annotation.split(' ')

                entity.append([entity_type, int(start_index), int(end_index), content])
        f.close()
        entity.sort(key=operator.itemgetter(1))#對標注的實體位置的索引從小到大排序
        return entity

def merge_ann(data_file, operation):
    rawtext = read_txt(data_file)
    entities = read_ann(data_file)
    annote = list()
    last_end_index = 0
    for i in range(len(entities)):
        annote.extend((int(entities[i][1]) - last_end_index) * ['others'])
        word_len = int(entities[i][2]) - int(entities[i][1])
        if entities[i][0] in ['test','test_result','body_location','operation','drug','negation','disorder']:
            if word_len > 1:
                annote.extend([entities[i][0]+'-B'])
                annote.extend((word_len-2) * (['others']))
                annote.extend([entities[i][0] + '-E'])
            else:
                annote.extend([entities[i][0] + '-S'])
        else:
            annote.extend((word_len) * (['others']))
        last_end_index = int(entities[i][2])
    annote.extend((len(rawtext) - last_end_index) * ['others'])

    text=''
    for i in range(len(rawtext)):
        text+=rawtext[i]+'\t'+annote[i]+'\n'
    write_train_file(text, operation)
    sentence_num = len(re.sub("。+","。",rawtext.replace('\n','。')).split('。'))
    return text, sentence_num

def write_train_file(text,operation):
    if len(text)>0:
        with open(filepath + operation+'-3.txt','a') as f:
            f.write(text)
            f.close()



if __name__ == '__main__':
    #if os.path.isdir(raw_data_file):
    folders = os.listdir(raw_data_file)
    total_sentences = 0
    count = 0
    for folder in folders:
        _, sentence_num = merge_ann(os.path.join(raw_data_file, folder, 'record'), args.operation)  # train,dev,test
        print("Converting file-%s is done!,num of sentences is %d" % (folder, sentence_num))
        total_sentences += sentence_num
        count += 1
    print('total num of sentences:%d' % total_sentences)

    '''
        for _,_,files in os.walk(raw_data_file):
            sentence_num = 0
            for file in files:
                print("The file-%s is converting..." % file)
                _, sentence_num = merge_ann(os.path.join(raw_data_file,file.split('.')[0]), args.operation)#train,dev,test
                print("Converting file-%s is done!,num of sentences is %d" % (file,sentence_num))
                total_sentences += sentence_num
                count += 1
        print('total num of sentences:%d'%total_sentences)
        '''