1. =missaal-eo= has an ant =build.xml= that
   1. uses =missaal-eo-markdown.xslt= to convert =canisius-met-correcties.xml= combined with liturgy and bible lookup tables to =missaal-eo.markdown=
      1. uses =bilberef-standalone= to run a web server that allows queries to "http://localhost:8080/yql/bibleref?language=nl&amp;xml=true&amp;bibleref="
   2. uses =pandoc= to convert that to =missaal-eo.pdf=.
2. [[https://github.com/vicmortelmans/lectionarium-van-de-tridentijnse-mis][vicmortelmans/lectionarium-van-de-tridentijnse-mis]] has a =Makefile+ that
   1. uses ~mdsplit~ to split =missaal-eo.markdown= into separate files in the =markdown= directory
   2. does some text replacements in =markdown/toc.md=
   3. copies =resources= in =docs= directory
   4. copies =index.md= in =docs= directory
   5. copies =CNAME= in =docs= directory
   6. runs ~sitemap.sh~ to generate =sitemap.xml=
   7. copies =sitemap.xml= and =robots.txt= in =docs= directory
   8. uses ~pandoc~ to convert =markdown/*.md= to =docs/*.html=
   9. uses =calendar-redirects.xslt= to generate =docs/YYYY-MM-DD.html= redirect files

The =docs= directory is served by github-pages.

Build workflow:

1. python3 -m venv env
2. source env/bin/activate
3. pip install -r requirements.txt
4. cd missaal-eo/bibleref-standalone
5. python main.py &
6. cd ..
7. ant
8. cp missaal-eo.markdown ../
9. cd ..
10. make clean
11. make

A sitemap is generated.

For each date (up till 2030), a page is created that redirects to the reading of that day (or the closest previous day that has a reading).
