from flask import Flask, render_template, request
from movie_recommendation_engine import get_title_from_index, get_similar_movies

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None

    if request.method == "POST":
        # get data from form
        name = request.form.get("mName", "").strip()
        print(f"Movie Name: {name}")

        if not name:
            error = "Please enter a movie name."
        else:
            try:
                similar_movies = get_similar_movies(name)  # updated function name
                recommended_movies = []

                for index, score in similar_movies[:5]:  # top 5
                    recommended_movies.append(get_title_from_index(index))

                result = recommended_movies

            except ValueError as e:
                # movie not found in dataset
                error = str(e)

    # result: list of titles | error: error message (if any)
    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)
