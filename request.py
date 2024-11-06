import requests

# Remplace l'URL par celle de ton projet Django
url = "http://localhost:8000/assign-tasks/1/2024-10-31/"
response = requests.get(url)

if response.status_code == 200:
    print("Réponse:", response.json())
else:
    print("Erreur:", response.status_code)
