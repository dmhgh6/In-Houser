from django.db import models
from django.dispatch import receiver
import os
# Create your models here.


class Player(models.Model):
    name = models.CharField(max_length=50)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    mvps = models.IntegerField(default=0)
    steamId = models.CharField(max_length=30, primary_key=True)
    roundsPlayed = models.IntegerField(default=0)
    roundsWon = models.IntegerField(default=0)
    gamesPlayed = models.IntegerField(default=0)
    gamesWon = models.IntegerField(default=0)

    @property
    def kda(self):
        if self.deaths != 0:
            return "{:.2f}".format(self.kills / float(self.deaths))
        else:
            return 0

    @property
    def mvpsGame(self):
        if self.gamesPlayed != 0:
            return "{:.2f}".format(self.mvps / float(self.gamesPlayed))
        else:
            return 0

    @property
    def roundWinPct(self):
        if self.roundsWon != 0:
            return "{:.1f}".format(self.roundsWon * 100 / float(self.roundsPlayed))
        else:
            return 0

    @property
    def killsRound(self):
        if self.roundsPlayed != 0:
            return "{:.2f}".format(self.kills / float(self.roundsPlayed))
        else:
            return 0

    @property
    def assistsRound(self):
        if self.roundsPlayed != 0:
            return "{:.2f}".format(self.assists / float(self.roundsPlayed))
        else:
            return 0

    @property
    def deathsRound(self):
        if self.roundsPlayed != 0:
            return "{:.2f}".format(self.deaths / float(self.roundsPlayed))
        else:
            return 0

    @property
    def gameWinPct(self):
        if self.gamesWon != 0:
            return "{:.1f}".format(self.gamesWon * 100 / float(self.gamesPlayed))
        else:
            return 0

    def __str__(self):
        return 'Name: ' + self.name


class Team(models.Model):
    playerOne = models.ForeignKey(Player, related_name='playerOne', on_delete=models.CASCADE)
    playerTwo = models.ForeignKey(Player, related_name='playerTwo', on_delete=models.CASCADE)
    playerThree = models.ForeignKey(Player, related_name='playerThree', on_delete=models.CASCADE)
    playerFour = models.ForeignKey(Player, related_name='playerFour', on_delete=models.CASCADE)
    playerFive = models.ForeignKey(Player, related_name='playerFive', on_delete=models.CASCADE)
    roundsWon = models.IntegerField(default=0)
    won = models.BooleanField(default=False)

    def __str__(self):
        return 'PlayerOneName: ' + self.playerOne.name


class Game(models.Model):
    map = models.CharField(max_length=50)
    date = models.DateField()
    teamOne = models.ForeignKey(Team, related_name='teamOne', on_delete=models.CASCADE)
    teamTwo = models.ForeignKey(Team, related_name='teamTwo', on_delete=models.CASCADE)
    roundsPlayed = models.IntegerField(default=0)

    def __str__(self):
        return 'Map: ' + self.map


class Document(models.Model):
    document = models.FileField(upload_to='documents/') #file path
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document.path