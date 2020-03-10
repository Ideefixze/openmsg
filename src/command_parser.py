import sys

commands = dict()

def ClearString(nick):
    nick = nick[0:20]
    return nick.rstrip()

def ChangeNickname(who, args,server):
    old = who[1]
    who[1] = ClearString(args[0])
    server.Broadcast(old + " is known as " + who[1] +".")

def UserJoined(who, args, server):
    who[1] =  ClearString(args[0])
    server.Broadcast(who[1] +" has joined the room.")

def Help(who, args, server):
    server.ServerPrivateMessage("\n/nickname <text> - Changes your nickname.", who)

commands["nickname"]=ChangeNickname
commands["join"]=UserJoined
commands["help"]=Help
def Parse(command, who, args, server):
    commands[command](who,args,server)


#user1 = ["data", "Juzef"]
#Parse("nickname",user1,"DUPA","HEHE")
#print(user1)




