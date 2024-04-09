#!/bin/bash

# url configuration
URL="https://lectionarium.gelovenleren.net/"

# values: always hourly daily weekly monthly yearly never
FREQ="weekly"

# begin new sitemap
exec 1> sitemap.xml

# print head
echo '<?xml version="1.0" encoding="UTF-8"?>'
echo '<!-- generator="Milkys Sitemap Generator, https://github.com/mcmilk/sitemap-generator" -->'
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

# print urls
find . -type f -prune -name "*.md" -printf "%TY-%Tm-%Td%p\n" | \
while read -r line; do
  DATE=${line:0:10}
  FILEMD=${line:12}
  FILE=${FILEMD/.md/.html}
  FILE=${FILE#markdown/}
  echo "<url>"
  echo " <loc>${URL}${FILE}</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"
done

# print foot
echo "</urlset>"
