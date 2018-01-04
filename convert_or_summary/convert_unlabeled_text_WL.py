#!/usr/bin
# -*- coding=utf-8 -*-
import operator
import  os,sys
import argparse
import jieba
dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)
jieba.load_userdict(os.path.join(dir,'dict','mydict.txt'))
raw_data_file = os.path.join(dir,'data','20170828complete')
filepath = os.path.join(dir,'data')

def seg_text(path):
    candi_entity = ''
    file=os.path.join(path, 'record.txt')
    if os.path.exists(file):
        with open(file, encoding='utf-8') as f:

            text = f.read()
            for word, start, end in jieba.tokenize(text, HMM=True):
                candi_entity += word+'\t'+str(start)+'\t'+str(end)+'\n'
            write_to_file(candi_entity,path)
    return candi_entity


def write_to_file(text,path=filepath):
    if not os.path.exists(os.path.join(path,'candidate_predict')):
        os.mkdir(os.path.join(path,'candidate_predict'))
        _,foldername = os.path.split(path)
    with open(os.path.join(filepath,'candidate_predict',foldername+'_candi_entity.txt'),'w') as f:
        f.write(text)
        f.close()

if __name__ == '__main__':
    #if os.path.isdir(raw_data_file):
    folders = os.listdir(raw_data_file)
    for folder in folders:
        print("The folder-%s is converting..." % folder)
        seg_text(os.path.join(raw_data_file,folder))#train,dev,test
        print("Converting folder-%s is done!" % folder)