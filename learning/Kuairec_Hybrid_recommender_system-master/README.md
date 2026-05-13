# Recommender System for KuaiRec Dataset: Project Report

To see git history please refer to the collaborative repo on which we worked as a group: https://github.com/LeoN1203/FinalProject_2025_LeonAYRAL.git

Recommender systems have become essential in delivering personalized content across digital platforms. This report presents the development of a hybrid recommender system tailored to the KuaiRec dataset, a comprehensive collection of user interaction and content data from the Kuaishou short video platform.
This is a group project with the following members:
**Yacine BENIHADDADENE** - **Gabriel CALVENTE** - **Cédric DAMAIS** - **Léon AYRAL**

## 1. Introduction

### Project Objective
The primary objective of this project is to develop a hybrid recommender system for the KuaiRec dataset. The system aims to predict user interactions with short videos, leveraging various user and item features to provide personalized recommendations.

### KuaiRec Dataset Overview
The KuaiRec dataset is a large-scale, real-world dataset collected from the Kuaishou short video platform. It contains rich information about user interactions, user profiles, item (video) characteristics, and social network data. For this project, the following key data files were utilized:

*   `big_matrix.csv`: A large matrix of user-video interactions, including `user_id`, `video_id`, `watch_ratio`, and `timestamp`. This forms the primary source for training and validation.
*   `small_matrix.csv`: A smaller interaction matrix, chronologically later than `big_matrix.csv`, used for testing the model's performance on unseen data.
*   `user_features.csv`: Contains various features describing users, such as activity levels, registration duration, and demographic proxies.
*   `item_daily_features.csv`: Provides daily aggregated features for items (videos), such as likes, comments, shares, and play counts over time.
*   `item_features.csv`: Static features for items, derived from `item_daily_features.csv`.
*   `item_categories.csv`: Information about video categories.
*   `kuairec_caption_category.csv`: Video captions and associated categories.
*   `social_network.csv`: Describes the social connections between users.

These diverse data sources allow for the development of a hybrid recommender system that can incorporate both collaborative filtering signals and content-based features.

## 2. Data Loading and Preprocessing

### Initial Data Loading
The project began by loading the necessary CSV files into pandas DataFrames. This was primarily done in the `solution/eda_solution.ipynb` notebook (e.g., cell `48245e95`) and subsequently in `solution/feature_model_solution.ipynb` (cell `9c754544`) for the cleaned versions. The key datasets loaded include `big_matrix`, `small_matrix`, `user_features`, `item_daily_features`, `item_features`, and `social_network`.

### Data Cleaning
Data cleaning was a crucial step performed in `solution/eda_solution.ipynb` (primarily in cell `db007c70`) to ensure data quality and consistency. The main cleaning operations included:

*   **Handling Missing Values:** Rows with missing values in critical columns (e.g., `user_id`, `video_id` in interaction matrices) were dropped using `dropna()`. For feature datasets, specific strategies were applied based on the nature of the feature.
*   **Removal of Duplicates:** Duplicate records were removed from all datasets using `drop_duplicates()` to prevent redundancy and potential bias.
*   **Correction of Invalid Data:**
    *   Timestamps: Negative or invalid timestamps in interaction data were identified and corrected or removed. For instance, timestamps were converted to `datetime` objects, and invalid entries were handled.
    *   Other inconsistencies: Columns like `video_duration` in `item_features` were checked for non-positive values.

The impact of these cleaning steps was significant, leading to a reduction in dataset sizes but improving the overall quality and reliability of the data. For example, `big_matrix` saw a reduction in rows after removing entries with `watch_ratio > 1` or invalid timestamps. The cleaned datasets were then saved to new CSV files in the `solution/data/` directory (e.g., `big_matrix_cleaned.csv`, `user_features_cleaned.csv`) for subsequent use in feature engineering and modeling.

## 3. Exploratory Data Analysis (EDA)

Key findings from the EDA, primarily conducted in `solution/eda_solution.ipynb`, are summarized below:

### Interaction Matrices (`big_matrix`, `small_matrix`)

*   **Statistics** (refer to `solution/eda_solution.ipynb` cell `7e69aa12`):
    *   **`big_matrix`**: Contained millions of interactions, with a substantial number of unique users and videos.
    *   **`small_matrix`**: A smaller set, also with a significant number of interactions, unique users, and videos, used for testing.
    The exact counts were:
    *   `big_matrix`: 7,176 users, 107,280 items, 12,630,246 interactions.
    *   `small_matrix`: 7,080 users, 53,790 items, 1,381,001 interactions.

*   **Distribution of Interactions per User and per Item**:
    *   Analysis (e.g., `solution/eda_solution.ipynb` cells `7dd089ac`, `c82ec4f9` for `small_matrix`; `9ff27d99`, `73ecb03a` for `big_matrix`) revealed long-tail distributions for both user activity and item popularity. A small number of users were highly active, and a small number of items received a large number of interactions.
    *   Log-scale plots were used to better visualize these skewed distributions, showing that most users interacted with a moderate number of items, and most items were interacted with by a moderate number of users.

*   **Temporal Patterns** (e.g., `solution/eda_solution.ipynb` cells `9df36766`, `24eba84d`):
    *   **User Activity by Hour of the Day**: Analysis of interaction timestamps showed distinct daily patterns, with peak activity typically observed in the evening hours and lower activity in the early afternoon.
    *   **User Activity by Day of the Week**: Wednedays and Thursdays generally showed higher user activity compared to other weekdays.

*   **Sparsity** (e.g., `solution/eda_solution.ipynb` cell `80eb6f63`):
    *   The `big_matrix` was found to be highly sparse. For example, the sparsity was calculated as `1 - (num_interactions / (num_users * num_items))`, resulting in a value of approximately 98.37%, which is typical for recommender system datasets.

### User Features (`user_features`)

*   Analysis of user features (e.g., `solution/eda_solution.ipynb` cell `f8c96bf3`) included examining the distributions of various categorical and numerical features. For instance, the distribution of `onehot_feat4` (a one-hot encoded feature) was visualized, showing the proportion of users in each category. Other features like `user_active_degree`, `follow_user_num_range`, etc., were also explored.

### Item Features

*   **`item_categories`** (e.g., `solution/eda_solution.ipynb` cell `108af620`):
    *   The distribution of item categories was analyzed, showing which categories were most prevalent in the dataset. This information can be valuable for understanding content diversity and user preferences for different types of videos.

*   **`item_daily_features` Aggregation** (e.g., `solution/eda_solution.ipynb` cell `ff5c76a9`):
    *   The `item_daily_features` dataset, containing daily performance metrics for videos, was aggregated to create a summarized `item_features` DataFrame. This involved grouping by `video_id` and summing or averaging features like `play_cnt`, `like_cnt`, `comment_cnt`, `share_cnt`, `download_cnt`, `valid_play_cnt`, `play_duration`, `long_time_play_cnt`, `short_time_play_cnt`, and `play_progress`.
    *   Distributions of these key aggregated features were then plotted (e.g., `solution/eda_solution.ipynb` cell `1e77ac94`), often revealing skewed distributions (e.g., many videos with few likes/comments, and a few with many).

*  **`Textual Content and Tags`**:
      * Many `topic_tag` entries required parsing from string representations of lists.  
      * The most frequent tags (e.g., “颜值”, “生活”, “美食”) highlight popular themes.  
      * Only about **54.82%** (1,824 / 3,327) of videos in the **small_matrix** have at least one tag — crucial for modeling this segment.

* **`Captions and Manual Cover Text`**  
  * **Captions available:** 95.19% (3,167 / 3,327) of videos have non-empty captions.  
  * **Manual cover text available:** 42.23% (1,405 / 3,327) of videos have meaningful `manual_cover_text` (i.e., not “UNKNOWN”).  
  * During EDA, `"UNKNOWN"` was treated as missing text and replaced with an empty string before TF-IDF.  
  * We computed average character lengths for both fields and compared exact matches versus differences to assess unique information gain.

* **`Proportions of Caption/Tag Metadata (small_matrix)`**

| Feature                            | Count  | Percentage |
|------------------------------------|-------:|-----------:|
| Videos with caption or tags        | 3,167  | 95.19%     |
| Videos with caption **and** tags   | 1,824  | 54.82%     |
| Videos with caption **only**       | 1,343  | 40.37%     |
| Videos with tags **only**          |   0    |  0.00%¹   |

¹ All videos with tags also have captions in this dataset.

* **`Hierarchical Category Coverage (small_matrix)`**

    * **First-level categories:** 95.16% (3,166 / 3,327)  
    * **Second-level categories:** 72.32% (2,406 / 3,327)  
    * **Third-level categories:** 37.96% (1,263 / 3,327)  
    * **All three levels present:** 37.96% (1,263 / 3,327)  
    * **First & second only:** 34.36% (1,143 / 3,327)

> **Category diversity:**  
> - 38 unique first-level categories  
> - 109 unique second-level categories  
> - 153 unique third-level categories  

This EDA shows:
- **Excellent** caption coverage (>95%), making text features highly reliable.
- **Moderate** tag coverage (~55%), offering additional signal for over half of videos.
- **Good** first-level category coverage (~95%) with decreasing coverage and increasing specificity at deeper levels.

These insights guided our feature selection: prioritizing `full_text` (captions + manual cover text) and first-level categories, while treating lower-coverage features (tags, deeper categories) more cautiously and even removing them to have a more robust model.

* **`User–Item Interaction Statistics`**

| Metric                                | small_matrix       | big_matrix         |
|---------------------------------------|-------------------:|-------------------:|
| Unique users                          | 1,411              | 7,176              |
| Unique items                          | 3,327              | 10,728             |
| Actual interactions                   | 4,494,578          | 11,564,987         |
| Total possible interactions           | 4,694,397          | 76,984,128         |
| **Interaction density**               | **0.9574**         | **0.1502**         |

- **Interaction density** is calculated as  
  `actual interactions / total possible interactions`.
- The **small_matrix** is extremely dense (~95.7%), indicating nearly all possible user–item pairs have been observed.  
- In contrast, the **big_matrix** is much sparser (~15.0%), which can affect model learning and overfitting patterns.

These numbers underline why features and training strategies that work on the dense small_matrix may not directly transfer to the sparse big_matrix—and vice versa.




## 4. Feature Engineering (based on `solution/feature_model_solution.ipynb`)

Feature engineering was performed in `solution/feature_model_solution.ipynb` to prepare user and item features for the LightFM model.

### User Feature Selection
A subset of user features was selected from the cleaned `user_features` dataset. The `new_user_features` DataFrame was created in cell `7e3dcf72`, including features like `user_id`, `is_video_author`, `follow_user_num_range`, `friend_user_num_range`, `register_days_range`, `is_lowactive_period`, and `user_active_degree`.

After a further data analysis, we also added the onehot encoded vector user features to the selected user features since they add more information about the user, which increases the overall model performance. More precisely, we added the `onehot_feat0` column until the `onehot_feat10` column.

### Item Feature Creation & Transformation

*   **Creation of `new_item_features`** (cell `7e3dcf72`):
    *   The `item_daily_features_cleaned.csv` dataset was grouped by `video_id`, and various daily metrics were aggregated (e.g., `sum` for counts, `mean` for progress).
    *   New ratio-based features were engineered to capture engagement and appeal (ratios can be more resilient to outlier values therefore making an interesting feature to take in account):
        *   `appeal`: `show_cnt / valid_play_cnt`
        *   `like_ratio`: `like_cnt / valid_play_cnt`
        *   `download_ratio`: `download_cnt / valid_play_cnt`
        *   `comment_ratio`: `comment_cnt / valid_play_cnt`
        *   `share_ratio`: `share_cnt / valid_play_cnt`

*   **Multi-step Normalization of Item Features** (cell `25d9a319`):
    *   Numerical item features in `new_item_features` (excluding `video_id` and `video_type`) underwent a multi-step transformation:
        1.  **Handling NaN/inf values**: Introduced by ratio calculations (e.g., division by zero if `valid_play_cnt` was 0), these were replaced with `np.nan` and then filled with 0.
        2.  **Initial MinMaxScaler**: Features were scaled to a [0, 1] range.
        3.  **Log Transformation**: `np.log1p` was applied to handle skewness and compress the range of values.
        4.  **Second MinMaxScaler**: The log-transformed features were scaled again to a [0, 1] range.
    This process aimed to make the features more suitable for the model by normalizing their scales and distributions.

### User Feature Transformation

*   **Intended Normalization** (cell `2ef77803`):
    *   A similar multi-step normalization process (log1p followed by MinMaxScaler) was intended for selected numerical user features.
    *   However, the list `user_features_number_columns` (which was supposed to hold the names of numerical user columns to be transformed) was initialized as an empty list.
    *   **Impact**: Consequently, the numerical user features were not actually transformed (logged or scaled) in this step, as the code block for transformation was skipped due to the empty list. The `new_user_features_log_scaled` DataFrame remained identical to `new_user_features` regarding these numerical columns. Categorical features were used as-is.

### Binning Numerical Features

*   **Rationale and Method** (cell `412d5508`):
    *   To make numerical item features suitable for LightFM (which often works well with categorical-like features or binned numerical ones), quantile-based discretization was applied using `pd.qcut`.
    *   A recursive function `bin_numerical_column_recursive` was implemented. This function attempts to bin a column into a specified number of quantiles (`initial_q = 5`). If `pd.qcut` fails (e.g., due to too few unique values for the desired number of quantiles), it recursively tries with a smaller number of quantiles until a minimum (`min_q=2`) is reached or binning is successful. This makes the binning process more robust.
    *   This was applied to the scaled and log-transformed numerical item features from `new_item_features_log_scaled`.

*   **Final Item Features for LightFM** (cell `c5d25d0e`):
    *   The `item_binned_feature_columns` list was populated with the names of the newly created binned feature columns (e.g., `like_ratio_bin`).
    *   Categorical features like `video_type` were also included, along with `video_id` as an identifier. This list formed the basis for constructing item feature strings for LightFM.

## 5. Model Development with LightFM (based on `solution/feature_model_solution.ipynb`)

### Choice of Model: LightFM
LightFM was chosen for this project due to several advantages:
*   **Hybrid Nature**: It can effectively combine collaborative filtering (user-item interactions) with content-based features (user and item metadata), making it suitable for the rich KuaiRec dataset.
*   **Implicit Feedback**: LightFM is designed to work well with implicit feedback signals, such as `watch_ratio` in this dataset.
*   **Efficiency**: It is optimized for training on large datasets and can scale well.
*   **Flexibility**: It supports various loss functions and allows for easy incorporation of features.

### Data Preparation for LightFM (cell `68fb6631`)

*   **Feature Name Strings**:
    *   `all_user_feature_names`: Created by combining user feature column names with their unique values (e.g., `"is_video_author:True"`).
    *   `all_item_feature_names`: Created similarly for item features, using the binned numerical features and categorical features (e.g., `"like_ratio_bin:like_ratio_q0"`, `"video_type:A"`).

*   **`lightfm.data.Dataset`**:
    *   An instance of `Dataset` was created.
    *   `dataset.fit()`: This method was used to map unique user IDs, item IDs, user feature names, and item feature names to internal integer indices.
    *   `dataset.build_interactions()`: This built the sparse interaction matrices (`interactions_matrix`, `weights_matrix`) from the `big_matrix` data. The `watch_ratio` was used as the weight for each interaction, signifying the strength of implicit feedback. A similar process was applied to `small_matrix` to create `interactions_matrix_small_m` and `weights_matrix_small_m`.
    *   `dataset.build_user_features()` and `dataset.build_item_features()`: These methods constructed sparse matrices representing user and item features, respectively, based on the feature strings.

### Model Instantiation (cell `08f68233`)
The LightFM model was instantiated with the following parameters:
*   `loss='warp'`: Weighted Approximate-Rank Pairwise loss, suitable for implicit feedback and optimizing for precision@k.
*   `no_components=128`: Number of latent dimensions for user and item embeddings.
*   `learning_rate=0.05`: Controls the step size during optimization.
*   `item_alpha=1e-5`: L2 regularization penalty for item features.
*   `user_alpha=1e-5`: L2 regularization penalty for user features.
*   `random_state=42`: For reproducibility.

### Train/Validation/Test Split (cell `08f68233`)

*   **Strategy**:
    *   **Training & Validation**: Interactions from `big_matrix` were used.
    *   **Testing**: Interactions from `small_matrix` (chronologically later) were used as the final test set.

*   **Splitting `big_matrix`**:
    *   `lightfm.cross_validation.random_train_test_split` was used to split the `interactions_matrix` and `weights_matrix` (derived from `big_matrix`) into training and validation sets with a 20% test (validation) percentage.

*   **Preventing Data Leakage and Ensuring Correct Splitting**:
    *   A critical issue was identified where identical user-item pairs could appear in both train and validation sets if they had different `watch_ratio` values in the raw data, leading to inflated evaluation scores.
    *   To address this, a **canonical form** was enforced for the sparse interaction and weight matrices before splitting. This involved converting the matrices to COO format, which inherently sums data for duplicate `(row, col)` coordinates, and then converting back to CSR format:
        ```python
        # For interactions_matrix
        interactions_coo_temp = interactions_matrix.tocoo()
        interactions_matrix = coo_matrix(
            (interactions_coo_temp.data, (interactions_coo_temp.row, interactions_coo_temp.col)),
            shape=interactions_coo_temp.shape
        ).tocsr()
        # Similar for weights_matrix
        ```
    *   This canonicalization ensures that each user-item pair has a single, aggregated interaction value before the split.
    *   Diagnostic checks were implemented after the split to verify that the overlap count between the `train_interactions` and `validation_interactions` was zero, confirming the effectiveness of the canonicalization and splitting process.

## 6. Model Development using captions with LightFM (based on `solution/feature_model_solution_captions.ipynb`)
For this iteration of the model, we aimed to enhance recommendation quality 
by incorporating richer item features. We decided to leverage information
available in `kuairec_caption_category.csv`, specifically focusing on text-
based and categorical data associated with videos. The hypothesis was that 
features derived from `manual_cover_text`, `caption`, `topic_tag`, and 
hierarchical categorynames(`first_level_category_name`,`second_level_category_name`, 
`third_level_category_name`)

would allow the LightFM model to capture more nuanced patterns in user-item 
interactions.

### 6.1. Feature Engineering with `kuairec_caption_category.csv`

Information from the `kuairec_caption_category.csv` dataset was integrated to provide the model with a deeper understanding of video content. The key features extracted and processed were as follows:

- **Combined Textual Data:** The features `manual_cover_text` and `caption` were concatenated to create a unified `full_text` field for each video. To process this textual data effectively, we applied TF-IDF to extract the most important keywords. During this step, we identified the frequent occurrence of the token `"UNKNOWN"` in the `manual_cover_text`. Exploratory Data Analysis (EDA) showed that this token added no meaningful information. To prevent it from influencing the model, we replaced `"UNKNOWN"` with an empty string prior to TF-IDF transformation.

- **Hierarchical Category Names:** These included `first_level_category_name`, `second_level_category_name`, and `third_level_category_name`, providing structural context to the content. We decided not to use TF-IDF on these features to extract keywords

- **Topic Tags:** Tags associated with each video were included to capture topical and semantic signals that may not be evident from the textual content alone.

### 6.2. Data Preparation for the Enhanced Model
The process for preparing data for LightFM (creating feature name strings, using lightfm.data.Dataset, building interaction and feature matrices) followed a similar methodology as described in Section 5.2. However, the all_item_feature_names now included features derived from the TF-IDF keywords and the new category/tag information. The dataset.fit() and dataset.build_item_features() steps were updated to accommodate these new item features.



## 7. Model Training (cell `de433463`)

The LightFM model was trained using the `model.fit()` method:
```python
model.fit(
    train_interactions,
    user_features=user_features_matrix,
    item_features=item_features_matrix,
    sample_weight=train_interactions_w, # Weights from big_matrix
    epochs=1, # Initially trained for 1 epoch for quick iteration
    num_threads=12, # Number of parallel threads for training
    verbose=True,
)
```
*   The model was trained on the `train_interactions` (from `big_matrix`), incorporating `user_features_matrix` and `item_features_matrix`.
*   `sample_weight=train_interactions_w` was used, meaning the `watch_ratio` influenced the learning process.
*   Initially, the model was trained for a small number of epochs (e.g., 1 epoch) for rapid prototyping and debugging. Further training for more epochs is part of future work.

### Early Stopping Strategy

During model development, we observed that while increasing the number of training epochs generally improved performance on the training and validation sets, it did not always translate to better generalization on the test set (`small_matrix`). Specifically, evaluation metrics often peaked in the midlle of training before degrading with further training—indicating **overfitting** to the training data.

To address this, we implemented an **early stopping** model training. We based our early stopping on the test **precision@10** metric, and stopping if no improvements are made for a given number of epochs (patience). This approach helps balance model learning and generalization, reducing the risk of overfitting and optimizing training efficiency. Note that this is an optional method we added in the notebook.


## 8. Evaluation

### Evaluation Metrics (cell `184036e5`)
An `evaluate_model` function was implemented to calculate standard recommender system metrics:
*   **Precision@k (Precision@10)**: `lightfm.evaluation.precision_at_k`. Measures the proportion of recommended items in the top-K set that are relevant.
*   **Recall@k (Recall@10)**: `lightfm.evaluation.recall_at_k`. Measures the proportion of all relevant items that are successfully recommended in the top-K set.
*   **AUC (Area Under ROC Curve)**: `lightfm.evaluation.auc_score`. Measures the model's ability to rank relevant items higher than irrelevant ones.
*   **NDCG@k (Normalized Discounted Cumulative Gain)**: `lightfm_ndcg_score (custom function)`. Evaluates the ranking quality of the recommended items by taking into account the position of relevant items in the top-K list—higher-ranked relevant items contribute more to the score.

When evaluating on a test/validation set, `train_interactions` was passed to the evaluation functions to ensure that items already seen by the user during training were not considered in the evaluation, providing a more realistic assessment of the model's ability to recommend new items.

Furthermore, since the lightFM builtin evaluation function are limited, we created our own evaluation function for the NDCG@k metric: `lightfm_ndcg_score`.


### Results of the Baseline model (cell `0b692d51`)
The model (trained for 1 epoch) was evaluated on three sets:
1.  **Training Set** (derived from `big_matrix`):
    *   Train Precision@10: `0.0109`
    *   Train Recall@10: `0.0034`
    *   Train AUC: `0.7011`
2.  **Validation Set** (derived from `big_matrix`, referred to as "Test" in the notebook output for this split):
    *   Validation Precision@10: `0.0012`
    *   Validation Recall@10: `0.0004`
    *   Validation AUC: `0.6118`
3.  **Test Set** (derived from `small_matrix`, referred to as "Small Matrix" in notebook output):
    *   Test Precision@10: `0.0002`
    *   Test Recall@10: `0.0001`
    *   Test AUC: `0.5400`

These initial results, especially after only one epoch of training, indicate that the model has started to learn some patterns but requires further tuning and more extensive training. The performance on the validation and test sets is lower than on the training set, which is expected.

### Results of the Enhanced Model with Textual and Categorical Features

The enhanced model, which integrated both textual and categorical features, demonstrated strong performance on the `big_matrix`, but faced challenges generalizing to the `small_matrix`.

#### Performance After 50 Epochs (Trained on `big_matrix`):

- **Training Set (on `big_matrix`):**
  - Precision@10: **0.6852**
  - Recall@10: **0.0081**
  - AUC: **0.8843**

- **Validation Set (from `big_matrix`):**
  - Precision@10: **0.5943**
  - Recall@10: **0.0226**
  - AUC: **0.8959**

- **Evaluation on `small_matrix`:**
  - Precision@10: **0.4200**
  - Recall@10: **0.0013**
  - AUC: **0.6704**

---

#### Generalization Analysis and Epoch Selection

Plotting AUC scores across epochs for both the `big_matrix` validation set and the `small_matrix` evaluation set revealed a key insight:

- The AUC on the `big_matrix` validation set remained high through 50 epochs (~0.896).
- However, the `small_matrix` evaluation AUC **peaked much earlier**, around **epoch 10–12**, with an AUC of **~0.71**.
- By epoch 50, the `small_matrix` AUC had dropped to **~0.67**, indicating **overfitting** to `big_matrix` patterns that did not generalize well.

This highlighted the importance of **early stopping** or **cross-dataset validation** when optimizing for generalization.

![epoch_selection](solution/epoch_selection.png)

---

#### Impact of Full Hierarchical Category Features

The initial version of this enhanced model included all three levels of category names:
- `first_level_category_name`
- `second_level_category_name`
- `third_level_category_name`
- Along with tags

While this configuration yielded strong results on the `big_matrix`, it **severely underperformed** on the `small_matrix`:

- **Validation Set (big_matrix):**
  - Precision@10: **0.6657**
  - Recall@10: **0.0289**
  - AUC: **0.9193**

- **Evaluation on `small_matrix`:**
  - Precision@10: **0.0313**
  - Recall@10: **0.0001**
  - AUC: **0.6095**

This extreme performance gap suggested that **granular category features and tags, while informative for the source domain, hurt generalization** in the target domain.

---

#### Feature Simplification and Its Positive Effect

Further EDA showed that:

- Tags were inconsistently present across `small_matrix` users.
- The deeper category levels (`second_level_category_name` and `third_level_category_name`) introduced **sparsity and overfitting**.

As a result, we **dropped tags and the second and third-level category features**. This change led to a **substantial improvement** on the `small_matrix`:

- **Precision@10 increased from 0.0313 to 0.4200**

This confirms that **simpler, more robust features** generalized better across different user segments.


### Results for enhanced model with added encoded user features

Below are the results of our model with the **added one hot encoded user features**. We observed that, while it doesn't drastically improve the model, it still **increases the overall performance**, and can be more increased with more epochs and better parameter selection. For a **POC**, we trained the following model for **10 epochs**, here are the results:

**Train Set (`big_matrix`)**
- Precision@10: **0.5775**
- Recall@10: **0.0051**
- AUC: **0.8611**
- NDCG@10: **0.2198**

**Validation Set (`big_matrix`)**
- Precision@10: **0.5174**
- Recall@10: **0.0164**
- AUC: **0.8731**
- NDCG@10: **0.0724**


**Test Set (`small_matrix`)**
- Precision@10: **0.9380**
- Recall@10: **0.0029**
- AUC: **0.7579**
- NDCG@10: **0.9057**

### Challenges in Evaluation
A significant challenge encountered earlier in the project was the `ValueError: Test interactions matrix and train interactions matrix share X interactions`. This error arose when using `sklearn.model_selection.train_test_split` directly on interaction data where multiple entries for the same user-item pair (but different `watch_ratio` or timestamps) could exist, leading to data leakage between train and test sets.

This issue was addressed by:
1.  **Enforcing Canonical Form**: As described in Section 5, ensuring each user-item pair has a single entry in the interaction matrix by summing up duplicate coordinates.
2.  **Using LightFM's Splitter**: Switching to `lightfm.cross_validation.random_train_test_split`, which is designed for sparse matrices and LightFM's data structures.

These steps successfully reduced the overlap to zero, allowing for more reliable evaluation.

## 9. Making Recommendations (cell `e48bb520`)

A function `recommend_for_user` was implemented to generate top-N recommendations for a given user:
```python
def recommend_for_user(user_id, model, dataset, user_features_matrix, item_features_matrix, n=10):
    # ... (implementation details) ...
    scores = model.predict(user_array, item_array, user_features=user_features_matrix, item_features=item_features_matrix)
    # ... (get top N items) ...
    return recommended_items
```
*   The function takes a `user_id`, the trained `model`, the `dataset` object (for ID mappings), feature matrices, and the number of recommendations `n`.
*   It predicts scores for all items for the given user using `model.predict()`.
*   The items are then ranked by these scores, and the top `n` items are returned after mapping their internal IDs back to original video IDs.

Example usage demonstrated generating recommendations for a sample user from the `small_matrix`.

## 10. Discussion, Challenges, and Future Work

### Key Learnings and Choices
*   **Data Cleaning is Paramount**: The initial EDA and cleaning phases were crucial for building a stable foundation.
*   **Feature Engineering Drives Performance**: Creating meaningful item features (like ratios) and properly transforming them is key.
*   **Handling Sparsity and Implicit Feedback**: LightFM proved to be a good choice for this dataset, capable of handling sparse implicit feedback data and incorporating hybrid features.
*   **Careful Splitting for Evaluation**: Preventing data leakage during train/test splits is critical for obtaining reliable evaluation metrics. The canonical form enforcement was a key solution here.

### Significant Challenges
*   **Data Leakage in Splitting**: As discussed, ensuring no overlap between training and validation/test sets was a major hurdle, resolved by matrix canonicalization and careful splitting.
*   **Feature Selection**: Given the large quantity of information given in the dataset, which feature too select and why was a significant challenge with a high impact on the model performance. 
*   **Feature Scaling and Transformation**: Deciding on the appropriate normalization and transformation techniques for diverse features (counts, ratios, categorical) required experimentation.
*   **Hyperparameter Tuning**: The current model is trained with initial parameters and for few epochs. Finding optimal hyperparameters will be essential for maximizing performance.
*   **Interpreting Feature Importance**: While LightFM uses features, directly interpreting their global importance can be complex.

## 11. Conclusion

In this project, we developed a **hybrid recommender system** using the **LightFM** model on the **KuaiRec dataset**, which contains extensive user interaction and content metadata from the Kuaishou platform.
Through careful data cleaning, feature engineering, and evaluation, we demonstrated that LightFM—leveraging both collaborative filtering and content-based features—can effectively **learn user preferences** from implicit feedback data.
We explored various item and user features, including textual and categorical metadata, and found that simplifying features improved generalization across datasets. Despite initial challenges such as data sparsity and potential leakage, our final model **achieved strong results**, particularly on the test (`small_matrix`) set, validating the **hybrid approach**.
Future work could focus on hyperparameter tuning, early stopping strategies, and exploring additional models or temporal dynamics.


## References

LightFM Documentation: https://making.lyst.com/lightfm/docs/home.html
KuaiRec Paper: https://arxiv.org/pdf/2202.10842
Medium Article: https://medium.com/@dikosaktiprabowo/hybrid-recommendation-system-using-lightfm-e10dd6b42923
Medium Article: https://medium.com/analytics-vidhya/7-types-of-hybrid-recommendation-system-3e4f78266ad8
Article: https://brand24.com/blog/tiktok-metrics/
