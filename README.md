# Style Snatcher
A web app that lets you do image search with fashion items and receive recommendations of similar listings from Farfetch.

<img width="450" alt="image" src="https://github.com/ingridxx/fashion-finder/assets/33936049/ed704fec-95ed-4e8e-92c4-f7cf04a139de">

## Setup
### Dataset
[Farfetch Listings](https://www.kaggle.com/datasets/alvations/farfetch-listings?resource=download) from Kaggle.

### Embedding Model
[FashionCLIP](https://github.com/patrickjohncyh/fashion-clip?tab=readme-ov-file) by Patrick John Chia.

### Database
[SingleStore](singlestore.com).

### Deployment
[Streamlit](streamlit.io).

## How to Use
1. Upload a picture containing a fashion item (with or without model)
2. The app will vectorize the image
3. Specify a max price and optional keywords (only products with keywords mentioned in description will be shown)
4. SingleStore will do a dot product between the vectorized query image and the embeddings stored in the db
5. SingleStore will return the top 3 or 6 matches, depending on the specified number
