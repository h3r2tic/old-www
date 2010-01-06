import os
import os.path
import shutil
import textile

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


def formatTemplate(s, level):
	return s % {
		'siteRoot' : '../' * level
	}

def untabify(line, ts = 4):
	n = ''
	for c in line:
		if '\t' == c:
			l = len(n)
			n += ' ' * (ts - l % ts)
		else:
			n += c
	return n

def formatText(text):
	text2 = ''
	lines = text.splitlines()
	while len(lines):
		line = lines[0]
		if '{{{' == line[0:3]:
			lang = line[3:]
			lines = lines[1:]
			code = ''
			numLines = 0
			while True:
				line = lines[0]
				if '}}}' == line:
					break
				code += untabify(line) + '\n'
				lines = lines[1:]
				numLines += 1
			lexer = get_lexer_by_name(lang, stripall=True)
			code = highlight(code, lexer, HtmlFormatter())
			text2 += 'notextile. '
			ntx = 0
			for l in code.splitlines():
				if len(l.strip()) > 0:
					text2 += l + '\n'
					ntx = 0
				else:
					text2 += '&nbsp;\n'
			text2 += '\n\n'
			print 'Formatted %s lines of code' % numLines
			#print code
		else:
			text2 += line + '\n'
		lines = lines[1:]

	return textile.textile(text2)

def textile2html(dir, path, level):
	outfile = 'output/' + dir + path[:-8] + '.html'
	contents = formatTemplate(
		open('textileTemplatePrefix.txt').read(),
		level
	)

	assert path[-8:] == '.textile'
	contents += formatText(open('input/'+dir+path).read())

	contents += formatTemplate(
		open('textileTemplateSuffix.txt').read(),
		level
	)

	open(outfile, 'w').write(contents)


def dir_textile2html(dir, level = 0):
	for file in os.listdir('input/' + dir):
		if file[-8:] == '.textile':
			print dir+file
			textile2html(dir, file, level)
		elif os.path.isdir('input/' + dir + file):
			if dir != '.' and dir != '..':
				p = dir + file + '/'
				try:	os.makedirs('output/'+p)
				except:	pass
				dir_textile2html(p, level+1)
		elif file[-4:] != '.swp' and file != 'Thumbs.db':
			shutil.copyfile('input/' + dir + file, 'output/' + dir + file)


dir_textile2html('')

cmds = [
	r'cp -R slider output/slider',
	r'cp *.css *.js output/',
	r'cp headerBackground.png settingsIcon.png teapot.png output/',
]
for c in cmds:
	os.system(c)
	
