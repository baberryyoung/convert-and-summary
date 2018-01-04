#!/usr/bin
# -*- coding=utf-8 -*-
import operator
import  os,sys
import argparse
import re
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
                    if entity_type not in ['number','size','person','time_point','period']:
                        entity_type = 'others'
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
        pattern = re.compile(''.re.M|re.I)
        date = re.finditer(pattern,text)

    except Exception:
        return None
    return text

if __name__ == '__main__':
    #if os.path.isdir(raw_data_file):
    for _,_,files in os.walk(raw_data_file):
        for file in files:
            print("The file-%s is converting..." % file)
            (os.path.join(raw_data_file,file.split('.')[0]))#train,dev,test
            print("Converting file-%s is done!" % file)
