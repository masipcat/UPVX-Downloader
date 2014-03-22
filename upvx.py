#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, os, sys, re
from urllib import urlopen
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup
from pytube import YouTube

print """ _   _ ______     ___  __
| | | |  _ \ \   / | \/ /
| | | | |_) \ \ / / \  / 
| |_| |  __/ \ V /  /  \ 
 \___/|_|     \_/  /_/\_\


Version 0.6.1 αlpha
Developed by Jordi Masip (jordi.masip.cat)"""

# =======================================================================================================
# S'HA DE MODIFICAR AQUESTA VARIABLE
# ACSID és el TOKEN de GOOGLE que et permet entrar al curs
# Heu d'anar al navegador i un cop iniciada sessió a la pàgina del curs s'ha de copiar la cookie
# ACSID={el token del teu compte aqui}
# ========================================================================================================
plain_cookies = "ACSID="

def isValidUrl(url):
	# thanks to django team
	regex = re.compile(
		r'^(?:http|ftp)s?://'
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
		r'localhost|' #localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
		r'(?::\d+)?'
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)
	return regex.match(url)

def find_between(s, first, last):
	try:
		start = s.index(first) + len(first)
		end = s.index(last, start)
		return s[start:end]
	except ValueError:
		return ""

def save_video(url, lesson_name, filename):
	if not os.path.exists(lesson_name):
		os.makedirs(lesson_name)

	path = lesson_name + "/" + filename

	if not os.path.exists(path):
		print "[Downloading '{0}'...]".format(filename)
		f = open(path, 'wb')
		f.write(urlopen(url).read())
		f.close()
	else:
		print "[Skipped '{0}']".format(filename)

def die(msg):
	print msg
	sys.exit(1)

if plain_cookies == "":
	die("\n[ERROR] You must set 'plain_cookies'")

plain_cookies = plain_cookies.split(";")
cookies = {}
for k, v in [c.split("=") for c in plain_cookies]:
	cookies[k] = v.strip()

print "\nType course URL (like http://cursointroduccionandroid.upvx.es/unit?unit=2)",
while True:
	courseURL = raw_input("\n> Course URL: ")

	if not isValidUrl(courseURL):
		print "[ERROR] '{0}' ins't a valid URL".format(courseURL)
		continue
	
	domain = urlparse(courseURL)
	domain = domain.scheme + "://" + domain.netloc
	
	print "\n[Getting course info...]"
	r = requests.get(courseURL, cookies=cookies)

	if "google" in urlparse(r.url).netloc:
		die("[ERROR] Cookie token expired")

	bs = BeautifulSoup(r.content)
	lesson_title = bs.findAll("h1")[0].renderContents().split("-")[0].strip()
	if lesson_title == "":
		die("[ERROR] This course seems it is invalid")

	menu = bs.findAll("div", attrs={"id":"gcb-nav-y"})
	if len(menu) == 0:
		die("[ERROR] Menu not found in lesson {0}".format(lesson_title))

	li = menu[0].findAll("li")
	if len(li) == 0:
		die("[ERROR] Units not found in this lesson {0}".format(lesson_title))

	leccions = {}

	for item in li:
		a = item.findAll("a")
		if len(a) != 0:
			title = a[0].renderContents().strip()
			if title != "Actividad":
				k, v = title.split("<br />")
				leccions[k] = {"name": v, "url": domain + a[0]["href"]}

	print "\n[Searching for videos in lesson '{0}'...]".format(lesson_title)
	
	for name, v in leccions.items():
		print "- {0}:".format(name),
		r = requests.get(v["url"], cookies=cookies);
		r.encoding = "utf-8"
		bs = BeautifulSoup(r.content)
		iframes = bs.findAll("iframe")
		
		if len(iframes) == 0:
			print " [no video in this unit]"
			continue
		try:
			yt = YouTube()
			yt.url = "http://www.youtube.com/watch?v={0}".format(find_between(iframes[0]["src"], "embed/", "?"))
			video = yt.filter("mp4")
			leccions[name]["mp4"] = video.url if isinstance(video, str) else video[-1].url
			save_video(leccions[name]["mp4"], lesson_title, "{0} - {1}.mp4".format(name, leccions[name]["name"]))
		except Exception as e:
			print "[ERROR] Unknown error: {0}".format(e)
	
	print "GOOD BYE! ;)"