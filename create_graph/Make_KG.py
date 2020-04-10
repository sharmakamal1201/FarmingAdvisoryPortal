from py2neo import Graph, Node, Relationship
import json
import glob


def MAKE_KG(filename):
	graph = Graph()
	cypher = graph.cypher

	#filename = input("Enter json_data_file path : ")
	#filename = 'output_kg_wheat.json'

	data_dict = {}
	with open(filename, 'r') as f:
		data_dict = json.load(f)


	for superkey, supervalue in data_dict.items(): # superkey is crop_name
		crop_name = superkey
		crop_node = Node("Crop", name=crop_name)
		graph.create(crop_node)
		print("\n")
		print("created a node with name " + crop_name)
		print("\n")
		for key,value in supervalue.items():

			if(key == "diseases"):
				key_node = Node(key, name = key)
				graph.create(key_node)
				graph.create(Relationship(crop_node, "may_suffer_from", key_node))
				print("created a node with name " + key + " and connected to crop_node")
				for disease_name in value: # value is of list type here
					for k,v in disease_name.items(): # k is disease name here and v in dict with keys: symptom, management
						k_node = Node(k, name = k)
						graph.create(k_node)
						graph.create(Relationship(key_node, "which_may_be", k_node))
						print("created a node with name " + k + " and connected to disease_node")
						for k1,v1 in v.items(): # k1 is symptom or management
							k1_node = Node(k1, name=k1, descrp=v1)
							graph.create(k1_node)
							graph.create(Relationship(k_node, "about_disease", k1_node))
							print("created a node with name " + k1 + " and connected to " + k + " named node")

			elif(key == "postProductionTechnique"):
				key_node = Node(key, name = key, descrp = value)
				graph.create(key_node)
				graph.create(Relationship(crop_node, "has_PPT", key_node))
				print("create_node with name " + key + " and connect to crop_node")

			elif(key == "pestManagement"):
				key_node = Node(key, name = key)
				graph.create(key_node)
				graph.create(Relationship(crop_node, "has_pestManagement", key_node))
				for k,v in value.items():
					k_node = Node(k, name=k, descrp=v)
					graph.create(k_node)
					graph.create(Relationship(key_node, "about_pestManagement", k_node))
					print("created a node with name " + k + " and connected to " + key + " named node")

			elif(key=="CropGrownIn" or key=="climateRequirement" or key=="soilRequirement" or key=="totalGrowingPeriod"):
				descriptions = value.split(',')
				qry = "MATCH(n) WHERE n.name={b} and n.descrp={a} RETURN n"
				for i in descriptions:
					res = cypher.execute(qry,a=i,b=key)
					if(len(res) == 0): # if node doesn't exists create it
						key_node = Node(key, name=key, descrp=i)
						graph.create(key_node)
					else:
						key_node = res[0].n
					graph.create(Relationship(crop_node, "requires", key_node))
					#graph.create(Relationship(key_node, "favours", crop_node))
					print("created a node with name "+key+" and connected to crop_node having descrp = "+i)
			
			elif(key=="waterRequirement" or key=="rainfallRequirement" or key=="temperatureRequirement"):
				descriptions = value.split(' to ')
				if(descriptions[0]=="NA"):
					descriptions = ['0','0']
				qry = "MATCH(n) WHERE n.name={b} and n.descrp={a} RETURN n"
				res1 = cypher.execute(qry, b="min"+key, a=descriptions[0])
				res2 = cypher.execute(qry, b="max"+key, a=descriptions[1])
				if(len(res1)==0):
					nm = "min"+key
					key_node = Node(nm, name=nm, descrp=descriptions[0])
					graph.create(key_node)
				else:
					key_node = res1[0].n
				graph.create(Relationship(crop_node, "requires", key_node))
				#graph.create(Relationship(key_node, "favours", crop_node))
				print("created a node with name "+"min"+key+" and connected to crop_node having descrp = "+descriptions[0])
				if(len(res2)==0):
					nm = "max"+key
					key_node = Node(nm, name=nm, descrp=descriptions[1])
					graph.create(key_node)
				else:
					key_node = res2[0].n
				graph.create(Relationship(crop_node, "requires", key_node))
				#graph.create(Relationship(key_node, "favours", crop_node))
				print("created a node with name "+"max"+key+" and connected to crop_node having descrp = "+descriptions[1])

			else:
				key_node = Node(key, name=key, descrp=value)
				graph.create(key_node)
				graph.create(Relationship(crop_node, "has", key_node))
				print("created a node with name " + key +" and connected to crop_node")


def Main():
	directory = "G://6th sem/SE/project_code/json_graphs"
	print("data folder path : ", directory)
	files = glob.glob(directory+"/*.json")
	for filename in files:
		MAKE_KG(filename)


if __name__ == "__main__":
	Main()