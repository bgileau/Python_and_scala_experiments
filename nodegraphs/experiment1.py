import http.client
import json
import csv

import urllib.request
import copy


class Graph:
    def __init__(self, with_nodes_file=None, with_edges_file=None):
        self.nodes = []
        self.edges = []
        if with_nodes_file and with_edges_file:
            nodes_CSV = csv.reader(open(with_nodes_file))
            nodes_CSV = list(nodes_CSV)[1:]
            self.nodes = [(n[0], n[1]) for n in nodes_CSV]

            edges_CSV = csv.reader(open(with_edges_file))
            edges_CSV = list(edges_CSV)[1:]
            self.edges = [(e[0], e[1]) for e in edges_CSV]


    def add_node(self, id: str, name: str) -> None:
        id_name_tuple = (id, name)
        if id_name_tuple not in self.nodes:
            self.nodes.append(id_name_tuple)


    def add_edge(self, source: str, target: str) -> None:
        source_target_tuple = (source, target)
        source_target_tuple_reversed = (target, source)
        if source_target_tuple not in self.edges and source_target_tuple_reversed not in self.edges: # since it's undirected a->b is the same as b->a. Check for both.
            self.edges.append(source_target_tuple)

    def total_nodes(self) -> int:
        return len(self.nodes)


    def total_edges(self) -> int:
        return len(self.edges)



    def max_degree_nodes(self) -> dict:
        # First just get a count for the degree of each node using the edges. Refine later.
        count_dict = {}
        for edges_tuple in self.edges:
            (source_edge_id, target_edge_id) = edges_tuple # unpack the tuple

            if source_edge_id not in count_dict:
                count_dict[source_edge_id] = 1
            else:
                count_dict[source_edge_id] += 1

            if target_edge_id not in count_dict:
                count_dict[target_edge_id] = 1
            else:
                count_dict[target_edge_id] += 1

        # get the highest degree(s)
        sorted_items = sorted(count_dict.items(), key=lambda x: x[1])[::-1]
        highest_degree = max(count_dict.values()) # get overall highest value

        # Finalize the results
        best_items = {}
        for items in sorted_items:
            if items[1] == highest_degree:
                best_items[items[0]] = items[1]
            else:
                break

        return best_items


    def print_nodes(self):
        print(self.nodes)


    def print_edges(self):
        print(self.edges)


    # Do not modify
    def write_edges_file(self, path="edges.csv")->None:
        edges_path = path
        edges_file = open(edges_path, 'w', encoding='utf-8')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")


    # Do not modify
    def write_nodes_file(self, path="nodes.csv")->None:
        nodes_path = path
        nodes_file = open(nodes_path, 'w', encoding='utf-8')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(n[0] + "," + n[1] + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")



class  TMDBAPIUtils:
    def __init__(self, api_key:str):
        self.api_key=api_key


    def get_movie_cast(self, movie_id:str, limit:int=None, exclude_ids:list=None) -> list:
        with urllib.request.urlopen(rf"http://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={self.api_key}&language=en-US") as response:
            response_read = response.read()
            response_dict = json.loads(response_read.decode())

        list_of_cast_members_info = []
        if "cast" in response_dict.keys():
            for cast_dict in response_dict["cast"]:
                # print(cast_dict)
                # print(cast_dict["id"])
                # print(cast_dict["order"], limit)
                if "id" in cast_dict and "order" in cast_dict:
                    # if int(cast_dict["id"]) not in exclude_ids:
                    #     limit_bool_met = True
                    #     if limit is not None:  # if none, then limit doesn't apply and thus we can treat it as having passed
                    #         if int(cast_dict["order"]) >= limit:
                    #             limit_bool_met = False # fail limit check

                    #     if limit_bool_met:
                    #         # print(cast_dict["order"], limit)
                    #         list_of_cast_members_info.append(cast_dict)
                    exclude_ids_check_good = True
                    limit_check_good = True

                    if exclude_ids is not None:
                        if int(cast_dict["id"]) in exclude_ids:
                            exclude_ids_check_good = False

                    if limit is not None:
                        if int(cast_dict["order"]) >= limit:
                            limit_check_good = False

                    if limit_check_good and exclude_ids_check_good:
                        list_of_cast_members_info.append(cast_dict)


                # else: 
                #     print(f"Skipping:",  cast_dict["id"])

        return list_of_cast_members_info


    def get_movie_credits_for_person(self, person_id:str, vote_avg_threshold:float=None)->list:
        with urllib.request.urlopen(rf"http://api.themoviedb.org/3/person/{person_id}/movie_credits?api_key={self.api_key}&language=en-US") as response:
            response_read = response.read()
            response_dict = json.loads(response_read.decode())

        list_of_person_movies_info = []
        for movies_dict in response_dict["cast"]:
            if movies_dict["vote_average"] >= vote_avg_threshold:
                movies_dict2 = {}
                movies_dict2["id"] = movies_dict["id"]
                movies_dict2["title"] = movies_dict["title"]
                movies_dict2["vote_avg"] = movies_dict["vote_average"]

                list_of_person_movies_info.append(movies_dict2)
            # else: 
            #     print(f"Skipping:",  cast_dict["id"])

        return list_of_person_movies_info


if __name__ == "__main__":

    ##################### Initial Debug Testing
    # graph.add_node(id='2975', name='Laurence Fishburne')
    # graph.add_node(id='1', name='test')
    # graph.add_node(id='2', name='test2')
    # graph.add_node(id='2', name='test2')
    # graph.add_node(id='3', name='test3')
    # graph.add_node(id='4', name='test4')
    # graph.add_edge(source='2975', target='1')
    # graph.add_edge(source='1', target='2975')
    # graph.add_edge(source='3', target='1')
    # graph.add_edge(source='2975', target='2')
    # graph.add_edge(source='2975', target='4')

    # print("total nodes ",graph.total_nodes())
    # print("total edges ",graph.total_edges())
    # print("max degree nodes ",graph.max_degree_nodes())


    # tmdb_api_utils = TMDBAPIUtils(api_key='')

    # get_movie_cast_return = tmdb_api_utils.get_movie_cast(movie_id="1359-american-psycho", exclude_ids=[3894], limit=3)
    # print(len(get_movie_cast_return))

    # get_person_credits_return = tmdb_api_utils.get_movie_credits_for_person(person_id="3894", vote_avg_threshold=8.0)
    # print(len(get_person_credits_return))

    ##################### Proper Attempt Testing
    graph = Graph()
    tmdb_api_utils = TMDBAPIUtils(api_key='')

    ############# INITIALIZE GRAPH
    graph.add_node(id='2975', name='Laurence Fishburne')

    ############# BEGIN BUILD BASE GRAPH:
    # First, get the movies which are highly rated to begin to see which good movies have coactors.
    good_movie_credits = tmdb_api_utils.get_movie_credits_for_person(person_id="2975", vote_avg_threshold=8.0)
    #print(good_movie_credits)

    added_nodes_list_base = []
    for movie_credit_dict in good_movie_credits:
        get_movie_cast_return = tmdb_api_utils.get_movie_cast(movie_id=str(movie_credit_dict["id"]), exclude_ids=[2975], limit=3) # 2975
        #print(get_movie_cast_return)

        for movie_cast_member_dict in get_movie_cast_return:
            movie_cast_member_tuple = (str(movie_cast_member_dict["id"]), movie_cast_member_dict["name"].replace(",",""))

            graph.add_node(id=str(movie_cast_member_dict["id"]), name=movie_cast_member_dict["name"].replace(",","")) # remove commas
            added_nodes_list_base.append(movie_cast_member_tuple)

            graph.add_edge(source="2975", target=str(movie_cast_member_dict["id"]))

    ############# END BUILD BASE GRAPH:

    ############# BEGIN LOOP - DO 2 TIMES:
    added_nodes_list_loop1 = []
    for i in range(0, 2):
        if i == 0:
            nodes = copy.deepcopy(added_nodes_list_base)
        else:
            nodes = copy.deepcopy(added_nodes_list_loop1)

        for j, node in enumerate(nodes):
            print(f"idx: {i} | On node: {node} | {j}/{len(nodes)}")
            good_movie_credits = tmdb_api_utils.get_movie_credits_for_person(person_id=node[0], vote_avg_threshold=8.0)

            for movie_credit_dict in good_movie_credits:
                get_movie_cast_return = tmdb_api_utils.get_movie_cast(movie_id=str(movie_credit_dict["id"]), exclude_ids=[int(node[0])], limit=3)  # node[0]

                for movie_cast_member_dict in get_movie_cast_return:
                    movie_cast_member_tuple = (str(movie_cast_member_dict["id"]), movie_cast_member_dict["name"].replace(",",""))

                    # TODO: make this check work well? The auto handling in the add_node won't return a boolean and will break auto-grader
                    if movie_cast_member_tuple not in graph.nodes:
                        graph.add_node(id=str(movie_cast_member_dict["id"]), name=movie_cast_member_dict["name"].replace(",","")) # remove commas
                        added_nodes_list_loop1.append(movie_cast_member_tuple)

                    edge_tuple = (node[0], str(movie_cast_member_dict["id"]))
                    edge_tuple_reverse = (str(movie_cast_member_dict["id"]), node[0])
                    if edge_tuple not in graph.edges and edge_tuple_reverse not in graph.edges:
                        graph.add_edge(source=node[0], target=str(movie_cast_member_dict["id"]))


    ###################### Part C #######################
    graph.write_edges_file()
    graph.write_nodes_file()

    # graph = Graph(with_edges_file="edges.csv", with_nodes_file="nodes.csv")
