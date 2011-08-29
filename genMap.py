#coding:utf8

import re,json
import codecs,os

from lat_lon_cn import lat_lon_data
import networkx as nx
import matplotlib.pyplot as plt

def extract(filepath):
    results=[]

    #load json data
    json_file=open(filepath,"rb")
    json_data=json.loads(json_file.read().decode('utf8'))
    json_file.close

    #extract all tweets
    for item in json_data:
        result=[]
        result.append(timeConvert(item["created_at"]))
        result.append(item["id"])
        result.append(item["text"])
        result.append(item["user"]["id"])
        result.append(item["user"]["screen_name"])
        result.append(item["user"]["location"])
        results.append(tuple(result))

    #retweeted tweet
    source=json_data[0]
    rtweeted=[]
    rtweeted.append(timeConvert(source["retweeted_status"]["created_at"]))
    rtweeted.append(source["retweeted_status"]["id"])
    rtweeted.append(source["retweeted_status"]["text"])
    rtweeted.append(source["retweeted_status"]["user"]["id"])
    rtweeted.append(source["retweeted_status"]["user"]["screen_name"])
    rtweeted.append(source["retweeted_status"]["user"]["location"])
    results.append(tuple(rtweeted))

    return results

def genTimelineMap(tweets):

    f=codecs.open("timemap.json","w","utf-8")
    f.write('[')
    format_str=u'''{"start":"%s","point":{"lat":%s,"lon":%s},"title":"%s","options":{"description": "%s","infoHtml":"%s"}},'''
    last_str=u'''{"start":"%s","point":{"lat":%s,"lon":%s},"title":"%s","options":{"description": "%s","infoHtml":"%s"}}'''
    '''
    for tweet in tweets:
        location=lookupLatLon(tweet[-1].split(" ")[-1])
        if location:
            tmpstr=format_str % (tweet[0],location[0],location[1],tweet[4],tweet[4],tweet[2])
            f.write(tmpstr)
    '''
    length=len(tweets)
    for x in range(length):
        tweet=tweets[x]
        location=lookupLatLon(tweet[-1].split(" ")[-1])
        if location:
            if x  == length -1:
                tmpstr=last_str % (tweet[0],location[0],location[1],tweet[4],tweet[4],tweet[2])
            else:
                tmpstr=format_str % (tweet[0],location[0],location[1],tweet[4],tweet[4],tweet[2])
            f.write(tmpstr)
    f.write(']')
    f.close()

def timeConvert(orgin_time):
    """convert time from 'Mon Apr 11 16:35:00 +0800 2011' to 'Mon Apr 11 16:35:00 +0800 2011'"""
    #orgin_time="Mon Apr 11 16:35:00 +0800 2011"
    input=orgin_time.split(" ")
    time_ele=input[3].split(":")
    time_span=8
    offset=(int(time_ele[0])+time_span) % 24
    if offset<10:
        time_ele[0]='0'+str(offset)

    else:
        time_ele[0]=str(offset)

    mon_dict={ "Jan":"01",
               "Feb":"02",
               "Mar":"03",
               "Apr":"04",
               "May":"05",
               "Jun":"06",
               "Jul":"07",
               "Aug":"08",
               "Sep":"09",
               "Oct":"10",
               "Nov":"11",
               "Dec":"12"}

    converted_time="%s-%s-%s %s:%s:%s" % (input[-1],mon_dict[input[1]],input[2],time_ele[0],time_ele[1],time_ele[2])

    return converted_time

def lookupLatLon(location):
    try:
        return lat_lon_data[location]
    except KeyError:return None

def drawGraph(tweets):

    G=nx.DiGraph()

    ptn="@(.+?):"

    nodes=[]
    edges=[]

    orgin=tweets[-1]

    for tweet in tweets:
        #tweet[2] meaning item["text"]
        text=tweet[2].split("//")
        retweet_counts=len(text)

        #tweet[4] means item["screen_name"]
        G.add_node(tweet[4],text=text[0])
        if retweet_counts>1:
            text.pop(0)
            temp_id=tweet[4]

            for line in text:
                if line == '':continue
                retweet_id=re.findall(ptn,line)
                if retweet_id:
                    G.add_node(retweet_id[0],text=line[len(retweet_id[0])])
                    edges.append(tuple([temp_id,retweet_id[0]]))
                    temp_id=retweet_id[0]

        else:
            edges.append(tuple([tweet[4],orgin[4]]))

    G.add_edges_from(edges)

    print len(G.nodes())
    print len(G.edges())
    try:
        import pylab
        limits=pylab.axis('off')
    except:pass

    plt.figure(figsize=(18,16),dpi=400)

    draw_args={ "pos":nx.spring_layout(G),
                "node_size":40,
                "node_color":'g',
                "node_shape":'s',
                "width":0.2,
                "style":"dotted",
                "font_size":10,
                "font_color":'b'}
    try:
        nx.draw_networkx(G,**draw_args)
        plt.savefig("tweet.png")
    except:
        print "can not to save image!"

def main():
    filepath=r"demo.json"
    results=extract(filepath)
    drawGraph(results)
    genTimelineMap(results)

if __name__ == "__main__":
    main()