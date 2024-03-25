import streamlit as st
import pandas as pd
from io import StringIO
import pymysql
from PIL import Image
import tempfile
from fashion_clip.fashion_clip import FashionCLIP
import json
import os

# background css
with open('./files/background.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# sidebar
with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

with open("ui/styles.md", "r") as styles_file:
    styles_content = styles_file.read()
st.write(styles_content, unsafe_allow_html=True)
st.sidebar.markdown(sidebar_content)
st.sidebar.markdown(f"### Example Hybrid Search Query")
query = '''SELECT brand_name, image_url, short_description, price, DOT_PRODUCT(image_cutout_embedding, query_embedding) AS similarity_score
        FROM farfetch_listings
        WHERE price <= 1500 AND MATCH(short_description) AGAINST('hat')
        ORDER BY similarity_score DESC
        LIMIT 6;'''
st.sidebar.code(query, language="sql")

gradient_text_html = """
<style>
.gradient-text {
    font-weight: bold;
    background: -webkit-linear-gradient(left, orange, purple);
    background: linear-gradient(to right, orange, purple);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline;
    font-size: 3em;
}
</style>
<div class="gradient-text">Style Snatcher</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)

st.caption("Your personal wardrobe wizard 🪄")

max_price = st.slider("Set maximum price ($)", min_value=500, max_value=5000, value=2500, step=100)
keyword = st.text_input("Enter keywords (optional):")
uploaded_file = st.file_uploader("Choose an image!", type=['jpg', 'png', 'jpeg', 'webp'])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='I want to snatch this style ☝️', use_column_width=False, width=250)
num_results = st.selectbox("Number of results:", options=[3, 6], index=0)  # Default to 3

submit_button = st.button('Find Matches')

def generate_embedding(image_path):
    fclip = FashionCLIP('fashion-clip')
    embeddings = fclip.encode_images([image_path], batch_size=1)
    embedding = embeddings[0]
    embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
    return embedding_list


# Function to find top matches
def find_top_matches(connection, embedding, embedding_type, max_price, keyword=None, num_results=3):
    query_embedding_str = ','.join([str(num) for num in embedding])

    # Prepare the SQL command to set the vector query
    set_vector_query = f"SET @query_vec = '[{query_embedding_str}]' :> VECTOR(512);"

    cursor = connection.cursor()

    cursor.execute(set_vector_query)

    if keyword:
        query = f"""
        SELECT brand_name, image_cutout_url, short_description, price, DOT_PRODUCT({embedding_type}_embedding, %s) AS similarity_score
        FROM farfetch_listings
        WHERE price <= %s AND MATCH(short_description) AGAINST(%s)
        ORDER BY similarity_score DESC
        LIMIT {num_results};
        """
        cursor.execute(query, (json.dumps(embedding), max_price, keyword))
    else:
        query = f"""
        SELECT brand_name, image_cutout_url, short_description, price, DOT_PRODUCT({embedding_type}_embedding, %s) AS similarity_score
        FROM farfetch_listings
        WHERE price <= %s
        ORDER BY similarity_score DESC
        LIMIT {num_results};
        """
        cursor.execute(query, (json.dumps(embedding), max_price))
    results = cursor.fetchall()
    return results

# Initialize connection
def init_connection():
    return pymysql.connect(**st.secrets["singlestore"])

# Main logic
if submit_button and uploaded_file is not None:
    with st.spinner('Finding similar items...'):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
            fp = tmpfile.name
            tmpfile.write(uploaded_file.getvalue())
    
        # Pass the temporary file path to the embedding function
        embedding = generate_embedding(fp)
        # Clean up the temporary file
        os.remove(fp)

        # Establish connection
        conn = init_connection()
        
        # Find top matches
        matches = find_top_matches(conn, embedding, 'model', max_price, keyword, num_results=num_results)
        
        # Display results
        # Calculate the number of rows needed
        cols_per_row = 3
        num_rows = (len(matches) + cols_per_row - 1) // cols_per_row  # Round up division
        
        # Create rows and columns dynamically
        for row in range(num_rows):
            cols = st.columns(cols_per_row)  # Create a new row of columns
            for i in range(cols_per_row):
                idx = row * cols_per_row + i  # Calculate overall index in matches
                if idx < len(matches):  # Check if the index is within the range of matches
                    match = matches[idx]
                    with cols[i]:
                        st.image(match[1], use_column_width=True)
                        st.markdown(f"{match[2]} By **{match[0]}**")
                        st.markdown(f"${match[3]}")
                        st.markdown(f"*Similarity score: {round(match[4],2)}*")