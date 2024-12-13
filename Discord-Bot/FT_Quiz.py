import random
import csv

class Quiz:
    def __init__(self,ques,qz_type=0):
        self.ques_no=ques
        self.points=0
        self.qlist=[]
        self.anslist=[]
        self.optlist=[]
        self.type=qz_type

    def arrange(self):
        dct={}
        if self.type==0:  #Text-based quiz
            with open (r"FT_QuizData.csv","r",newline="") as f:
                csvr=csv.reader(f)
                i=1
                for q,op1,op2,op3,op4,ans in csvr:
                    options=[op1,op2,op3,op4]
                    random.shuffle(options)
                    opt="A- {}\nB- {}\nC- {}\nD- {}\n".format(options[0],options[1],options[2],options[3])
                    dct[i]={"Q":q,"Opt":opt,"Ans":ans,"Opt_Dict":{"A":options[0],"B":options[1],"C":options[2],"D":options[3]}}
                    i+=1
        if self.type==1:  #Image-based quiz
            with open (r"Face_QuizData.csv","r",newline="") as f:
                csvr=csv.reader(f)
                i=1
                for player,face in csvr:
                    dct[i]={"Q":face,"Ans":player}
                    i+=1
        if self.type==2:  #Image-based quiz
            with open (r"Flag_QuizData.csv","r",newline="") as f:
                csvr=csv.reader(f)
                i=1
                for player,face in csvr:
                    dct[i]={"Q":face,"Ans":player}
                    i+=1
        keys=list(dct.keys())
        random.shuffle(keys)
        keys=keys[:self.ques_no]
        self.ques_dct=[dct[k] for k in keys]

    def quiz(self):
        self.arrange()
        for d in self.ques_dct:
            if self.type==0:
                self.qlist.append(d["Q"]+"\n"+d["Opt"])
            elif self.type>=1:
                self.qlist.append(d["Q"])
            self.anslist.append(d["Ans"])
            try:
                self.optlist.append(d["Opt_Dict"])
            except:
                self.optlist.append(None)
        return self.qlist,self.anslist,self.optlist

if __name__=="__main__":
    ob=Quiz(3)
    ob.quiz()
