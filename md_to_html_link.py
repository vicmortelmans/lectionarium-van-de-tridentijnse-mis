import panflute as pf

def action(elem, doc):
    if isinstance(elem, pf.Link) and elem.url.endswith('.md'):
        elem.url = elem.url[:-3] + '.html'
    return elem

def main(doc=None):
    return pf.run_filter(action, doc=doc)

if __name__ == '__main__':
    main()

