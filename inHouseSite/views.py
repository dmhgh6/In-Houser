# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Player, Document
from .demoinfocsgo.demodump import DemoDump
import os

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
        self.won = 0

        self.kills_this_round = 0
        self.clutch_kills = 0
        self.is_connected = True
        self.is_alive = False
        self.team = 0  # 2 is T, 3 is CT?


class HighlightFinder(object):
    def __init__(self, filename):
        self.filename = filename
        self.demo = DemoDump()
        self.players = {}
        self.current_round = 0
        self.highlights = []
        self.teamScores = [0, 0] # 0 is CT, 1 is T
        self.roundsPlayed = 0

    def parse(self):
        if self.demo.open(self.filename):
            print "Beginning parsing"
            self.demo.register_on_gameevent(7, self.player_connected)
            self.demo.register_on_gameevent(8, self.player_connected)
            self.demo.register_on_gameevent(9, self.player_disconnected)
            self.demo.register_on_gameevent(21, self.player_join_team)
            self.demo.register_on_gameevent(27, self.player_spawn)
            self.demo.register_on_gameevent(40, self.game_start)  # only start counting when warmup is over
            self.demo.dump()
        else:
            print "Demo unparsable"
        pass

    def player_connected(self, data):
        if data.userid not in self.players.keys():
            self.players[data.userid] = Players(data.index, data.name, data.userid, data.networkid)
        self.players[data.userid].is_connected = True
        print "New player %i" % data.userid

    def player_disconnected(self, data):
        if data.networkid == 'BOT':  # if bot, just remove
            self.players.pop(data.userid, None)
        else:
            self.players[data.userid].is_connected = False

    def player_join_team(self, data):
        if data.team == 0:  # disconnect?
            return
        print "%i joined team %i" % (data.userid, data.team)
        self.players[data.userid].team = data.team

    def player_spawn(self, data):
        self.players[data.userid].is_alive = True
        self.players[data.userid].kills_this_round = 0
        self.players[data.userid].clutch_kills = 0

    def game_start(self, data):
        self.current_round = 0
        self.demo.register_on_gameevent(36, self.round_start)
        self.demo.register_on_gameevent(42, self.round_end)
        self.demo.register_on_gameevent("round_mvp", self.mvp)
        self.demo.register_on_gameevent(23, self.player_death)

    def mvp(self, data):
        self.players[data.userid].mvps += 1

    def round_start(self, data):
        self.current_round += 1

    def round_end(self, data):
        print "Round ended, winner: %i, reason: %i, message: %s" % (data.winner, data.reason, data.message)
        self.roundsPlayed += 1
        half = self.current_round >= 15
        if not half:
            self.teamScores[data.winner-2] += 1
        elif data.winner == 2:
            self.teamScores[1] += 1
        else:
            self.teamScores[0] += 1
        for player in self.players.values():
            if player.kills_this_round >= 3:
                self.highlights.append(
                    "%s got a %ik in round %i" % (player.name, player.kills_this_round, self.current_round))
            if player.is_alive and player.team == data.winner and self.count_alive(
                    player.team) == 1 and self.count_alive(
                    self.invert_team(player.team)) == 0 and player.clutch_kills >= 2:
                self.highlights.append(
                    "%s clutched a 1v%i in round %i" % (player.name, player.clutch_kills, self.current_round))

    def player_death(self, data):
        self.players[data.userid].deaths += 1
        self.players[data.userid].is_alive = False

        if data.userid != data.attacker and self.players[data.attacker].team != self.players[data.userid].team:  # not suicide or team kill?
            self.players[data.attacker].kills += 1
            self.players[data.attacker].kills_this_round += 1  # used for finding highlights

            if self.count_alive(self.players[data.attacker].team) == 1:
                self.players[data.attacker].clutch_kills += 1
            print "%s killed %s with %s%s" % (
            self.players[data.attacker].name, self.players[data.userid].name, data.weapon,
            " (headshot)" if data.headshot else "")
        else:
            self.players[data.attacker].kills -= 1

        if data.assister != 0:  # someone assisted DOES THIS NEED TO BE IN THE SUICIDE/TEAM KILL CHECK?
            self.players[data.assister].assists += 1

    def count_alive(self, teamid):
        alive = 0
        for player in self.players.values():
            if player.is_connected and player.is_alive and player.team == teamid:
                alive += 1
        return alive

    def invert_team(self, teamid):
        if teamid == 2 or teamid == 3:
            return 3 if teamid == 2 else 2
        return teamid

    def print_results(self):
        print "%i players found" % len(self.players)
        for playerid, player in self.players.items():
            if player.networkid != "BOT":
                print vars(player)

        print ""
        print "Highlights: %i" % len(self.highlights)
        for highlight in self.highlights:
            print highlight

    def storeResults(self): #NEED TO CHECK IF THE STEAM ID WAS ALREADY ADDED, NEED TO LIKE PARSE ALL PLAYERS AND REMOVE DUPLICATES BASED ON STEAM ID
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
        print 'HERE'
        filePath = Document.objects.all().get().document.path
        Document.objects.all().delete()
        print filePath
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
            parseDemoFile(form.instance.document.path)
            return redirect('index')
    else:
        form = DocumentForm()
    return render(request, 'inHouseSite/model_form_upload.html', {
        'form': form
    })

def parseDemoFile(filePath):
    hlfinder = HighlightFinder(filePath)
    hlfinder.parse()
    hlfinder.storeResults()