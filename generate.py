import os
import os.path
import shutil


def formatTemplate(s, level):
	return s % {
		'siteRoot' : '../' * level
	}

def rst2html(dir, rst, level):
	outfile = 'output/' + dir + rst[:-4] + '.html'
	contents = formatTemplate(
		open('rstTemplatePrefix.txt').read(),
		level
	)

	assert rst[-4:] == '.rst'
	cmd = r'C:\dload\docutils-snapshot\docutils\tools\rst2html.py '
	cmd += '--template=rstTemplate.txt '
	cmd += 'input/' + dir + rst + ' '
	contents += os.popen(cmd).read()

	contents += formatTemplate(
		open('rstTemplateSuffix.txt').read(),
		level
	)

	open(outfile, 'w').write(contents)


def dir_rst2html(dir, level = 0):
	for file in os.listdir('input/' + dir):
		if file[-4:] == '.rst':
			print dir+file
			rst2html(dir, file, level)
		elif os.path.isdir('input/' + dir + file):
			if dir != '.' and dir != '..':
				p = dir + file + '/'
				try:	os.makedirs('output/'+p)
				except:	pass
				dir_rst2html(p, level+1)
		elif file[-4:] != '.swp':
			shutil.copyfile('input/' + dir + file, 'output/' + dir + file)


dir_rst2html('')

cmds = [
	r'cp -R slider output/slider',
	r'cp *.css *.js output/',
	r'cp headerBackground.png settingsIcon.png teapot.png output/',
]
for c in cmds:
	os.system(c)
	
