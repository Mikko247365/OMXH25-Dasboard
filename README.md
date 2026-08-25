OMXH25 Osakedashboard

## Projektin kuvaus

OMXH25 Osakedashboard on kouluprojektina toteutettu interaktiivinen sovellus, jonka tarkoituksena on visualisoida OMXH25-yhtiöiden kurssi- ja talousdataa selkeässä ja helposti tulkittavassa muodossa. Sovelluksella käyttäjä voi tarkastella yksittäisten yhtiöiden kehitystä, vertailla useita yhtiöitä keskenään sekä analysoida kvartaalituloksia.

Projektin tavoitteena on yhdistää talousdata, datankäsittely ja visualisointi toimivaksi kokonaisuudeksi, joka auttaa hahmottamaan yhtiöiden kehitystä yhdellä näkymällä.

---

## Ominaisuudet

- Yhtiökohtainen kurssikehityksen tarkastelu
- Avaintunnuslukujen näyttäminen valitulle yhtiölle
- Kvartaalitulosten visualisointi pylväskaavioina ja taulukkona
- Usean yhtiön vertailu samassa näkymässä
- Normalisoitu kurssivertailu, jossa eri yhtiöiden kehitystä voidaan verrata samalla asteikolla
- Päivämäärä- tai kvartaalipohjainen tarkastelu

---

## Käytetyt teknologiat

- Python
- Streamlit
- Pandas
- Plotly
- yfinance
- CSV-tiedostot datan tallennuksessa ja kvartaalidatan hallinnassa

---

## Projektin rakenne

- `app.py`  
  Sovelluksen pääkäynnistys, käyttöliittymän perusrakenne ja näkymien kokoaminen.

- `data.py`  
  Datan haku, käsittely, esikäsittely ja apufunktiot, kuten kurssidatan normalisointi.

- `charts.py`  
  Visualisointien, kaavioiden ja vertailutaulukoiden renderöinti.

- `Kvarttaalidata.csv`  
  Kvartaalitulosten lähdedata visualisointeja varten.

---

## Datan lähteet

Sovelluksen markkinadata ja osa tunnusluvuista haetaan `yfinance`-kirjaston kautta. Kvartaalitulokset tallennetaan erilliseen CSV-tiedostoon, jota käytetään dashboardin pääasiallisena lähteenä kvartaalitulosten visualisoinneissa.

Projektissa on pyritty pitämään ratkaisu kevyenä, minkä vuoksi CSV-tiedostoa käytetään tietokannan sijaan.

---

## Käyttö

Sovelluksessa käyttäjä voi:

- valita tarkastelutavan päivämäärän tai kvartaalin perusteella
- tarkastella yhden yhtiön kurssikehitystä
- nähdä valitun yhtiön tunnusluvut
- tarkastella kvartaalituloksia pylväskaaviona
- vertailla useita yhtiöitä samassa näkymässä
- tarkastella yhtiöitä joko euromääräisen kurssin tai normalisoidun kehityksen perusteella

---

## Rajoitteet ja jatkokehitys

Projektissa käytetään kevyttä CSV-pohjaista ratkaisua tietokannan sijaan. Tämä on toimiva ratkaisu kouluprojektiin, mutta jatkokehityksessä sovellusta voisi laajentaa esimerkiksi seuraavilla tavoilla:

- automaattisempi kvartaalidatan päivitys
- laajemmat tunnusluvut ja analyysit
- useampia visualisointivaihtoehtoja
- datan validointi virallisista lähteistä
- sovelluksen julkaisu verkkoon muiden tarkasteltavaksi

---

## Yhteenveto
OMXH25 Osakedashboard yhdistää datan käsittelyn, talousinformaation ja visualisoinnin yhdeksi selkeäksi työkaluksi. Projektin avulla voidaan tarkastella suomalaisia pörssiyhtiöitä sekä yhtiökohtaisesti että vertailumuodossa, mikä tekee sovelluksesta hyödyllisen oppimisprojektin sekä datan että käyttöliittymien näkökulmasta.