from fashion_clip.fashion_clip import FashionCLIP
import pandas as pd
import numpy as np
import singlestoredb
import json

fclip = FashionCLIP('fashion-clip')

# Connect to SingleStore database
conn_params = {
  'host': 'xxx.svc.singlestore.com', # SingleStore workspace host
  'user': '', # workspace username
  'password': '', # workspace password
  'database': '', # database name
  'port': 3306, 
}
connection = singlestoredb.connect(**conn_params)

# Read first 50k rows
path = '/Users/ingridxu/Downloads/archive (1)/current_farfetch_listings.csv' # Download from Kaggle https://www.kaggle.com/datasets/alvations/farfetch-listings/data
articles = pd.read_csv(
    path,
    nrows=50000
)

# Drop unnecessary columns
columns_to_keep = ['Unnamed: 0', 'brand.name', 'gender', 'images.cutOut', 'images.model', 'priceInfo.finalPrice', 'shortDescription']
articles_filtered = articles[columns_to_keep]

model_images = articles['images.model'].tolist()
cutout_images = articles['images.cutOut'].tolist()
texts = articles['shortDescription'].tolist()

def safe_encode_images(fclip, model_image_url, cutout_image_url):
    try:
        # Attempt to encode both model and cutout images
        model_embedding = fclip.encode_images([model_image_url], batch_size=30)
        cutout_embedding = fclip.encode_images([cutout_image_url], batch_size=30)
        return model_embedding, cutout_embedding
    except Exception as e:
        print(f"Error encoding images: Model URL: {model_image_url}, CutOut URL: {cutout_image_url}. Error: {e}")
        return None, None

# Process and insert each article into the database
for index, row in articles_filtered.iterrows():
    model_image_url, cutout_image_url = row['images.model'], row['images.cutOut']
    model_embedding, cutout_embedding = safe_encode_images(fclip, model_image_url, cutout_image_url)
    
    if model_embedding is not None and cutout_embedding is not None:
        model_embedding_str = '[' + ','.join(map(str, model_embedding.flatten().tolist())) + ']'
        cutout_embedding_str = '[' + ','.join(map(str, cutout_embedding.flatten().tolist())) + ']'
        
        # Insert into table
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO farfetch_listings (brand_name, gender, image_cutout_url, image_model_url, price, short_description, model_embedding, cutout_embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (row['brand.name'], row['gender'], cutout_image_url, model_image_url, row['priceInfo.finalPrice'], row['shortDescription'], model_embedding_str, cutout_embedding_str))
            connection.commit()
            print("inserted!")

connection.close()

