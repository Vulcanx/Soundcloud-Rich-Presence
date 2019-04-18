import pypresence as pp
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
import win32gui, win32process
import re
from time import time
import os

subprocess.Popen([R"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "--new-window", "https://soundcloud.com/you/likes"])
pid, hWnd = None, None
song = {'start': None, 'title': None}

def cb(handle, windows):
	global pid, hWnd, song
	text = win32gui.GetWindowText(handle)
	_pid = win32process.GetWindowThreadProcessId(handle)[1]
	if pid is None and hWnd is None: # look for window we need to watch
		for n in ['SoundCloud', 'Google Chrome']:
			if not n in text:
				return
		pid = _pid
		hWnd = handle
		windows.append((text,))
	elif _pid == pid and hWnd == handle: # make sure we only look at the window we want
		text = text.replace(' - Google Chrome', '')
		song_name = text[:text.find(' by ')] if text.find(' by ') != -1 else '' # spaghetti
		artist = text[text.find(' by ') + 4:] if text.find(' by ') != -1 else '' # spaghetti
		if artist != '' and song_name != '':
			windows.append((song_name, artist))
			# new song found, update title and start time
			if not song or song['title'] != song_name:
				song = {'start': int(time()), 'title': song_name}
		else:
			windows.append(('Idle',))
			song = {'start': None, 'title': None}

p = pp.Presence(client_id=565382800010641429)
p.connect()

def update():
	windows = []
	win32gui.EnumWindows(cb, windows)
	if windows:
		if windows[0][0] == 'Idle' or 'SoundCloud' in windows[0][0]:
			p.update(pid=pid, large_image='img', state='  ', details='Idle')
		else:
			p.update(pid=pid, large_image='img', state=windows[0][0], details=windows[0][1], start=song and song['start'] or None, end=None)
	else:
		os.kill(os.getpid(), 1)

s = BlockingScheduler()
s.add_job(update, 'interval', seconds=1)
s.start()