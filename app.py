import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
from supabase import create_client
import uuid
import io
from datetime import datetime

# Supabase Verbindung
SUPABASE_URL = "DEINE_SUPABASE_URL"
SUPABASE_KEY = "DEIN_SUPABASE_ANON_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Modell laden
model = tf.keras.models.load_model("keras_model.h5")

# Labels laden
def load_labels():
    labels = []
    with open("labels.txt", "r") as f:
        for line in f:
            label = line.strip().split(" ", 1)[1]
            labels.append(label)
    return labels

labels = load_labels()

st.title("Fundbüro")

uploaded_file = st.file_uploader("Bild hochladen", type=["jpg","jpeg","png"])

beschreibung = st.text_input("Beschreibung")

typ = st.selectbox("Typ", ["Fund", "Verlust"])

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Hochgeladenes Bild", width=300)

    # Bild für Modell vorbereiten
    img = image.resize((224,224))
    img_array = np.array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)

    class_index = np.argmax(prediction)

    kategorie = labels[class_index]

    st.write("Erkannte Kategorie:", kategorie)

    if st.button("Speichern"):

        try:

            filename = f"{uuid.uuid4()}.jpg"

            image_bytes = io.BytesIO()
            image.save(image_bytes, format="JPEG")

            supabase.storage.from_("images").upload(
                path=filename,
                file=image_bytes.getvalue(),
                file_options={"content-type": "image/jpeg"}
            )

            public_url = supabase.storage.from_("images").get_public_url(filename)

            supabase.table("fundbuero").insert({
                "bild_url": public_url,
                "kategorie": kategorie,
                "beschreibung": beschreibung,
                "typ": typ,
                "datum": datetime.now().strftime("%d.%m.%Y")
            }).execute()

            st.success("Upload erfolgreich!")

        except Exception as e:

            st.error(f"Fehler: {e}")     st.write(eintrag["kategorie"])
        st.write(eintrag["beschreibung"])
        st.write(eintrag["datum"])
