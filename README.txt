The source file `missaal-eo.markdown` is generated elsewhere. It contains the whole content. It is split on 2nd-level headers using `mdsplit` (`python -m pip install mdsplit`) and then converted to html.

A sitemap is generated.

For each date (up till 2030), a page is created that redirects to the reading of that day (or the closest previous day that has a reading).

To generate the website:

`make clean`

`make`

`make htmls` (not sure why `make` doesn't do this...)

