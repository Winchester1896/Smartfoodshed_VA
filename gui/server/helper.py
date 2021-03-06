from neo4j import GraphDatabase, basic_auth
import ast
import json
from itertools import combinations
from py2neo import Subgraph

def filterGraph(data, num, sort):
    ## filter nodes 
    nodes = data['results'][0]['data'][0]['graph']['nodes']
    
    #reformat nodes into the dict list 
    reformat_nodes = []
    for node in nodes:
        reformat_nodes.append({
            'id': node['id'],
            'influence_average': node['properties']['influence_average'],
            'influence_sum': node['properties']['influence_sum'],
            'degree': node['properties']['degree'],
            'influence_adj': node['properties']['influence_adj'],
            'betweenness': node['properties']['betweenness'],
            'pagerank': node['properties']['pagerank'],
            'name': node['properties']['name'],
            'community': node['properties']['community']
        })
    new_nodes = sorted(reformat_nodes, key = lambda i: i[sort],reverse=True)[0:num]

    edges = data['results'][0]['data'][0]['graph']['relationships']
    valid_node_ids = [ele['id'] for ele in new_nodes]
    new_edges = []

    for e in edges:
        if e['startNode'] in valid_node_ids and e['endNode'] in valid_node_ids:
            new_edges.append(e)
    
    backformat = []
    for node in new_nodes:
        backformat.append({
            'type':'node',
            'id': node['id'],
            'labels': ['ENTITY'],
            'properties':{
                'influence_average': node['influence_average'],
                'influence_sum': node['influence_sum'],
                'degree': node['degree'],
                'name': node['name'],
                'influence_adj': node['influence_adj'],
                'betweenness': node['betweenness'],
                'id': node['name'],
                'pagerank': node['pagerank'],
                'community': node['community']
            }
        })
   
    output = {
        "results": [{
            "columns":[],
            "data":[{
                "graph":{
                    "nodes": backformat,
                    "relationships":new_edges
                }
            }]
        }],
        "errors":[]
    }
    return output

# Input: a graph object from py2neo,
#           entity_type is a string,
#           limit_number denotes the maximum number of entity instance you want to get
#Output: entity_list, a list of dictionary, includes the table_data
#         table_info, a list of dictionary, includes the table info
def entity_table(graph, entity_type, limit_number=None):
    if not limit_number:
        all_entities = graph.nodes.match(entity_type).all()
    else:
        all_entities = graph.nodes.match(entity_type).limit(limit_number)
    entity_list = []
    # get the table info
    keys = list(all_entities[0].keys())
    values = list(all_entities[0].values())
    table_info = []
    for index, i in enumerate(keys):
        info_dict = {"label": i, "value": i, "type": str(type(values[index]).__name__)}
        table_info.append(info_dict)

    # start to construct the entity list
    for entity in all_entities:
        entity_dict = dict(entity)
        entity_dict.update({"id": entity.identity})
        entity_list.append(entity_dict)
    return entity_list, table_info

# Input:    graph, a graph object from py2neo,
#           relation_type is a string, denotes the relationship type which you want to generate a table
#           entity_identifier, a string, denotes the property name which you want to display in the front end (same as the mapping property)
#           entity_identifier, a string, denotes the property name which you want to display in the front end (same as the mapping property)
#           limit_number, denotes the maximum number of relationship instance you want to get
#Output: relation_list, a list of dictionary, includes the table_data
#         table_info, a list of dictionary, includes the table info
def relation_table(graph, relation_type, entity_identifier, limit_number=None):
    if not limit_number:
        all_relation = graph.relationships.match(r_type=relation_type).all()
    else:
        all_relation = graph.relationships.match(r_type=relation_type).limit(limit_number).all()
    relation_list = []

    # get table info
    keys = list(all_relation[0].keys())
    values = list(all_relation[0].values())
    table_info = []
    for index, i in enumerate(keys):
        info_dict = {"label": i, "value": i, "type": str(type(values[index]).__name__)}
        table_info.append(info_dict)
    # add the starting node and ending node column
    start_node_name = list(all_relation[0].start_node.labels)[0] + "_start"
    end_node_name = list(all_relation[0].end_node.labels)[0] + "_start"
    table_info.append({"label": start_node_name, "value": start_node_name, "type": "str"})
    table_info.append({"label": end_node_name, "value": end_node_name, "type": "str"})

    # start to construct the relation list
    for relation in all_relation:
        start_entity_type = list(relation.start_node.labels)[0] + "_start"
        end_entity_type = list(relation.end_node.labels)[0] + "_end"
        relation_id = relation.identity
        start_id = relation.start_node.identity
        end_id = relation.end_node.identity
        start_node = relation.start_node[entity_identifier]
        end_node = relation.end_node[entity_identifier]
        r_dict = {start_entity_type: start_node, end_entity_type: end_node, "relation_id": relation_id,
                  "start_id": start_id, "end_id": end_id}
        r_dict.update(dict(relation))
        relation_list.append(r_dict)
    return relation_list, table_info

#Input: graph, a graph object from py2neo
#       entity_type_list, a list of entity_type
#       out_file, the path for the out put file
#       limit_number, a number indicating the maximum number of instance we want to put in the table
def write_entities_to_json(graph,entity_type_list,out_file,limit_number=None):
    entity_table_list = []
    for entity in entity_type_list:
        table_data,table_info = entity_table(graph,entity,limit_number)
        entity_dic = {"table_name":entity,"table_data":table_data,"table_info":table_info}
        entity_table_list.append(entity_dic)
    with open(out_file, 'w') as outfile:
        json.dump(entity_table_list, outfile)

#Input: graph, a graph object from py2neo
#       relation_type_list, a list of relationship_type
#       out_file, the path for the out put file
#       entity_identifier, a string, denotes the property name which you want to display in the front end (same as the mapping property)
#       limit_number, a number indicating the maximum number of instance we want to put in the table
def write_relations_to_json(graph,relation_type_list,out_file,entity_identifier,limit_number=None):
    relation_table_list = []
    for relation in relation_type_list:
        table_data,table_info = relation_table(graph,relation,entity_identifier,limit_number)
        relation_dic = {"table_name":relation,"table_data":table_data,"table_info":table_info}
        relation_table_list.append(relation_dic)
    with open(out_file, 'w') as outfile:
        json.dump(relation_table_list, outfile)

#Input: graph, a graph object from py2neo
#       node_id_list, a list of int, each element is an id for a node
#       relation_id_list, a list of int, each element is an id for a relationship
#Ouput: a sugraph object in py2neo
def get_subgraph(graph,node_id_list,relation_id_list):
    node_list = [graph.nodes.get(i) for i in node_id_list]
    all_pairs = [set(comb) for comb in combinations(node_list, 2)]
    subgraph = Subgraph()

    #get all the relationships where the ending node and starting node all belong to the node set and put in the subgraph
    for pair in all_pairs:
        relation = graph.match(pair).first()
        if relation is not None:
            subgraph = subgraph | relation

    #concatenate the subgraph with relationship list
    relation_list = [graph.relationships.get(i) for i in relation_id_list]
    for relation in relation_list:
        subgraph = subgraph | relation
    return subgraph

#Input: subgraph, a subgraph object in py2neo
#       entity_identifier, a string, denotes the property name which you want to display in the front end (same as the mapping property)
#Ouput: a dictionary containing the graph in json format
def convert_subgraph_to_json(subgraph,entity_identifier):
    #construct list of node dicitionary
    node_dict_list = []
    for n in list(subgraph.nodes):
        node_property = dict(n)
        node_property.update({"mapping":entity_identifier})
        node_dict = {"id":n.identity,"labels":[],"properties":node_property,"type":"node"}
        node_dict_list.append(node_dict)

    #construct list of relationship dicitionary
    relation_dict_list = []
    for r in list(subgraph.relationships):
        relation_property = dict(r)
        relation_property.update({"mapping":"relationship_type"})
        relation_property.update({"relationship_type":type(r).__name__})
        relation_dict = {"startNode":r.start_node.identity,"endNode":r.end_node.identity,
                         "id":r.identity,"label":[],"properties":relation_property}
        relation_dict_list.append(relation_dict)

    graph_dict = {"nodes":node_dict_list,"relationships":relation_dict_list}
    data_dict = {"graph":graph_dict}
    dict_result = {"results":[{"columns":[],"data":[data_dict]}]}
    return dict_result

def print_(tx, ):
    record = tx.run("""
        CALL apoc.export.json.all(null,{useTypes:true, stream: true})
        YIELD file, nodes, relationships, properties, data
        RETURN file, nodes, relationships, properties, data
    """)
    return [rr for rr in record]

