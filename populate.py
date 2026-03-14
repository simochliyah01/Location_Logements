import os
import django
import urllib.request

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from logements.models import Logement
from accounts.models import User
from django.core.files import File
import tempfile

proprietaire = User.objects.filter(role='proprietaire').first()
if not proprietaire:
    print("❌ Aucun propriétaire trouvé ! Crée d'abord un compte propriétaire.")
    exit()

logements_data = [
    {
        'titre': 'Villa Luxueuse avec Piscine — Marrakech',
        'description': 'Magnifique villa avec piscine privée dans la Palmeraie de Marrakech. Jardin andalou, terrasse panoramique, décoration orientale authentique. Idéale pour familles et groupes.',
        'adresse': 'Route de la Palmeraie, Circuit de la Palmeraie',
        'ville': 'Marrakech',
        'prix_par_nuit': 1200,
        'capacite': 8,
        'type_logement': 'villa',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800',
    },
    {
        'titre': 'Riad Authentique — Médina de Fès',
        'description': 'Riad traditionnel restauré au cœur de la médina de Fès. Zeliges artisanaux, fontaine centrale, terrasse avec vue sur les toits. Expérience marocaine unique.',
        'adresse': 'Derb Tazi, Médina',
        'ville': 'Fès',
        'prix_par_nuit': 450,
        'capacite': 6,
        'type_logement': 'riad',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=800',
    },
    {
        'titre': 'Appartement Vue Mer — Tanger',
        'description': 'Superbe appartement avec vue panoramique sur le détroit de Gibraltar. Terrasse privée, cuisine équipée, parking inclus. À 5 min de la plage.',
        'adresse': 'Boulevard Mohammed VI, Corniche',
        'ville': 'Tanger',
        'prix_par_nuit': 380,
        'capacite': 4,
        'type_logement': 'appartement',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800',
    },
    {
        'titre': 'Villa Bord de Mer — Agadir',
        'description': 'Villa directement sur la plage d\'Agadir. Accès privé à la plage, piscine chauffée, 4 chambres avec salle de bain. Vue imprenable sur l\'océan Atlantique.',
        'adresse': 'Secteur Balnéaire, Boulevard du 20 Août',
        'ville': 'Agadir',
        'prix_par_nuit': 950,
        'capacite': 8,
        'type_logement': 'villa',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1613977257363-707ba9348227?w=800',
    },
    {
        'titre': 'Appartement Moderne — Casablanca Centre',
        'description': 'Appartement contemporain au cœur de Casablanca, quartier Maarif. Entièrement meublé et équipé, climatisation, wifi haut débit. À proximité des restaurants et centres commerciaux.',
        'adresse': 'Quartier Maarif, Rue Socrate',
        'ville': 'Casablanca',
        'prix_par_nuit': 350,
        'capacite': 4,
        'type_logement': 'appartement',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800',
    },
    {
        'titre': 'Appartement Hassan II — Rabat',
        'description': 'Bel appartement lumineux proche de la Tour Hassan et du Mausolée Mohammed V. Idéal pour découvrir la capitale du Maroc. Quartier calme et sécurisé.',
        'adresse': 'Avenue Moulay Hassan, Quartier Hassan',
        'ville': 'Rabat',
        'prix_par_nuit': 300,
        'capacite': 3,
        'type_logement': 'appartement',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800',
    },
    {
        'titre': 'Maison Bleue — Chefchaouen',
        'description': 'Maison typique dans la célèbre ville bleue du Rif. Décoration artisanale, vue sur les montagnes, terrasse privée. Ambiance unique et reposante.',
        'adresse': 'Médina, Rue Targui',
        'ville': 'Chefchaouen',
        'prix_par_nuit': 280,
        'capacite': 5,
        'type_logement': 'maison',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1570939274717-7eda259b50ed?w=800',
    },
    {
        'titre': 'Studio Cosy — Guéliz Marrakech',
        'description': 'Studio moderne et cosy dans le quartier européen de Marrakech. À deux pas des restaurants branchés et boutiques de luxe. Parfait pour une escapade en couple.',
        'adresse': 'Rue de la Liberté, Guéliz',
        'ville': 'Marrakech',
        'prix_par_nuit': 220,
        'capacite': 2,
        'type_logement': 'studio',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800',
    },
    {
        'titre': 'Appartement Agdal — Rabat',
        'description': 'Grand appartement dans le prestigieux quartier Agdal de Rabat. Proche des ambassades, ministères et universités. Idéal pour séjour professionnel ou familial.',
        'adresse': 'Avenue Fal Ould Oumeir, Agdal',
        'ville': 'Rabat',
        'prix_par_nuit': 320,
        'capacite': 4,
        'type_logement': 'appartement',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800',
    },
    {
        'titre': 'Riad Jardin — Meknès',
        'description': 'Magnifique riad avec jardin fleuri dans la ville impériale de Meknès. Proche du Méchouar et des remparts historiques. Petit-déjeuner marocain inclus.',
        'adresse': 'Médina, Rue Rouamzine',
        'ville': 'Meknès',
        'prix_par_nuit': 350,
        'capacite': 6,
        'type_logement': 'riad',
        'disponible': True,
        'image_url': 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800',
    },
]

ddef telecharger_image(url, nom_fichier):
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/jpeg'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            tmp.write(response.read())
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠️  Image non téléchargée: {e}")
        return None

print("🚀 Création des logements...\n")

for data in logements_data:
    image_url = data.pop('image_url')

    logement = Logement(proprietaire=proprietaire, **data)

    # Télécharger et attacher l'image
    tmp_path = telecharger_image(image_url, data['titre'])
    if tmp_path:
        with open(tmp_path, 'rb') as f:
            nom = data['titre'][:30].replace(' ', '_').replace('—', '').strip() + '.jpg'
            logement.image.save(nom, File(f), save=False)
        os.unlink(tmp_path)

    logement.save()
    print(f"✅ {logement.titre} — {logement.ville} ({logement.prix_par_nuit} DH/nuit)")

print(f"\n🎉 {len(logements_data)} logements créés avec succès !")