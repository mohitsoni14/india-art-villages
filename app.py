import streamlit as st
import pandas as pd
import snowflake.connector
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_calendar import calendar
from datetime import datetime
import csv
import sqlite3
import altair as alt

# --- Set Page Configuration ---
st.set_page_config(
    page_title="India's Cultural Canvas | Incredible India",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Page Header with Background Image ---
st.markdown(
    """
    <style>
    .header {
        background-image: url('https://images.pexels.com/photos/2477374/pexels-photo-2477374.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2');
        background-size: cover;
        background-position: center;
        border-radius: 15px;
        padding: 80px;
        color: WHITE;
        text-align: center;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
    }
    .header h1 {
        font-size: 50px;
        font-weight: bold;
        letter-spacing: 1px;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
    }
    .header p {
        font-size: 20px;
        letter-spacing: 0.5px;
    }
    .tabs {
        display: flex;
        justify-content: center;
        margin-top: 30px;
        border-bottom: 2px solid #ccc;
    }
    .tab-button {
        padding: 12px 25px;
        margin: 0 20px;
        background-color: #fff;
        color: #555;
        border: 2px solid #4CAF50;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 18px;
        font-weight: 500;
    }
    .tab-button:hover {
        background-color: #f0f0f0;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    .tab-button.selected {
        background-color: #4CAF50;
        color: white;
        box-shadow: 0px 4px 15px rgba(76, 175, 80, 0.3);
    }
    .content {
        padding: 20px;
        animation: fadeIn 0.5s ease;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

# Big India Canvas Headline with Background Image
st.markdown('<div class="header"><h1>India’s Cultural Canvas 🎨</h1><p>Celebrating the rich heritage of India’s vibrant art villages and cultural destinations.</p></div>', unsafe_allow_html=True)

st.markdown("### 🌟 Discover, Experience, and Preserve India's Cultural Roots")
st.markdown("##### From hidden art villages to timeless traditions, explore the unseen side of India.")

# --- Connect to Snowflake and Load Data ---
@st.cache_data
def load_data():
    conn = snowflake.connector.connect(
        user='MOHITSONI09',
        password='Mohitsoni@&1234',
        account='jvqrqhg-mq37542',
        warehouse='COMPUTE_WH',
        database='ART_TOURISM_DB',
        schema='PUBLIC'
    )
    query = "SELECT * FROM ART_VILLAGES_TABLE"
    cur = conn.cursor()
    cur.execute(query)
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(data, columns=columns)
    conn.close()
    return df

villages_df = load_data()

# --- Clean the State Names ---
villages_df['STATE'] = villages_df['STATE'].str.strip().str.upper()

# --- Sidebar Filter ---
states = sorted(villages_df['STATE'].dropna().unique())

selected_state = st.sidebar.selectbox("Select a state", ["ALL"] + states)

if selected_state != "ALL":
    filtered_df = villages_df[villages_df['STATE'] == selected_state]
else:
    filtered_df = villages_df

# Search Box in Sidebar with unique key
search_query = st.sidebar.text_input("🔍 Search by Village or Art Form", key="village_search")

# Navigation tabs using st.tabs
tabs = st.tabs(["🏠 Home", "🗺️ Cultural Map", "📅 Events Calendar", "📈 Analytics", "📖 Stories", "🛍️ Artisan Marketplace"])

# ------------------- HOME -------------------
with tabs[0]:
    st.markdown(
        """
        <style>
        
        .fade-in {
            opacity: 0;
            animation: fadeInUp 1s ease-out forwards;
        }
        .fade-in.delay-1 { animation-delay: 0.3s; }
        .fade-in.delay-2 { animation-delay: 0.6s; }
        .fade-in.delay-3 { animation-delay: 0.9s; }
        .fade-in.delay-4 { animation-delay: 1.2s; }

        @keyframes fadeInUp {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .home-hero {
            background-image: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1350&q=80');
            background-size: cover;
            background-position: center;
            height: 400px;
            border-radius: 15px;
            position: relative;
            color: white;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            margin-bottom: 2rem;
        }
        .home-hero h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
        }
        .home-hero p {
            font-size: 1.3rem;
            max-width: 700px;
            margin: 0 auto;
            text-shadow: 1px 1px 6px rgba(0,0,0,0.6);
        }
        .info-cards {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 3rem;
            flex-wrap: wrap;
        }
        .info-card {
            background: #fffaf3;
             color: #3e2723;
            border-left: 5px solid #8d6e63;

            padding: 25px 30px;
            border-radius: 12px;
            max-width: 280px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
            
        }
        .info-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .info-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: #4CAF50;
        }
        .video-container {
            margin: 3rem auto;
            max-width: 720px;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Background gradient
    st.markdown("""
      <style>
        body {
    background: linear-gradient(to right, #fdfcfb, #e2d1c3);
          }
              </style>
                  """, unsafe_allow_html=True)
    
    # Smooth scroll
    st.markdown("""
<style>
html {
  scroll-behavior: smooth;
}
</style>
""", unsafe_allow_html=True)


    # Hero section with animation
    st.markdown(
        """
        <div class="home-hero fade-in delay-1">
            <h1>Welcome to India’s Cultural Canvas</h1>
            <p>Discover the vibrant art villages and timeless cultural traditions that define India’s rich heritage.</p>
        </div>
        """, unsafe_allow_html=True)

    # Info Cards Section with animations
    st.markdown(
        """
        <div class="info-cards">
            <div class="info-card fade-in delay-2">
                <div class="info-icon">🎨</div>
                <h3>Explore Traditional Art</h3>
                <p>Dive deep into centuries-old art forms and crafts from every corner of India.</p>
            </div>
            <div class="info-card fade-in delay-3">
                <div class="info-icon">🗺️</div>
                <h3>Interactive Cultural Map</h3>
                <p>Find and visit unique art villages with our easy-to-use interactive map.</p>
            </div>
            <div class="info-card fade-in delay-4">
                <div class="info-icon">🤝</div>
                <h3>Support Local Artisans</h3>
                <p>Connect with artisans and help preserve India's living cultural heritage.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
# After Info Cards Section (still in tabs[0])
total_villages = len(villages_df)
total_states = len(villages_df['STATE'].unique())
total_art_forms = len(villages_df['ART_FORM'].unique())

st.markdown("""
<div style="margin-top: 3rem; display: flex; justify-content: center; gap: 2.5rem;">
    <div style="text-align: center;">
        <h2 style="color: #ff6f61;">{}</h2>
        <p>Total Art Villages</p>
    </div>
    <div style="text-align: center;">
        <h2 style="color: #6a1b9a;">{}</h2>
        <p>Unique Art Forms</p>
    </div>
    <div style="text-align: center;">
        <h2 style="color: #00897b;">{}</h2>
        <p>States Represented</p>
    </div>
</div>
""".format(total_villages, total_art_forms, total_states), unsafe_allow_html=True)


st.markdown(
    """
    <div class="video-container fade-in delay-4" style="overflow: hidden; border-radius: 15px; max-width: 100%; max-height: 405px;">
        <iframe 
            width="100%" 
            height="405" 
            src="https://www.youtube.com/embed/rTDaZoDDW5g" 
            title="India's Art and Culture" 
            frameborder="0" 
            allowfullscreen
            style="border-radius: 15px; display: block;"
        ></iframe>
    </div>
    """, 
    unsafe_allow_html=True
)




st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

.image-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
    margin-top: 2rem;
    padding: 10px 20px;
    font-family: 'Merriweather', serif;
}
.image-gallery img {
    width: 100%;
    height: 220px;
    object-fit: cover;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: transform 0.3s ease;
}
.image-gallery img:hover {
    transform: scale(1.05);
}
.gallery-title {
    font-family: 'Merriweather', serif;
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-top: 3rem;
    margin-bottom: 1rem;
    color: #2c3e50;
    letter-spacing: 1.2px;
}
</style>

<h2 class="gallery-title">Gallery</h2>
<div class="image-gallery">
    <img src="https://images.pexels.com/photos/1007431/pexels-photo-1007431.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2" alt="Art Village 1" />
    <img src="https://images.pexels.com/photos/27028141/pexels-photo-27028141/free-photo-of-exterior-of-the-chhatrapati-shivaji-maharaj-terminus-station.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2" alt="Art Village 2" />
    <img src="https://images.pexels.com/photos/12414078/pexels-photo-12414078.jpeg?auto=compress&cs=tinysrgb&w=600" alt="Art Village 3" />
    <img src="https://images.pexels.com/photos/11474965/pexels-photo-11474965.jpeg?auto=compress&cs=tinysrgb&w=600" alt="Art Village 4" />
</div>
""", unsafe_allow_html=True)

# Minimal Footer
st.markdown("""
<hr style="margin-top: 4rem;">
<div style="text-align: center; color: gray; font-size: 0.9rem;">
    Made with ❤️ for the Snowflake Hackathon 2025 · © Mohit Soni
</div>
""", unsafe_allow_html=True)



# ------------------- CULTURAL MAP -------------------
with tabs[1]:
    st.subheader(f"🗺️ Village Map - {selected_state}")

    # Initialize the map, set initial zoom, and center at a general India location
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='OpenStreetMap')

    # Marker Cluster for better handling of multiple points
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for each village with tooltips
    for idx, row in filtered_df.iterrows():
        lat = row['LATITUDE']
        lon = row['LONGITUDE']
        village_name = row['VILLAGE_NAME']
        art_form = row['ART_FORM']

        if pd.notnull(lat) and pd.notnull(lon):
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>{village_name}</b><br>Art Form: {art_form}",
                tooltip=f"{village_name} - {art_form}",  # Tooltip text
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

    # Display the map in Streamlit using folium_static
    folium_static(m, width=700)  # Fix map size by specifying width

# ------------------- EVENTS CALENDAR -------------------
with tabs[2]:
    # Sample events data (this can come from Snowflake or any dynamic source)
    events = [
        {"title": "Pattachitra Festival", "start": "2025-12-10", "end": "2025-12-12", "location": "Odisha"},
        {"title": "Madhubani Art Mela", "start": "2025-10-05", "end": "2025-10-07", "location": "Bihar"},
        {"title": "Kalamkari Crafts Week", "start": "2025-01-20", "end": "2025-01-25", "location": "Telangana"},
        {"title": "Blue Pottery Fair", "start": "2025-03-10", "end": "2025-03-12", "location": "Rajasthan"}
    ]

    # Convert events to DataFrame for easier manipulation
    df_events = pd.DataFrame(events)

    # Convert the 'start' and 'end' columns to datetime
    df_events['start'] = pd.to_datetime(df_events['start']).dt.date
    df_events['end'] = pd.to_datetime(df_events['end']).dt.date

    # Title and Description
    st.title("India’s Cultural Canvas 🎨")
    st.markdown("### 🎭 Cultural Events Calendar")

    # Date selection input
    selected_date = st.date_input("Select a Date", min_value=pd.to_datetime("2025-01-01").date())

    # Filter events based on the selected date
    filtered_events = df_events[(df_events['start'] <= selected_date) & (df_events['end'] >= selected_date)]

    # Display events if any are found
    if not filtered_events.empty:
        st.markdown("#### Events on " + selected_date.strftime('%Y-%m-%d') + ":")
        for idx, event in filtered_events.iterrows():
            st.markdown(f"""
            - **{event['title']}** in {event['location']} 
              (from {event['start']} to {event['end']})
            - **Description**: Experience the vibrancy of traditional art forms.
            - [More Info](https://www.google.com/search?q={event['title']})
            """)
    else:
        st.write("No events on this day.")

# ------------------- ANALYTICS -------------------
with tabs[3]:
    st.markdown("## 📊 Cultural Insights Dashboard")
    st.markdown("Visualize trends and patterns from over 1000+ art villages across India.")

    tab1, tab2 = st.tabs(["🎨 Top Art Forms", "📍 Top States"])

    with tab1:
        st.markdown("#### Top 20 Art Forms by Village Count")

        top_arts = villages_df['ART_FORM'].value_counts().reset_index()
        top_arts.columns = ['Art Form', 'Count']

        art_chart = alt.Chart(top_arts.head(20)).mark_bar(size=15).encode(
            x=alt.X('Count:Q', title='Number of Villages'),
            y=alt.Y('Art Form:N', sort='-x', title=''),
            tooltip=['Art Form', 'Count'],
            color=alt.Color('Art Form:N', legend=None)
        ).properties(
            height=500,
            width=700,
            title='🎨 Most Practiced Art Forms'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16,
            anchor='start',
            color='gray'
        )

        st.altair_chart(art_chart, use_container_width=True)

    with tab2:
        st.markdown("#### Top 20 States by Number of Art Villages")

        top_states = villages_df['STATE'].value_counts().reset_index()
        top_states.columns = ['State', 'Count']

        state_chart = alt.Chart(top_states.head(20)).mark_bar(size=15).encode(
            x=alt.X('Count:Q', title='Number of Villages'),
            y=alt.Y('State:N', sort='-x', title=''),
            tooltip=['State', 'Count'],
            color=alt.Color('State:N', legend=None)
        ).properties(
            height=500,
            width=700,
            title='📍 States with Highest Concentration of Art Villages'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16,
            anchor='start',
            color='gray'
        )

        st.altair_chart(state_chart, use_container_width=True)

# ------------------- STORIES -------------------
with tabs[4]:
    st.markdown("## 📝 Visitor Stories & Cultural Narratives")

    # SQLite connection for storing visitor stories (persistent)
    conn = sqlite3.connect('visitor_stories.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, story TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')

    # Story submission form
    with st.form("story_form", clear_on_submit=True):
        name = st.text_input("Your Name")
        story = st.text_area("Your Story or Experience")
        submitted = st.form_submit_button("Submit Story")

        if submitted:
            if name.strip() == "" or story.strip() == "":
                st.warning("Please fill both name and story fields.")
            else:
                c.execute('INSERT INTO stories (name, story) VALUES (?, ?)', (name, story))
                conn.commit()
                st.success("Thank you for sharing your story!")

    # Display stories
    c.execute('SELECT name, story, date FROM stories ORDER BY date DESC LIMIT 10')
    stories = c.fetchall()

    if stories:
        for s in stories:
            st.markdown(f"**{s[0]}** ({s[2]}):")
            st.write(s[1])
            st.markdown("---")
    else:
        st.info("No stories yet. Be the first to share your experience!")

    conn.close()

# ------------------- ARTISAN MARKETPLACE -------------------
with tabs[5]:
    st.markdown("## 🛒 Artisan Marketplace - Support Local Crafts")

    # Load artisan marketplace data from CSV or any data source
    # For demo, creating dummy data
    artisans = [
        {"Name": "Ramesh Kumar", "Craft": "Madhubani Painting", "State": "Bihar", "Contact": "ramesh@example.com", "Price Range": "₹500-2000"},
        {"Name": "Meera Devi", "Craft": "Pattachitra", "State": "Odisha", "Contact": "meera@example.com", "Price Range": "₹1000-3500"},
        {"Name": "Anil Singh", "Craft": "Blue Pottery", "State": "Rajasthan", "Contact": "anil@example.com", "Price Range": "₹800-3000"},
        {"Name": "Sunita Patel", "Craft": "Kalamkari", "State": "Telangana", "Contact": "sunita@example.com", "Price Range": "₹600-2500"},
    ]

    artisans_df = pd.DataFrame(artisans)
    gb = GridOptionsBuilder.from_dataframe(artisans_df)
    gb.configure_pagination(enabled=True, paginationPageSize=5)
    gb.configure_default_column(editable=False, groupable=True)
    grid_options = gb.build()

    st.markdown("Browse local artisans and support traditional crafts by contacting them directly.")

    AgGrid(artisans_df, gridOptions=grid_options, height=300, theme='fresh')

    st.markdown("If you are an artisan or know local artists, submit your details to be featured here!")

    # Artisan submission form (dummy implementation) 
    with st.form("artisan_form", clear_on_submit=True):
        artisan_name = st.text_input("Artisan Name")
        craft = st.text_input("Craft")
        state = st.selectbox("State", states)
        contact = st.text_input("Contact Email")
        price_range = st.text_input("Price Range")
        submit_artisan = st.form_submit_button("Submit")

        if submit_artisan:
            if artisan_name and craft and state and contact and price_range:
                st.success(f"Thank you {artisan_name} for submitting your craft details! We will review and add it soon.")
            else:
                st.warning("Please fill all the fields to submit your artisan details.")
