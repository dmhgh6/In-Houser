# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Player, Document
from .demoinfocsgo.demodump import DemoDump
import os
import json

from .forms import DocumentForm

TEAM_T = 2
TEAM_CT = 3


class Players(object):
    def __init__(self, index, name, userid, networkid):
        self.index = index
        self.name = name
        self.userid = userid
        self.networkid = networkid
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.mvps = 0
        self.headshots = 0
        self.won = 0

        self.team = 0  # 2 is T, 3 is CT?

    def reset_stats(self):
        print '--------------STATS RESET--------------'
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.mvps = 0
        self.headshots = 0


class Game(object):
    def __init__(self, filename):
        self.filename = filename
        self.demo = DemoDump()
        self.players = {}
        self.current_round = 0
        #self.highlights = []
        self.teamScores = [0, 0] # 0 is CT, 1 is T
        self.roundsPlayed = 0

        self.demo.register_on_gameevent("player_death", self.player_death)
        #self.demo.register_on_gameevent("round_mvp", self.mvp)
        self.demo.register_on_gameevent(36, self.round_start)
        self.demo.register_on_gameevent(42, self.round_end)

    def parse(self):
        if self.demo.open(self.filename):
            print "Beginning parsing"
            self.demo.register_on_gameevent(7, self.player_connected)
            self.demo.register_on_gameevent(8, self.player_connected)
            #self.demo.register_on_gameevent(9, self.player_disconnected)
            #self.demo.register_on_gameevent(27, self.player_spawn)
            self.demo.register_on_gameevent(40, self.game_start)  # only start counting when warmup is over
            self.demo.dump()
            print "Done parsing"
            print self.players
        else:
            print "Demo unparsable"
        pass

    def player_connected(self, data):
        if data.userid not in self.players.keys():
            self.players[data.userid] = Players(data.index, data.name, data.userid, data.networkid)
        self.players[data.userid].index = data.index
        self.players[data.userid].name = data.name
        self.players[data.userid].userid = data.userid
        self.players[data.userid].networkid = data.networkid

    def player_join_team(self, data):
        if data.team == 0:  # disconnect?
            return
        print "%i joined team %i" % (data.userid, data.team)
        self.players[data.userid].team = data.team

    def player_spawn(self, data):
        if data.userid not in self.players.keys():
            self.players[data.userid] = Players(data.index, data.name, data.userid, data.networkid)

    def game_start(self, data):
        self.current_round = 0
        for index, player in self.players.items():
            player.reset_stats()

    def player_death(self, data):
        if data.userid not in self.players:
            print "Player %i died, but could not be found" % data.userid
            return

        self.players[data.userid].deaths += 1

        if data.attacker not in self.players:
            print "Attacker %i could not be found" % data.attacker
            return

        if data.userid != data.attacker:  # not suicide? maybe check for same team?
            self.players[data.attacker].kills += 1
            if data.headshot:
                print "%i headshot %i" % (data.attacker, data.userid)
                self.players[data.attacker].headshots += 1
            else:
                print "%i killed %i" % (data.attacker, data.userid)

        #if data.assister != 0:  # someone assisted
            #self.players[data.assister].assists += 1

    def mvp(self, data):
        self.players[data.userid].mvps += 1

    def round_start(self, data):
        self.current_round += 1

    def round_end(self, data):
        print "Round ended, winner: %i " % data.winner
        self.roundsPlayed += 1
        half = self.current_round >= 15
        if not half:
            self.teamScores[data.winner-2] += 1
        elif data.winner == 2:
            self.teamScores[1] += 1
        else:
            self.teamScores[0] += 1

    def storeResults(self):
        steamIds = []
        for playerid, player in self.players.items():
            if self.teamScores[0] > self.teamScores[1] and player.team == 3:
                player.won = 1
            elif self.teamScores[1] > self.teamScores[0] and player.team == 2:
                player.won = 1
            if Player.objects.filter(steamId=player.networkid).exists():
                plyr = Player.objects.get(steamId=player.networkid)
                plyr.kills += player.kills
                plyr.deaths += player.deaths
                plyr.assists += player.assists
                plyr.mvps += player.mvps
                if player.networkid not in steamIds:
                    plyr.roundsPlayed += self.roundsPlayed
                    if player.team == 3:
                        plyr.roundsWon += self.teamScores[0]
                    elif player.team == 2:
                        plyr.roundsWon += self.teamScores[1]
                    plyr.gamesPlayed += 1
                    plyr.gamesWon += player.won
                else:
                    if player.team == 3:
                        plyr.roundsWon -= self.teamScores[1]
                        plyr.roundsWon += self.teamScores[0]
                        if self.teamScores[1] > self.teamScores[0]:
                            plyr.gamesWon -= 1
                    elif player.team == 2:
                        plyr.roundsWon -= self.teamScores[0]
                        plyr.roundsWon += self.teamScores[1]
                        if self.teamScores[0] > self.teamScores[1]:
                            plyr.gamesWon -= 1
                    plyr.gamesWon += player.won
                plyr.save()
            else:
                roundsWon = 0
                if player.team == 3:
                    roundsWon = self.teamScores[0]
                elif player.team == 2:
                    roundsWon = self.teamScores[1]
                plyr = Player(name=player.name, kills=player.kills, deaths=player.deaths, assists=player.assists, mvps=player.mvps, steamId=player.networkid, roundsPlayed=self.roundsPlayed, roundsWon=roundsWon, gamesPlayed=1, gamesWon=player.won)
                plyr.save()
            steamIds.append(player.networkid)

# Create your views here.
def index(request):
    if Document.objects.all().exists():
        #print 'HERE'
        filePath = Document.objects.all().get().document.path
        Document.objects.all().delete()
        #print filePath
        os.remove(filePath)
    playerList = Player.objects.order_by('name')
    context = {'playerList': playerList}
    return render(request, 'inHouseSite/index.html', context)

def detail(request, player_id):
    return HttpResponse("You're looking at player %s." % player_id)

def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if ".dem" in form.instance.document.path:
                parseDemoFile(form.instance.document.path)
            elif ".json" in form.instance.document.path:
                parseJsonFile(form.instance.document.path)

            return redirect('index')
    else:
        form = DocumentForm()
    return render(request, 'inHouseSite/model_form_upload.html', {
        'form': form
    })

def parseDemoFile(filePath):
    game = Game(filePath)
    game.parse()
    game.storeResults()

def parseJsonFile(filePath):
    game = json.load(open(filePath))

    #Team One Parsing
    for i in game["TeamOne"]:
        win = 0
        if game["TeamOneScore"] > game["TeamTwoScore"]:
            win = 1

        if Player.objects.filter(steamId=i["SteamId"]).exists():
            #print "exists"
            p = Player.objects.get(steamId=i["SteamId"])
            p.kills += i["Kills"]
            p.deaths += i["Deaths"]
            p.assists += i["Assists"]
            p.mvps += i["Mvps"]
            p.roundsPlayed += game["TeamOneScore"] + game["TeamTwoScore"]
            p.roundsWon += game["TeamOneScore"]
            p.gamesWon += win
            p.gamesPlayed += 1

            p.save()

        elif not i["isBot"]:
            p = Player(name=i["Name"], kills=i["Kills"], deaths=i["Deaths"], assists=i["Assists"], mvps=i["Mvps"],
                       steamId=i["SteamId"], roundsPlayed=game["TeamOneScore"]+game["TeamTwoScore"],
                       roundsWon=game["TeamOneScore"], gamesPlayed=1, gamesWon=win)
            p.save()

    # Team Two Parsing
    for i in game["TeamTwo"]:
        win = 0
        if game["TeamOneScore"] < game["TeamTwoScore"]:
            win = 1

        if Player.objects.filter(steamId=i["SteamId"]).exists():
            #print "exists"
            p = Player.objects.get(steamId=i["SteamId"])
            p.kills += i["Kills"]
            p.deaths += i["Deaths"]
            p.assists += i["Assists"]
            p.mvps += i["Mvps"]
            p.roundsPlayed += game["TeamOneScore"] + game["TeamTwoScore"]
            p.roundsWon += game["TeamTwoScore"]
            p.gamesWon += win
            p.gamesPlayed += 1

            p.save()

        elif not i["isBot"]:
            p = Player(name=i["Name"], kills=i["Kills"], deaths=i["Deaths"], assists=i["Assists"], mvps=i["Mvps"],
                   steamId=i["SteamId"], roundsPlayed=game["TeamOneScore"] + game["TeamTwoScore"],
                   roundsWon=game["TeamTwoScore"], gamesPlayed=1, gamesWon=win)
            p.save()