cd output

zip -9 -T siteUpdate `find . -iname '*.html'`
scp siteUpdate.zip h3@team0xf.com:public_html/
rm siteUpdate.zip
ssh h3@team0xf.com "cd public_html && unzip -o siteUpdate.zip && rm siteUpdate.zip"

#for f in `find output -iname "*.html"`
#do
#	path=`dirname $f | sed -e 's/^output//g'`
#	fname=`basename $f`
#	remotePath=public_html${path}/
#	echo $f
#	echo ${remotePath}
#done
