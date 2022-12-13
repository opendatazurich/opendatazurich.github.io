# Zürich Tourismus API

Über das Zürich Tourismus API lassen sich Daten von Zürich Tourismus über Attraktionen, Unterkünfte, Restaurants und mehr abfragen.
Zürich Tourismus hat das [API auf ihrer eigenen Seite dokumentiert](https://zt.zuerich.com/de/open-data).

## API in Version 2.0 (Januar 2023)

Bis Januar 2023 sind sowohl Version 1 wie auch Version 2 des Zürich Tourismus API verfügbar.

Hier die wichtigsten [Änderungen in v2](https://zt.zuerich.com/en/open-data/v2#change-log):

- Das Beschreibungsfeld (`description`) kann nun folgende HTML-Tags enthalten (in v1 war nur `<p>` erlaubt)
  - Hervorhebung: `<em>`, `<strong>`
  - Code: `<code>`
  - Listen: `<ul>`, `<ol>`, `<li>`
  - Definitionen: `<dl>`, `<dt>`, `<dd>`
  - Überschriften: `<h1>`, `<h2>`, `<h3>`, `<h4>`, `<h5>`, `<h6>`
  - Bilder: `<img>`
  - Absätze: `<pre>`, `<p>`, `<br>`
  - Links: `<a>`
  - Tabellen: `<table>`, `<caption>`, `<tbody>`, `<thead>`, `<tfoot>`, `<th>`, `<td>`, `<tr>`
  
- Weitere Werte für das `@type`-Feld (in v1 gab es nur 3 mögliche Werte `LodgingBusiness`, `Place` und `LocalBusiness`)
  - Event (oder abgeleitete Kindelemente): https://schema.org/Event
  - Place (oder abgeleitete Kindelemente): https://schema.org/Place
  - Organization (oder abgeleitete Kindelemente): https://schema.org/Organization
  - CreativeWork  (oder abgeleitete Kindelemente):https://schema.org/CreativeWork

## Programmier-Beispiele

Im [Jupyter-Notebook ZuerichTourismusAPI-Beispiele.ipynb](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/zt-api/ZuerichTourismusAPI-Beispiele.ipynb) sind einige Python-Beispiele im Umgang mit dem API beschrieben.

Jupyter-Notebook interaktiv im Browser starten: 

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/opendatazurich/opendatazurich.github.io/master?filepath=zt-api/ZuerichTourismusAPI-Beispiele.ipynb)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/opendatazurich/opendatazurich.github.io/blob/master/zt-api/ZuerichTourismusAPI-Beispiele.ipynb)
