# Dies ist der Pseudocode zum erstellen des Reports für den Data Donation Day 2024 für das Projekt Social Media und Direkte Demokratie. 

# Vorbemerkungen zu offenen Punkten
# Bei den Daten gibt es noch ein Encoding Problem mit den Umlauten (Sowohl in den Facebook Daten als auch den Metadaten des Data Donation Lab Exportes):
# Mein Vorschlag zuerst bei allen Rohdaten die Umlaute entsprehcend der Hexa-Codes(?) einfügen.

# Zuerst hatte ich vor nur die Drei Monate vor der Abstimmung zu analysieren, bei der Recherceh habe ich nun gesehn, dass die Profile der Kampagen bereits viel früher existieren
# und teilweise aktiv sind. Gleichzeitig sind gewisse FB Daten nur für die vergangenen 90 Tage verfügbar. Daher bin ich noch unsicher, wie der Zeitraum eingegrenzt werden soll.

# Für Personen, die sowohl ihre INsta als auch FB Daten spenden: Soll es da pro Spende ein Report geben, oder jeweils für die Insta und FB Spende ein separater?

# Ich wusste nicht, wie die aggregierte Datenstruktur aller Datenspenden aussieht, weshalb ich die Analysen auf dieser aggregierten Eben nicht so genau beschreiben konnte.

#Schliesslich, sind die gespendeten Daten noch nicht clean, da ich noch nicht dazu gekommen bin, die Daten bereits im Data Donation fenster zu säubern. (z.B )
#{
#    "Gelikte Posts Instagram": [
#        [
#            {
#                "title": "luki_hir",
#                "string_list_data": [
#                    {
#                        "href": "https://www.instagram.com/p/C8U54N2t_p9/",
#                        "value": "\u00f0\u009f\u0091\u008d",
#                        "timestamp": 1718653285
#                   }
#                ]
#            }]]}

# anstatt

#{
#    "title": "luki_hir",
#    "href": "https://www.instagram.com/p/C8U54N2t_p9/",
#    "timestamp": 1718653285
#    }

# Der Bericht ist grundsätzlich dreiteilig und jeder Teil bestehe aus mehreren Plots. Im ersten Teil geht es darum, welcehn politischen 
# Kanälen eine Person folgt, im zweiten Teil zur Interaktion mit politischem Inhalt und im Dritten Teil Stimmentscheidung und Nutzung von sozailen Medien auf der aggrgierten Ebene

# Dieses Script hat zuerst eine Übersicht über die verwendeten Variablen, danach pro Variable die Datenquelle in der Donation für Instagram und Facebook und jeweils ein Vorschlag, 
# wie sie aus den Rohdaten berechnet werden könnte. Der Pseudocode ist R flavoured mit Tidyverse Logik

library(tidyverse)

# Variablen
n_accounts = n # Total gefolgter Kanäle, als einfach Nummer, die angezeigt werden kann in Text

platform = c("Facebook", "Instagram", "beide") # Herkunft der Datenspende
platform_quest = c("Facebook", "Instagram", "beide") # Welche Plattformen werden von der Spender:in genutzt? kommt aus dem Fragebogen

profile = c("Parteien", "Medien", "nationale Politker:innen", "Organisation", "Andere") # Count der einzelnen Kategorien politischer Profile pro Spender:in

interaction = c("Reaktion auf Story", "Like", "Comment") # Count der verschiedenen Inhalten von politischen Profilen

proposed = c("Ads", "Profiles", "Posts", "Videos") # Art des vorgeschlagenen Inhaltes, der von R angeschaut worden ist (Instagram). angeschauter Inhalt in den diversen Feeds (Posts, Videos,...; Facebook)

searches = c("...", "...") # Character String mit den Keywords der vergangenen Suchen (Profile und Gruppen (Facebook) respektive Hashtags (Insta))

SP = c(0, 1) # R folgt SP
Mitte = c(0, 1) # R folgt Mitte
FDP = c(0, 1) # R folgt FDP
SVP = c(0, 1) # R folgt SVP 


# Datenquellen
data = 'einzelne Datenspende'
db = 'Datenbank aller Datenspenden'

# Data Extraction
## instagram

### n_accounts: "Gefolgte Kanäle Instagram" Blueprint. Daten solltenim "string_list_data" als json Struktur mit key href sein.
data %>%
select("Gefolgte Kanäle Instagram") %>%
mutate(n_accounts = count(unique(href))) 

### platform
# Kann eine Variable generiert werden, bei welchem Uploader Daten eingepsiesen worden sind? dann wäre platform: c("Facebook", "Instagram", "beide")
data %>%
mutate(platform_quest = case_when(insta == 1 & fb == 0 ~ "Instagram",
                                  insta == 0 & fb == 1 ~ "Facebook",
                                  insta == 1 & fb == 1 ~ "beide" ))  # used platfroms created from Questionnaire

### profile: Art des gefolgten politischen Profils, Andere sollte schlussendlich nicht als Kategorie angezeigt werden, aber für die Berechnung von 100% berücksichtigt 
# werden
# From "Gefolgte Kanäle Instagram" Blueprint. Daten solltenim "string_list_data" als json Struktur mit key href sein.

data %>%
select("Gefolgte Kanäle Instagram") %>%
mutate(profile = case_when(href %in% party ~ "Partei",
                           href %in% media ~ "Medien",
                           href %in% politician ~ "nationale Politiker:in",
                           href %in% organisation ~ "Organisation",
                           .default = "andere")) %>%
group_by(profile) %>%
aggregate(n_accounts = count(unique(href)))


### interactions in blueprint "Gelikte Posts Instagram", "Kommentare Instagram", "Reels Kommentare Instagram" und "Story Likes Instagram"
interaction = c("Reaktion auf Story", "Like", "Kommentar")
# by likes muss by title noch "https://www.instagram.com/" vorn an das 'title' Feld gerpinted werden
likes = data %>%
select('Gelikte Posts Instagram')
mutate(Like = case_when(title %in% party ~ "Partei",
                        title %in% media ~ "Medien",
                        title %in% politician ~ "nationale Politiker:in",
                        title %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Like")

comments = data %>%
select('Kommentare Instagram') %>%
mutate(Like = case_when(href %in% party ~ "Partei",
                        href %in% media ~ "Medien",
                        href %in% politician ~ "nationale Politiker:in",
                        href %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Kommentar")

reels = data %>%
select('Reels Kommentare Instagram') %>%
mutate(Like = case_when(href %in% party ~ "Partei",
                        href %in% media ~ "Medien",
                        href %in% politician ~ "nationale Politiker:in",
                        href %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href)) %>%
mutate(interaction = "Reel")


story = data %>%
select('Story Likes Instagram') %>%
mutate(Like = case_when(href %in% party ~ "Partei",
                        href %in% media ~ "Medien",
                        href %in% politician ~ "nationale Politiker:in",
                        href %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Story")

data = rbind(likes, comments, reels, story)
          
### proposed content "Geschaute Werbung Instagram", "Vorgeschlagene Profile", "Geschaute Posts Instagram", "Geschaute Videos Instagram"

# by ads, profiles muss by value noch "https://www.instagram.com/" vorn an das 'title' Feld gerpinted werden
ads = data %>%
select('Geschaute Werbung Instagram') %>%
mutate(Like = case_when(value %in% party ~ "Partei",
                        value %in% media ~ "Medien",
                        value %in% politician ~ "nationale Politiker:in",
                        value %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Werbung")

profiles = data %>%
select('Vorgeschlagene Profile') %>%
mutate(Like = case_when(value %in% party ~ "Partei",
                        value %in% media ~ "Medien",
                        value %in% politician ~ "nationale Politiker:in",
                        value %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Profile")

posts = data %>%
select('Geschaute Posts Instagram') %>%
mutate(Like = case_when(value %in% party ~ "Partei",
                        value %in% media ~ "Medien",
                        value %in% politician ~ "nationale Politiker:in",
                        value %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Posts")

videos = data %>%
select('Geschaute Videos Instagram')
mutate(Like = case_when(value %in% party ~ "Partei",
                        value %in% media ~ "Medien",
                        value %in% politician ~ "nationale Politiker:in",
                        value %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Videos")

data = rbind(ads, profiles, posts, videos)


# searches: "Gesuchte Profile Instagram", "Gesuchte Hashtags Instagram"

data %>%
select("Gesuchte Profile Instagram", "Gesuchte Hashtags Instagram") %>%
long_format()

searches = c("...", "...") # Character String mit den Keywords der vergangenen Suchen


# party dummies: werden aufgrund der Datenbank und nicht des einzelnen Exportes berechnet

db %>%
select("ID", "Gefolgte Kanäle Instagram") %>%
group_by(ID)%>%
aggregate(ID = ID,
          SP = max(title %in% sp_profiles),  # If present then 1 otherwise 0
          Mitte = max(title %in% mitte_profiles),  # If present then 1 otherwise 0
          FDP = max(title %in% fdp_profiles),  # If present then 1 otherwise 0
          SVP = max(title %in% svp_profiles)  # If present then 1 otherwise 0
          )


## Facebook

### n_accounts: Gefolgte Personen Facebook (mit FB Namen und nicht URL), Gefolgte Seiten Facebook (Mit Namen und niht URL), Freunde Facebook (Mit Namen und nicht URL)
data %>%
select("Gefolgte Personen Facebook", "Gefolgte Seiten Facebook", "Freunde Facebook")%>%
long_format()%>%
aggregate(n_accounts = count(unique(name))) # unique ist wichtig, da dieselben Profile sowohl bei gefolgte Seiten als auch Personen auftauchen kann.

### platform
# Kann eine Variable generiert werden, bei welchem Uploader Dateneingepsiesen worden sind? dann wäre platform: c("Facebook", "Instagram", "beide")
data %>%
mutate(platform_quest = case_when(insta == 1 & fb == 0 ~ "Instagram",
                                  insta == 0 & fb == 1 ~ "Facebook",
                                  insta == 1 & fb == 1 ~ "beide" ))  # used platfroms created from Questionnaire

### profile: Art des gefolgten politischen Profils, Andere sollte schlussendlich nicht als Kategorie angezeigt werden, aber für die Berechnung von 100% berücksichtigt 
# werden
# From Gefolgte Personen Facebook, Gefolgte Seiten Facebook, Freunde Facebook Blueprints.

data %>%
select("Gefolgte Personen Facebook", "Gefolgte Seiten Facebook", "Freunde Facebook") %>%
long_format() %>%
mutate(profile = case_when(name %in% party ~ "Partei",
                           name %in% media ~ "Medien",
                           name %in% politician ~ "nationale Politiker:in",
                           name %in% organisation ~ "Organisation",
                           .default = "andere")) %>%
group_by(profile) %>%
aggregate(n_accounts = count(unique(name)))


### interactions in blueprints "Kommentare Facebook", "Likes Facebook", "Story Interaction Facebook" 

# Hier muss noch ein Regex über die Daten laufen: "Ferdinand Grunz hat 20 Minutens Beitrag kommentiert." aus der Donation muss mit "20 Minuten" aus der Liste gematched werden. Dies ist für alle 3 Blueprints so.

likes = data %>%
select('Likes Facebook') %>%
mutate(Like = case_when(title %in% party ~ "Partei",
                        title %in% media ~ "Medien",
                        title %in% politician ~ "nationale Politiker:in",
                        title %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Like")

comments = data %>%
select('Kommentare Facebook')%>%
mutate(Like = case_when(title %in% party ~ "Partei",
                        title %in% media ~ "Medien",
                        title %in% politician ~ "nationale Politiker:in",
                        title %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Kommentar")

story = data %>%
select('Story Interaction Facebook')%>%
mutate(Like = case_when(title %in% party ~ "Partei",
                        title %in% media ~ "Medien",
                        title %in% politician ~ "nationale Politiker:in",
                        title %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Story")

data = rbind(likes, comments, story)
          
### proposed content: "Kürzlich besucht Facebook", "Kürzlich geschaut Facebook"

# by ads, profiles muss by value noch "https://www.instagram.com/" vorn an das 'title' Feld gerpinted werden


profiles = data %>%
select('Vorgeschlagene Profile' %>% 'Profilaufrufe')%>%
mutate(Like = case_when(uri %in% party ~ "Partei",
                        uri %in% media ~ "Medien",
                        uri %in% politician ~ "nationale Politiker:in",
                        uri %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Profile")

posts = data %>%
select('Kürzlich geschaut Facebook' %>% 'Beiträge, die dir im Feed angezeigt wurden')%>%
mutate(Like = case_when(name %in% party ~ "Partei",
                        name %in% media ~ "Medien",
                        name %in% politician ~ "nationale Politiker:in",
                        name %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Posts")

videos = data %>%
select('Kürzlich geschaut Facebook' %>% 'Gesehene Videos')%>%
mutate(Like = case_when(name %in% party ~ "Partei",
                        name %in% media ~ "Medien",
                        name %in% politician ~ "nationale Politiker:in",
                        name %in% organisation ~ "Organisation",
                        .default = "andere")) %>%
group_by(profile) %>%
aggregate(count = count(href))%>%
mutate(interaction = "Videos")

data = rbind(profiles, posts, videos)


# searches: "Seitensuche Facebook", "Gruppensuche Facebook"
data %>% 
select("Seitensuche Facebook", "Gruppensuche Facebook")%>%
long_format()

searches = c("...", "...") # Character String mit den values für den key 'text'


reference = c("Du", "Andere")

# Party Dummies: Wir nicht aus dem einzelnen Export berechnet sondern der Datenbank

db %>%
select("ID", "Gefolgte Personen Facebook", "Gefolgte Seiten Facebook", "Freunde Facebook") %>%
long_format(cols = c("Gefolgte Personen Facebook", "Gefolgte Seiten Facebook", "Freunde Facebook")) %>%
group_by(ID)%>%
aggregate(ID = ID,
          SP = max(title %in% sp_profiles),  # If present then 1 otherwise 0
          Mitte = max(title %in% mitte_profiles),  # If present then 1 otherwise 0
          FDP = max(title %in% fdp_profiles),  # If present then 1 otherwise 0
          SVP = max(title %in% svp_profiles)  # If present then 1 otherwise 0
          )


# Teil 1: gefolgte politische Kanäle

## Text mit Count für total gefolgte Accounts


print("Du folgst ", n_accounts, "Kanälen auf ", platform)

## Tiles plot für Aufsplittung der Art der gefolgten Profilen


data %>%
groub_by(profile) %>%
aggregate(share = 100 * (n_accounts / sum(n_accounts))) %>% # Berechne den Anteil der Follows der verschiedenen Profiltypen an allen Follows

tiles_plot(x = share, fill_colour = parties) +  
title("Von den Profilen denen Du folgst sind")


## Scatter Plot gefolgter Profilen

db %>%
groub_by(reference, profile) %>%
aggregate(mean = mean(n_accounts)) %>% # Berechne die durchschnittliche Anzahl Follows der einzelnen Profiltypen für alle Rs der Data Donation im Vergleich zu einzelner R.

scatter_plot(x = mean, y = profile, shape = reference) +
title("Im Vergleich zu anderen sieht dein Followerprofil so aus:")

## Scatter Plot politische Interesse

db %>%
groub_by(reference) %>%
share(mean = mean(polint)) %>% # Berechne die durchschnittliche Anzahl Follows der einzelnen Profiltypen für alle Rs der Data Donation im Vergleich zu einzelner R.

scatter_plot(x = mean, shape = reference)

# Teil 2: Interaktion mit Content von politischen Profilen

## Bar plot für Interaktionen

data %>%
filter(channel == 1) %>%
group_by(interaction, profile) %>%
aggregate(count = n_accounts) %>%

bar_plot(x = interaction, y = count, fill_color = profile) +
title("So interagierst du mit dem Content dieser Profile")

## Bar Plot von angeschautem Inhalt der von Plattfrom vorgeschlagen worden ist

data %>%
group_by(proposed, profile) %>%
aggregate(count = n_accounts) %>%

bar_plot(x = proposed, y = count, fill_color = profile) +
title("So viele vorgeschlagene Inhalte von folgenden Profilen hast du dir angesehen")

# Wordcloud vergangener Suchbegriffe (Hier ist noch unklar, ob die Daten noch gefiltert werden sollten nach politischem Inhalt. Dies ist allerdings schwierig und 
# würde eine komplexere Mehtode bedingen, die Politisches von unpolitischem trennen könnten, oder es würden nur Profilsuchen angezeigt werden, die auf der Liste sind. 
# Oder ob einfach alle Suchen angezeigt werden sollten. Hast Du da eine Idee?)

data %>%
filter('???') %>%
mutate(text = text_non_capital(text)) # Alle Buchstaben in Kleinbucstaben umwandeln
wordcloud(x = searches, color = profile)

# 3. Teil: Nutzung Sozialer Medien und politische Merkmale auf aggregierter Ebene

## Bar Plot Nutzung von Facebook und Insta in  Abhängigkeit der Stimmentscheidung. Hier noch unklar, welche Variable reinfliessen soll: Ursprungsplattform der Datenspende(n) (platform)  oder 
# zusätzliche Frage im Fragebogen (platform_quest): Welche Plattfromen nutzen Sie? (Mehrfachantwort) Insta, Facebook Kategorien = c(" Instagram", "Facebook", "beide") 



db %>%
mutate(prop = c("Biodiversitätsinitiative", "Reform der beruflichen Vorsorge")) %>%
group_by(prop, vote) %>%
aggregate(count = platform) %>%

bar_plot(x = vote, y = count, fill_color = platform) +
facets(prop)

# Density Plot der Nutzenden von Facebook und Instagram
db %>%
density_plot(x = lrsp) +
facet(platform)

# Density Plot für links-rechts Verteilung der Followerschaft der Bundesratsparteien auf Instagram und Facebook


plot_grid(
db %>%
filter(SP == 1) %>%
density_plot(x = lrsp, color = platform) +
title("SP"),

db %>%
filter(SP == 1) %>%
density_plot(x = lrsp, color = platform) +
title("Mitte"),

db %>%
filter(SP == 1) %>%
density_plot(x = lrsp, color = platform) +
title("FDP"),

db %>%
filter(SP == 1) %>%
density_plot(x = lrsp, color = platform) +
title("SVP"),

n_columns = 2)


# Snippets

## Transform timestamp to date (in Python)

import datetime

# Given timestamp
timestamp = 1716197395

# Convert the timestamp to a datetime object
date_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)

print(date_time)

# Dictionary for Umlaute and other non-ASCII characters
non_ASCII_chars = {
    "\u00c3\u00a0": "à",
    "\u00c3\u00a1": "á",
    "\u00c3\u00a2": "â",
    "\u00c3\u00a3": "ã",
    "\u00c3\u00a4": "ä",
    "\u00c3\u00a5": "å",
    "\u00c3\u00a6": "æ",
    "\u00c3\u00a7": "ç",
    "\u00c3\u00a8": "è",
    "\u00c3\u00a9": "é",
    "\u00c3\u00aa": "ê",
    "\u00c3\u00ab": "ë",
    "\u00c3\u00ac": "ì",
    "\u00c3\u00ad": "í",
    "\u00c3\u00ae": "î",
    "\u00c3\u00af": "ï",
    "\u00c3\u00b0": "ð",
    "\u00c3\u00b1": "ñ",
    "\u00c3\u00b2": "ò",
    "\u00c3\u00b3": "ó",
    "\u00c3\u00b4": "ô",
    "\u00c3\u00b5": "õ",
    "\u00c3\u00b6": "ö",
    "\u00c3\u00b8": "ø",
    "\u00c3\u00b9": "ù",
    "\u00c3\u00ba": "ú",
    "\u00c3\u00bb": "û",
    "\u00c3\u00bc": "ü",
    "\u00c3\u00bd": "ý",
    "\u00c3\u00bf": "ÿ",
    "\u00c4\u0080": "Ā",
    "\u00c4\u0081": "ā",
    "\u00c4\u0086": "Ć",
    "\u00c4\u0087": "ć",
    "\u00c4\u008c": "Č",
    "\u00c4\u008d": "č",
    "\u00c4\u0090": "Đ",
    "\u00c4\u0091": "đ",
    "\u00c4\u0092": "Ē",
    "\u00c4\u0093": "ē",
    "\u00c4\u0098": "Ę",
    "\u00c4\u0099": "ę",
    "\u00c4\u009a": "Ě",
    "\u00c4\u009b": "ě",
    "\u00c4\u009e": "Ğ",
    "\u00c4\u009f": "ğ",
    "\u00c4\u00a0": "Ġ",
    "\u00c4\u00a1": "ġ",
    "\u00c4\u00a2": "Ģ",
    "\u00c4\u00a3": "ģ",
    "\u00c4\u00aa": "Ī",
    "\u00c4\u00ab": "ī",
    "\u00c4\u00ae": "Į",
    "\u00c4\u00af": "į",
    "\u00c4\u00b0": "İ",
    "\u00c4\u00b1": "ı",
    "\u00c4\u00bb": "Ļ",
    "\u00c4\u00bc": "ļ",
    "\u00c4\u00bd": "Ľ",
    "\u00c4\u00be": "ľ",
    "\u00c4\u00bf": "Ŀ",
    "\u00c5\u0080": "Ł",
    "\u00c5\u0081": "ł",
    "\u00c5\u0084": "Ń",
    "\u00c5\u0085": "ń",
    "\u00c5\u0087": "Ň",
    "\u00c5\u0088": "ň",
    "\u00c5\u0089": "ŉ",
    "\u00c5\u0092": "Œ",
    "\u00c5\u0093": "œ",
    "\u00c5\u009a": "Ś",
    "\u00c5\u009b": "ś",
    "\u00c5\u009e": "Ş",
    "\u00c5\u009f": "ş",
    "\u00c5\u00a0": "Š",
    "\u00c5\u00a1": "š",
    "\u00c5\u00a2": "Ţ",
    "\u00c5\u00a3": "ţ",
    "\u00c5\u00a4": "Ť",
    "\u00c5\u00a5": "ť",
    "\u00c5\u00aa": "Ū",
    "\u00c5\u00ab": "ū",
    "\u00c5\u00af": "Ů",
    "\u00c5\u00b0": "ű",
    "\u00c5\u00b1": "ų",
    "\u00c5\u00b2": "Ų",
    "\u00c5\u00b3": "Ŵ",
    "\u00c5\u00b4": "ŵ",
    "\u00c5\u00b8": "Ÿ",
    "\u00c5\u00ba": "Ź",
    "\u00c5\u00bb": "ź",
    "\u00c5\u00bc": "Ż",
    "\u00c5\u00bd": "ž",
    "\u00c5\u00be": "ź",
    "\u00c6\u0084": "Ƅ",
    "\u00c6\u0085": "ƅ",
    "\u00c7\u008d": "Ǎ",
    "\u00c7\u008e": "ǎ",
    "\u00c7\u009f": "ǟ",
    "\u00c7\u00b1": "Ǳ",
    "\u00c7\u00b2": "ǲ",
    "\u00c7\u00b3": "ǳ",
    "\u00c7\u00b5": "ǵ",
    "\u00c7\u00b6": "Ƕ",
    "\u00c7\u00b7": "Ƿ",
    "\u00c7\u00b8": "Ǹ",
    "\u00c7\u00b9": "ǹ",
    "\u00c7\u00ba": "Ǻ",
    "\u00c7\u00bb": "ǻ",
    "\u00c7\u00bc": "Ǽ",
    "\u00c7\u00bd": "ǽ",
    "\u00c7\u00be": "Ǿ",
    "\u00c7\u00bf": "ǿ",

    "\u00c2\u00b7": "·"
}