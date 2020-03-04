import sys

commands = dict()

def ChangeNickname(who, args,server):
    old = who[1]
    who[1] = args[0]
    server.Broadcast(old + " is known as " + who[1] +".")

commands["nickname"]=ChangeNickname
def Parse(command, who, args, server):
    commands[command](who,args,server)


#user1 = ["data", "Juzef"]
#Parse("nickname",user1,"DUPA","HEHE")
#print(user1)




