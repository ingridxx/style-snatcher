# Style Snatcher
Style Snatcher is a web app that lets you do image search with fashion items and receive recommendations of similar listings from [Farfetch](farfetch.com).
### Dataset
[Farfetch Listings](https://www.kaggle.com/datasets/alvations/farfetch-listings?resource=download)  from Kaggle.

### Embedding Model
[FashionCLIP](https://github.com/patrickjohncyh/fashion-clip?tab=readme-ov-file)  by Patrick John Chia.

### Database
[SingleStore](singlestore.com) 🚀.

## How to Use
1. Upload a picture containing a fashion item (with or without model)
2. The app will vectorize the image
3. Specify a max price and optional keywords (only products with keywords mentioned in description will be shown)
4. SingleStore will do a dot product between the vectorized query image and the embeddings stored in the db
5. SingleStore will return the top 3 matches (hover over the images to see the similarity score)

*Note: this dataset contains women fashion only, sorry gentlemen! :)*