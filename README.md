# OMXH25-Dasboard

School project for analyzing OMXH25 companies with Python and Streamlit.

## Run locally

#Dashboardin alustavan layoutin luonnostelu VK29
Dashboardin alustava layoutin luonnostelu aloitettiin VK29-vaiheessa. Suunnittelin, miten kurssikehitys, kvartaalitulokset ja tunnusluvut tullaan esittämään dashboardissa. Työ keskeytyi hetkeksi GitHub-tilin lukituksen vuoksi, mutta jatkui heti kun pääsin takaisin repositorioon.

#Käyttöliittymän luonnos yhtiövalinnalle ja aikavälin valinnalle VK30
VK30-vaiheessa luonnostelin käyttöliittymän yhtiövalinnalle ja aikavälin valinnalle. Loin projektia varten uuden Git-haaran päähaarasta, jotta työskentely pysyy erillään muiden tiimin jäsenten keskeneräisistä osioista. Suunnittelin sivupalkin valinnat, joissa käyttäjä voi valita OMXH25-indeksin yhtiön sekä tarkasteltavan aikavälin (1y, 3y, 5y). Nämä valinnat ohjaavat dashboardin datan hakua ja visualisointeja.

#Datan käsittelyn kuvaus VK30
Projektissa käytettävä data haetaan yfinance-kirjaston avulla, joka tarjoaa rajapinnan pörssinoteerattujen yhtiöiden kurssitietoihin. Dashboardissa käytettävä data koostuu OMXH25-indeksin yhtiöiden historiallisista kurssitiedoista, tunnusluvuista ja kvartaalituloksista. Datan lataus tapahtuu projektin data.py-moduulissa, jossa määritellään yhtiökohtainen datan haku ja aikavälin suodatus käyttäjän valintojen perusteella.
Datan käsittely sisältää kurssihistorian hakemisen yfinance-kirjaston Ticker-olion avulla, DataFrame-muunnoksen, päivämääräsarakkeen normalisoinnin, puuttuvien arvojen käsittelyn sekä mahdollisten tunnuslukujen ja kvartaalitulosten yhdistämisen erillisistä lähteistä. Lopullinen data sisältää päivämäärän, yhtiön kurssin, tunnusluvut ja kvartaalitulokset, joita käytetään dashboardin visualisoinneissa.

#Dashboardin layoutin toteutus VK31
VK31-vaiheessa toteutin dashboardin peruslayoutin omaan Git-haaraani niina-ui-design. Rakensin Streamlit-sovelluksen, jossa käyttöliittymä jakautuu kahteen palstaan: vasemmalla kurssikehityksen viivagraafi ja oikealla yhtiön perustiedot selkeänä tietokorttina. Lisäksi rakensin omat osiot kvartaalituloksille ja tunnusluvuille, jotka täytetään myöhemmin datatiimin tuottamilla arvoilla.

#Aikavälin valintakomponentit käyttöliittymässä VK31
VK31-vaiheessa toteutin toimivan aikavälin valintakomponentin, jonka avulla käyttäjä voi tarkastella yhtiön kurssikehitystä eri ajanjaksoilla. Valinta ohjaa datan hakua ja graafin päivittymistä reaaliaikaisesti. Testasin toiminnallisuuden Streamlitin kautta ja varmistin, että yhtiövalinta, aikavälin valinta ja graafin päivittyminen toimivat oikein.

#Dokumentointi: käyttöliittymän rakenne VK31
Lopuksi dokumentoin käyttöliittymän rakenteen VK31-vaiheessa. Kuvasin, miten dashboard koostuu kolmesta pääosiosta: kurssikehitys, kvartaalitulokset ja tunnusluvut. Selitin sivupalkin valinnat, kaksipalstaisen layoutin, perustietokortin sekä placeholder-osioiden tarkoituksen. Dokumentointi tukee käyttöliittymän jatkokehitystä ja varmistaa, että rakenne vastaa projektisuunnitelman vaatimuksia.

#Käyttöliittymän parannukset visualisointeja varten VK32
VK32-vaiheessa keskityttiin dashboardin visualisointien parantamiseen ja käyttöliittymän selkeyttämiseen. Tavoitteena oli tehdä graafeista informatiivisempia ja helpommin tulkittavia sekä varmistaa, että eri osiot muodostavat yhtenäisen kokonaisuuden. Parannuksia tehtiin kurssikehityksen viivagraafiin, yhtiön perustietokorttiin sekä kvartaalitulosten ja tunnuslukujen esitystapaan.

Kurssikehityksen graafiin lisättiin selkeämpi värimaailma, korostukset ja paremmat akselimerkinnät, jotta eri aikavälien vertailu olisi helpompaa. Lisäksi varmistettiin, että graafi reagoi välittömästi käyttäjän tekemiin valintoihin sivupalkissa. Yhtiön perustietokorttia muokattiin visuaalisesti yhtenäisemmäksi ja siihen lisättiin tilaa mahdollisille lisätiedoille, kuten markkina-arvolle ja toimialalle.

Kvartaalitulosten ja tunnuslukujen osioita valmisteltiin tulevaa dataintegraatiota varten. Näihin osioihin lisättiin selkeä rakenne, joka mahdollistaa datan esittämisen taulukkomuodossa tai graafisesti riippuen siitä, miten datatiimi toimittaa arvot. Käyttöliittymän yleistä asettelua parannettiin siten, että eri osiot ovat visuaalisesti tasapainossa ja käyttäjä pystyy siirtymään niiden välillä sujuvasti.