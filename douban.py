# -*- coding: utf-8 -*-
import urllib2
import re
import time

#抓取豆瓣电影标签
f=urllib2.urlopen('http://movie.douban.com/tag/?view=cloud').read()
n1=f.find('007')
n2=f.find('宗教')        #n1是第一个标签，n2是第二个标签，利用这两个标签定位标签们在f中的位置
f1=f[(n1-4):(n2+10)]    #去掉标签旁边的杂质
f2=re.findall('\>\S{1,}?\<',f1)         #初步抓取标签
movie_tags=[]   #movie_tags为电影标签
for n in f2:
    n=n[1:-1]
    movie_tags.append(n)

#抓取每个标签打开后的网页地址
class Movie_list:
    def __init__(self):
        self.url1='http://movie.douban.com/tag/' 
    def request_open(self,n1,n2): #n1是标签list中的序号，n2是页码
        self.url2='?start='+str(n2*20)+'&type=T'
        self.page1=urllib2.urlopen(self.url1+movie_tags[n1]+self.url2).read()
        return self.page1 #点击标签打开后的页面地址
        
    

#抓取电影列表的页码数
class Next_page:
    def __init__(self):
        self.url1='http://movie.douban.com/tag/'
    def np(self,n1):
        self.page1=urllib2.urlopen(self.url1+movie_tags[n1]).read()
        self.url2=re.findall('amp.*\d{1,2}',self.page1)
        if self.url2:
            self.num2=self.url2[-1][13:]
            if int(self.num2)<50 or int(self.num2)==50:
                return int(self.num2)
            else:
                return 50       #电影列表页数超过50页则只扫描前50页
        else:
            return 1

movie_list=Movie_list()
movie=[]


#抓取电影信息（名字，评价人数，排名，地址）
class Movie_info:
    def __init__(self):
        pass
    def m(self,n1,n2):
    # 抓取每部电影的电影名称
        self.movie_name2=[]
        self.movie_name1=re.findall('title="\S{1,}?"',movie_list.request_open(n1,n2))
        for x in range(len(self.movie_name1)-1):
            self.movie_name2.append(self.movie_name1[x][7:-1]) 
    
    # 抓取每部电影的评价人数
        self.movie_comment2=[]
        self.movie_comment1=re.findall('span class=\"pl.*评价|span class=\"pl.*上映',movie_list.request_open(n1,n2))
        for s in self.movie_comment1:
            if re.findall('\d{1,}',s):
                self.movie_comment2.append(re.findall('\d{1,}',s)[0])
            else:
                self.movie_comment2.append('0')

    # 抓取每部电影的评分
        self.movie_rating2=[]
        self.movie_rating1=re.findall('class=\"star clearfix[\s\S]*?pl',movie_list.request_open(n1,n2))
        for s in self.movie_rating1:
            self.p2=re.findall('\d\.\d',s)
            if self.p2:
                self.movie_rating2.append(self.p2[0])
            else:
                self.movie_rating2.append('没有评分')    

    # 抓取每部电影的链接
        self.movie_url2=[]
        self.n=0
        self.movie_url1=re.findall('http://movie.douban.com/subject/\d{1,10}',movie_list.request_open(n1,n2))
        for i in range(len(self.movie_url1)/2):
            self.movie_url2.append(self.movie_url1[2*self.n])
            self.n+=1   

 # 把每部电影的4个信息合并成一个list--self.dic，再依次存到movie这个大list中
        for i in range(len(self.movie_name2)):
            self.dic=[]                                        #用self.dic暂时存储电影信息
            self.dic.append(self.movie_name2[i])               #名字
            self.dic.append(self.movie_comment2[i])            #评价人数
            self.dic.append(self.movie_rating2[i])             #评分
            self.dic.append(self.movie_url2[i])                #地址
            if int(self.dic[1])>25000:    #评价人数少于25000的直接放弃
                movie.append(self.dic)
                if len(movie)>2:
                    for i in range(len(movie)-1):              #去重
                        if movie[-1][0]==movie[i][0]:   #用电影名字判定是否重复
                            del movie[-1]
                            break
                print '%d/3000'%(len(movie))      #打印进度
            else:
                continue

next_page=Next_page()
movie_info=Movie_info() 


#执行，开始抓取
for x in range(len(movie_tags)):          #x代表标签在movie_tags这个list中的位置
    print "正在抓取标签“%s”中的电影"%(movie_tags[x])
    starttime2=time.time()
    for i in range(next_page.np(x)):       #i代表正在抓取当前标签的第i页
        print "开始抓取第%d页，抓取进度："%(i+1)
        starttime2=time.time()
        movie_info.m(x,i)
        endtime2=time.time()
        print "抓取第%d页完毕，用时%.2fs"%(i+1,endtime2-starttime2)     #输出抓取每个页面所花费的时间
        time.sleep(2)
    endtime2=time.time()
    print "抓取“%s”标签完毕，用时%.2fs\n"%(movie_tags[x],endtime2-starttime2)   #输出抓取每个标签所花费的时间


#删除超过3000部的电影
if len(movie)>3000:
    for i in range(len(movie)-3000):
        del movie[-i]

#排序
def comment(s):
    return int(s[1])
starttime4=time.time()
print '开始排序……'
movie.sort(key = comment, reverse=True)
endtime4=time.time()
print '排序完毕，共耗时%.2f'%(endtime4-starttime4)

#写到html文件里面
f=file('Douban_movies.html','w')
f.write('<!DOCTYPE html>\n<html>\n<head>\n')
f.write('<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">\n')
f.write('</head>\n\n<body>\n')
f.write('<h1>豆瓣电影榜单</h1>'+' '+'<h3>按评价人数排名，共3000部</h3>')  #标题
s=1     #s是电影序号
for i in movie:
    f.write('<p>'+str(s)+'. '+'<a href=\"'+i[3]+'\">'+i[0]+'</a>'+'，共'+i[1]+'人评价，'+'得分：'+i[2]+'分；'+'\n')
    s+=1
f.write('</body>')
f.close()

print '完成！请查看html文件，获取豆瓣电影榜单。'











        

