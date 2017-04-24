#!usr/bin/python python

from google import search
import websocket
import threading
import json
import sys
import random
import time
import ssl

class ChatBot(threading.Thread):
	def __init__(self, BotName, Room):
		threading.Thread.__init__(self)

		self.trigger = '*'
		self.botname = BotName
		self.room = Room
		self.online = []

		self.bots = ['AtlasBot', 'coderRank', 'hatBot', 'modBot', 'TBotT', 'wwbot']
		self.botsInfo = {
			'AtlasBot': {
				'creator': 'Atlas',
				'version': '1.0',
				'trigger': '*'
			},
			'TBotT': {
				'creator': 'M4GNV5',
				'version': '?',
				'trigger': '!'
			},
			'wwbot': {
				'creator': 'wwandrew',
				'version': '1.5',
				'trigger': '#'
			}
		}

	# Commands

	def help_(self, data):
		self.sendMessage("Commands are: " + self.trigger + "help, "  + self.trigger + "info, "  + self.trigger + "slap.")

	def checkBots(self):
		onlineBots = set(self.bots) & set(self.online)
		if len(list(onlineBots)) == 0:
			self.sendMessage("There are no active bots in this room.")
		else:
			online = ("Yes. Current active bots are: " + ', '.join(onlineBots) + ". Type *info <botname> to see more information about bot")
			self.sendMessage(online)

	def checkMods(self):
		pass

	def info(self, data):
		if len(self.msg) == 1:
			self.sendMessage("Type *info <subject> for information about said subject.")
		else:
			if (self.msg[1] in self.bots) == True:
				info = "Info about " + self.msg[1] + ": " + str(self.botsInfo[self.msg[1]])
				self.sendMessage(info)

	# Chat

	def main(self, data):
		print(data['nick']) + ":"
		print(data['text'])

		self.splitData(data['text'])
		trig = ''.join(self.msg[0])
		self.trig = trig.split()[0][:1]

		if data['nick'] != self.botname:
			pass
			self.checkMessage(data)
			self.commands(data)


	def online_Set(self, data):
		self.online = data['nicks']
		print("[*] Users online:")
		for n in data['nicks']:
			print(n)

	def online_Add(self, data):
		self.online.append(data['nick'])
		print("[*] User " + data['nick'] + " joined.")

	def online_Remove(self, data):
		self.online.remove(data['nick'])
		print("[*] User " + data['nick'] + " left.")

	def handleInfo(self, data):
		print("[*] Unknown Info.")
		print(data)
	
	# Functions

	def ping(self):
		self.sendJSON({"cmd":"ping"})
		threading.Timer(30.0, self.ping).start()

	def sendJSON(self, data):
		self.ws.send(json.dumps(data))

	def sendMessage(self, data):
		self.ws.send(json.dumps({"cmd": "chat", "text": data}))

	def splitData(self, data):
		self.msg = (data.split())
		self.Lmsg = [x.lower() for x in self.msg]

	def checkMessage(self, data):

		if set(['are', 'there', 'any']) & set(self.Lmsg) == set(['are', 'there', 'any']):
			try:
				{
					'bots': self.checkBots,
					'mods': self.checkMods
				}[self.msg[3]]()
			except Exception as b:
				print b
		elif ('google' in self.Lmsg[0]) == True:
			results = [url for url in search(' '.join(self.msg[1:]), stop=1)]
			results = ', '.join(results[:1])
			self.sendMessage(results)

	def commands(self, data):
		if self.trig == self.trigger:
			try:
				{
					self.trigger + 'help': self.help_,
					self.trigger + 'info': self.info
				}[self.msg[0]](data)
			except Exception as a:
				if len(self.msg) == 1:
					self.sendMessage("Not a valid command.")
				else:
					pass

	# Websockets
	
	def on_message(self, wbsk, message):
		print
		data = json.loads(message)
		cmd = data['cmd']
		try:
			{
				"onlineSet":self.online_Set,
				"onlineAdd":self.online_Add,
				"onlineRemove":self.online_Remove,
				"chat":self.main,
				"info":self.handleInfo
			}[cmd](data)
		except Exception as e:
			print(e)

	def on_error(self, wbsk, error):
		print error

	def on_close(self, wbsk):
		print("Closed")

	def on_open(self, wbsk):
		self.sendJSON({"cmd": "join", "channel": self.room, "nick": self.botname})
		self.sendMessage("Type '*help' for help.")
		self.ping()

	def run(self):
		self.ws = websocket.WebSocketApp('wss://hack.chat/chat-ws', on_message = self.on_message, on_error = self.on_error, on_close = self.on_close)
		self.ws.on_open = self.on_open
		self.ws.run_forever(sslopt={"cert_reqs":ssl.CERT_NONE})

BotName = raw_input("Input Bot name and trip:: ")
Room = raw_input("Input room name:: ")

Bot = ChatBot(BotName, Room)
Bot.start()
