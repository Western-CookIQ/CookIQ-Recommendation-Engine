from flask import Flask

from pickles import models

# Set up app
app = Flask(__name__)
model = models.Models()


@app.route("/recommendations/<id>")
def get_recommendations_by_id(id: int):
    try:
        return model.get_recommendations_by_id(int(id))
    except:
        [f"{id} is not an integer"]


@app.route("/recommendationsByTitle/<title>")
def get_recommendations_by_title(title: str):
    return model.get_recommendations_by_title(title)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
