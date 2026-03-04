# test_gpu_connection.py - Tester la connexion au serveur GPU
from gpu_client import get_gpu_client
from prompt_utils import optimize_prompt

print("=" * 60)
print("🧪 Test de connexion au serveur GPU distant")
print("=" * 60)

# Récupérer le client
gpu_client = get_gpu_client()

# Test 1 : Vérifier la connexion
print("\n📡 Test 1: Vérification de la connexion...")
is_connected = gpu_client.check_connection()

if not is_connected:
    print("\n❌ Impossible de se connecter au serveur GPU")
    print("Vérifie que :")
    print("  - Le serveur est bien allumé")
    print("  - L'URL est correcte: http://37.26.187.4:8000")
    print("  - Le token est valide: tristanlovesia")
    exit(1)

# Test 2 : Générer une image
print("\n🎨 Test 2: Génération d'une vraie image...")
prompt = "Marseille avec des arbres partout"
optimized_prompt = optimize_prompt(prompt)

print(f"\n📝 Prompt utilisateur: {prompt}")
print(f"✨ Prompt optimisé: {optimized_prompt}")

try:
    images = gpu_client.generate_image(
        prompt=optimized_prompt,
        width=512,
        height=512,
        steps=9
    )
    
    # Sauvegarder l'image
    import base64
    from PIL import Image
    from io import BytesIO
    
    image_data = base64.b64decode(images[0])
    image = Image.open(BytesIO(image_data))
    image.save("generated_image.png")
    
    print(f"\n✅ SUCCÈS !")
    print(f"💾 Image sauvegardée: generated_image.png")
    print(f"🖼️  Taille: {image.size}")
    
    # Ouvrir l'image
    image.show()
    
except Exception as e:
    print(f"\n❌ Erreur lors de la génération: {str(e)}")

print("\n" + "=" * 60)