import json

def clean_tree(tree: dict) -> dict:
    cleaned = {}
    for parent, children in tree.items():
        # Rimuovi il figlio che ha lo stesso nome del genitore
        new_children = {
            k: v for k, v in children.items()
            if k != parent
        }
        # Ricorsione sui figli rimanenti
        cleaned[parent] = clean_tree(new_children) if new_children else {}
    return cleaned

# Carica il file JSON
with open("RYMGenreHierarchy_copy.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Pulisci l'albero
cleaned_data = clean_tree(data)

# Salva il risultato in un nuovo file
with open("generi_clean.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
