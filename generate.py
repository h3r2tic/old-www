import os
import os.path
import shutil
import textile
import subprocess

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

disqusComments = '''<div id="disqus_thread"></div><script type="text/javascript" src="http://disqus.com/forums/h3r3ticsgrimoire/embed.js"></script><noscript><a href="http://disqus.com/forums/h3r3ticsgrimoire/?url=ref">View the discussion thread.</a></noscript>'''


class CodegenConf(object):
	def __init__( self, dir, path, level, ver_num ):
		self.dir = dir
		self.path = path
		self.level = level
		self.outname = path[:-8]
		self.outfile = 'output/' + dir + self.outname + '.html'
		self.mtime = os.stat( 'input/' + dir + path ).st_mtime + ver_num
		try:
			self.out_of_date = os.stat( self.outfile ).st_mtime + 0.001 < self.mtime
		except IOError:
			self.out_of_date = True


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
	os.utime( outname, (conf.mtime,) * 2 )
	return 'p=. !%s!\n\n' % fname

def generateLaTeX(code, outname, i, conf):
	with open( 'latextemp.tex', 'w' ) as f:
		f.write( code )
	os.system( 'latex -quiet latextemp.tex' )
	fname = '%s_graph%s.png' % (outname, i)
	cmd = 'dvipng -T tight -D 190 --gamma 1.0 --truecolor -q -o %s latextemp.dvi 1>NUL' % fname
	os.system( cmd )
	os.system( cmd )
	os.utime( fname, (conf.mtime,) * 2 )
	return 'p(formula)=. !%s!\n\n' % fname

def formatText(text, outname, wantComments, conf):
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
			elif lang[0:3] == "tex":
				params = lang[3:].strip().split(' ')
				prefix = r'''
					\documentclass{article}
					\usepackage[active]{preview}
					\usepackage{color}
					\begin{document}
					\begin{preview}
					\definecolor{bggray}{rgb}{0.215,0.215,0.215}
					\pagecolor{bggray}
					\setlength\fboxsep{4.0pt}
					\setlength\fboxrule{0.2pt}
					\color{bggray}
					\fbox{
					\[
					\textcolor{white}{$
				'''
				suffix = r'''$}
					\]
					}
					\end{preview}
					\end{document}
				'''
				text2 += generateLaTeX(prefix + code + suffix, outname, graphCntr, conf)
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


def textile2html( conf ):
	outname = conf.outname
	outfile = conf.outfile

	assert conf.path[-8:] == '.textile'
	inputData = open('input/'+conf.dir+conf.path).read()

	curDir = os.getcwd()
	os.chdir('output/'+conf.dir)
	wantComments = [False]
	contentsBody = formatText(inputData, outname, wantComments, conf)
	wantComments = wantComments[0]
	os.chdir(curDir)

	contentsPrefix = formatTemplate(
		open('textileTemplatePrefix.txt').read(),
		conf.level,
		conf.dir + outname,
		wantComments
	)

	contentsSuffix = formatTemplate(
		open('textileTemplateSuffix.txt').read(),
		conf.level,
		conf.dir + outname,
		wantComments
	)

	contents = contentsPrefix + contentsBody + contentsSuffix

	open(outfile, 'w').write(contents)
	return outfile

codegen_vernum = 0

def dir_textile2html(dir, level = 0):
	for file in os.listdir('input/' + dir):
		is_dir = False
		src_file = 'input/' + dir + file
		dst_file = None
		dst_mtime = None
		if file[-8:] == '.textile':
			conf = CodegenConf( dir, file, level, codegen_vernum )
			if conf.out_of_date:
				dst_file = textile2html( conf )
				dst_mtime = conf.mtime
				print '   ', dir+file, 'is out of date; generating.'
			else:
				print '   ', dir+file, 'is up to date.'
				continue
		elif os.path.isdir('input/' + dir + file):
			is_dir = True
			if dir != '.' and dir != '..':
				p = dir + file + '/'
				try:	os.makedirs('output/'+p)
				except:	pass
				dir_textile2html(p, level+1)
		elif file[-4:] != '.swp' and file != 'Thumbs.db':
			dst_file = 'output/' + dir + file
			shutil.copyfile('input/' + dir + file, dst_file)
			dst_mtime = os.stat( src_file ).st_mtime

		if not is_dir:
			os.utime( dst_file, (dst_mtime,) * 2 )

print 'Generating website data...'

dir_textile2html('')

print 'Copying misc files...'

cmds = [
	r'cp -pR slider output/slider',
	r'cp -p *.css *.js output/',
	r'cp -p headerBackground.png settingsIcon.png teapot.png output/',
]
for c in cmds:
	print '   ', c
	os.system(c)
	
print 'Done.'