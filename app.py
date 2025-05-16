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
from datetime import date
import calendar

# --- Set Page Configuration --- its important guys keep it on top
st.set_page_config(
    page_title="India's Cultural Canvas | Incredible India",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Page Header with Background Image --- (CSS We can work with)
st.markdown(
    """
    <style>
    .header {
        background-image: url('https://images.unsplash.com/photo-1716396635935-b7ba3d91a1cb?q=80&w=2071&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
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

# Big India Canvas Headline with Background Image(BG)
st.markdown('<div class="header"><h1>Explore the Soul of India, One Village at a Time</h1><p>Celebrating the rich heritage of India’s vibrant art villages and cultural destinations.</p></div>', unsafe_allow_html=True)

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

    

    

# Fixed Search Implementation
search_query = st.sidebar.text_input("🔍 Search by Village or Art Form", key="village_search")

# Apply search filter if query exists
if search_query:
    search_query = search_query.strip().lower()
    filtered_df = filtered_df[
        (filtered_df['VILLAGE_NAME'].str.lower().str.contains(search_query)) |
        (filtered_df['ART_FORM'].str.lower().str.contains(search_query))
    ]

#journey planner
st.sidebar.markdown("## 🗺️ Journey Planner")
st.sidebar.markdown("---")

start_date = st.sidebar.date_input("🛫 Start Date", value=date.today())
end_date = st.sidebar.date_input("🛬 End Date", value=date.today())


# Create two columns in sidebar for Apply and Reset buttons
col1, col2 = st.sidebar.columns(2)

apply = col1.button("Apply")
reset = col2.button("Reset")

if reset:
    # Reset dates to today by rerunning with initial values
    st.session_state["start_date"] = date.today()
    st.session_state["end_date"] = date.today()
    # Optionally clear any other state or variables you use for filtering

if apply:
    if start_date > end_date:
        st.error("⚠️ End date must be after start date.")
    else:
        st.markdown("## 🗓️ Your Journey Plan")
        st.markdown(f"From **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}**")

        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user='MOHITSONI09',
            password='Mohitsoni@&1234',
            account='jvqrqhg-mq37542',
            warehouse='COMPUTE_WH',
            database='ART_TOURISM_DB',
            schema='PUBLIC'
        )
        cursor = conn.cursor()

        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date)

        journey_months = list(range(start_date.month, end_date.month + 1))

        # --- 1. Festivals During Your Journey ---
        with st.expander("🎉 Festivals During Your Journey", expanded=False):
            query_festivals = f"""
                SELECT FESTIVAL_ID, TITLE, VILLAGE_NAME, START_DATE, END_DATE, LOCATION, DESCRIPTION
                FROM FESTIVALS_TABLE
                WHERE START_DATE <= '{end_ts.date()}'
                  AND END_DATE >= '{start_ts.date()}'
            """
            cursor.execute(query_festivals)
            fest_data = cursor.fetchall()
            fest_cols = [desc[0] for desc in cursor.description]
            festivals_df = pd.DataFrame(fest_data, columns=fest_cols)

            if festivals_df.empty:
                st.write("No festivals found during your journey dates.")
            else:
                for _, fest in festivals_df.iterrows():
                    st.write(
                        f"**{fest['TITLE']}** at **{fest['VILLAGE_NAME']}** from "
                        f"{fest['START_DATE'].strftime('%b %d, %Y')} to {fest['END_DATE'].strftime('%b %d, %Y')}"
                    )


        # Define month sets for seasons
        summer_months = set(range(3, 10))  # March to September inclusive
        winter_months = set(list(range(10, 13)) + list(range(1, 3)))  # Oct to Feb inclusive

        # Calculate journey months as a set
        if start_date <= end_date:
            journey_months = set(range(start_date.month, end_date.month + 1))
        else:
            journey_months = set(list(range(start_date.month, 13)) + list(range(1, end_date.month + 1)))

        # Determine journey season(s)
        journey_seasons = set()
        if journey_months.intersection(summer_months):
            journey_seasons.add("summer")
        if journey_months.intersection(winter_months):
            journey_seasons.add("winter")

        if not journey_seasons:
            st.warning("Could not detect journey season from selected dates.")
        else:
            seasons_display = ", ".join([s.capitalize() for s in journey_seasons])
            st.markdown(f"### 🗓️ Detected Journey Season(s): **{seasons_display}**")

        # --- Add the missing function here ---
        def is_in_best_time(season_str):
            if not isinstance(season_str, str):
                return False
            s = season_str.strip().lower()
            if s == "all year":
                return True
            return s in journey_seasons

        # Filter villages dataframe from Snowflake
        villages_in_best_time = villages_df[villages_df['BEST_TIME_TO_VISIT'].apply(is_in_best_time)]

        st.markdown("### 📅 Villages in Their Best Time to Visit During Your Journey")

        with st.expander("Show Villages in Best Time to Visit", expanded=True):
            if villages_in_best_time.empty:
                st.write("No villages found matching your journey season or 'All year'.")
            else:
                for _, row in villages_in_best_time.iterrows():
                    st.write(
                        f"**{row['VILLAGE_NAME']}** ({row['STATE']}) — "
                        f"{row['DESCRIPTION'][:150]}{'...' if len(row['DESCRIPTION']) > 150 else ''}"
                    )



        
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
            background-image: url('https://images.pexels.com/photos/2477374/pexels-photo-2477374.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2');
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
# ------------------- EVENTS CALENDAR -------------------
with tabs[2]:
    @st.cache_data
    def load_festival_data():
        conn = snowflake.connector.connect(
            user='MOHITSONI09',
            password='Mohitsoni@&1234',
            account='jvqrqhg-mq37542',
            warehouse='COMPUTE_WH',
            database='ART_TOURISM_DB',
            schema='PUBLIC'
        )
        query = "SELECT TITLE, START_DATE, END_DATE, VILLAGE_NAME, DESCRIPTION FROM FESTIVALS_TABLE"
        cur = conn.cursor()
        cur.execute(query)
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(data, columns=columns)
        conn.close()
        return df

    # Load festival data
    festivals_df = load_festival_data()

    # Convert to calendar events format
    events = []
    for _, row in festivals_df.iterrows():
        events.append({
            "title": row['TITLE'],
            "start": row['START_DATE'].strftime('%Y-%m-%d') if pd.notnull(row['START_DATE']) else None,
            "end": row['END_DATE'].strftime('%Y-%m-%d') if pd.notnull(row['END_DATE']) else None,
            "location": row['VILLAGE_NAME'],
            "description": row['DESCRIPTION'] if pd.notnull(row['DESCRIPTION']) else "Cultural festival"
        })

    # Filter out events with invalid dates
    valid_events = [e for e in events if e['start'] and e['end']]

    # Title and Description
    st.title("India's Cultural Canvas 🎨")
    st.markdown("### 🎭 Festival Calendar (Live from Snowflake)")

    # Date selection input
    selected_date = st.date_input("Select a Date", min_value=pd.to_datetime("2025-01-01").date())

    # Filter events for selected date
    filtered_events = [
        e for e in valid_events 
        if pd.to_datetime(e['start']).date() <= selected_date <= pd.to_datetime(e['end']).date()
    ]

    # Display events
    if filtered_events:
        st.markdown(f"#### Festivals on {selected_date.strftime('%B %d, %Y')}:")
        for event in filtered_events:
            with st.expander(f"🎪 {event['title']} - {event['location']}"):
                st.markdown(f"""
                **📅 Dates:** {event['start']} to {event['end']}  
                **📍 Location:** {event['location']}  
                **📝 Description:** {event['description']}  
                """)
    else:
        st.info("No festivals found on this date")

# ------------------- ANALYTICS -------------------
# Snowflake connection setup — adjust with your credentials
def get_snowflake_connection():
    return snowflake.connector.connect(
        user='MOHITSONI09',
        password='Mohitsoni@&1234',
        account='jvqrqhg-mq37542',
        warehouse='COMPUTE_WH',
        database='ART_TOURISM_DB',
        schema='PUBLIC'
    )

@st.cache_data(ttl=3600)
def load_visitor_data():
    conn = get_snowflake_connection()
    query = """
    SELECT VILLAGE_NAME, MONTH, SUM(VISITOR_COUNT) AS VISITOR_COUNT
    FROM TOURISM_TRENDS
    GROUP BY VILLAGE_NAME, MONTH
    ORDER BY VILLAGE_NAME, MONTH
    """
    cur = conn.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    df = pd.DataFrame(data, columns=['VILLAGE_NAME', 'MONTH', 'VISITOR_COUNT'])
    df['MONTH'] = pd.to_datetime(df['MONTH'])
    return df

with tabs[3]:
    st.markdown("## 📊 Cultural Insights Dashboard")
    st.markdown("Visualize trends and patterns from over 1000+ art villages across India.")

    tab1, tab2, tab3 = st.tabs(["📈 Visitor Trends", "📍 Top States", "🎨 Top Art Forms"])

    with tab3:
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

    with tab1:
        st.markdown("#### 📈 Monthly Visitor Counts with Village-wise Distribution")

        visitor_df = load_visitor_data()
        villages = visitor_df['VILLAGE_NAME'].unique().tolist()
        default_selection = villages[:5]

        selected_villages = st.multiselect(
            "Select Villages",
            options=villages,
            default=default_selection,
            key="visitor_trends_villages"
        )

        filtered_df = visitor_df[visitor_df['VILLAGE_NAME'].isin(selected_villages)]

        if filtered_df.empty:
            st.info("Select at least one village to see visitor trends.")
        else:
            filtered_df = filtered_df.sort_values(['VILLAGE_NAME', 'MONTH'])

            col1, col2 = st.columns([2, 1])

            with col1:
                line_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
                    x=alt.X('MONTH:T', title='Month'),
                    y=alt.Y('VISITOR_COUNT:Q', title='Visitor Count'),
                    color=alt.Color('VILLAGE_NAME:N', legend=alt.Legend(title="Village")),
                    tooltip=['VILLAGE_NAME', alt.Tooltip('MONTH:T', title='Month'), 'VISITOR_COUNT']
                ).properties(
                    width=700,
                    height=400,
                    title="Monthly Visitor Trends by Village"
                ).configure_axis(
                    labelFontSize=12,
                    titleFontSize=14
                ).configure_title(
                    fontSize=18,
                    anchor='start',
                    color='white'
                )
                st.altair_chart(line_chart, use_container_width=True)

            with col2:
                total_visitors = filtered_df.groupby('VILLAGE_NAME')['VISITOR_COUNT'].sum().reset_index()

                pie_chart = alt.Chart(total_visitors).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="VISITOR_COUNT", type="quantitative"),
                    color=alt.Color(field="VILLAGE_NAME", type="nominal", legend=alt.Legend(title="Village")),
                    tooltip=['VILLAGE_NAME', 'VISITOR_COUNT']
                ).properties(
                    width=300,
                    height=300,
                    title="Total Visitors Distribution"
                    
                ).configure_title(
                    fontSize=16,
                    anchor='middle',
                    color='white'
                )
                st.altair_chart(pie_chart)
                   
                # 🌱 Responsible Tourism Insights Section
with tab1:

    # --- Section Header ---
    st.markdown("### 🌱 Responsible Tourism Insights", unsafe_allow_html=True)

    # --- Process Data ---
    total_visitors = visitor_df.groupby('VILLAGE_NAME')['VISITOR_COUNT'].sum().reset_index()
    low_threshold = 1000
    high_threshold = 3000

    low_visitor_villages = total_visitors[total_visitors['VISITOR_COUNT'] < low_threshold]['VILLAGE_NAME'].tolist()
    high_visitor_villages = total_visitors[total_visitors['VISITOR_COUNT'] > high_threshold]['VILLAGE_NAME'].tolist()

    # --- Promote Villages Box ---
    if low_visitor_villages:
        promote_text = ", ".join(low_visitor_villages)
        st.markdown(f"""
            <div style="background-color:#e8f5e9; padding:12px 16px; border-radius:8px; margin: 12px 0;">
                <strong style="color:#2e7d32;">🔹 Promote these villages:</strong>
                <span style="color:#1b5e20;"> {promote_text}</span><br>
                <small style="color:#388e3c;">These villages have low visitor numbers and great potential for sustainable growth.</small>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background-color:#f1f8e9; padding:12px 16px; border-radius:8px; margin: 12px 0;">
                <strong style="color:#558b2f;">✅ No villages currently need promotion based on visitor data.</strong>
            </div>
        """, unsafe_allow_html=True)

    # --- Monitor Villages Box ---
    if high_visitor_villages:
        monitor_text = ", ".join(high_visitor_villages)
        st.markdown(f"""
            <div style="background-color:#fff3e0; padding:12px 16px; border-radius:8px; margin: 12px 0;">
                <strong style="color:#ef6c00;">⚠️ Monitor these villages carefully:</strong>
                <span style="color:#e65100;"> {monitor_text}</span><br>
                <small style="color:#fb8c00;">They have high visitor numbers and might be at risk of over-tourism.</small>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background-color:#e8f5e9; padding:12px 16px; border-radius:8px; margin: 12px 0;">
                <strong style="color:#388e3c;">✅ No villages currently show signs of over-tourism.</strong>
            </div>
        """, unsafe_allow_html=True)

    # --- Footer Text ---
    st.markdown("""
        <div style="font-style: italic; color: #666; margin-top: 8px; font-size: 13.5px;">
            Use these insights to guide responsible tourism strategies and balance visitor distribution for sustainability.
        </div>
    """, unsafe_allow_html=True)


        

        

# ------------------- STORIES TAB (FIXED VERSION) -------------------
with tabs[4]:
    # Connection manager (auto-reconnects if needed)
    class SnowflakeConnection:
        def __init__(self):
            self.conn = None
            self.connect()
        
        def connect(self):
            try:
                self.conn = snowflake.connector.connect(
                    user='MOHITSONI09',
                    password='Mohitsoni@&1234',
                    account='jvqrqhg-mq37542',
                    warehouse='COMPUTE_WH',
                    database='ART_TOURISM_DB',
                    schema='PUBLIC',
                    client_session_keep_alive=True
                )
                return True
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")
                return False
        
        def get_cursor(self):
            try:
                if not self.conn or self.conn.is_closed():
                    self.connect()
                return self.conn.cursor()
            except:
                return None
        
        def close(self):
            if self.conn and not self.conn.is_closed():
                self.conn.close()

    # Initialize connection
    if 'snowflake_conn' not in st.session_state:
        st.session_state.snowflake_conn = SnowflakeConnection()

    # ------------------- STORY SUBMISSION -------------------
    with st.expander("✍️ Share Your Story", expanded=False):
        with st.form("story_form"):
            name = st.text_input("Your Name (Optional)", key="story_name")
            story = st.text_area("Your Experience", height=150, key="story_content")
            
            if st.form_submit_button("Publish", type="primary"):
                if not story.strip():
                    st.warning("Please write your story first")
                else:
                    cursor = st.session_state.snowflake_conn.get_cursor()
                    if cursor:
                        try:
                            cursor.execute(
                                "INSERT INTO visitor_stories (name, story) VALUES (%s, %s)",
                                (name.strip() or "Anonymous", story.strip())
                            )
                            st.session_state.snowflake_conn.conn.commit()
                            st.success("Published successfully!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save: {str(e)}")
                        finally:
                            cursor.close()
                    else:
                        st.error("Database unavailable")

    # ------------------- STORY DISPLAY -------------------
    st.markdown("## 🌟 Recent Stories")
    
    # Fixed story display function
    def display_story(name, story, date):
        # Header section
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**🧑 {name}**")
        with col2:
            st.caption(f"📅 {date.strftime('%b %d, %Y')}")
        
        # Story content
        st.markdown(f"""
        <div style='color: #FFFFFF; line-height: 1.6; margin-bottom: 10px;'>
            {story if len(story) < 250 else story[:250] + '...'}
        </div>
        """, unsafe_allow_html=True)
        
        # Read more expander
        if len(story) > 250:
            with st.expander("Read full story"):
                st.markdown(f"""
                <div style='color: #FFFFFF; line-height: 1.6; padding: 10px;'>
                    {story}
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()

    # Fetch and display stories
    cursor = st.session_state.snowflake_conn.get_cursor()
    if cursor:
        try:
            cursor.execute("""
                SELECT name, story, date 
                FROM visitor_stories 
                ORDER BY date DESC 
                LIMIT 10
            """)
            stories = cursor.fetchall()
            
            if stories:
                for name, story, date in stories:
                    display_story(name, story, date)
            else:
                st.info("No stories yet. Be the first to share!")
        except Exception as e:
            st.error(f"Failed to load stories: {str(e)}")
        finally:
            cursor.close()
    else:
        st.error("Database connection unavailable")

    # Connection cleanup
    if hasattr(st.session_state, 'snowflake_conn'):
        st.session_state.snowflake_conn.close()



# ------------------- ARTISAN MARKETPLACE -------------------
with tabs[5]:
    st.markdown("## 🛒 Artisan Marketplace - Support Local Crafts")

    # --- Snowflake Connection ---
    conn = snowflake.connector.connect(
        user='MOHITSONI09',
        password='Mohitsoni@&1234',
        account='jvqrqhg-mq37542',
        warehouse='COMPUTE_WH',
        database='ART_TOURISM_DB',
        schema='PUBLIC',
    )

    # --- Fetch Artisans from Snowflake ---
    def get_artisans():
        query = "SELECT * FROM ARTISAN_MARKETPLACE"
        return pd.read_sql(query, conn)

    # --- Insert Artisan into Snowflake ---
    def insert_artisan(name, craft, state, contact, price_range):
        cur = conn.cursor()
        insert_query = """
            INSERT INTO ARTISAN_MARKETPLACE (NAME, CRAFT, STATE, CONTACT, PRICE_RANGE)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (name, craft, state, contact, price_range))
        cur.close()

    # --- Load Artisan Data ---
    artisans_df = get_artisans()

    # --- Filter Section ---
    st.markdown("#### 🔍 Filter Artisans")
    col1, col2 = st.columns(2)
    selected_state = col1.selectbox("Select State", ["All"] + sorted(artisans_df["STATE"].unique()))
    selected_craft = col2.selectbox("Select Craft", ["All"] + sorted(artisans_df["CRAFT"].unique()))

    filtered_df = artisans_df.copy()
    if selected_state != "All":
        filtered_df = filtered_df[filtered_df["STATE"] == selected_state]
    if selected_craft != "All":
        filtered_df = filtered_df[filtered_df["CRAFT"] == selected_craft]

    st.markdown("### 🎨 Featured Artisans")

    cols_per_row = 2

    for i in range(0, len(filtered_df), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, idx in enumerate(range(i, min(i + cols_per_row, len(filtered_df)))):
            row = filtered_df.iloc[idx]
            with cols[j]:
                st.markdown(f"""
                <div style="
                    border: 1.5px solid #2e7d32; 
                    border-radius: 12px; 
                    padding: 20px; 
                    margin-bottom: 18px; 
                    background-color: #0f3d2f; 
                    color: #e0e0d8; 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    line-height: 1.5;
                    min-width: 280px;
                    max-width: 480px;
                ">
                    <h3 style="
                        font-size: 22px; 
                        margin-bottom: 10px; 
                        color: #a8d5ba;
                        font-weight: 700;
                    ">
                        {row['NAME']} <span style='font-weight: 500; color: #c6e2d9;'>({row['CRAFT']})</span>
                    </h3>
                    <p style="font-size: 16px; margin: 6px 0;">
                        <strong>State:</strong> {row['STATE']}
                    </p>
                    <p style="font-size: 16px; margin: 6px 0;">
                        <strong>Contact:</strong> <a href='mailto:{row['CONTACT']}' style='color:#a8d5ba; text-decoration:none;'>{row['CONTACT']}</a>
                    </p>
                    <p style="font-size: 16px; margin: 6px 0;">
                        <strong>Price Range:</strong> {row['PRICE_RANGE']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # Fill empty columns if last row has fewer cards (keeps layout aligned)
        remaining_cols = cols_per_row - (len(filtered_df) - i)
        if remaining_cols > 0:
            for k in range(remaining_cols):
                with cols[cols_per_row - 1 - k]:
                    st.markdown("<div style='visibility:hidden; height:200px;'></div>", unsafe_allow_html=True)

    # --- Submission Form ---
    st.markdown("---")
    st.markdown("### 📥 Submit Artisan Details")
    st.markdown("If you are an artisan or know someone, help them get discovered!")

    with st.form("artisan_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        artisan_name = col1.text_input("Artisan Name")
        craft = col2.text_input("Craft")
        state = col1.selectbox("State", states)
        contact = col2.text_input("Contact Email")
        price_range = col1.text_input("Price Range (e.g., ₹500-2000)")

        submit_artisan = st.form_submit_button("Submit")

        if submit_artisan:
            if artisan_name and craft and state and contact and price_range:
                insert_artisan(artisan_name, craft, state, contact, price_range)
                st.success(f"✅ Thank you **{artisan_name}** for submitting your details! You've been added to our list.")
                st.rerun()  # Use this instead of st.rerun() as per Streamlit's API
            else:
                st.warning("⚠️ Please fill all the fields before submitting.")
