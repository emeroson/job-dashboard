import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.novojob.com/cote-d-ivoire/offres-d-emploi"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

postes = []
entreprises = []
villes = []

jobs = soup.find_all("h2", class_="ellipsis row-fluid")

for job in jobs:

    poste = job.get_text(strip=True)

    spans = job.find_all_next("span", limit=2)

    entreprise = spans[0].get_text(strip=True) if len(spans) > 0 else None
    ville = spans[1].get_text(strip=True) if len(spans) > 1 else None

    postes.append(poste)
    entreprises.append(entreprise)
    villes.append(ville)

df = pd.DataFrame({
    "poste": postes,
    "entreprise": entreprises,
    "ville": villes
})

df.to_csv("data.csv", index=False, encoding="utf-8-sig")

print("Scraping terminé")