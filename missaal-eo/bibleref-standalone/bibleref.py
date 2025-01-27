import re
import logging
from lxml import etree
from itertools import permutations
import sys
import json


chapterseparator = ''
listseparator = ''
rangeseparator = ''
chapterversereference = ''
openchapter = ''
book = ''
localbook = ''
spokenbook = ''
osisbook = ''
bookoutlinerecord = {}
tolerance = ''
with open('bible_configuration/books.json') as books_file:
    books = json.load(books_file)
with open('bible_configuration/bible-outline.json') as bible_outline_file:
    bible_outline = json.load(bible_outline_file)


"""
  DEBUGGING TIPS
* entry point is parse_reference()
* example:
    print(json.dumps(parse_reference("Mc 1:2a-4b", language="nl"), indent=2))
* easy debugging xml by printing etree.tostring(...)
"""


def find_book(name):
    matching_books = []
    for book in books:
        for iter_input in book["input"]:
            if iter_input.lower() == name.lower():
                matching_books.append(book)
    if matching_books:
        return matching_books[0]
    else:
        logging.error("No book found with name %s" % name)
        raise ValueError("No book found with name %s" % name)


def find_book_outline(osisbook):
    for book in bible_outline:
        if book["name"] == osisbook:
            return book
    else:
        logging.error("No book outline found with name %s" % osisbook)
        raise ValueError("No book outline found with name %s" % osisbook)


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)


def log_to_stdout():
    # I use this function only when debugging in pdb
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log.addHandler(stream)


def split_on_first_re(string, regex):
    split = re.split(regex, string, maxsplit=1)
    return {'before': split[0], 'after': split[1]}


def deromanize(str):
    # return value is a number!
    str = str.upper()
    validator = r'^M*(?:D?C{0,3}|C[MD])(?:L?X{0,3}|X[CL])(?:V?I{0,3}|I[XV])$'
    token = r'[MDLV]|C[MD]?|X[CL]?|I[XV]?'
    key = {'M': 1000, 'CM': 900, 'D': 500, 'CD': 400, 'C': 100, 'XC': 90, 'L': 50, 'XL': 40, 'X': 10, 'IX': 9, 'V': 5, 'IV': 4, 'I': 1}
    num = 0
    if not str or not re.search(validator, str):
        logging.error("Not a valid roman number: " + str)
        raise ValueError("Not a valid roman number")
    for m in re.findall(token, str):
        num += key[m]
    return num


def getosisbook(bookrecord):
    for code in bookrecord["code"]:
        if code == "osis":
            return bookrecord["code"][code]
    else:
        logging.error("No osis code found for %s" % bookrecord["input"][0])


def getlocalbook(bookrecord, lang):
    for code in bookrecord["language"]:
        if code == lang:
            return bookrecord["language"][lang]
    else:
        logging.error("No local book name found for %s in %s" % (bookrecord["input"][0], lang))


def getspokenbook(bookrecord, lang):
    for code in bookrecord["spoken"]:
        if code == lang:
            return bookrecord["spoken"][lang]
    else:
        logging.error("No spoken book name found for %s in %s" % (bookrecord["input"][0], lang))


def get_number_of_verses(bookoutlinerecord, chapternr):
    if chapternr > len(bookoutlinerecord["chapter"]):
        logging.info("Invalid chapter number: %s" % chapternr)
        raise ValueError("Invalid chapter number: %s" % chapternr)
    try:
        number_of_verses = int(bookoutlinerecord["chapter"][chapternr - 1]["number_of_verses"])
    except IndexError:
        raise ValueError("Chapter %s not found in book %s" % (chapternr, book))
    logging.info("Number of verses in chapter %s is %s" % (chapternr, number_of_verses))
    return number_of_verses


# functions for determining the function of separators

def getOccuringCharacters(string, chars):
    intersection = set(chars).intersection(set(string))
    return "".join(intersection)


def getPermutations(separators):
    return [''.join(p) for p in permutations(separators)]


def getProbability(separatorPermutation):
    separatorProbability = {}
    logging.info("Calculating probability for " + separatorPermutation)
    separatorProbability['-'] = {'chapter': 1, 'list': 4, 'range': 9}
    separatorProbability['.'] = {'chapter': 8, 'list': 3, 'range': 5}
    separatorProbability[','] = {'chapter': 7, 'list': 8, 'range': 0}
    separatorProbability[';'] = {'chapter': 6, 'list': 9, 'range': 0}
    separatorProbability[':'] = {'chapter': 9, 'list': 5, 'range': 2}
    separatorProbability['/'] = {'chapter': 4, 'list': 2, 'range': 1}
    separatorProbability[' '] = {'chapter': 5, 'list': 3, 'range': 0}
    separatorProbability['#'] = {'chapter': 0, 'list': 0, 'range': 0}
    # calculate probability based on occurring separators
    probability = separatorProbability[separatorPermutation[0]]['chapter'] + \
        separatorProbability[separatorPermutation[1]]['list'] + \
        separatorProbability[separatorPermutation[2]]['range']
    logging.info("Probability for %s = %s" % (separatorPermutation, probability))
    return probability


def getSeparators(string):
    separatorPermutationProbability = {}
    separators = getOccuringCharacters(string,'-.,;:/ ')
    logging.info("Separators : " + separators)
    if len(separators) > 3:
        logging.error("Invalid bible reference - too many different separators %s" % str)
        raise ValueError("Invalid bible reference - too many different separators")
    separators = separators.rjust(3, '#')
    separatorPermutations = getPermutations(separators)
    logging.info("Permutations # : %s" % len(separatorPermutations))
    for separatorPermutation in separatorPermutations:
        separatorPermutationProbability[separatorPermutation] = getProbability(separatorPermutation)
    separatorPermutationOrder = \
            [key for key, value in sorted(separatorPermutationProbability.items(), key=lambda k_v: k_v[1], reverse=True)]
    return separatorPermutationOrder


def split_on_first_char(string, character):
    split = re.split(re.escape(character), string, maxsplit=1)
    return {'before': split[0], 'after': split[1] if len(split) > 1 else ''}



def parse_chapter(string):
    # return value is a number!
    global chapterversereference
    logging.info("parse_chapter %s" % string)
    if re.search(r'^[0-9]+$', string):
         chapter = int(string)
    elif re.search(r'^[ivxlc]+$', string, flags=re.IGNORECASE):
         chapter = deromanize(string)
         chapterversereference = re.sub(string, str(chapter), chapterversereference)
    else:
         raise ValueError("Fallback: Not a chapter number: %s" % string)
    return chapter


def parse_verse(string):
    logging.info("parse_verse %s" % string)
    if not re.search(r'^[0-9]+[a-z]?$', string):
        raise ValueError("Fallback: Not a verse number: %s" % string)
    if re.search(r'[a-z]', string):
        logging.info("number %s, phrase %s" % (string[0:-1], string[-1]))
        return {'number': int(string[0:-1]), 'phrase': string[-1]}
    else:
        return {'number': int(string), 'phrase': ''}


def parse_location(mode, location):
    global chapterversereference
    global openchapter
    logging.info("parse_location %s %s" % (mode, location))
    split = split_on_first_char(location, chapterseparator)
    if mode == "explicit" and not split['after']:
        raise ValueError("Fallback: Missing verse number: %s" % location)
    elif mode == "explicit" or split['after']:
        chapter = parse_chapter(split['before'])
        verse = parse_verse(split['after'])
    else:
        chapter = openchapter
        verse = parse_verse(split['before'])
    if not verse:
        raise ValueError("Fallback: invalid verse number: %s" % location)
    number_of_verses = get_number_of_verses(bookoutlinerecord, chapter)
    if mode == "explicit" and verse['number'] > number_of_verses:
        raise ValueError("Fallback: non-existent verse: %s (chapter has %s verses)" % (verse['number'], number_of_verses))
    if tolerance == "true" and mode == "implicit" and verse['number'] > number_of_verses:
        # although it's wrong, I'm accepting it as 'till end of chapter'
        chapterversereference = re.sub(str(verse['number']), str(number_of_verses), chapterversereference)
        verse['number'] = number_of_verses
    verse['remainingverses'] = number_of_verses - int(verse['number'])
    openchapter = chapter
    return {'chapter': chapter, 'verse': verse}


def verseinbook(chapter, verse):
    sum = 0;
    #import pdb; pdb.set_trace()
    for c in bookoutlinerecord["chapter"]:
        if int(c["number"]) < chapter:
            sum += int(c["number_of_verses"])
    sum += verse
    return sum


def listrecord(book, chapter, verse, phrase, osisbook, remainingverses):
    v = verseinbook(chapter, verse)
    return {
        'book': book,
        'localbook': localbook,
        'osisbook': osisbook,
        'chapterversereference': chapterversereference,
        'verseinbook': v,
        'chapter': chapter,
        'verse': verse,
        'phrase': phrase,
        'osisref': "%s.%s.%s%s%s" % (osisbook, chapter, verse, '!' if phrase else '', phrase),
        'sequence': osisbook + str(1000000 + 1000 * chapter + verse),
        'remainingverses': remainingverses,
        'spoken': spokenbook
    }


def parse_range(mode, rng):
    logging.info("parse_range %s" % rng)
    list = []
    split = split_on_first_char(rng, rangeseparator)
    begin = parse_location(mode, split['before'])
    if split['after']:
        end = parse_location("implicit", split['after'])
    else:
        end = begin
    if begin['chapter'] > end['chapter']:
        raise ValueError("Fallback: Invalid bible chapter range")
    logging.info("iterating chapters %s to %s" % (begin['chapter'], end['chapter']))
    for chapter in range(begin['chapter'], end['chapter'] + 1):
        number_of_verses = get_number_of_verses(bookoutlinerecord, chapter)
        chapterbeginversenumber = begin['verse']['number'] if chapter == begin['chapter'] else 1
        chapterendversenumber = end['verse']['number'] if chapter == end['chapter'] else number_of_verses
        if chapterbeginversenumber > chapterendversenumber:
            raise ValueError("Fallback: Invalid bible verse range")
        logging.info("iterating verses %s to %s" % (chapterbeginversenumber, chapterendversenumber))
        for versenumber in range(chapterbeginversenumber, chapterendversenumber + 1):
            # for all versesnumbers in the chapter
            if begin['chapter'] == end['chapter'] and begin['verse']['number'] == end['verse']['number']:
                # if begin and end verse are the same
                if bool(begin['verse']['phrase']) ^ bool(end['verse']['phrase']):  #  implementation of XOR
                    # if only one of begin and end verses have a phrase letter
                    raise ValueError("Fallback: Invalid reference; to indicate a range within a verse: Ester 8:9a-9b")
                elif begin['verse']['phrase']:
                    # if both begin and end verse have a phrase letter
                    phrases = "abcdefghijkl"
                    for phrase in char_range(begin['verse']['phrase'], end['verse']['phrase']):
                        logging.info("adding [1] %s | %s | %s%s | %s" % (book, chapter, begin['verse']['number'], phrase, osisbook))
                        list.append(listrecord(book, chapter, begin['verse']['number'], phrase, osisbook, end['verse']['remainingverses']))
                else:
                    # if neither begin or end verse have a phrase letter
                    logging.info("adding [2] %s | %s | %s%s | %s" % (book, chapter, begin['verse']['number'], begin['verse']['phrase'], osisbook))
                    list.append(listrecord(book, chapter, begin['verse']['number'], begin['verse']['phrase'], osisbook, end['verse']['remainingverses']))
            else:
                # if begin and end verse are different
                phrase = ''
                if chapter == begin['chapter'] and versenumber == begin['verse']['number']:
                    phrase = begin['verse']['phrase'] + '-' if begin['verse']['phrase'] else ''
                elif chapter == end['chapter'] and versenumber == end['verse']['number']:
                    phrase = '-' + end['verse']['phrase'] if end['verse']['phrase'] else ''
                logging.info("adding [3] %s | %s | %s%s | %s" % (book, chapter, versenumber, phrase, osisbook))
                list.append(listrecord(book, chapter, versenumber, phrase, osisbook, end['verse']['remainingverses']))
    return list


def parse_list(mode, string):
    logging.info("parse_list %s" % string)
    split = split_on_first_char(string, listseparator)
    list = parse_range(mode, split['before'])
    if split['after']:
        list += parse_list("implicit", split['after'])
    return list


def parse_reference(bibleref, language="en", tolerance_param="false"):
    global chapterseparator
    global listseparator
    global rangeseparator
    global chapterversereference
    global book
    global localbook
    global spokenbook
    global osisbook
    global bookoutlinerecord
    global tolerance
    tolerance = tolerance_param
    # eliminate superfluous spaces and separator characters
    bibleref = re.sub(r'[\.,;:\- ]*([\.,;:\- ]) *', r'\1', bibleref)
    logging.info("parse_reference " + bibleref)
    split = split_on_first_re(bibleref, r' ')
    if re.search(r'^[0-9]+$', split['before']):
        book = split['before'] + " "
    elif re.search(r'^[iv]+$', split['before'], flags=re.IGNORECASE):
        book = str(deromanize(split['before'])) + " "
    else:
        book = ""
        split['after'] = bibleref
    split2 = split_on_first_re(split['after'], r'[:\., ]')
    book = book + split2['before']
    bookrecord = find_book(book)
    osisbook = getosisbook(bookrecord)
    if language:
        localbook = getlocalbook(bookrecord, language)
        spokenbook = getspokenbook(bookrecord, language)
    bookoutlinerecord = find_book_outline(osisbook)
    # determine the functions of the separators being used
    separatorsOrder = getSeparators(split2['after'])
    separatorIndex = 0
    parseSuccess = 0
    while not parseSuccess:
        try:
            logging.info("Trying with separators (chapter, list, range): %s" % separatorsOrder[separatorIndex])
            chapterseparator = separatorsOrder[separatorIndex][0]
            listseparator = separatorsOrder[separatorIndex][1]
            rangeseparator = separatorsOrder[separatorIndex][2]
            table = str.maketrans(separatorsOrder[separatorIndex], ":,-")
            chapterversereference = str(split2['after']).translate(table)
            parseResult = parse_list("explicit", split2['after'])
            parseSuccess = 1
        except ValueError as e:
            separatorIndex += 1
            if separatorIndex < len(separatorsOrder):
                logging.info("Trying another interpretation of separators, because " + str(e))
            else:
                logging.error("Invalid bible reference syntax.")
                raise ValueError("Invalid bible reference syntax.")
    return parseResult


