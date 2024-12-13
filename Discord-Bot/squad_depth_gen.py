import pickle
import statistics as st
import time
#import matplotlib.pyplot as plt

def fetch_data(league,season):
    global d
    global clubs
    global depth_club
    global pkeys
    with open (r"{}_{}_posdata.dat".format(str(season),str(league)),"rb") as f:
        d=pickle.load(f)
    clubs= []
    depth_club=dict()
    pkeys=[u'Goalkeeper',u'Left-Back',u'Sweeper',u'Centre-Back',u'Right-Back',u'Defensive Midfield',u'Central Midfield',u'Left Midfield',u'Left Winger',u'Right Midfield',u'Right Winger',u'Attacking Midfield',u'Second Striker',u'Centre-Forward']
    for i in range(len(d)):
        try:
            clubs.extend(d[i+1].keys())
        except KeyError:
            continue
    clubs=list(set(clubs))

def sort_mode(lst):
    """Takes a list containing the total names of players collected for each position at a time
from each match and returns a sorted list of no.of appearances in a particular position"""
    try:
        if len(lst)>0:
            list1=list(set([lst.count(n) for n in lst if lst.count(n)]))
            return sorted(list1,reverse=True)
        else:
            return None
    except:
        return None
def get_squadepth(n,league="ISL",season="2021",mode="default",team="all"):
    fetch_data(league,season)
    for club in clubs:
        if team=="all":
            pass
        elif team.lower() not in club.lower():
            continue
        squad=[]
        pls=0
        for i in range(1,len(d)+1):
            try:
                squad.append(d[i][club])
            except KeyError:
                continue
        pos={u'Goalkeeper':[],u'Centre-Back':[],u'Sweeper':[],u'Left-Back':[],u'Right-Back':[],u'Defensive Midfield':[],u'Central Midfield':[],u'Right Midfield':[],u'Left Midfield':[],u'Left Winger':[],u'Right Winger':[],u'Attacking Midfield':[],u'Second Striker':[],u'Centre-Forward':[]}
        for lineup in squad:
            for player in lineup:
                if "Return" not in player[0]:
                    pos[player[0]].append(player[1])
        names=[]
        depth=dict.copy(pos)
        for position,pl_list in pos.items():
            app=sort_mode(pl_list)
            if app!=None:
                lst2=[]
                for i in range(len(app)):
                    p1=list(set([name for name in pl_list if pl_list.count(name)==app[i]]))
                    pls+=len(p1)
                    if mode=="default":
                        player="("+", ".join(p1)+")"
                    elif mode=="raw":
                        player=", ".join(p1)
                    lst2.append(": ".join([player,str(app[i])]))
                    if i==n-1:         #Depth of the number upto n
                        break
                if len(lst2)>0:
                    depth[position]=lst2
                    depth_club[club]=depth
        for p in pkeys:
            if len(depth[p])>0:
                pass
        return depth_club

    
