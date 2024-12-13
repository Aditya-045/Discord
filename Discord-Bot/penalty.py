import matplotlib.pyplot as plt
from PIL import Image as im

color={1:'#56f207',0:'#f2160f'}
def shootout(teams,scores):
    axes=plt.axes()
    img=im.open("goal1.jpg")
    plt.imshow(img)
    x,y=70,18
    sc=[0,0]
    if len(scores)>5 and len(scores)%5!=0:
        for score in scores[:5*(len(scores)//5)]:
            sc[0]+=score[0]
            sc[1]+=score[1]
        scores=scores[5*(len(scores)//5):]
    for score in scores:
        circle=plt.Circle((x,y),10,color=color[score[0]])
        axes.add_artist(circle)
        circle1=plt.Circle((x,y+30),10,color=color[score[1]])
        axes.add_artist(circle1)
        x+=30
        sc[0]+=score[0]
        sc[1]+=score[1]
    plt.tick_params(left = False,bottom=False)
    axes.xaxis.set_ticklabels([])
    axes.yaxis.set_ticklabels([])
    plt.text(6,50,"{}\n\n{}".format(*teams),color='w',size=13,weight='bold')
    plt.text(225,52,"{}\n{}".format(*sc),color='k',size=27)
    plt.tight_layout()
    plt.savefig("game_img.png")
    plt.clf()
    return sc

def fixtures(matches=None,scores=None):
    axes=plt.axes()
    pos_qf={0:60,1:74,2:152,3:165,4:242.5,5:256,6:335,7:348}
    pos_sf={0:105,1:119,2:289,3:302}
    pos_f={0:198,1:212}
    img=im.open("bracket.jpg")
    plt.imshow(img)
    for s in range(len(matches)):
        i=0
        stage=matches[s]
        if s==0:
            pos=pos_qf
            x=17
        elif s==1:
            x=163
            pos=pos_sf
        else:
            x=308
            pos=pos_f
        for m in stage:
            plt.text(x,pos[i],m[0],size=6.5,color='k')
            i+=1
            plt.text(x,pos[i],m[1],size=6.5,color='k')
            i+=1
    if scores!=None:
        for s in range(len(scores)):
            i=0
            score=scores[s]
            if s==0:
                x=125
                pos=pos_qf
            elif s==1:
                x=271
                pos=pos_sf
            else:
                x=416
                pos=pos_f
            for s in score:
                plt.text(x,pos[i]+15,str(s[0])+"\n"+str(s[1]),size=9.5,color='k')
                i+=2
    plt.axis('off')
    plt.axis('tight')
    plt.tight_layout()
    plt.savefig("bracket_img.png",bbox_inches='tight', pad_inches = 0)

