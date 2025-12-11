from flask import Flask, render_template, request
from movie_recommendation_engine import get_title_from_index, get_similar_movies, df
import difflib

app = Flask(__name__)

# ---------- Precomputed helper data for UI ----------
# All movie titles (for datalist + suggestions)
ALL_MOVIES = sorted(df["title"].astype(str).tolist())

# All unique genres (for genre dropdown)
all_genres_set = set()
if "genres" in df.columns:
    for g in df["genres"]:
        for part in str(g).split("|"):
            part = part.strip()
            if part:
                all_genres_set.add(part)
ALL_GENRES = sorted(all_genres_set)

TOTAL_MOVIES = len(df)
TOTAL_GENRES = len(ALL_GENRES)


@app.route("/", methods=["GET", "POST"])
def home():
    result = None              # list of recommended movie dicts
    error = None               # error string
    suggestions = []           # "Did you mean" titles
    movie_input = ""           # what user typed
    matched_movie = None       # closest title in dataset
    selected_movie = None      # details of matched movie
    selected_genre = ""        # genre filter
    num_rec = 5                # number of recommendations

    if request.method == "POST":
        movie_input = request.form.get("mName", "").strip()
        selected_genre = request.form.get("genreFilter", "").strip()

        # how many recommendations user selected
        try:
            num_rec = int(request.form.get("numRec", 5))
        except ValueError:
            num_rec = 5

        if not movie_input:
            error = "Please enter a movie name."
        else:
            # All titles from dataset
            all_titles = ALL_MOVIES

            # Fuzzy match user input to dataset title
            close_matches = difflib.get_close_matches(movie_input, all_titles, n=1, cutoff=0.6)

            if not close_matches:
                # No close match mila
                error = f"Movie '{movie_input}' not found in database!"
                suggestions = difflib.get_close_matches(movie_input, all_titles, n=5, cutoff=0.3)
            else:
                matched_movie = close_matches[0]

                try:
                    # Yeh function tumhaare engine me exact title expect karta hai
                    similar_movies = get_similar_movies(matched_movie)

                    # Matched movie ka detail (top row jiska title matched ho)
                    row = df[df["title"] == matched_movie].iloc[0]
                    selected_movie = {
                        "title": row.get("title", ""),
                        "genres": row.get("genres", ""),
                        # overview ho to dikhega, warna blank rahega
                        "overview": row.get("overview", "")
                    }

                    # Now build result list for UI
                    result = []
                    for index, score in similar_movies:
                        row = df.loc[index]

                        # Agar user ne genre select kiya hai to filter:
                        movie_genres = [g.strip() for g in str(row.get("genres", "")).split("|")]
                        if selected_genre and selected_genre not in movie_genres:
                            continue

                        result.append({
                            "title": row.get("title", ""),
                            "genres": row.get("genres", ""),
                            "overview": row.get("overview", ""),
                            "similarity": round(float(score) * 100, 1)
                        })

                        if len(result) >= num_rec:
                            break

                    # Agar genre filter laga aur kuch nahi mila
                    if selected_genre and not result:
                        error = (
                            f"No movies found with genre '{selected_genre}' "
                            f"similar to '{matched_movie}'. Try removing the genre filter."
                        )
                        result = None

                except ValueError as e:
                    # get_similar_movies ne ValueError diya (movie not found etc.)
                    error = str(e)

    return render_template(
        "index.html",
        result=result,
        error=error,
        all_movies=ALL_MOVIES,
        movie_input=movie_input,
        matched_movie=matched_movie,
        num_rec=num_rec,
        all_genres=ALL_GENRES,
        selected_genre=selected_genre,
        selected_movie=selected_movie,
        suggestions=suggestions,
        total_movies=TOTAL_MOVIES,
        total_genres=TOTAL_GENRES,
    )


if __name__ == "__main__":
    app.run(debug=True)
