import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from supabase import create_client, Client
from st_supabase_connection import SupabaseConnection

# Supabase-Setup (ersetze mit deinen Keys; besser in secrets.toml speichern)
SUPABASE_URL = "https://dein-projekt.supabase.co"
SUPABASE_KEY = "eyJ...dein-anon-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Modell laden (dein .h5 aus Teachable Machine)
model = tf.keras.models.load_model('keras_model.h5')  # Pfad zu deinem .h5
with open('labels.txt', 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Streamlit-App
st.title("Fundbüro-App: Fundsachen hochladen und suchen")

# Abschnitt: Bild hochladen und klassifizieren
uploaded_file = st.file_uploader("Lade ein Bild hoch (z.B. Kleidung)", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    # Bild anzeigen
    image = Image.open(uploaded_file)
    st.image(image, caption="Hochgeladenes Bild", use_column_width=True)
    
    # Vorbereitung für Modell: Resize zu 224x224 (Standard für Teachable Machine)
    image = image.resize((224, 224))
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    
    # Klassifizieren
    predictions = model.predict(image_array)
    predicted_class = np.argmax(predictions)
    kategorie = labels[predicted_class]
    st.write(f"Erkannte Kategorie: **{kategorie}**")
    
    # Beschreibung optional
    beschreibung = st.text_input("Beschreibung hinzufügen (optional)")
    
    if st.button("In Fundbüro speichern"):
        # Bild in Supabase Storage hochladen
        file_bytes = io.BytesIO()
        image.save(file_bytes, format='JPEG')
        file_bytes.seek(0)
        upload_response = supabase.storage.from_("fundbilder").upload(
            f"{uploaded_file.name}", file_bytes.read(), {"content-type": "image/jpeg"}
        )
        
        if upload_response:
            bild_url = f"{SUPABASE_URL}/storage/v1/object/public/fundbilder/{uploaded_file.name}"
            
            # In DB einfügen
            data = {
                "kategorie": kategorie,
                "bild_url": bild_url,
                "beschreibung": beschreibung
            }
            insert_response = supabase.table("fundsachen").insert(data).execute()
            
            if insert_response:
                st.success("Fundsache
