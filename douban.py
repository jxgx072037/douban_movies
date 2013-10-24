# -*- coding: utf-8 -*-
import urllib2
import re

#抓取豆瓣电影标签
f=urllib2.urlopen('http://movie.douban.com/tag/?view=cloud').read()
n1=f.find('007')
n2=f.find('宗教')        #n1是第一个标签，n2是第二个标签，利用这两个标签定位标签们在f中的位置
f1=f[(n1-4):(n2+10)]    #4和10是随便取的数字
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
k=1          #用来记录进度


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
        self.movie_comment1=re.findall('class=\"pl.*评价',movie_list.request_open(n1,n2))
        for s in self.movie_comment1:
            self.movie_comment2.append(re.findall('\d{1,}',s)[0])

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
                global k
                print '抓取进度：'+str(k)+'/3000'      #打印进度
                k+=1
            else:
                continue

next_page=Next_page()
movie_info=Movie_info()

#执行
for x in range(len(movie_tags)):
    for i in range(next_page.np(x)):
        movie_info.m(x,i)
        if len(movie)>3000:
            break
        else:
            continue
    if len(movie)>3000:
        break
    else:
        continue

#排序
def comment(s):
    return int(s[1])
print '开始排序……'
movie.sort(key = comment, reverse=True)

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

print '完成！'











        

