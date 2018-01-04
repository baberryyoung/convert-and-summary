import operator
import  os,sys
import argparse
import jieba
dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)
parser = argparse.ArgumentParser()
parser.add_argument('-p','--path',default='test')
parser.add_argument('-e','--entity',default='disorder')
args = parser.parse_args()
raw_data_file = os.path.join(dir,'data','rawdata',args.path)
filepath = os.path.join(dir,'data')
targets=['disorder','image_feature','pathology_feature','size']#args.entity.split(',')
def read_ann(path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
        entity = dict()

        for line in lines:
            #
            if line[0] == 'T':
                [id, annotation, content] = line.strip().split('\t')
                if ';' in annotation:
                    pass
                else:
                    [entity_type, start_index, end_index] = annotation.split(' ')
                    entity[id] = [entity_type, int(start_index), int(end_index), content]

        f.close()
        entity_list = list(entity.values())
        entity_list.sort(key=operator.itemgetter(1))#對標注的實體位置的索引從小到大排序
        return entity_list

def Load_data(data_file, operation='report'):
    entities = read_ann(data_file)
    #entities.extend(read_ann(folderdir))
    text = data_file+'\t'
    word={}
    if entities:
        for target in targets:
            word[target]=target+':'
        for i in range(len(entities)):
            if entities[i][0] in targets:
                word[entities[i][0]]+=entities[i][3]+','
        for target in targets:
            word[target] = word[target][:-1]
            text+=word[target]+'\t'

    text+='\n'
    print(text)
    write_train_file(text, operation)


def write_train_file(text,operation='report'):
    if len(text)>0:
        with open(os.path.join(filepath, operation+'.csv'),'a') as f:
            f.write(text)
            f.close()

if __name__ == '__main__':
    #if os.path.isdir(raw_data_file):
    folders = os.listdir(raw_data_file)
    for folder in folders:
        Load_data(os.path.join(raw_data_file, folder, 'record.ann'))  # train,dev,test
        print("Converting file-%s is done!" % (folder))

    '''
    for _,_,files in os.walk(raw_data_file):
        for file in files:
            if file.endswith('record.ann'):
                print("The file-%s is converting..." % file)
                Load_data(os.path.join(raw_data_file,file))#train,dev,test
                print("Converting file-%s is done!" % file)
                '''
