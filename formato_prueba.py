import base64
import requests
import re

# === CONFIGURACIÓN ===
IMAGE_PATH = "crops/persona1.jpg"
SERVER_URL = "http://localhost:8080/v1/chat/completions"
PROMPT = """
Describe the main person in the image using the following format:

hair:  
shirt:  
pants:  
shoes:  
accessories:  
skin color:  
estimated gender:  
estimated age:  
estimated height:  

If something is not visible, leave it blank. Only respond using the format above. Do not add any extra text or description.
"""

# === LISTAS DE PALABRAS CLAVE ===
COLORS = [
    "white", "black", "gray", "grey", "blue", "light blue", "dark blue", "navy blue",
    "red", "green", "yellow", "pink", "brown", "beige", "orange", "purple",
    "light brown", "dark brown", "peach", "cream", "tan", "teal"
]
SHIRT_TYPES = ["shirt", "t-shirt", "tank top", "blouse", "jacket", "sweater", "hoodie", "hawaiian shirt", "sweatshirt", "pullover", "top"]
PANTS_TYPES = ["jeans", "pants", "shorts", "skirt", "bermuda", "trousers", "leggings", "sweatpants"]
SHOE_TYPES = ["shoes", "sneakers", "boots", "sandals", "loafers", "heels", "trainers"]
HAIR_COLORS = ["blonde", "brown", "black", "gray", "red", "dark"]
HAIR_LENGTHS = ["long", "short"]
HAIR_STYLES = ["curly", "straight", "wavy", "ponytail", "bald"]
ACCESSORY_TYPES = ["hat", "cap", "goggles", "glasses", "sunglasses", "watch", "bracelet", "backpack", "bag", "purse"]

# === FUNCIONES AUXILIARES ===
def query_llama(image_path, prompt):
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "model": "smolvlm",
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": prompt.strip()},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ]}
        ],
        "max_tokens": 250,
        "temperature": 0
    }
    response = requests.post(SERVER_URL, json=payload)
    return response.json()["choices"][0]["message"]["content"]

def extract_keywords(text, keywords):
    text = text.lower()
    return list(set([kw for kw in keywords if kw in text]))

def extract_field(content, field):
    match = re.search(rf"{field}:\s*([^:,]+(?:,[^:,]+)*)", content, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_color_for_item(desc, item_keywords):
    found_colors = []
    for item in item_keywords:
        matches = re.findall(rf"([a-z ]+?) {item}", desc)
        for phrase in matches:
            found_colors += extract_keywords(phrase.strip(), COLORS)
    return list(set(found_colors))

# === PARSER PRINCIPAL ===
def parse_description(description):
    desc = description.replace("\n", " ").strip().lower()
    parsed = {
        "shirt": {"color": [], "type": []},
        "pants": {"color": [], "type": []},
        "shoes": {"color": [], "type": []},
        "hair": {"color": [], "length": [], "style": []},
        "accessories": [],
        "estimated gender": "",
        "estimated age": "",
        "estimated height": ""
    }

    # === CAMPOS EXPLÍCITOS ===
    parsed["estimated gender"] = extract_field(desc, "estimated gender")
    parsed["estimated age"] = extract_field(desc, "estimated age")
    parsed["estimated height"] = extract_field(desc, "estimated height")

    parsed["shirt"]["type"] = extract_keywords(extract_field(desc, "shirt"), SHIRT_TYPES)
    parsed["pants"]["type"] = extract_keywords(extract_field(desc, "pants"), PANTS_TYPES)
    parsed["shoes"]["type"] = extract_keywords(extract_field(desc, "shoes"), SHOE_TYPES)

    parsed["shirt"]["color"] = extract_keywords(extract_field(desc, "shirt"), COLORS)
    parsed["pants"]["color"] = extract_keywords(extract_field(desc, "pants"), COLORS)
    parsed["shoes"]["color"] = extract_keywords(extract_field(desc, "shoes"), COLORS)

    parsed["hair"]["color"] = extract_keywords(extract_field(desc, "hair"), HAIR_COLORS)
    parsed["hair"]["length"] = extract_keywords(extract_field(desc, "hair"), HAIR_LENGTHS)
    parsed["hair"]["style"] = extract_keywords(extract_field(desc, "hair"), HAIR_STYLES)

    parsed["accessories"] = extract_keywords(extract_field(desc, "accessories"), ACCESSORY_TYPES)

    # === INFERENCIA NARRATIVA: GÉNERO Y EDAD ===
    if parsed["estimated gender"] == "":
        gender_terms = {
            "male": [" a man ", " man ", "male", "masculine", "guy", "gentleman", " he ", " his "],
            "female": [" a woman ", " woman ", "female", "feminine", "lady", "girl", " she ", " her "]
        }
        detected_gender = ""
        for gender, terms in gender_terms.items():
            if any(term in desc for term in terms):
                detected_gender = gender
                break
        parsed["estimated gender"] = detected_gender

    if parsed["estimated age"] == "":
        age_terms = {
            "child": ["child", "kid", "boy", "girl"],
            "teen": ["teen", "teenager"],
            "young adult": ["young adult", "20s", "in their twenties", "early thirties"],
            "middle-aged": ["middle-aged", "middle age", "40s", "50s"],
            "senior": ["elderly", "old man", "old woman", "senior", "aged", "60s", "70s"]
        }
        for label, terms in age_terms.items():
            if any(term in desc for term in terms):
                parsed["estimated age"] = label
                break

    # === ASOCIACIÓN GENERAL DE COLORES POR PRENDA ===
    parsed["shirt"]["color"] += extract_color_for_item(desc, SHIRT_TYPES)
    parsed["pants"]["color"] += extract_color_for_item(desc, PANTS_TYPES)
    parsed["shoes"]["color"] += extract_color_for_item(desc, SHOE_TYPES)

    # === ASOCIACIÓN GENERAL DE TIPOS POR TEXTO COMPLETO ===
    parsed["shirt"]["type"] += extract_keywords(desc, SHIRT_TYPES)
    parsed["pants"]["type"] += extract_keywords(desc, PANTS_TYPES)
    parsed["shoes"]["type"] += extract_keywords(desc, SHOE_TYPES)

    # === CABELLO: inferir color, largo, estilo desde frases tipo "short curly dark hair"
    if not any(parsed["hair"].values()):
        hair_matches = re.findall(r"((?:short|long)? ?(?:curly|wavy|straight)? ?(?:blonde|black|brown|red|gray|dark)?) hair", desc)
        for phrase in hair_matches:
            parsed["hair"]["length"] += extract_keywords(phrase, HAIR_LENGTHS)
            parsed["hair"]["style"] += extract_keywords(phrase, HAIR_STYLES)
            parsed["hair"]["color"] += extract_keywords(phrase, HAIR_COLORS)

    # === Accessories narrativos también
    if not parsed["accessories"]:
        parsed["accessories"] = extract_keywords(desc, ACCESSORY_TYPES)

    # === Eliminar duplicados
    for section in ["shirt", "pants", "shoes", "hair"]:
        for key in parsed[section]:
            parsed[section][key] = list(set(parsed[section][key]))

    parsed["accessories"] = list(set(parsed["accessories"]))

    return parsed

# === MAIN ===
if __name__ == "__main__":
    print("🔍 Enviando imagen al modelo...\n")
    raw_response = query_llama(IMAGE_PATH, PROMPT)

    print("=== 📥 Respuesta original del modelo ===")
    print(raw_response)

    print("\n=== 🧠 Datos extraídos por el script ===")
    structured = parse_description(raw_response)

    for part, attrs in structured.items():
        print(f"\n{part.upper()}:")
        if isinstance(attrs, dict):
            for key, val in attrs.items():
                print(f"  {key}: {', '.join(val) if val else 'unknown'}")
        elif isinstance(attrs, list):
            print(f"  items: {', '.join(attrs) if attrs else 'none'}")
        else:
            print(f"  value: {attrs if attrs else 'unknown'}")
