class Models():

    def __init__(self, indices, indices_to_name):
        self.indices = indices
        self.indices_to_name = indices_to_name

    def _get_recommendation_indicies(self, id: int, num_recommend=2):

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = [[137739, 0.32], [31490, 0.2], [112140, 0.12]]
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Get the scores of the 10 most similar movies
        top_similar = sim_scores[1:num_recommend+1]
        # Get the recipe indices
        recipe_indicies = [i[0] for i in top_similar]
        # Return the top 10 most similar movies
        return recipe_indicies

    def get_recommendations_by_title(self, title: str):

        if title not in self.indices:
            return [f"{title} not found"]

        id = self.indices[title]
        recipe_indicies = self.get_recommendations_by_id(id)

        recommendations = []
        for i in recipe_indicies:
            recommendations.append(self.indices_to_name[i])
        return recommendations

    def get_recommendations_by_id(self, id: int):
        return self._get_recommendation_indicies(id)
