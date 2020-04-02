rm(list = ls())
gc()

# Falls erforderlich: Packages installieren
#install.packages("httr")
#install.packages("stringr")
#install.packages("jsonlite")

library(httr)
library(stringr)
library(jsonlite)

startdatum<-as.Date("2020-01-01")
# Wenn vorhanden bitte SSZ-Zugang verwenden
usr<-Sys.getenv("SSZ_USER")
pw<-Sys.getenv("SSZ_PASS")


### get locations

response <- GET('https://vbz.diamondreports.ch:8012/api/location',
                authenticate(usr,pw, type = 'basic'))
raw.content <- rawToChar(response$content)
locations <- fromJSON(raw.content)
locations$Name<-str_replace(locations$Name, "Ã¼", "ü")

#Anpassung für link
locations$Name_link<-str_replace(locations$Name, " ", "%20")
locations$Name_link<-str_replace(locations$Name_link, "ü", "%C3%BC")


output<-list()
for(j in 1:nrow(locations)) {

inner_output<-list()
for(i in 1:366) {
datum<-format(startdatum+i-1, "%Y%m%d")

response <- GET(paste0("https://vbz.diamondreports.ch:8012/api/location/counter/",locations$Name_link[j],"?aggregate=5&date=",datum),
                authenticate(usr,pw, type = 'basic'))
raw.content <- rawToChar(response$content)
content <- fromJSON(raw.content)
tbl<-content[["Counters"]][["Counts"]][[1]]
if (is.null(nrow(tbl))){next}

tbl$Name<-locations$Name[j]

inner_output[[i]]<-tbl

if (as.Date(datum,"%Y%m%d") == Sys.Date()){break}
}
inner_output<-do.call(rbind.data.frame, inner_output)
output[[j]]<-inner_output
}

output<-do.call(rbind.data.frame, output)
output<-subset(output, select=-c(OpeningTime))

#Output speichern
write.table(output, file = "Frequenzen_Hardbruecke_2020.csv", sep = ",",row.names = F)

