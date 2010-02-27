import os
import os.path
import shutil
import textile
import subprocess

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

disqusComments = '''<div id="disqus_thread"></div><script type="text/javascript" src="http://disqus.com/forums/h3r3ticsgrimoire/embed.js"></script><noscript><a href="http://disqus.com/forums/h3r3ticsgrimoire/?url=ref">View the discussion thread.</a></noscript>'''


def formatTemplate(s, level, curPage, wantComments):
	global disqusComments
	return s % {
		'siteRoot' : '../' * level,
		'currentPage' : curPage,
		'disqusComments' : (disqusComments if wantComments else '')
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

def generateGraph(code, outname, i):
	fname = '%s_graph%s.png' % (outname, i)
	args = 'dot -Lg -Tpng -o ' + fname
	proc = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE)
	pipe = proc.stdin
	pipe.write(code)
	pipe.close()
	proc.wait()
	return 'p=. !%s!\n\n' % fname


def formatText(text, outname, wantComments):
	text2 = ''
	lines = text.splitlines()
	graphCntr = 0
	lineNr = -1

	while len(lines):
		lineNr += 1
		line = lines[0]

		if 'disqus' == line:
			assert 0 == lineNr
			wantComments[0] = True
		elif '{{{' == line[0:3]:
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
			if lang[0:3] == "dot":
				params = lang[3:].strip().split(' ')
				prefix = ''
				suffix = ''
				for p in params:
					if "digraph" == p:
						prefix = 'Digraph G {' + prefix
						suffix += '}'
					elif "std" == p:
						prefix += '''
							graph [concentrate=false, remincross=true, labeljust=l, rankdir=LR, ratio=compress, nodesep=0.5, fontname=Verdana, fontsize=12, fontcolor="#e0e0e0", bgcolor="#282828", pad=0.2];
							style = "filled,rounded"
							fillcolor = "#383838";

							node [
								shape = "Mrecord"
								fontname = "Verdana"
								fontsize = 12
								style = "filled"
								color = "#e0e0e0"
							];

							edge [
								fontname = "Verdana"
								fontsize = 10
								color = "#f0f0f0"
							];
						'''
					else: assert false, p
				text2 += generateGraph(prefix + code + suffix, outname, graphCntr)
				graphCntr += 1
			else:
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
	outname = path[:-8]
	outfile = 'output/' + dir + outname + '.html'

	assert path[-8:] == '.textile'
	inputData = open('input/'+dir+path).read()

	curDir = os.getcwd()
	os.chdir('output/'+dir)
	wantComments = [False]
	contentsBody = formatText(inputData, outname, wantComments)
	wantComments = wantComments[0]
	os.chdir(curDir)

	contentsPrefix = formatTemplate(
		open('textileTemplatePrefix.txt').read(),
		level,
		dir + outname,
		wantComments
	)

	contentsSuffix = formatTemplate(
		open('textileTemplateSuffix.txt').read(),
		level,
		dir + outname,
		wantComments
	)

	contents = contentsPrefix + contentsBody + contentsSuffix

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
	
