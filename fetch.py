#!/urs/bin/env python
# coding:utf-8

import urllib2,re
import cookielib
from lxml import etree

#urls
login_url=r"http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.12)"
post_data=r"service=sso&client=ssologin.js%28v1.3.12%29&entry=sso&encoding=GB2312&gateway=1&savestate=0&from=&useticket=0&username=tmtmtest@yahoo.com&password=12345678&callback=parent.sinaSSOController.loginCallBack"
hotlist_url=r"http://t.sina.com.cn/pub/topmblog?type=re&act=week"

#setup for urllib2
cookiejar=cookielib.CookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
opener.addheaders=[('User-Agent', 'Mozilla/5.0')]
urllib2.install_opener(opener)

def save_to_file(filename,content):
    """save to file"""
    output=open(filename,"w")
    output.writelines(content)
    output.close()

def get_hot_list(ttype='re',act='day'):
    """simulate browser login to fetch hot list"""
    print "fetch start."

    #login to sina
    req=urllib2.Request(login_url,post_data)
    ret_str=urllib2.urlopen(req).read()

    #fetch hot list and extract
    hot_list=extract(urllib2.urlopen(hotlist_url).read())

    print "fetch end."
    return hot_list

def extract(hotlist_content):
    """xpath to extract name,mid,content,rt,comm,date"""
    print "extract start."
    s = hotlist_content
    tree=etree.fromstring(s, etree.HTMLParser())

    name_list=tree.xpath("//div[@class='MIB_feed_c']/p/a[@title]/text()")
    mid_list=[mid.items()[1][1] for mid in tree.xpath("//div[@class='MIB_feed_c']/p")]
    #content_list=tree.xpath("//div[@class='MIB_feed_c']/p/text()")
    content_list=[]
    for obj in tree.xpath("//div[@class='MIB_feed_c']/p"):
        content=obj.xpath("text()")
        #no extract need name anymore, extract content in tag <a>
        for child in obj.getchildren()[1:]:
            if child.text is not None:
                content.append(child.text)
        content_list.append(" ".join(content))
    from_list=tree.xpath("//div[@class='feed_att']/div/cite/a[@target]/text()")
    date_list=tree.xpath("//div[@class='feed_att']/div/cite/a/strong[@date]/text()")
    rtcount_list=tree.xpath("//div[@class='feed_att']/div[@class='rt']/a/strong[@type='rttCount']/text()")
    comment_list=tree.xpath("//div[@class='feed_att']/div[@class='rt']/a/strong[@type='commtCount']/text()")

    hot_list=zip(name_list,mid_list,content_list,from_list,date_list,rtcount_list,comment_list)

    print "extract end."
    return filter(hot_list)

def filter(hot_list):
    print "filter start."
    """calculate rt/comm. filter most meaningless messages"""
    refined_list=[]
    for hot_tweet in hot_list:
        if int(hot_tweet[5][1:-1]) / int (hot_tweet[6][1:-1]) <=4:
            refined_list.append(hot_tweet)
    print "extract end."
    return refined_list

if __name__ =="__main__":
    hot_list=get_hot_list()
    print len(hot_list)
