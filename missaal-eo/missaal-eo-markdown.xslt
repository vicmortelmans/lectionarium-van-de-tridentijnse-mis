<?xml version="1.0"?>
<xsl:stylesheet version="2.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text"/>
    <xsl:variable name="index" select="doc('Index of liturgical days - missal.xml')/data"/>
    <xsl:variable name="days" select="doc('Catholic Liturgical Days - extraordinary form - values.xml')/data/*"/>
    <xsl:variable name="books" select="doc('books.xml')/root"/>
    <xsl:variable name="can" select="doc('canisius-met-correcties.xml')/dataroot"/>
    <xsl:variable name="ord" select="doc('Gewone Gebeden van de Mis - bible.xml')/data"/>
    <xsl:variable name="images" select="doc('missaal-eo-image-titles.xml')/data"/>
    <xsl:template match="/">
      <!--report images that are not included-->
      <xsl:message>
          <xsl:text>Images not included:</xsl:text>
          <xsl:text>&#10;</xsl:text>
          <xsl:for-each select="$images/*">
              <xsl:if test="not($index/*[coordinates=current()/id])">
                  <xsl:value-of select="file"/>
                  <xsl:text>&#10;</xsl:text>
              </xsl:if>
          </xsl:for-each>
      </xsl:message>
      <!--start rendering output-->
      <xsl:text>---&#10;</xsl:text>
      <xsl:text>title: Lectionarium van de Tridentijnse Mis&#10;</xsl:text>
      <xsl:text>lang: nl&#10;</xsl:text>
      <xsl:text>fontsize: 10pt&#10;</xsl:text>
      <!--xsl:text>classoption:&#10;</xsl:text>
      <xsl:text>- twocolumn&#10;</xsl:text-->
      <xsl:text>geometry: twoside, paperheight=167mm, paperwidth=115mm, top=22pt, headheight=10pt, headsep=10pt, footskip=20pt, bottom=22pt, left=15mm, right=12mm, includeheadfoot&#10;</xsl:text>
      <xsl:text>toc: false&#10;</xsl:text>
      <xsl:text>header-includes: |&#10;</xsl:text>
      <xsl:text>    \usepackage{fancyhdr}&#10;</xsl:text>
      <xsl:text>    \pagestyle{fancy}&#10;</xsl:text>
      <xsl:text>    \fancyhead[CO,CE]{\small{\rightmark}}&#10;</xsl:text>
      <xsl:text>    \fancyfoot[CE,CO]{\small{\thepage}}&#10;</xsl:text>
      <xsl:text>    \fancyhead[LO,LE,RO,RE]{}&#10;</xsl:text>
      <xsl:text>    \fancyfoot[LO,LE,RO,RE]{}&#10;</xsl:text>
      <xsl:text>    \usepackage{caption}&#10;</xsl:text>
      <xsl:text>    \DeclareCaptionFormat{empty}{}&#10;</xsl:text>
      <xsl:text>    \captionsetup{format=empty}&#10;</xsl:text>
      <xsl:text>...&#10;</xsl:text>
      <xsl:text>&#10;</xsl:text>
      <xsl:text>De teksten in dit lectionarium komen overeen met de lezingen die worden voorgeschreven in het missaal van de Tridentijnse Mis, onder het pontificaat van paus Benedictus XVI ook gekend als de Buitengewone Vorm van de Latijnse Ritus. De Nederlandse vertalingen zijn genomen uit de Petrus Canisius bijbelvertaling, een  vertaling uit de grondtekst in opdracht van de Apologetische Vereniging *Petrus Canisius* ondernomen met goedkeuring van de hoogwaardige bisschoppen van Nederland (oorspronkelijke uitgave 1939). De integrale tekst van deze vertaling vindt men op https://bijbel.gelovenleren.net. De afbeeldingen bij de evangelieteksten zijn genomen uit *Evangelicæ historiæ imagines: ex ordine evangeliorum, quæ toto anno in missæ sacrificio recitantur, in ordinem temporis vitæ Christi digestæ* (Jerónimo Nadal sj, Antwerpen, 1593).&#10;</xsl:text>
      <xsl:text>&#10;</xsl:text>
      <xsl:text># Proprium&#10;</xsl:text>
      <xsl:text>&#10;</xsl:text>
      <xsl:apply-templates select="$index/*[form='eo']" mode="day"/>
      <xsl:text>&#10;</xsl:text>
      <xsl:text># Ordinarium&#10;</xsl:text>
      <xsl:text>&#10;</xsl:text>
      <xsl:apply-templates select="$ord/*[not(eo = '')]" mode="ord"/>
      <xsl:text>\clearpage&#10;</xsl:text>
      <xsl:text>\tableofcontents&#10;</xsl:text>
      <xsl:text>&#10;</xsl:text>
    </xsl:template>
    <xsl:template match="*" mode="ord">
        <xsl:text>## </xsl:text><xsl:value-of select="name"/><xsl:text>&#10;</xsl:text>
        <xsl:text>&#10;</xsl:text>
        <xsl:value-of select="nl"/>
        <xsl:text>&#10;</xsl:text>
        <xsl:text>&#10;</xsl:text>
        <xsl:value-of select="la"/>
        <xsl:text>&#10;</xsl:text>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
    <xsl:template match="*" mode="day"><!-- item in Index of liturgical days -->
        <xsl:variable name="name" select="$days[ref = name(current())]/nl"/>
        <xsl:if test="not($name)">
            <xsl:message>Missing name for <xsl:value-of select="name(current())"/></xsl:message>
        </xsl:if>
        <xsl:text>## </xsl:text><xsl:value-of select="$name"/><xsl:text>&#10;</xsl:text>
        <xsl:text>&#10;</xsl:text>
        <xsl:call-template name="passage">
            <xsl:with-param name="refs" select="epistle"/>
            <xsl:with-param name="type" select="'Epistel'"/>
            <xsl:with-param name="name" select="$name"/>
            <xsl:with-param name="coordinates" select="coordinates"/>
        </xsl:call-template>
        <xsl:call-template name="passage">
            <xsl:with-param name="refs" select="gospel"/>
            <xsl:with-param name="type" select="'Evangelie'"/>
            <xsl:with-param name="name" select="$name"/>
            <xsl:with-param name="coordinates" select="coordinates"/>
        </xsl:call-template>
    </xsl:template>
    <xsl:template name="passage">
        <xsl:param name="refs"/>
        <xsl:param name="type"/>
        <xsl:param name="name"/>
        <xsl:param name="coordinates"/>
        <xsl:for-each select="tokenize($refs, '\|')">
            <xsl:variable name="epistle_ref" select="."/>
            <xsl:variable name="epistle_verses" select="doc(concat('http://localhost:8080/yql/bibleref?language=nl&amp;xml=true&amp;bibleref=', $epistle_ref))/query/results/biblerefs"/>
            <xsl:variable name="book_osis" select="$epistle_verses/bibleref[1]/osisbook"/>
            <xsl:variable name="book_nl" select="$books/row[code/osis = $book_osis]/spoken/nl"/>
            <xsl:variable name="epistle_ref_nl" select="concat($book_nl, ' ', $epistle_verses/bibleref[1]/chapterversereference)"/>
            <xsl:if test="not($epistle_ref_nl)">
                <xsl:message>No bibleref in nl for <xsl:value-of select="$epistle_ref"/></xsl:message>
            </xsl:if>
            <xsl:variable name="book_can" select="$books/row[code/osis = $book_osis]/code/can"/>
            <xsl:if test="$type='Evangelie'">
                <xsl:for-each select="$images/*[id=$coordinates]">
                    <xsl:text>![image](images/</xsl:text><xsl:value-of select="file"/><xsl:text>)</xsl:text>
                    <xsl:text>&#10;&#10;</xsl:text>
                </xsl:for-each>
            </xsl:if>
            <xsl:text>*</xsl:text><xsl:value-of select="$epistle_ref_nl"/><xsl:text>*</xsl:text>
            <xsl:text>&#10;</xsl:text>
            <xsl:for-each select="$epistle_verses/bibleref">
                <xsl:variable name="verse" select="normalize-space($can/Bible[Book_x0020_ID = $book_can][Chapter = current()/chapter][Verse = current()/verse]/Scripture)"/>
                <xsl:if test="not($verse)">
                    <xsl:message>No verse for <xsl:value-of select="$epistle_ref"/> (<xsl:value-of select="concat('book ',$book_can,', chapter: ',chapter,', verse: ',verse)"/>)</xsl:message>
                </xsl:if>
                <xsl:choose>
                    <xsl:when test="$verse and (position() = 1) and (substring($verse,1,1) = lower-case(substring($verse,1,1)))">
                        <xsl:message>Passage starts with lowercase: <xsl:value-of select="$epistle_ref"/></xsl:message>
                        <xsl:value-of select="concat(upper-case(substring($verse,1,1)), substring($verse,2))"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="$verse"/>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:text> </xsl:text>
            </xsl:for-each>
            <xsl:text>&#10;</xsl:text>
            <xsl:text>&#10;</xsl:text>
        </xsl:for-each>
    </xsl:template>
    <xsl:template match="@*|node()">
        <xsl:copy>
          <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>

