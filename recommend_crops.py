from py2neo import Graph
from pprint import pprint
import pyowm
import csv
import requests
from collections import OrderedDict 

def initialise_votes(cypher, vote):
    qry = "MATCH(n:Crop) RETURN n"
    res = cypher.execute(qry)
    for i in range(len(res)):
        crop_name = res[i].n['name']
        vote[crop_name] = 0.0
    print("\nVotes_initialized")

def show_climate_req(cypher):
    qry = "MATCH(n:climateRequirement) RETURN n"
    res = cypher.execute(qry)
    conditions = []
    for i in range(len(res)):
        conditions.append(res[i].n['descrp'])  
    print(conditions)


def show_soil_req(cypher):
    qry = "MATCH(n:soilRequirement) RETURN n"
    res = cypher.execute(qry)
    conditions = []
    for i in range(len(res)):
        conditions.append(res[i].n['descrp'])  
    print(conditions)


# for state, climate and soil based votes
# name : condition name
# type : climate/soil/states
def UpdateVote1(cypher, name, vote_prior, type, vote):
    qry = "MATCH(n2:Crop)-[r:requires]->(n) WHERE n.name={a} and n.descrp={b} RETURN n2"
    res = cypher.execute(qry, a=type, b=name)
    if(type=="CropGrownIn"):
        q = "MATCH(n2:Crop)-[r:requires]->(n) WHERE n.descrp={a} RETURN n2"
        name = "ALL_INDIAN_STATES"
        r = cypher.execute(q, a=name)
        for i in range(len(r)):
            vote[r[i].n2['name']] += vote_prior
    for i in range(len(res)):
        crop_name = res[i].n2['name']
        vote[crop_name] += vote_prior



# for rainfall, temperature
# type : rain/temp
# req : temp in C or rainfall in cm 
def UpdateVote2(cypher, vote_prior, type, vote, req):
    qry = "MATCH(n2:Crop)-[r:requires]->(n) WHERE n.name={a} RETURN n,n2"
    res_min = cypher.execute(qry, a="min"+type)
    res_max = cypher.execute(qry, a="max"+type)
    if(len(res_min) != len(res_max)):
        print("\nSOME ERROR OCCURED!!! >>>>> length mismatched\n")

    else:
        for i in range(len(res_min)):
            min_req = int(res_min[i].n['descrp'])
            max_req = int(res_max[i].n['descrp'])
            if(req>=(min_req-5) and req<=(max_req+5)):
                crop_name = res_min[i].n2['name'] # same as res_max[i].n2['name']
                vote[crop_name] += vote_prior/2
            if(req>=min_req and req<=max_req):
                crop_name = res_min[i].n2['name'] # same as res_max[i].n2['name']
                vote[crop_name] += vote_prior/2


def Main():

    API_key = input('ENTER API KEY ONLY FOR ADMIN : ')

    graph = Graph()
    cypher = graph.cypher

    vote = {} # dict containing votes for each crop e.g. "wheat":3
    state_vote = 3.0
    climate_vote1 = 1.5
    climate_vote2 = 1.0
    soil_vote1 = 1.5
    soil_vote2 = 1.0
    temp_vote = 1.2
    rain_vote = 1.0

    initialise_votes(cypher, vote)

    states_SF = {}
    states_FF = {}

    with open('indian_states.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            states_SF[row[1]] = row[2]
            states_FF[row[2]] = row[1]

    print("states_name : ")
    for k,v in states_SF.items():
        print(k,end=', ')


    print("\n")
    state_name = input('Enter State name : ')
    state_name = states_SF[state_name]
    UpdateVote1(cypher, state_name, state_vote, "CropGrownIn",vote)
    #print("\n")
    district_name = input('Enter your district/city name : ')
    print('\n')
    #print("votes : ", vote)
    #print("\n")

    print("Possible climatic conditions : ")
    show_climate_req(cypher)
    print("\nYou can select two options from the list\n")
    climate_cnd1 = input("Enter climate condition 1 (e.g. input - kharif): ")
    climate_cnd2 = input("Enter climate condition 2 (If you prefer only 1 reenter it) : ")
    print("\n")
    UpdateVote1(cypher, climate_cnd1, climate_vote1, "climateRequirement", vote)
    UpdateVote1(cypher, climate_cnd2, climate_vote2, "climateRequirement", vote)
    #print("votes : ", vote)
    #print("\n")

    print("Possible soil conditions : ")
    show_soil_req(cypher)
    print("\nYou can select two options from the list\n")
    soil_cnd1 = input("Enter soil condition 1 (e.g. input - clay) : ")
    soil_cnd2 = input("Enter soil condition 2 (If you prefer only 1 reenter it) : ")
    print("\n")
    UpdateVote1(cypher, soil_cnd1, soil_vote1, "soilRequirement", vote)
    UpdateVote1(cypher, soil_cnd2, soil_vote2, "soilRequirement", vote)
    #print("votes : ", vote)
    #print("\n")


    temp_ip = '30'
    try:
        url = 'http://api.openweathermap.org/data/2.5/weather?q='+district_name+',IN&APPID='+API_key
        r = requests.get(url)
        a = r.json()
        if(a['cod'] == '404'):
            url = 'http://api.openweathermap.org/data/2.5/weather?q='+states_FF[state_name]+',IN&APPID='+API_key 
            r = requests.get(url)
            a = r.json()
        tp = a['main']
        temp_ip = str(int(tp['temp']) - 273)
    except:
        temp_ip = '28'
    
    if(temp_ip != '28'):
        print("Today's temperature in C : ", temp_ip)
    temp_ip = input("Enter temperature in C (Enter temperature between 5 and 43): ")
    req = int(temp_ip)
    UpdateVote2(cypher, temp_vote, "temperatureRequirement", vote, req)
    #print("\n")
    #print("votes : ", vote)
    #print("\n")


    rain_ip = input("Enter annual rainfall in cm (Enter rainfall between 10 and 305)(e.g input 146): ")
    req = int(rain_ip)
    UpdateVote2(cypher, rain_vote, "rainfallRequirement", vote, req)
    print("\n")
    #print("votes : ", vote)
    #print("\n")


    print("Final_votes :")
    final_vote = OrderedDict(sorted(vote.items(), key=lambda item: item[1]))
    for i in final_vote:
        print(i + " : " + str(round(final_vote[i],1)))
    print("Higher votes recommended\n")
    



if __name__ == "__main__":
    Main()