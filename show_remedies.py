from py2neo import Graph

def show_disease_list(cypher, crop_name):
    result = cypher.execute("MATCH(n1:Crop) - [r1:may_suffer_from] -> (n2) - [r2:which_may_be] -> (n3) WHERE n1.name={a} RETURN n3", a=crop_name)
    disease_list = []
    for i in range(len(result)):
        disease_list.append(str(result[i].n3['name']))

    print("disease names : ")
    print(disease_list)


def Main():
    graph = Graph()
    cypher = graph.cypher

    crop_name = input("Enter crop_name : ")
    show_disease_list(cypher, crop_name)
    disease_name = input("Enter disease name from the list above : ")

    query1 = "MATCH(n1:Crop) - [r1:may_suffer_from] -> (n2) - [r2:which_may_be] -> (n3) - [r3:about_disease] -> (n4:symptom) WHERE n1.name={a} and n3.name={b} RETURN n4"
    query2 = "MATCH(n1:Crop) - [r1:may_suffer_from] -> (n2) - [r2:which_may_be] -> (n3) - [r3:about_disease] -> (n4:management) WHERE n1.name={a} and n3.name={b} RETURN n4"
    result1 = cypher.execute(query1, a=crop_name, b=disease_name)
    result2 = cypher.execute(query2, a=crop_name, b=disease_name)

    print("\n")
    print("Symptom(s) : ", result1[0].n4['descrp'])
    print("\n")
    Manage_list = result2[0].n4['descrp'].split('::')
    print("Management(s) : ")
    for i in range(len(Manage_list)):
        print(">>> ", Manage_list[i])


if __name__ == "__main__":
    Main()