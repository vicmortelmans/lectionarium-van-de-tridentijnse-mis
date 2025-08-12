Python 3 compatible standalone server for YQL-like querying of bible references.

Run a web server that allows queries to "http://localhost:8080/yql/bibleref?language=nl&xml=true&bibleref="

1. python3 -m venv env
2. source env/bin/activate
3. pip install -r requirements.txt
4. python main.py

Sample result:

<query>
  <results>
    <biblerefs>
      <bibleref>
        <book>2 Thess</book>
        <localbook>2 tes</localbook>
        <osisbook>2Thess</osisbook>
        <chapterversereference>1:4-13</chapterversereference>
        <verseinbook>4</verseinbook>
        <chapter>1</chapter>
        <verse>4</verse>
        <phrase></phrase>
        <osisref>2Thess.1.4</osisref>
        <sequence>2Thess1001004</sequence>
        <remainingverses>-1</remainingverses>
        <spoken>de tweede brief aan de tessalonicenzen</spoken>
      </bibleref>
      ...
