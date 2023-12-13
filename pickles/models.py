import pickle as pkl
import pandas as pd
import os


def get_pickle(pickle_path):
    pickle = None
    file_path = os.path.join(os.path.dirname(__file__), pickle_path)
    # rb standards for read binary, and needed for pickles
    with open(file_path, 'rb') as f:
        pickle = pkl.load(f)
    return pickle


cosine_sim = get_pickle('cosine-similarities.pkl')
indices = get_pickle('indicies.pkl')
indices_to_name = get_pickle('indicies-to-name.pkl')


class Models():

    def _get_recommendation_indicies(self, id: int, cosine_sim=cosine_sim, num_recommend=10):

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[id]))
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Get the scores of the 10 most similar movies
        top_similar = sim_scores[1:num_recommend+1]
        # Get the recipe indices
        recipe_indicies = [i[0] for i in top_similar]
        # Return the top 10 most similar movies
        return recipe_indicies

    def get_recommendations_by_title(self, title: str):

        if title not in indices:
            return [f"{title} not found"]

        id = indices[title]
        recipe_indicies = self.get_recommendations_by_id(id)

        recommendations = []
        for i in recipe_indicies:
            recommendations.append(indices_to_name[i])
        return recommendations

    def get_recommendations_by_id(self, id: int):
        return self._get_recommendation_indicies(id)
