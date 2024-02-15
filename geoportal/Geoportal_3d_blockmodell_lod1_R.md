# LOD1 3D Blockmodell via WFS beziehen

In diesem Markdown wird gezeigt, wie 3D-Blockmodell-Geodaten via WFS in **R** abgefragt werden können. Das Dokument ist eine Kurzversion [von diesem Dokument](https://github.com/opendatazurich/opendatazurich.github.io/blob/master/geoportal/Geoportal_3d_blockmodell_lod1.ipynb), das die entsprechenden Schritte etwas ausführlicher in Python erklärt.

```{r packages, echo=FALSE}
# Laden der benötigten Packages
library(sf) # simple features packages for handling vector GIS data
library(httr) # generic webservice package
library(ows4R) # interface for OGC webservices
```

```{r layers, echo=TRUE}
# Layer Informationen abrufen
wfs_url <- "https://www.ogd.stadt-zuerich.ch/wfs/geoportal/3D_Blockmodell_LoD1"
wfs_client <- WFSClient$new(wfs_url, serviceVersion = "1.0.0")
wfs_client$getFeatureTypes(pretty = TRUE)
```

## LOD1-Daten laden

```{r getdata, echo=FALSE}
# Request zusammenstellen
layer = "lod1_gebaeude_max_3d"

url <- parse_url(wfs_url)
url$query <- list(service = "WFS",
                  version = "1.0.0", 
                  typename = layer,
                  request = "GetFeature")
request <- build_url(url)

# Daten direkt mit dem sf Package abrufen  
res <- sf::st_read(request)

# Als simple feature collection in R vorhanden
res
```
