#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, os, sys, re, json
from urllib import urlopen
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup
from pytube import YouTube
import mechanize

print """ooooo     ooo ooooooooo.   oooooo     oooo ooooooo  ooooo 
`888'     `8' `888   `Y88.  `888.     .8'   `8888    d8'  
 888       8   888   .d88'   `888.   .8'      Y888..8P    
 888       8   888ooo88P'     `888. .8'        `8888'     
 888       8   888             `888.8'        .8PY888.    
 `88.    .8'   888              `888'        d8'  `888b   
   `YbodP'    o888o              `8'       o888o  o88888o 

Versió 0.7b
Desenvolupat per Jordi Masip (jordi.masip.cat)""".decode("utf-8")

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

def googleLogin():
	print u"\nCarregant l'inici de sessió de Google..."

	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [("User-agent", u"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0")]
	response = br.open(courseURL)

	logged_in = False
	while not logged_in:
		if config["account"] == "":
			account = raw_input("\n> Compte de Google: ")
		else:
			account = config["account"]
			print u"\n  Compte de Google: {0}".format(account)
		
		pswd = raw_input("> Contrasenya (desenmascarada): ")

		print u"\nIniciant sessió al compte de Google..."
		
		for form in br.forms():
			if form.attrs['id'] == 'gaia_loginform':
				br.form = form
				break
		else:
			die(u"  error: no s'ha pogut iniciar sessió, sembla ser que la pàgina no té el formulari d'inici de sessió (1)")
		
		br.form.find_control("Email").value = account
		br.form.find_control("Passwd").value = pswd
		response = br.submit()
		if response.read().count("error-msg") > 1:
			print u"  error: el compte de Google o la contrasenya és incorrecta"
		else:
			logged_in = True
	
	config["account"] = account
	
	try:
		br.form = list(br.forms())[0]
		response = br.submit(id='approve_button')
		g_cookies = br._ua_handlers['_cookies'].cookiejar
		for c in g_cookies:
			if c.name == "ACSID":
				config["ACSID"] = c.value
				saveConfig("config.json", config)
				break
		else:
			die(u"  error: no s'ha pogut iniciar sessió, sembla ser que la pàgina no té el formulari d'inici de sessió (2)")
	except Exception as e:
		die(u"  error: no s'ha pogut iniciar sessió, sembla ser que la pàgina no té el formulari d'inici de sessió (3)")

	return response.read()

def loadConfig(fn):
	if not os.path.isfile(fn):
		with open(fn, "w") as f:
			f.write("{}")
	try:
		with open(fn, "r") as f:
			return json.load(f)
	except IOError as e:
		die(u"  error: no s'ha pogut obrir el fitxer '{0}'".format(fn))
	except Exception as e:
		die(u"  error: no s'ha pogut carregar la configuració ({0})".format(e))

def saveConfig(fn, c):
	try:
		with open(fn, "w") as f:
			f.write(json.dumps(c))
	except IOError as e:
		die(u"  error: no s'ha pogut desar el fitxer '{0}'".format(fn))
	except Exception as e:
		die(u"  error: no s'ha pogut carregar la configuració ({0})".format(e))

def find_between(s, first, last):
	try:
		start = s.index(first) + len(first)
		end = s.index(last, start)
		return s[start:end]
	except ValueError:
		return ""

def save_video(url, lesson_name, filename):
	filename = filename.decode("utf-8")
	if not os.path.exists(lesson_name):
		os.makedirs(lesson_name)

	path = lesson_name + "/" + filename

	if not os.path.exists(path):
		print u"Baixant '{0}'...".format(filename)
		f = open(path, 'wb')
		f.write(urlopen(url).read())
		f.close()
	else:
		print u"El vídeo '{0}' ja ha estat baixat".format(filename)

def die(msg=""):
	if msg != u"": print msg
	sys.exit(0 if msg == "" else 1)

# Load user configuration from file
config = loadConfig("config.json")
config["account"] = "" if not config.has_key("account") else config["account"]
config["ACSID"] = "" if not config.has_key("ACSID") else config["ACSID"]

print u"\nEscriu la URL de la unitat, per exemple:\n  http://cursointroduccionandroid.upvx.es/unit?unit=2"

while True:
	courseURL = raw_input("\n> URL de la unitat: ")

	if not isValidUrl(courseURL):
		print u"  error: la URL té un format invàlid"
		continue
	
	domain = urlparse(courseURL)
	domain = domain.scheme + "://" + domain.netloc

	if config["ACSID"] == "":
		bs = BeautifulSoup(googleLogin())
	else:
		print u"\nObtenint informació del curs..."

		r = requests.get(courseURL, cookies={"ACSID": config["ACSID"]})

		if "google" in urlparse(r.url).netloc:
			bs = BeautifulSoup(googleLogin())
		else:
			bs = BeautifulSoup(r.content)

	unit_title = bs.findAll("h1")[0].renderContents().split("-")[0].strip()
	if unit_title == "":
		die(u"  error: aquesta unitat sembla ser invàlida")

	menu = bs.findAll("div", attrs={"id":"gcb-nav-y"})
	if len(menu) == 0:
		die(u"  error: no s'ha trobat cap menú a aquesta unitat")

	li = menu[0].findAll("li")
	if len(li) == 0:
		die(u"  error: no s'ha trobat cap lliçó a aquesta unitat")

	lessons = {}

	for item in li:
		a = item.findAll("a")
		if len(a) != 0:
			title = a[0].renderContents().strip()
			if title != "Actividad":
				k, v = title.split("<br />")
				lessons[k] = {"name": v, "url": domain + a[0]["href"]}

	total_lessons = len(lessons.keys())

	print u"S'han trobat {0} lliçons!".format(total_lessons)
	print u"Estem cercant vídeos a cada lliçó...\n"
	
	i = 1
	for name, v in lessons.items():
		print u"({0}/{1})".format(i, total_lessons),
		r = requests.get(v["url"], cookies={"ACSID": config["ACSID"]});
		r.encoding = "utf-8"
		bs = BeautifulSoup(r.content)
		iframes = bs.findAll("iframe")
		
		i += 1

		if len(iframes) == 0:
			print u"No s'ha trobat cap vídeo a aquesta lliçó"
			continue
		try:
			yt = YouTube()
			yt.url = u"http://www.youtube.com/watch?v={0}".format(find_between(iframes[0]["src"], "embed/", "?"))
			video = yt.filter("mp4")
			lessons[name]["mp4"] = video.url if isinstance(video, str) else video[-1].url
			save_video(lessons[name]["mp4"], unit_title, "{0} - {1}.mp4".format(name, lessons[name]["name"]))
		except Exception as e:
			print u"error: {0}".format(e)