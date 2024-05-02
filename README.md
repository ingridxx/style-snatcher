# Style Snatcher
A web app that lets you do image search with fashion items and receive recommendations of similar listings from Farfetch. Try it [here](https://style-snatcher.streamlit.app/).

## Setup
### Dataset
[Farfetch Listings](https://www.kaggle.com/datasets/alvations/farfetch-listings?resource=download) from Kaggle.

### Embedding Model
[FashionCLIP](https://github.com/patrickjohncyh/fashion-clip?tab=readme-ov-file) by Patrick John Chia.

### Database
[SingleStore](singlestore.com).

### Deployment
[Streamlit](streamlit.io).

## How to Use (via Streamlit)
1. Upload a picture containing a fashion item (with or without model)
2. The app will vectorize the image
3. Specify a max price and optional keywords (only products with keywords mentioned in description will be shown)
4. SingleStore will do a dot product between the vectorized query image and the embeddings stored in the db
5. SingleStore will return the top 3 or 6 matches, depending on the specified number

## How to Test Locally
1. Clone this repo
2. Run `pip install -r requirements.txt`
3. Create a `secrets.toml` file in the `.streamlit` folder and enter your SingleStore connection details
   
   ```[singlestore]
      host = "svc-xxx.svc.singlestore.com"
      port = 3306 (or 3333 if using shared tier)
      database = "" (your database name)
      user = "" (your workspace group user name)
      password = "" (your workspace group password)
5. Save the project and run `streamlit run streamlit_app.py`, the app should open in a localhost browser.
