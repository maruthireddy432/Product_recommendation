import streamlit as st
import pandas as pd
import pickle
from textblob import TextBlob

# Load models and data
with open('recommendation_model.pkl', 'rb') as file:
    model = pickle.load(file)
with open('product_pivot.pkl', 'rb') as file:
    products = pickle.load(file)
with open('cosine_sim.pkl', 'rb') as file:
    cosine = pickle.load(file)
with open('product_indices.pkl', 'rb') as file:
    product_indices = pickle.load(file)

data = pd.read_csv('cleaned_amazon.csv')

# Streamlit Configuration
st.set_page_config(page_title="Find It Fast", page_icon="🛒", layout="wide")

# Add a banner or header
st.markdown("""
<div style="text-align: center; background-color: orange; padding: 10px; border-radius: 10px;">
    <h1 style="color: white;">🛒 Find It Fast: AI-Driven Recommendations</h1>
    <h5>AI-powered product recommendations, sentiment analysis, and search in one place!</h5>
</div>
""", unsafe_allow_html=True)

# Tabs for Navigation
tab1, tab2, tab3 = st.tabs(["Products", "Review Analysis", "Search"])

### TAB 1: Products ###
with tab1:
    st.subheader("🛍️ Product Recommendations")
    st.write("Select a product and the number of recommendations to find similar items.")

    # User Input for Recommendations
    option = st.selectbox(label="Select a Product", options=products.index)
    number = st.slider("Number of Recommendations", min_value=4, max_value=10)

    def recommend_products(product_name, cosine_sim=cosine, num_recommendations=number):
        try:
            idx = product_indices[product_name]
            sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:num_recommendations + 1]
            product_indices_recommended = [i[0] for i in sim_scores]
            return data['product_name'].iloc[product_indices_recommended]
        except KeyError:
            return []   
    if st.button("Get Recommendations"):
        recommendations = recommend_products(option)
        if not recommendations.empty:
            st.markdown("### Recommended Products")
            cols = st.columns(len(recommendations))
            for i, col in enumerate(cols):
                with col:
                    st.image(data.loc[recommendations.index[i], 'img_link'], use_column_width=True)
                    st.write(recommendations.iloc[i][:40])
        else:
            st.warning("No recommendations available for this product.")

### TAB 2: Reviews ###
with tab2:
    st.subheader("📝 Product Reviews")
    product = st.selectbox("Select a Product to View Reviews", options=products.index)
    product_reviews = data[data['product_name'] == product]['review_content']

    if not product_reviews.empty:
        st.write(f"### Reviews for {product[:40]}")
        for review in product_reviews:
            st.write(f"🗣️ {review}")

        # Sentiment Analysis
        if st.button("Analyze Sentiment"):
            sentiments = [TextBlob(review).sentiment.polarity for review in product_reviews]
            sentiment_labels = ["Positive" if p > 0 else "Neutral" if p == 0 else "Negative" for p in sentiments]
            st.success(f"Sentiment Distribution: {sentiment_labels[0]}")

    else:
        st.warning("No reviews available for this product.")

### TAB 3: Search ###
with tab3:
    st.subheader("🔎 Product Search")
    search_query = st.text_input("Search for Products")
    if search_query:
        search_results = data[data['product_name'].str.contains(search_query, case=False, na=False)]
        st.write(search_results[['product_name', 'actual_price','discounted_price', 'rating']])
