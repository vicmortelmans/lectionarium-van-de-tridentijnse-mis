<?xml version="1.0"?>
<xsl:stylesheet version="2.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <!-- input: calendar-eo.xml
       reads: calendar-url-mapping.xml
       output: dummy
       writes: docs/YYYY-MM-DD.html redirecting to Proprium/NN.html
    -->
  <xsl:output method="html" name="html" version="5.0" encoding="UTF-8" indent="yes" />
  <xsl:variable name="map" select="document('calendar-url-mapping.xml')//day"/>
  <xsl:template match="day">
	<xsl:variable name="previous-days" select="//day[date &lt;= current()/date]"/>
	<xsl:variable name="previous-days-in-lectionary" select="$previous-days[$map/id=coordinates]"/>
	<xsl:variable name="coordinates" select="$previous-days-in-lectionary[last()]/coordinates"/>
	<!--xsl:message><xsl:value-of select="date"/> maps to <xsl:value-of select="$coordinates"/></xsl:message-->
	<xsl:variable name="url" select="$map[id=$coordinates]/url"/>
	<!--xsl:message><xsl:value-of select="$coordinates"/> maps to <xsl:value-of select="$url"/></xsl:message-->
	<xsl:choose>
      <xsl:when test="$url">
		<xsl:result-document method="html" href="docs/{date}.html">
			<html lang="nl">
			<head>
				<meta charset="UTF-8"/>
				<meta http-equiv="refresh" content="0; url={$url}"/>
				<title>Doorverwijzing...</title>
			</head>
			<body>
				<p>Als je niet doorverwezen wordt, <a href="{$url}">klik hier</a>.</p>
			</body>
			</html>
		</xsl:result-document>
      </xsl:when>
      <xsl:otherwise>
		<xsl:message>No url for <xsl:value-of select="date"/></xsl:message>
	  </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template match="@*|node()">
    <xsl:apply-templates select="@*|node()"/>
  </xsl:template>
</xsl:stylesheet>

