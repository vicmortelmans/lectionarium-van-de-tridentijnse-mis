import re
import json
import logging
import bibleref as bibleref_module
from collection.data import getHtml, getJsonPath, getXml, getJsonPathPOST
import sys


class EmptyQueryOutput(Exception):
    pass


def log_to_stdout():
    # I use this function only when debugging in pdb
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log.addHandler(stream)


with open('bible_configuration/editions.json') as editions_file:
    editions = json.load(editions_file)
with open('bible_configuration/services.json') as services_file:
    services = json.load(services_file)


def trim(text):
    return re.sub(r"^\s+|\s+$", "", text)


def get_all_edition_service_pairs():
    # and add name to service object
    all_edition_service_pairs = []
    for iter_edition in editions:
        if "code" in iter_edition:
            for service_name in iter_edition["code"]:
                if service_name in services:
                    iter_service = services[service_name]
                    iter_service["name"] = service_name
                    all_edition_service_pairs.append((iter_edition, iter_service))
    return all_edition_service_pairs


def get_edition(edition_name):
    for iter_edition in editions:
        for iter_input in iter_edition["input"]:
            if iter_edition["input"][iter_edition].lower() == edition_name.lower():
                return iter_edition
    else:
        return None


def get_language(edition):
    return edition["language"]


def find_biblerefs(bibleref, language, tolerance_param):
    return bibleref_module.parse_reference(bibleref, language, tolerance_param)


def translate(text, conversion_dict):
    """
    https://stackoverflow.com/a/48953324/591336

    Translate words from a text using a conversion dictionary

    Arguments:
        text: the text to be translated
        conversion_dict: the conversion dictionary
    """
    # if empty:
    if not text: return text
    t = text
    for key, value in list(conversion_dict.items()):
        t = t.replace(key, str(value))
    return t


def process_step(step, url, book_code, edition_code, chapter, verse):
    translations = {
        "$url": url,
        "$book": book_code,
        "$edition": edition_code,
        "$chapter": chapter,
        "$passage": verse
    }
    if step["type"] == "json":
        url = translate(step["url"], translations)
        select = translate(step["select"], translations) if "select" in step else None
        parser = translate(step["parser"], translations) if "parser" in step else None
        return getJsonPath(url, select, parser)
    if step["type"] == "jsonpost":
        url = translate(step["url"], translations)
        data_string = translate(step["postdata"], translations)
        select = translate(step["select"], translations) if "select" in step else None
        parser = translate(step["parser"], translations) if "parser" in step else None
        return getJsonPathPOST(url, data_string, select, parser)
    elif step["type"] == "html":
        url = translate(step["url"], translations)
        select = translate(step["xpath"], translations)
        return getHtml(url, select)
    elif step["type"] == "xml":
        url = translate(step["url"], translations)
        select = translate(step["itemPath"], translations)
        return getXml(url, select)
    elif step["type"] == "url":
        url = translate(step["url"], translations)
        return url



def get_bible_text(edition_name, service_name, book_name, chapter, passage, bibleref_string, language="en", tolerance_param="false", chunksize=99, chunk=1):
    tolerance = tolerance_param
    if not edition_name and not language:
        language = "en"
    if not language and edition_name:
        language = get_language(get_edition(edition_name))
    all_edition_service_pairs = get_all_edition_service_pairs()
    edition_service_pairs = []
    for (iter_edition, iter_service) in all_edition_service_pairs:
        match_points = 0
        if language == iter_edition["language"]:
            match_points += 1
        if service_name and iter_service["name"].lower() == service_name.lower():
            match_points += 1
        if edition_name and edition_name in list(iter_edition["input"].values()):
            match_points += 1
        if match_points > 1:
            edition_service_pairs = [(iter_edition, iter_service)] + edition_service_pairs
        elif match_points > 0:
            edition_service_pairs.append((iter_edition, iter_service))
    if not tolerance_param:
        tolerance = "false"
    if not bibleref_string:
        if not book_name and not chapter:
            logging.error("At least a book and a chapter number should be provided")
            raise ValueError("At least a book and a chapter number should be provided")
        biblerefs = [{
            "book": book_name,
            "chapter": chapter,
            "verse": passage
        }]
        bibleref = book_name + ' ' + chapter + ':' + passage
    else:
        biblerefs = find_biblerefs(bibleref_string, tolerance_param=tolerance, language=language)
    logging.info("Fetching bible verses %s" % ", ".join([b["osisref"] for b in biblerefs]))
    local_biblerefs = find_biblerefs(bibleref_string, tolerance_param=tolerance, language=language)
    local_bibleref = local_biblerefs[0]["localbook"] + ' ' + local_biblerefs[0]["chapterversereference"]
    book_name = biblerefs[0]["book"]
    book = bibleref_module.find_book(book_name)
    logging.info("Using book %s" % book["input"][1])
    (edition, service) = edition_service_pairs.pop(0)
    while True:
        logging.info("Trying to fetch from edition %s and service %s" % (edition["input"]["input1"], service["name"]))
        book_code = book["code"][service["bookskey"]]
        edition_code = edition["code"][service["editionskey"]]["id"]
        verse_count = 0
        output = ""
        if chunk and chunksize:
            verse_chunk_start = (chunk - 1) * chunksize + 1
            verse_chunk_end = chunk * chunksize
        try:
            for bibleref_data in biblerefs:
                verse_count += 1
                if chunk and (verse_count < verse_chunk_start or verse_chunk_end < verse_count):
                    continue  # with next bibleref
                end_bibleref = bibleref_data  # just keep track, so I'll know in the end which verse was last
                url = ""
                for step in service["step"][:-1]:
                    # these steps return an url
                    url = process_step(step, url, book_code, edition_code, chapter=bibleref_data["chapter"], verse=bibleref_data["verse"]) or ""
                # the last step returns the data
                query_output = process_step(service["step"][-1], url, book_code, edition_code, chapter=bibleref_data["chapter"], verse=bibleref_data["verse"]) or ""
                query_output = trim(query_output)
                if not query_output:
                    raise EmptyQueryOutput("Output is empty")
                verse_indication = re.search(r'/^([0-9]+)', query_output)
                if verse_indication and verse_indication.group(1) == bibleref["verse"]:
                    query_output = re.sub(r'^[0-9]+[.\s]*', '', query_output)
                # extractPhrase not implemented
                output = output + query_output + ' '
            break  # all output collected, break the infinite while loop
        except (EmptyQueryOutput, KeyError, IndexError) as e:
            logging.warning("Service %s is not working (%s)" % (service["name"], e))
            if edition_service_pairs:
                (edition, service) = edition_service_pairs.pop(0)
                logging.warning("Going to use edition %s and service %s as fallback" % (edition["input"]["input1"], service["name"]))
                continue  # resume the while loop
            else:
                logging.error("No more service to use as fallback")
                raise
    if chunk and chunksize:
        remaining_verses_in_passage = max(0, verse_count - verse_chunk_end)
    else:
        remaining_verses_in_passage = 0
    output = trim(output)
    output = re.sub(r'\s+', ' ', output)  # replace exotic white-spacing by single space
    punctuation = re.search(r'([.?!,:;])$', output)
    if not punctuation:
        output = output + '.'
    elif re.search(r'[,:;]', punctuation.group(1)):
        output = re.sub(r'[,:;]', '.', output)
    # handling of curly quotes not implemented
    name = ''
    if 'input' in edition:
        input12 = 'input2' if 'input2' in edition['input'] else 'input1'
        name = edition['input'][input12]
    copyright = ''
    if 'copyright' in edition:
        copyright = edition['copyright']
    return {
        "bibleref": local_bibleref,
        "remainingversesinpassage": remaining_verses_in_passage,
        "remainingversesinchaper": end_bibleref["remainingverses"],
        "book": end_bibleref["book"],
        "chapter": end_bibleref["chapter"],
        "endverse": end_bibleref["verse"],
        "spoken": local_biblerefs[0]["spoken"],
        "passage": output,
        "name": name,
        "copyright": copyright
    }


def test_bible(bibleref_string):
    output = {}
    for edition in editions:
        edition_output = {}
        edition_name = edition["input"]["input1"]
        output[edition_name] = edition_output
        edition_output["language"] = edition["language"]
        if not "code" in edition:
            edition_output["status"] = "No services defined"
        else:
            for service_name in edition["code"]:
                service_output = {}
                edition_output[service_name] = service_output
                try:
                    json_output = get_bible_text(edition_name, service_name, None, None, None, bibleref_string)
                    service_output["output"] = json_output["passage"]
                except Exception as e:
                    service_output["status"] = "An error occurred: %s" % e
                    logging.exception(e)
    return output



