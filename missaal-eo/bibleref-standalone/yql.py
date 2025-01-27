from bibleref import parse_reference
from flask import Response
import json
from lxml import etree
import urllib


def create_xml_tree(root, dict_tree):
    # Node : recursively create tree nodes
    # https://gist.github.com/kjaquier/1e61ff4054577c54960d
    if type(dict_tree) == dict:
        for k, v in dict_tree.items():
            if type(v) == list:
                for item in v:
                    create_xml_tree(etree.SubElement(root, k), item)
            else:
                create_xml_tree(etree.SubElement(root, k), v)
        return root
    # Leaf : just set the value of the current node
    else:
        try:
            root.text = dict_tree
        except TypeError:
            root.text = str(dict_tree)


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    Source : http://stackoverflow.com/questions/17402323/use-xml-etree-elementtree-to-write-out-nicely-formatted-xml-files
    """
    from xml.dom import minidom
    rough_string = etree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="".join([' '] * 4))


def yqlBibleRefHandler(request):
    # /yql/bibleref?bibleref=Mc+1,10-12&language=nl&tolerance=true&xml=true
    bibleref = urllib.parse.unquote(request.args.get('bibleref'))  # e.g. Mt+1:4-5
    language = urllib.parse.unquote(request.args.get('language'))  # e.g. nl
    try:
        tolerance_param = urllib.parse.unquote(request.args.get('tolerance'))  # e.g. true
    except TypeError:
        tolerance_param = "false"
    callback = request.args.get('callback')
    xml_requested = request.args.get('xml')
    yql_data = parse_reference(bibleref, language, tolerance_param)
    if xml_requested:
        query = etree.Element('query')
        results = etree.SubElement(query,'results')
        biblerefs = etree.SubElement(results,'biblerefs')
        xml_ready = {'bibleref': yql_data}
        create_xml_tree(biblerefs, xml_ready)
        response = etree.tostring(query, pretty_print=True)
        flask_response = Response(response)
        flask_response.headers['Content-Type'] = 'text/xml'
        return flask_response
    else:
        response = json.dumps(yql_data)
        if callback:
            response = callback + '(' + response + ')'
        flask_response = Response(response)
        flask_response.headers['Content-Type'] = 'application/json'
        return flask_response


