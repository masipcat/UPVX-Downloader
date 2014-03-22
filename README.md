UPVX Downloader
===============

Descarrega els vídeos dels cursos MOOC de la UPV fàcilment.
## Què necessito?

És necessari tenir instal·lat Python 2.6+ i les següents dependències (per instal·lar les dependències podeu utilitzar `pip` o `easy_install`):

* BeautifulSoup
* pytube (0.2.1+)
* requests

## Com ho faig per baixar els vídeos?

Primer de tot heu de dirigir-vos a la direcció del curs des del vostre navegador i iniciar sessió (si no estava iniciada). Tot seguit, heu de cercar la *cookie* amb nom `ACSID` i copieu el valor dins el fitxer `upvx.py` (dins la variable `plain_cookies`).

Ara només heu de copiar `upvx.py` al directori on voleu que es baixin els vídeos i un cop allà obrir el terminal i escriure `python upvx.py` i seguir les indicacions del *script*.