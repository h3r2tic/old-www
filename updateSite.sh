cd output

zip -9 -T siteUpdate `find . -iname '*.html' -or -iname '*_graph*.png' -or -iname '*.jpg'` *.css *.js
scp siteUpdate.zip h3gdpo@webhost.daily.co.uk:public_html/
rm siteUpdate.zip
ssh h3@team0xf.com "cd public_html && unzip -o siteUpdate.zip && rm siteUpdate.zip"

