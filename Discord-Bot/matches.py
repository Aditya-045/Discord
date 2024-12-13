import json
import requests
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from PIL import Image as im
import numpy as np
import os


emoji_dct={"Hyderabad":"<:HyderabadFC:743665597228777493>","Kerala Blasters":"<:logo_KBFC:735720770767945818>","East Bengal":"<:Emami_EastBengal:1013320555379839007>","ATK Mohun Bagan":"<:ATKMB:761460279556308992>","Chennaiyin":"<:logo_CFC:735721016935841854>","Goa":"<:logo_FCG:735720980881604608>","Bengaluru":"<:logo_BFC:735721059222814730>","Mumbai City":"<:MCFC:735720893124313150>","NorthEast United":"<:MCFC:735720893124313150>","Jamshedpur":"<:MCFC:735720893124313150>","Odisha":"<:logo_OFC:735720833653145670>"}

def all_matches():
    f=open("ISL_Matches.json",encoding='utf-8-sig')
    matches=json.loads(f.read())
    dct={}
    for match in matches:
        date=dt.strptime(match["match_date"]+match["kick_off"],"%Y-%m-%d%H:%M:%S.%f")
        team1,team2=match["home_team"]["home_team_name"],match["away_team"]["away_team_name"]
        dct[match["match_id"]]=[date,team1+"\t{}-{}\t".format(str(match["home_score"]),str(match["away_score"]))+team2]
    #print (sorted(list(dct.values()))[:10])
    mid=list(zip(*sorted(list(dct.values()))))
    matches=list(zip(*sorted(dct.items(),key=lambda n:n[1])))
    matches=matches[0]
    mid=mid[1]
    return matches,mid
    
def get_match(id):
    url="https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{}.json".format(id)
    r=requests.get(url)
    event=r.text
    match=json.loads(event)
    return match

def pitch():
    ax=fig.add_subplot(1,1,1)
    bg=[20,210,4] #Green
    #Pitch Outline & Centre Line
    #plt.plot([0,0],[0,90], color="white")
    plt.plot([0,120],[90,90], color="white")
    #plt.plot([120,120],[90,0], color="white")
    plt.plot([120,0],[0,0], color="black")
    plt.plot([60,60],[0,90], color="white")
    plt.plot([16.5,16.5],[65,25],color="white")
    plt.plot([0,16.5],[65,65],color="white")
    plt.plot([16.5,0],[25,25],color="white")#Assign circles to variables - do not fill the centre circle!
    centreCircle = plt.Circle((60,45),11.15,color="white",fill=False)
    centreSpot = plt.Circle((60,45),0.8,color="white")

    #Right Penalty Area
    plt.plot([120,103.5],[65,65],color="white")
    plt.plot([103.5,103.5],[65,25],color="white")
    plt.plot([103.5,120],[25,25],color="white")

    #Left 6-yard Box
    plt.plot([0,5.5],[54,54],color="white")
    plt.plot([5.5,5.5],[54,36],color="white")
    plt.plot([5.5,0.5],[36,36],color="white")
        
    #Right 6-yard Box
    plt.plot([120,114.5],[54,54],color="white")
    plt.plot([114.5,114.5],[54,36],color="white")
    plt.plot([114.5,120],[36,36],color="white")
    #Draw the circles to our plot
    ax.add_patch(centreCircle)
    ax.add_patch(centreSpot)

    p=np.zeros((90,120,3), dtype=np.uint8)
    for i in range(90):
        for j in range(120):
            p[i,j]=bg
    plt.imshow(p)

def average(lst):
    avg=[0 for n in range(2)]
    for elem in lst:
        for i in range(len(elem)):
            avg[i]+=elem[i]
    for i in range(len(avg)):
        avg[i]=avg[i]/len(lst)
    return avg


def passmap(match,pos1,pos2):
    team1,team2=match[1]["possession_team"]["name"],match[1]["team"]["name"]
    lineup1,lineup2=dict(),dict()
    for pl in match[0]["tactics"]["lineup"]:
        lineup1.update({pl["player"]["name"]:{}  })
    for pl in match[1]["tactics"]["lineup"]:
        lineup2.update({pl["player"]["name"]:{}  })
    
    for event in match:
        if "type" in event and event["type"]["id"]==30:
            pass_by=event["player"]["name"]
            try:
                pass_recipient=event["pass"]["recipient"]["name"]
            except:
                pass_recipient=""
            if pass_by in lineup1 and pass_recipient in lineup1:
                try:
                    if pass_by not in lineup1[pass_recipient]:
                        lineup1[pass_by][pass_recipient]+=1
                except:
                    lineup1[pass_by][pass_recipient]=1
            if pass_by in lineup2 and pass_recipient in lineup2:
                try:
                    if pass_by not in lineup2[pass_recipient]:
                        lineup2[pass_by][pass_recipient]+=1
                except:
                    lineup2[pass_by][pass_recipient]=1
    for i,j in lineup1.items():
        for pl,ps in j.items():
            plt.plot([pos1[i][0],pos1[pl][0]],[90.0-pos1[i][1],90.0-pos1[pl][1]],color="r",linewidth=ps/3,alpha=0.45 )
    for i,j in lineup2.items():
        for pl,ps in j.items():
            plt.plot([120.0-pos2[i][0],120.0-pos2[pl][0]],[pos2[i][1],pos2[pl][1]],color="b",linewidth=ps/4,alpha=0.45 )

fig=plt.figure()
def avg_position(m_num):
    pitch()
    m_id,matches=all_matches()
    match=get_match(str(m_id[m_num]))
    team1,team2=match[1]["possession_team"]["name"],match[1]["team"]["name"]
    lineup1,lineup2=dict(),dict()
    for pl in match[0]["tactics"]["lineup"]:
        lineup1.update({pl["player"]["name"]:str(pl["jersey_number"])})
    for pl in match[1]["tactics"]["lineup"]:
        lineup2.update({pl["player"]["name"]:str(pl["jersey_number"])})
    mt=matches[m_num]
    string=emoji_dct[team1]+team1+"\n"
    for i,j in lineup1.items():
        string=string+j+"\t"+i+"\n"
    string=string+"\n"+emoji_dct[team2]+team2+"\n"
    for i,j in lineup2.items():
        string=string+j+"\t"+i+"\n"
    avg1=dict.fromkeys(lineup1,())
    avg2=dict.fromkeys(lineup2,())
    for player in lineup1.keys():
        for event in match:
            if "type" in event and event["type"]["id"]==30 and event["player"]["name"]==player:  #Pass
                avg1[player]=avg1[player]+((event["location"]),)
    for pl,pos in avg1.items():
        lst=avg1[pl]
        if pos==():
            avg1.pop(pl)
            continue
        avg=average(lst)
        avg1[pl]=avg
        plt.scatter(avg[0],90.0-avg[1],color="r")
        plt.text(avg[0],90.0-avg[1],pl.split()[0],fontsize=9,color="k")
    for player in lineup2.keys():
        for event in match:
            if "type" in event and event["type"]["id"]==30 and event["player"]["name"]==player:  #Pass
                avg2[player]=avg2[player]+((event["location"]),)
    for pl,pos in avg2.items():
        lst=avg2[pl]
        if pos==():
            avg2.pop(pl)
            continue
        avg=average(lst)
        avg2[pl]=avg
        plt.scatter(120.0-avg[0],avg[1],color="b")
        plt.text(120.0-avg[0],avg[1],pl.split()[0],fontsize=9,color="k")
    plt.xlim([0,120.5])
    plt.ylim([0,90.5])
    plt.tick_params(labelleft=False,labelbottom=False,left=False,bottom=False)
    plt.scatter(-1,-1,label=team1,color="r")
    plt.scatter(-1,-1,label=team2,color="b")
    passmap(match,avg1,avg2)
    plt.legend()
    im=plt.imread("StatsBomb_Logo.png")
    newax = fig.add_axes([0.149,0.08,0.2,0.2], anchor='W', zorder=1)
    newax.imshow(im)
    newax.axis('off')
    plt.savefig("Figure_1-1.png",bbox_inches = 'tight',dpi=150)
    plt.clf()
    #plt.show()
    return mt,string
