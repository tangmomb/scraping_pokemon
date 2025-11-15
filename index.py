import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Fonction pour extraire tous les noms de Pokémon depuis la page nationale
def extract_all_pokemon_names(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    names = [a.text.strip() for a in soup.find_all("a", class_="ent-name")]
    return names

# Fonction pour générer le lien Pokédex pour chaque Pokémon
def get_pokedex_url(name):
    base_url = "https://pokemondb.net/pokedex/"
    # Nettoyer le nom : minuscules, espaces et caractères spéciaux remplacés par '-'
    name_clean = name.lower()
    name_clean = name_clean.replace(" ", "-")
    return f"{base_url}{name_clean}"

# --- Extraction de tous les noms de Pokémon depuis la page nationale ---
national_url = "https://pokemondb.net/pokedex/national"
all_names = extract_all_pokemon_names(national_url)
# Ajouter la colonne lien pokedex
links = [get_pokedex_url(name) for name in all_names]
df_names = pd.DataFrame({"Nom": all_names, "Lien": links})
df_names.to_csv("pokemon_names.csv", index=False, encoding="utf-8")
print(df_names)


# Fonction pour générer le lien de l'image à partir du nom du Pokémon
def get_pokemon_image_url(name):
    base_url = "https://img.pokemondb.net/artwork/large/"
    # Nettoyer le nom : minuscules, espaces et caractères spéciaux remplacés par '-'
    name_clean = name.lower()
    name_clean = re.sub(r"[^a-z0-9]+", "-", name_clean)
    name_clean = name_clean.strip('-')
    return f"{base_url}{name_clean}.jpg"

# Fonction générique pour extraire les infos d'un tableau à partir du titre h2
def extract_table_data(soup, h2_title):
    """Extrait les infos d'un tableau identifié par le titre h2 sous forme de dictionnaire."""
    h2 = soup.find("h2", string=h2_title)
    data = {}
    if h2:
        table = h2.find_next("table", class_="vitals-table")
        if table:
            for row in table.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    key = th.text.strip()
                    # Pour les types, abilities, local numbers, on veut le texte complet (avec <br> séparés)
                    if key in ["Type", "Abilities", "Local №"]:
                        value = " | ".join([t.strip() for t in td.stripped_strings])
                    else:
                        value = td.text.strip()
                    data[key] = value
    return data


url = "https://pokemondb.net/pokedex/arcanine"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Exemple : récupérer le nom du Pokémon
name = soup.find("h1").text.strip()


# Utilisation de la fonction pour extraire les données de plusieurs tableaux
data = {}
for section in ["Pokédex data", "Training", "Breeding", "Base stats"]:
    section_data = extract_table_data(soup, section)
    # Pour éviter les collisions de clés, préfixer si besoin
    for k, v in section_data.items():
        if k in data:
            data[f"{section} - {k}"] = v
        else:
            data[k] = v


# Ajouter le nom du Pokémon comme première colonne et l'image à la fin
image_url = get_pokemon_image_url(name)
data_with_name = {"Nom": name}
data_with_name.update(data)
data_with_name["Image"] = image_url
df = pd.DataFrame([data_with_name])
df.to_csv("pokedex_data.csv", index=False, encoding="utf-8")


# Afficher le CSV avec les champs en colonnes
read_csv = pd.read_csv("pokedex_data.csv")
print(read_csv)