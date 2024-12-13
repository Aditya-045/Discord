from itertools import permutations as pr
from itertools import combinations as cr
import random as r

def create_table(dct):
    data=[["Team","M","W","D","L","GF","GA","GD","Pts"]]
    for k,val in dct.items():
        dct[k]["GD"]=val["GF"]-val["GA"]
        dct[k]["Pts"]=val["W"]*3+val["D"]
    keys=sorted(list(dct.items()),key=lambda k:(k[1]["Pts"],k[1]["GD"],k[1]["GF"]),reverse=True)
    data.extend([ [a,v["M"],v["W"],v["D"],v["L"],v["GF"],v["GA"],v["GD"],v["Pts"]] for a,v in keys] )
    print (data)
    column_widths = [max(len(str(item)) for item in column) for column in zip(*data)]
    print (column_widths)
    header = "|"+" | ".join(f"{column:<{width}}" for column, width in zip(data[0], column_widths))+"|"
    separator = "+".join("-" * (width+2 ) for width in column_widths)
    rows = [f"|{' | '.join(f'{item:<{width}}' for item, width in zip(row, column_widths))}|" for row in data[1:]]
    print(separator)
    print(header)
    print(separator)
    print("\n".join(rows))
    print(separator)
def extract_score(dct):
    table={}
    for k,v in dct.items():
        team1,team2=k.upper().split(" VS ")[0],k.upper().split(" VS ")[1]
        goal1,goal2=int(v.split("-")[0]),int(v.split("-")[1])
        table.setdefault(team1,{"M":0,"W":0,"D":0,"L":0,"GF":0,"GA":0})
        table.setdefault(team2,{"M":0,"W":0,"D":0,"L":0,"GF":0,"GA":0})
        table[team1]["M"]+=1
        table[team2]["M"]+=1
        table[team1]["GF"]+=goal1
        table[team2]["GF"]+=goal2
        table[team1]["GA"]+=goal2
        table[team2]["GA"]+=goal1
        if goal1>goal2:
            table[team1]["W"]+=1
            table[team2]["L"]+=1
        elif goal1<goal2:
            table[team2]["W"]+=1
            table[team1]["L"]+=1
        else:
            table[team1]["D"]+=1
            table[team2]["D"]+=1
    return table
def generate_fixtures(teams,double=True):
    match_dct={}
    if double:
        fixtures=list(pr(teams,2))
    else:
        fixtures=list(cr(teams,2))
    match_dct=match_dct.fromkeys(["{} vs {}".format(t[0],t[1]) for t in fixtures])
    return match_dct
def group_draw(teams1,groups):
    grp_dct={}
    teams=list(teams1)
    grps=['A','B','C','D','E','F']
    for i in range(3):
        r.shuffle(teams)
    for i in range(len(teams)):
        g=i%groups
        grp_dct.setdefault(grps[g],[])
        grp_dct[grps[g]].append(teams.pop().strip())
        r.shuffle(teams)
    return grp_dct