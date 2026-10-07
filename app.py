import openai
import streamlit as st


PROMPT_SISTEMA_DJ = (
    "Eres un DJ residente en clubes underground y un selector musical de élite. "
    "Tu único objetivo es recomendar 3 canciones NO mainstream (joyas ocultas, "
    "sellos independientes, fuera de los top charts comerciales) que armonicen "
    "perfectamente en BPM, clave armónica y energía con la canción que te indique "
    "el usuario. Estima el BPM y la Clave Armónica (Key) de cada recomendación. "
    "Responde estrictamente con una canción por línea, sin números al principio, "
    "usando únicamente este formato y separando los datos con barras verticales: "
    "[Título] | [Artista] | [BPM] | [Key] | [Explicación]."
)


def buscar_mezclas(cancion, artista, genero, energia, estructura, api_key):
    """Busca recomendaciones de mezclas usando la API de OpenAI."""
    try:
        cliente = openai.OpenAI(api_key=api_key)
        respuesta = cliente.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA_DJ},
                {
                    "role": "user",
                    "content": (
                        f"Busca mezclas para la canción: {cancion} del artista: "
                        f"{artista}. El género de la sesión es {genero}. "
                        f"El nivel de energía deseado es {energia}/10 y la pista "
                        f"debe ser {estructura}"
                    ),
                },
            ],
        )
        return respuesta.choices[0].message.content
    except openai.AuthenticationError:
        return (
            "No se pudo autenticar con OpenAI. Comprueba que la API Key "
            "sea correcta."
        )
    except Exception as error:
        return f"No se pudieron buscar mezclas en este momento: {error}"


st.set_page_config(
    page_title="Underground Matcher",
    page_icon="🎧",
    layout="centered",
)


with st.sidebar:
    st.header("Configuración")
    openai_api_key = st.text_input(
        "API Key de OpenAI",
        type="password",
        placeholder="sk-...",
    )
    st.caption("Tu clave solo se utiliza durante esta sesión y no se guarda.")


st.title("🎧 Underground Matcher")
st.subheader("Encuentra joyas ocultas (no mainstream) que armonicen perfectamente con tu track")
st.write(
    "Introduce los datos de tu track actual y descubre nuevas mezclas "
    "para elevar tu sesión."
)


with st.form("track_search_form"):
    song_name = st.text_input("Nombre de la canción original")
    artist = st.text_input("Artista")
    vibe = st.selectbox(
        "Género o Vibe de la sesión",
        ["Techno", "Tech House", "Melodic", "Hip Hop", "Comercial", "Otro"],
    )
    energia = st.slider(
        "Nivel de Energía de la mezcla (1 = Warm up chill, 10 = Peak time rompepistas)",
        min_value=1,
        max_value=10,
        value=7,
    )
    estructura = st.radio(
        "Estructura",
        ["Indiferente", "Estrictamente Instrumental", "Con Vocales"],
    )
    submitted = st.form_submit_button("Buscar Tracks Ocultos")


if submitted:
    if not song_name.strip() or not artist.strip():
        st.warning("Completa el nombre de la canción y el artista para continuar.")
    elif not openai_api_key.strip():
        st.warning("Introduce tu API Key de OpenAI para buscar mezclas.")
    else:
        with st.spinner("Buscando en los vinilos más ocultos..."):
            resultado = buscar_mezclas(
                song_name,
                artist,
                vibe,
                energia,
                estructura,
                openai_api_key,
            )

        try:
            canciones = []
            for linea in resultado.splitlines():
                if not linea.strip():
                    continue
                datos = [dato.strip() for dato in linea.split("|")]
                if len(datos) != 5:
                    raise ValueError("La respuesta no contiene cinco campos.")
                canciones.append(datos)

            if not canciones:
                raise ValueError("La respuesta no contiene canciones.")

            for titulo, artista_recomendado, bpm, key, explicacion in canciones:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{titulo}**")
                    st.write(artista_recomendado)
                    artista_url = artista_recomendado.replace(" ", "+")
                    titulo_url = titulo.replace(" ", "+")
                    st.markdown(
                        f"[🎵 Escuchar en YouTube]"
                        f"(https://www.youtube.com/results?search_query="
                        f"{artista_url}+{titulo_url})"
                    )
                with col2:
                    st.metric(label="BPM", value=bpm)
                with col3:
                    st.metric(label="Key", value=key)

                st.caption(explicacion)
                st.divider()
        except (AttributeError, ValueError, TypeError):
            st.warning(
                "La IA no devolvió el formato esperado. Mostrando la respuesta "
                "en texto plano."
            )
            st.write(resultado)

        st.download_button(
            label="Descargar setlist",
            data=resultado,
            file_name="setlist.txt",
            mime="text/plain",
        )
