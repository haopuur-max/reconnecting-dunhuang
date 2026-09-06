<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:tei="http://www.tei-c.org/ns/1.0"
  xmlns:xml="http://www.w3.org/XML/1998/namespace"
  exclude-result-prefixes="tei xml">

  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="tei:TEI tei:teiHeader tei:standOff tei:text tei:body tei:back tei:div tei:list tei:listBibl tei:listPerson tei:listPlace tei:listOrg tei:listEvent"/>

  <xsl:key name="by-id" match="*[@xml:id]" use="@xml:id"/>

  <xsl:template match="/tei:TEI">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title><xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/></title>
        <style>
          :root {
            color: #26231f;
            background: #f7f4ee;
            font-family: "Avenir Next", "Segoe UI", system-ui, sans-serif;
            line-height: 1.58;
          }
          body {
            margin: 0;
            background: #f7f4ee;
          }
          header, main, .semantic-layer {
            max-width: 980px;
            margin: 0 auto;
            padding: 0 24px;
          }
          header {
            padding-top: 42px;
            padding-bottom: 20px;
          }
          h1 {
            margin: 0 0 8px;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 2.45rem;
            line-height: 1.12;
            font-weight: 700;
          }
          .source-meta {
            margin: 0;
            color: #635c52;
          }
          .source-article {
            background: #fffdfa;
            border-top: 1px solid #ded6ca;
            border-bottom: 1px solid #ded6ca;
            padding-top: 24px;
            padding-bottom: 34px;
          }
          section {
            margin: 0 0 28px;
          }
          h2 {
            margin: 32px 0 12px;
            font-size: 1.55rem;
            line-height: 1.22;
          }
          p {
            margin: 0 0 14px;
          }
          ul, ol {
            padding-left: 1.45rem;
          }
          li {
            margin: 0.35rem 0;
          }
          figure {
            margin: 18px 0;
            border-left: 4px solid #b9985a;
            padding: 10px 14px;
            background: #f7f1e7;
          }
          figcaption {
            color: #4b463f;
            font-size: 0.96rem;
          }
          blockquote.tei-cit {
            margin: 18px 0;
            padding: 16px 18px;
            border-left: 4px solid #597e87;
            background: #eef5f5;
          }
          .tei-quote {
            display: block;
            margin: 0 0 8px;
          }
          .tei-attribution {
            display: block;
            margin: 0 0 8px;
            color: #5b625f;
            font-style: normal;
          }
          a {
            color: #265f74;
          }
          .citation {
            font-size: 0.86em;
            text-decoration: none;
            vertical-align: baseline;
          }
          .tei-entity {
            border-bottom: 1px dotted currentColor;
            text-decoration: none;
            padding-bottom: 1px;
          }
          .tei-person { color: #7a3f52; }
          .tei-place { color: #386744; }
          .tei-org { color: #4d5792; }
          .tei-object { color: #7a5a2f; }
          .tei-concept { color: #6a4d8f; }
          time {
            color: #775e1a;
            font-variant-numeric: tabular-nums;
          }
          .references {
            padding-left: 1.75rem;
          }
          .references li {
            margin-bottom: 0.6rem;
          }
          cite.tei-title {
            font-style: italic;
          }
          .semantic-layer {
            padding-top: 40px;
            padding-bottom: 52px;
          }
          .semantic-layer > h2 {
            margin-top: 0;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 2rem;
          }
          .semantic-note {
            color: #635c52;
            margin-bottom: 24px;
          }
          .entity-group {
            margin: 24px 0;
          }
          .entity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 12px;
          }
          .entity-card {
            background: #fffdfa;
            border: 1px solid #ded6ca;
            border-radius: 6px;
            padding: 12px;
          }
          .entity-card h4 {
            margin: 0 0 8px;
            font-size: 1rem;
          }
          .entity-card dl {
            margin: 0;
          }
          .entity-card dt {
            color: #665f55;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
          }
          .entity-card dd {
            margin: 0 0 7px;
            overflow-wrap: anywhere;
          }
          details {
            margin: 22px 0;
            background: #fffdfa;
            border: 1px solid #ded6ca;
            border-radius: 6px;
            padding: 12px;
          }
          summary {
            cursor: pointer;
            font-weight: 700;
          }
          table {
            width: 100%;
            margin-top: 12px;
            border-collapse: collapse;
            font-size: 0.92rem;
          }
          th, td {
            border-top: 1px solid #ded6ca;
            padding: 8px;
            text-align: left;
            vertical-align: top;
          }
          th {
            color: #4c463e;
            background: #f1ece3;
          }
          .evidence-enriched {
            font-weight: 700;
            color: #8a4d11;
          }
          .property-uri {
            overflow-wrap: anywhere;
          }
          .property-semantics {
            display: block;
            margin-top: 4px;
            color: #635c52;
            font-size: 0.86rem;
          }
        </style>
      </head>
      <body>
        <header>
          <h1><xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/></h1>
          <p class="source-meta">
            Source: frozen English Wikipedia revision oldid
            <xsl:text> </xsl:text>
            <xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:bibl/tei:idno[@type='wikipedia-oldid']"/>
            <xsl:text>, </xsl:text>
            <xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:bibl/tei:date"/>
          </p>
        </header>
        <main class="source-article">
          <xsl:apply-templates select="tei:text/tei:body/tei:div"/>
          <xsl:apply-templates select="tei:text/tei:back"/>
        </main>
        <xsl:call-template name="semantic-layer"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="tei:body/tei:div">
    <section>
      <xsl:attribute name="id"><xsl:value-of select="@xml:id"/></xsl:attribute>
      <xsl:attribute name="class">
        <xsl:text>source-section</xsl:text>
        <xsl:if test="@type='lead'"> lead</xsl:if>
      </xsl:attribute>
      <xsl:if test="not(@type='lead')">
        <h2><xsl:value-of select="tei:head"/></h2>
      </xsl:if>
      <xsl:apply-templates select="node()[not(self::tei:head)]"/>
    </section>
  </xsl:template>

  <xsl:template match="tei:back">
    <xsl:apply-templates select="tei:div"/>
  </xsl:template>

  <xsl:template match="tei:back/tei:div">
    <section class="source-section back-matter">
      <xsl:attribute name="id"><xsl:value-of select="@xml:id"/></xsl:attribute>
      <h2><xsl:value-of select="tei:head"/></h2>
      <xsl:apply-templates select="node()[not(self::tei:head)]"/>
    </section>
  </xsl:template>

  <xsl:template match="tei:p">
    <xsl:choose>
      <xsl:when test="count(*) = 1 and tei:cit and normalize-space(text()) = ''">
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:otherwise>
        <p><xsl:apply-templates/></p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="tei:list">
    <ul><xsl:apply-templates/></ul>
  </xsl:template>

  <xsl:template match="tei:item">
    <li><xsl:apply-templates/></li>
  </xsl:template>

  <xsl:template match="tei:figure">
    <figure>
      <figcaption><xsl:apply-templates select="tei:figDesc/node()"/></figcaption>
    </figure>
  </xsl:template>

  <xsl:template match="tei:cit">
    <blockquote class="tei-cit">
      <xsl:apply-templates/>
    </blockquote>
  </xsl:template>

  <xsl:template match="tei:quote">
    <span class="tei-quote"><xsl:apply-templates/></span>
  </xsl:template>

  <xsl:template match="tei:bibl[@type='attribution']">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="tei:seg[@type='attribution']">
    <span class="tei-attribution"><xsl:apply-templates/></span>
  </xsl:template>

  <xsl:template match="tei:listBibl">
    <xsl:choose>
      <xsl:when test="ancestor::tei:div[@xml:id='references']">
        <ol class="references">
          <xsl:apply-templates select="tei:bibl"/>
        </ol>
      </xsl:when>
      <xsl:otherwise>
        <ul class="bibliography">
          <xsl:apply-templates select="tei:bibl"/>
        </ul>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="tei:bibl">
    <li>
      <xsl:if test="@xml:id">
        <xsl:attribute name="id"><xsl:value-of select="@xml:id"/></xsl:attribute>
      </xsl:if>
      <xsl:apply-templates/>
    </li>
  </xsl:template>

  <xsl:template match="tei:back//tei:bibl//tei:title">
    <cite class="tei-title"><xsl:apply-templates/></cite>
  </xsl:template>

  <xsl:template match="tei:ref[starts-with(@target, '#bibl-')]">
    <a>
      <xsl:attribute name="href"><xsl:value-of select="@target"/></xsl:attribute>
      <xsl:attribute name="class">citation</xsl:attribute>
      <xsl:apply-templates/>
    </a>
  </xsl:template>

  <xsl:template match="tei:ref[starts-with(@target, 'http://') or starts-with(@target, 'https://')]">
    <a>
      <xsl:attribute name="href"><xsl:value-of select="@target"/></xsl:attribute>
      <xsl:attribute name="target">_blank</xsl:attribute>
      <xsl:attribute name="rel">noopener noreferrer</xsl:attribute>
      <xsl:apply-templates/>
    </a>
  </xsl:template>

  <xsl:template match="tei:ref">
    <a>
      <xsl:attribute name="href"><xsl:value-of select="@target"/></xsl:attribute>
      <xsl:apply-templates/>
    </a>
  </xsl:template>

  <xsl:template match="tei:persName[@ref]">
    <a class="tei-entity tei-person">
      <xsl:attribute name="href">#entity-<xsl:value-of select="substring-after(@ref, '#')"/></xsl:attribute>
      <xsl:attribute name="data-ref"><xsl:value-of select="@ref"/></xsl:attribute>
      <xsl:apply-templates/>
    </a>
  </xsl:template>

  <xsl:template match="tei:placeName[@ref]">
    <a class="tei-entity tei-place">
      <xsl:attribute name="href">#entity-<xsl:value-of select="substring-after(@ref, '#')"/></xsl:attribute>
      <xsl:attribute name="data-ref"><xsl:value-of select="@ref"/></xsl:attribute>
      <xsl:apply-templates/>
    </a>
  </xsl:template>

  <xsl:template match="tei:orgName[@ref]">
    <a class="tei-entity tei-org">
      <xsl:attribute name="href">#entity-<xsl:value-of select="substring-after(@ref, '#')"/></xsl:attribute>
      <xsl:attribute name="data-ref"><xsl:value-of select="@ref"/></xsl:attribute>
      <xsl:apply-templates/>
    </a>
  </xsl:template>

  <xsl:template match="tei:objectName[@ref]">
    <a class="tei-entity tei-object">
      <xsl:attribute name="href">#entity-<xsl:value-of select="substring-after(@ref, '#')"/></xsl:attribute>
      <xsl:attribute name="data-ref"><xsl:value-of select="@ref"/></xsl:attribute>
      <xsl:apply-templates/>
    </a>
  </xsl:template>

  <xsl:template match="tei:term[@ana]">
    <span class="tei-entity tei-concept">
      <xsl:attribute name="data-ana"><xsl:value-of select="@ana"/></xsl:attribute>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <xsl:template match="tei:date[@when]">
    <time>
      <xsl:attribute name="datetime"><xsl:value-of select="@when"/></xsl:attribute>
      <xsl:apply-templates/>
    </time>
  </xsl:template>

  <xsl:template match="tei:foreign[@xml:lang]">
    <span>
      <xsl:attribute name="lang"><xsl:value-of select="@xml:lang"/></xsl:attribute>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <xsl:template name="semantic-layer">
    <section id="tei-semantic-layer" class="semantic-layer" aria-labelledby="semantic-layer-title">
      <h2 id="semantic-layer-title">TEI Semantic Layer</h2>
      <p class="semantic-note">Project Annotation. This section is generated from the existing TEI standOff model layer and is separate from the frozen Wikipedia source article rendered above.</p>

      <section class="entity-register" aria-labelledby="encoded-entities-title">
        <h3 id="encoded-entities-title">Encoded Entities</h3>
        <xsl:call-template name="entity-group">
          <xsl:with-param name="title">Persons</xsl:with-param>
          <xsl:with-param name="nodes" select="tei:standOff/tei:listPerson/tei:person"/>
          <xsl:with-param name="kind">person</xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="entity-group">
          <xsl:with-param name="title">Places</xsl:with-param>
          <xsl:with-param name="nodes" select="tei:standOff/tei:listPlace/tei:place"/>
          <xsl:with-param name="kind">place</xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="entity-group">
          <xsl:with-param name="title">Organizations</xsl:with-param>
          <xsl:with-param name="nodes" select="tei:standOff/tei:listOrg/tei:org"/>
          <xsl:with-param name="kind">organization</xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="entity-group">
          <xsl:with-param name="title">Dunhuang Manuscripts Aggregate Holding</xsl:with-param>
          <xsl:with-param name="nodes" select="tei:standOff/tei:list[@xml:id='aggregate-holdings']/tei:item"/>
          <xsl:with-param name="kind">aggregate-holding</xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="entity-group">
          <xsl:with-param name="title">Digital Surrogate</xsl:with-param>
          <xsl:with-param name="nodes" select="tei:standOff/tei:list[@xml:id='digital-objects']/tei:item"/>
          <xsl:with-param name="kind">digital-object</xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="entity-group">
          <xsl:with-param name="title">Time-Span Nodes</xsl:with-param>
          <xsl:with-param name="nodes" select="tei:standOff/tei:list[@xml:id='time-spans']/tei:item"/>
          <xsl:with-param name="kind">time-span</xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="entity-group">
          <xsl:with-param name="title">Event Nodes</xsl:with-param>
          <xsl:with-param name="nodes" select="tei:standOff/tei:listEvent/tei:event"/>
          <xsl:with-param name="kind">event</xsl:with-param>
        </xsl:call-template>
      </section>

      <section class="model-relations" aria-labelledby="model-relations-title">
        <h3 id="model-relations-title">Model Relations</h3>
        <details open="open">
          <summary>Canonical Relations</summary>
          <table class="relations canonical-relations">
            <thead>
              <tr>
                <th>Relation ID</th>
                <th>Subject</th>
                <th>Relation name</th>
                <th>Object</th>
                <th>Evidence status</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="tei:standOff/tei:listRelation[@type='canonical']/tei:relation">
                <tr class="relation-row canonical-relation">
                  <xsl:attribute name="data-relation-id"><xsl:value-of select="@xml:id"/></xsl:attribute>
                  <td><xsl:value-of select="@xml:id"/></td>
                  <td><xsl:call-template name="linked-node"><xsl:with-param name="ref" select="@active"/></xsl:call-template></td>
                  <td><xsl:value-of select="@name"/></td>
                  <td><xsl:call-template name="linked-node"><xsl:with-param name="ref" select="@passive"/></xsl:call-template></td>
                  <td>
                    <xsl:call-template name="evidence">
                      <xsl:with-param name="ana" select="@ana"/>
                    </xsl:call-template>
                  </td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </details>
        <details open="open">
          <summary>Conceptual Relations</summary>
          <table class="relations conceptual-relations">
            <thead>
              <tr>
                <th>Conceptual edge ID</th>
                <th>Source node</th>
                <th>Property name</th>
                <th>Target</th>
                <th>Corresp</th>
                <th>Evidence status</th>
                <th>Ontology property URI</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="tei:standOff/tei:listRelation[@type='conceptual']/tei:relation">
                <tr class="relation-row conceptual-relation">
                  <xsl:attribute name="data-relation-id"><xsl:value-of select="@xml:id"/></xsl:attribute>
                  <xsl:if test="@mutual">
                    <xsl:attribute name="data-mutual">true</xsl:attribute>
                  </xsl:if>
                  <td><xsl:value-of select="@xml:id"/></td>
                  <td>
                    <xsl:choose>
                      <xsl:when test="@active">
                        <xsl:call-template name="linked-node"><xsl:with-param name="ref" select="@active"/></xsl:call-template>
                      </xsl:when>
                      <xsl:when test="@mutual">
                        <xsl:call-template name="linked-node"><xsl:with-param name="ref" select="substring-before(@mutual, ' ')"/></xsl:call-template>
                      </xsl:when>
                      <xsl:otherwise>not encoded</xsl:otherwise>
                    </xsl:choose>
                  </td>
                  <td><xsl:value-of select="@name"/></td>
                  <td>
                    <xsl:choose>
                      <xsl:when test="@mutual">
                        <span class="mutual-nodes">
                          <xsl:attribute name="data-mutual"><xsl:value-of select="@mutual"/></xsl:attribute>
                          <xsl:call-template name="linked-node"><xsl:with-param name="ref" select="substring-after(@mutual, ' ')"/></xsl:call-template>
                          <span class="property-semantics">Property semantics: symmetric / TEI encoded with @mutual.</span>
                        </span>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:call-template name="linked-node"><xsl:with-param name="ref" select="@passive"/></xsl:call-template>
                      </xsl:otherwise>
                    </xsl:choose>
                  </td>
                  <td><xsl:value-of select="@corresp"/></td>
                  <td>
                    <xsl:call-template name="evidence">
                      <xsl:with-param name="ana" select="@ana"/>
                    </xsl:call-template>
                  </td>
                  <td class="property-uri">
                    <xsl:choose>
                      <xsl:when test="@ref">
                        <a>
                          <xsl:attribute name="href"><xsl:value-of select="@ref"/></xsl:attribute>
                          <xsl:attribute name="target">_blank</xsl:attribute>
                          <xsl:attribute name="rel">noopener noreferrer</xsl:attribute>
                          <xsl:value-of select="@ref"/>
                        </a>
                      </xsl:when>
                      <xsl:when test="starts-with(@name, 'dm:')">
                        <a>
                          <xsl:attribute name="href">https://haopuur-max.github.io/reconnecting-dunhuang/ontology/<xsl:value-of select="substring-after(@name, 'dm:')"/></xsl:attribute>
                          <xsl:attribute name="target">_blank</xsl:attribute>
                          <xsl:attribute name="rel">noopener noreferrer</xsl:attribute>
                          <xsl:text>https://haopuur-max.github.io/reconnecting-dunhuang/ontology/</xsl:text><xsl:value-of select="substring-after(@name, 'dm:')"/>
                        </a>
                      </xsl:when>
                      <xsl:otherwise>not encoded in TEI</xsl:otherwise>
                    </xsl:choose>
                  </td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </details>
      </section>
    </section>
  </xsl:template>

  <xsl:template name="entity-group">
    <xsl:param name="title"/>
    <xsl:param name="nodes"/>
    <xsl:param name="kind"/>
    <section class="entity-group">
      <xsl:attribute name="data-entity-kind"><xsl:value-of select="$kind"/></xsl:attribute>
      <h4><xsl:value-of select="$title"/></h4>
      <div class="entity-grid">
        <xsl:for-each select="$nodes">
          <xsl:call-template name="entity-card">
            <xsl:with-param name="kind" select="$kind"/>
          </xsl:call-template>
        </xsl:for-each>
      </div>
    </section>
  </xsl:template>

  <xsl:template name="entity-card">
    <xsl:param name="kind"/>
    <article class="entity-card">
      <xsl:attribute name="id">entity-<xsl:value-of select="@xml:id"/></xsl:attribute>
      <xsl:attribute name="data-tei-id"><xsl:value-of select="@xml:id"/></xsl:attribute>
      <xsl:attribute name="data-entity-kind"><xsl:value-of select="$kind"/></xsl:attribute>
      <h4>
        <xsl:call-template name="node-label">
          <xsl:with-param name="node" select="."/>
        </xsl:call-template>
      </h4>
      <dl>
        <dt>xml:id</dt>
        <dd><xsl:value-of select="@xml:id"/></dd>
        <dt>Conceptual class</dt>
        <dd><xsl:value-of select="tei:note[@type='conceptualClass']"/></dd>
        <xsl:if test="tei:idno">
          <dt>Authority identifiers</dt>
          <dd>
            <xsl:for-each select="tei:idno">
              <span class="authority-id">
                <xsl:value-of select="@type"/>
                <xsl:text>: </xsl:text>
                <xsl:value-of select="."/>
              </span>
              <xsl:if test="position() != last()"><br/></xsl:if>
            </xsl:for-each>
          </dd>
        </xsl:if>
      </dl>
    </article>
  </xsl:template>

  <xsl:template name="linked-node">
    <xsl:param name="ref"/>
    <xsl:variable name="id" select="substring-after($ref, '#')"/>
    <a class="model-node">
      <xsl:attribute name="href">#entity-<xsl:value-of select="$id"/></xsl:attribute>
      <xsl:attribute name="data-ref"><xsl:value-of select="$ref"/></xsl:attribute>
      <xsl:choose>
        <xsl:when test="key('by-id', $id)">
          <xsl:call-template name="node-label">
            <xsl:with-param name="node" select="key('by-id', $id)[1]"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise><xsl:value-of select="$ref"/></xsl:otherwise>
      </xsl:choose>
    </a>
  </xsl:template>

  <xsl:template name="node-label">
    <xsl:param name="node"/>
    <xsl:choose>
      <xsl:when test="$node/tei:persName[1]"><xsl:value-of select="$node/tei:persName[1]"/></xsl:when>
      <xsl:when test="$node/tei:placeName[1]"><xsl:value-of select="$node/tei:placeName[1]"/></xsl:when>
      <xsl:when test="$node/tei:orgName[1]"><xsl:value-of select="$node/tei:orgName[1]"/></xsl:when>
      <xsl:when test="$node/tei:name[1]"><xsl:value-of select="$node/tei:name[1]"/></xsl:when>
      <xsl:when test="$node/tei:label[1]"><xsl:value-of select="$node/tei:label[1]"/></xsl:when>
      <xsl:when test="$node/tei:date[1]"><xsl:value-of select="$node/tei:date[1]"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="$node/@xml:id"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="evidence">
    <xsl:param name="ana"/>
    <xsl:variable name="evidence-id" select="substring-after($ana, '#evidence-')"/>
    <span>
      <xsl:attribute name="class">evidence evidence-<xsl:value-of select="$evidence-id"/></xsl:attribute>
      <xsl:choose>
        <xsl:when test="$evidence-id='direct'">Direct</xsl:when>
        <xsl:when test="$evidence-id='enriched'">Enriched</xsl:when>
        <xsl:otherwise><xsl:value-of select="$ana"/></xsl:otherwise>
      </xsl:choose>
    </span>
  </xsl:template>

</xsl:stylesheet>
