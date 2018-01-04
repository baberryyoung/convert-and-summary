import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os,sys
import csv
dir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)

data = pd.read_csv(os.path.join(dir,"data","出院小结.txt"), delimiter='\t', quoting=csv.QUOTE_NONE, skip_blank_lines=False, header=None,names=["word", "label"])

labelcount = {label:len(list(filter(lambda x:x == label ,data['label']))) for label in list(set(data['label']))}
print (labelcount)

plt.figure(figsize=(10, 8))
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.03*height, '%s' % float(height))


#plt.title(u"")
plt.ylim(0,max(labelcount.values())+1000)
plt.xlim(-0.5,len(labelcount))
plt.xticks(range(len(labelcount)),labelcount.keys())
rect = plt.bar(left = range(len(labelcount)),height = labelcount.values(),width = 0.5,align="center",color='g')

#plt.legend((rect,),(u"图例",))
autolabel(rect)
plt.savefig('test.jpg')#保存统计图
plt.show()