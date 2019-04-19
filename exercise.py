import sys
import linprog
import collections

tasks_name= []
task_content=[]
dict_task={}

	
subtask=[]
percentage=[]
subtask_content=[]
dict_subtask_utility={}
dict_subtask_percentage={} 
current_utility=0

alphabet= ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

task_expected_utility = {}
mine_expected_utilities ={}
peer_expected_utilities={}
 
updated_tasks={}

class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)


def parseInput(decisions_nbr,rules):
	k=0
	while(k<len(rules)):
		if(rules[k]=="T"):
			task="T"
			k+=1
			while(rules[k] != "="):
				task+=rules[k]
				k+=1
			tasks_name.append(task)		
		if(rules[k]=="["):
			j=k
			s=Stack()
			open_brackets=1
			closed_brackets=0
			while(open_brackets!=closed_brackets): 
				if(rules[j]=="[" and j!=k):
					open_brackets+=1
				if(rules[j]=="]"):
					closed_brackets+=1
#				if(rules[k]!="[" and rules[k]!="]"):
				s.push(rules[j]);
				j+=1	
			k=j
			a=""	
			while(s.isEmpty()!=True):
				a+=s.pop()
			if(a!=""):
				task_content.append(a[::-1])
		else:
			k+=1
	
	for k in range(0, len(tasks_name)):
		dict_task[tasks_name[k]] = task_content[k]

def parseSubtasks(keys, values, flag):
	#{'T1||A': '3)', 'T1||B': '-1)', 'T2||A': '[A1=(18,4),A2=(2,2)])', 'T2||B': '[B1=(80%,2),B2=(20%,3)])', 'T2||C': '1)'}

	#[A=(30%,[A1=(18,4),A2=(2,2)]),B=(40%,[B1=(80%,2),B2=(20%,3)]),C=(30%,1)]
	#[A=(60%,-1),B=(40%,1)]
	#[A=(1,1)]

	#(T1=[A=(60%,3),B=(40%,-1)],T2=[A=(30%,0),B=(30%,2),C=(30%,[B1=(80%,[X=(20%,[X1=(20%,1),X2=(80%,3)]),Y=(80%,3)]),B2=(20%,3)]),D=(10%,1)],T3=[A=(100%,1.4)]) 1
	for key in range(0,len(keys)):
		value=values[key]
		k=1
		while(k<len(value)-1):#remove the first and last rect brackets
			if((flag==False and value[k] in alphabet and value[k+1]=="=") or (flag==True and value[k] in alphabet)):
				sub_name=""
	
				while(value[k]!="="): # to get the subtask Name
					sub_name+=value[k]
					k+=1

				p=""
				while(value[k]!=","): # to get the subtask percentage
					if(value[k]!="=" and value[k]!= "("):
						p+=value[k]
					k+=1

				k+=1 # to discard the first comma
				open_brackets=1
				closed_brackets=0
				st=Stack()
				while (open_brackets!=closed_brackets):
					if(value[k]=="("):
						open_brackets+=1
					elif (value[k]==")"):
						closed_brackets+=1
					st.push(value[k]);
					k+=1
				if(value[k]==","):
					k+=1

				a=""
				while(st.isEmpty()!=True):
					a+=st.pop()
				if("[" in a and "]" in a and len(a)>5): # means that there are some more things to parse
					if(flag==True):
						dict_subtask_percentage[keys[key]+"."+sub_name] = p
						parseSubtasks([keys[key]+"."+sub_name], [a[::-1][:-1]], True)

					else:	
						dict_subtask_percentage[keys[key]+"||"+sub_name] = p
						parseSubtasks([keys[key]+"||"+sub_name], [a[::-1][:-1]], True)

				else:
					if(flag==True):
						subtask.append(keys[key]+"."+sub_name)
					else:
						subtask.append(keys[key]+"||"+sub_name)
					subtask_content.append(a[::-1][:-1])
					percentage.append(p)

	for k in range(0, len(subtask)):
		dict_subtask_utility[subtask[k]] = subtask_content[k]
		dict_subtask_percentage[subtask[k]] = percentage[k]
				

def decide_rational():
	
# dict_task = {'T1': '[A=(60%,3),B=(40%,-1)]', 'T2': '[A=(30%,[A1=(18,4),A2=(2,2)]),B=(40%,[B1=(80%,2),B2=(20%,3)]),C=(30%,1)]'}
# dict_subtask_utility = {'T1||A': '3', 'T1||B': '-1', 'T2||A.A1': '4', 'T2||A.A2': '2', 'T2||B.B1': '2', 'T2||B.B2': '3', 'T2||C': '1'}
# dict_subtask_percentage = {'T2||A': '30%', 'T1||A': '60%', 'T1||B': '40%', 'T2||A.A1': '18', 'T2||A.A2': '2', 'T2||B': '40%', 'T2||B.B1': '80%', 'T2||B.B2': '20%', 'T2||C': '30%'}

	dict_all_tasks_utilities={}
	for t in dict_subtask_percentage:
		utility=0
		found=False
		for t2 in dict_subtask_utility:
			if(t == t2):
				found=True
				perc= dict_subtask_percentage.get(t) # get the content (percentage or number) of the subtask 
 	
				if("%" in perc):
					utility= (int(perc[:-1]) /100)* float(dict_subtask_utility.get(t))
				elif("%" not in perc):
					upper_level = getUpperLevel(t)
					task_length = len(t) 
					total_observations=0

					for subtask in dict_subtask_percentage:
						if((upper_level!= subtask) and upper_level in subtask and len(subtask)==task_length):
							total_observations+=int(dict_subtask_percentage.get(subtask))
					utility = (int(perc) /total_observations )* float(dict_subtask_utility.get(t))
		if(found==True):
			dict_all_tasks_utilities[t]=utility
		else:
			dict_all_tasks_utilities[t]=dict_subtask_percentage.get(t)

	#at this point we got something like this:
	#{'T2||A': '30%', 'T1||A': 1.7999999999999998, 'T1||B': -0.4, 'T2||A.A1': 3.6, 'T2||A.A2': 0.2, 'T2||B': '40%', 'T2||B.B1': 1.6, 'T2||B.B2': 0.6000000000000001, 'T2||C': 0.3}

	deleted_keys={}
	for key in dict_subtask_percentage:
		if(key not in dict_subtask_utility): # check if the value correponds to one upper velue's level
			value=dict_all_tasks_utilities[key]
			deleted_keys[key] = value 

	for key in deleted_keys:
		del dict_all_tasks_utilities[key] # delete all the entries with "%" and not only .. it could be a number

	dict_all_tasks= collections.OrderedDict(sorted(dict_all_tasks_utilities.items()))

	calculateExpectedUtilities(dict_all_tasks,deleted_keys,[],"")

	task_expected= collections.OrderedDict(sorted(task_expected_utility.items()))

	current_utility= max(list(task_expected.values()))
	#print(task_expected_utility)
	return [t for t in task_expected if (task_expected.get(t) == current_utility)][0]

def calculateExpectedUtilities(d,deleted_keys,already_visited, decideNash):
	new_dic = d
	#print("d: ",d)
	for key in d:
	#	print("key: ", key)
		upper_level = getUpperLevel(key)
		#print("upper: ",upper_level)
		if(key not in already_visited):
			expected_utility = d.get(key)
			joint=False
			for k in d:# joint the utilities of the same level
				if (key!=k and getUpperLevel(k) == upper_level): 
					joint=True
					expected_utility+=d.get(k)
					already_visited.append(key)
					already_visited.append(k)
			if(joint==False): # didn't found any more task to joint
				already_visited.append(key)

			if(upper_level in dict_task): # if we already reached the most upper level
				if(decideNash==""):
					task_expected_utility[upper_level]=expected_utility
				elif(decideNash=="decideNash_mine"):
					mine_expected_utilities[upper_level]=expected_utility

				elif(decideNash=="decideNash_peer"):
					peer_expected_utilities[upper_level]=expected_utility

			else:	
				#print(upper_level)
				for deleted in deleted_keys: 
					if(upper_level == deleted ):
						value = deleted_keys.get(deleted)
						if("%" in value):
							expected_utility*=int(value[:-1])/100
						else:
							total_observations=int(value)
							found=False
							for k in deleted_keys:
								if(len(k) == len(deleted) and k!=deleted and getUpperLevel(upper_level) in k):
									found=True
									total_observations+=int(deleted_keys.get(k))
							if(found==False): # means that it was not found in the deleted_keys dictionary 
								for k in dict_subtask_percentage:
									if(len(k) == len(deleted) and k!=deleted and getUpperLevel(upper_level) in k):
										#print("k: ",k," deleted : ",deleted)
										total_observations+=int(dict_subtask_percentage.get(k))
							#print("total_observations: ",total_observations)
							expected_utility *= (int(value)/total_observations)

						new_dic[upper_level] = expected_utility
						break;
				if(decideNash==""):
					return calculateExpectedUtilities(new_dic,deleted_keys,already_visited,"")
				elif(decideNash=="decideNash_mine"):
					return calculateExpectedUtilities(new_dic,deleted_keys,already_visited,"decideNash_mine")
				elif(decideNash=="decideNash_peer"):
					return calculateExpectedUtilities(new_dic,deleted_keys,already_visited,"decideNash_peer")


def decideRisk():
	# dict_subtask_utility = {'T1||A': '3', 'T1||B': '-1', 'T2||A.A1': '4', 'T2||A.A2': '2', 'T2||B.B1': '2', 'T2||B.B2': '3', 'T2||C': '1'}
	
	dict_all_tasks_utilities={}
	
	for t in dict_subtask_percentage:
		utility=0
		found=False
		for t2 in dict_subtask_utility:
			if(t == t2):
				found=True
				perc= dict_subtask_percentage.get(t) # get the content (percentage or number) of the subtask 
 	
				if("%" in perc):
					utility= (float(perc[:-1]) /100)* int(dict_subtask_utility.get(t))
				elif("%" not in perc):
					upper_level = getUpperLevel(t)
					task_length = len(t) 
					total_observations=0
					for subtask in dict_subtask_percentage:
						if((upper_level!= subtask) and upper_level in subtask and len(subtask)==task_length):
							total_observations+=int(dict_subtask_percentage.get(subtask))
					utility = (float(perc) /total_observations )* float(dict_subtask_utility.get(t))
		if(found==True):
			dict_all_tasks_utilities[t]=utility
		else:
			dict_all_tasks_utilities[t]=dict_subtask_percentage.get(t)

	dict_all_tasks_utilities = collections.OrderedDict(sorted(dict_all_tasks_utilities.items()))

	#at this point we got something like this:
	#{'T1||A': 3.0, 'T1||B': 0.0, 'T2||A': 3.0, 'T3||A': 2.0}

	if(len(dict_task) ==1): # only one task was provided 
		#print("(1.00,"+list(dict_task.keys())[0]+")")
		return "(1.00,"+list(dict_task.keys())[0]+")"

	else:
		calculateExpectedUtilities(dict_all_tasks_utilities,[],[],"")

		expected_utilities = task_expected_utility
		minimum_utility_task = getMinUtilityPerTask(dict_subtask_utility,[])
       	
		expected_utilities = collections.OrderedDict(sorted(expected_utilities.items()))
		minimum_utility_task = collections.OrderedDict(sorted(minimum_utility_task.items()))

	#	print("expected_utilities: ",expected_utilities)
#		print("minimum utility : ",minimum_utility_task)

		all_neg_utilities=[u for u in list(minimum_utility_task.values()) if u<0]
		if(len(all_neg_utilities) == len(minimum_utility_task)): #all min utilities are negative
			max_negative_utility = max(all_neg_utilities)

			l=[el for el in minimum_utility_task if(minimum_utility_task.get(el) == max_negative_utility)] #list that contains all the tasks with the max negative utility
			
			weight='%.2f' %(1.00/len(l))
			l2=[str(weight)+","+el for el in l]

			result=""
			for el in l2:
				if(el!= l2[-1]): #if not the last
					result+=el+";"
				else:
					result+=el
			result= "("+result+")"	
			return result

		else: # use the LP solver
			C=[-utility for utility in expected_utilities.values()]

			A=[]
			A.append([-utility for utility in minimum_utility_task.values()])
			for i in range(0,len(C)):
				new=[]
				for n in range(0,len(C)):
					if(i==n):
						new.append(-1)
					else:
						new.append(0)
				A.append(new)	

			eq_left=[[1 for n in C]]
			ineq_right = [0 for i in range(0, len(A))]

			resolution, sol=linprog.linsolve(C,ineq_left=A, ineq_right=ineq_right, eq_left=eq_left, eq_right=[1])
			
			#print("\n #################\nsol -> ", sol)

			# check if there are tasks with the same expected utility
			all_repeated_tasks=[] #all repeated tasks with the same expected utilities are in this list of lists
			already_visited=[]
			for task in expected_utilities:
				if(task not in already_visited):
					outter_value=expected_utilities.get(task)
					l=[task]
					for t in expected_utilities:
						inner_value=expected_utilities.get(t)
						#if(t!=task and outter_value ==inner_value and minimum_utility_task.get(t)>0 and minimum_utility_task.get(task)>0):
						#if(t!=task and outter_value ==inner_value):
						if(t!=task and outter_value ==inner_value):
							already_visited.append(t)
							already_visited.append(task)
							if(minimum_utility_task.get(t)>=0):
								l.append(t)
							elif(minimum_utility_task.get(t) == minimum_utility_task.get(task)):
								l.append(t)


					if(len(l)>1): # if there is some task with the same expected utility
						all_repeated_tasks.append(l)
						already_visited.append(task)

#			print("repeated tasks: ",all_repeated_tasks)
			task_res =[]
			tasks=list(minimum_utility_task.keys())
			
			res=[] # ['1.00,T1', '2.00,T2', ...]
			for i in range(0,len(sol)):
				if(sol[i]>0):
					repeated=False
					for l in all_repeated_tasks:
						if(tasks[i] in l):
							repeated=True
							for l2 in l:
								res.append(str('%.2f' %(sol[i]/len(l)))+","+l2)	
							break;	

					if(repeated==False):
						res.append(str('%.2f' %(sol[i]))+","+tasks[i])

			result="("
			for el in res:
				if(el!=res[-1]): # not the last element
					result+=el+";"
				else:
					result+=el
			result= result+")"	
			return result		


def getAllTasksUtilities(dict_subtask_utility, dict_subtask_percentage):

	dict_all_tasks_utilities={}
	
	for t in dict_subtask_percentage:
		utility=0
		found=False
		for t2 in dict_subtask_utility:
			if(t == t2):
				found=True
				perc= dict_subtask_percentage.get(t) # get the content (percentage or number) of the subtask 
				if("%" in perc):
					utility= (float(perc[:-1]) /100)* int(dict_subtask_utility.get(t))
				elif("%" not in perc):
					upper_level = getUpperLevel(t)
					task_length = len(t) 
					total_observations=0
					for subtask in dict_subtask_percentage:
						if("%" not in dict_subtask_percentage.get(subtask)):
							if((upper_level!= subtask) and upper_level in subtask and len(subtask)==task_length):
								total_observations+=int(dict_subtask_percentage.get(subtask))
					utility = (float(perc) /total_observations )* float(dict_subtask_utility.get(t))

		if(found==True):
			dict_all_tasks_utilities[t]=utility
		else:
			dict_all_tasks_utilities[t]=dict_subtask_percentage.get(t)

	dict_all_tasks_utilities = collections.OrderedDict(sorted(dict_all_tasks_utilities.items()))
	return dict_all_tasks_utilities


def deleteOutsidekeys(mine_payoff_percentage, mine_payoff, mine_dict_all_tasks_utilities): #deletes the keys from the dict_all_tasks_utilities which belong to an outsider level 
	deleted_keys={}
	for key in mine_payoff_percentage:
		if(key not in mine_payoff): # check if the value correponds to one upper value's level
			value=mine_dict_all_tasks_utilities[key]
			deleted_keys[key] = value 

	for key in deleted_keys:
		del mine_dict_all_tasks_utilities[key] # delete all the entries with "%" and not only .. it could be a number

	mine_dict_all_tasks_utilities= collections.OrderedDict(sorted(mine_dict_all_tasks_utilities.items()))	
	deleted_keys= collections.OrderedDict(sorted(deleted_keys.items()))
	return mine_dict_all_tasks_utilities, deleted_keys

def parseAndBuilMatrix(mine_rules, peer_rules):

	#mine=(T0|T0=[A=(1,2)],T0|T1=[A=(1,0)],T1|T0=[A=(1,0)],T1|T1=[A=(1,4)])
	#Mine
	parseInput(0,mine_rules[1:len(mine_rules)-1])
	parseSubtasks(list(dict_task.keys()), list(dict_task.values()), False)
	mine_payoff = collections.OrderedDict(sorted(dict_subtask_utility.items()))
	mine_payoff_percentage= collections.OrderedDict(sorted(dict_subtask_percentage.items()))
	mine_dict_all_tasks_utilities_preProcessed = collections.OrderedDict(sorted(getAllTasksUtilities(mine_payoff, mine_payoff_percentage).items()))
	mine_dict_all_tasks_utilities, deleted_keys=deleteOutsidekeys(mine_payoff_percentage, mine_payoff, mine_dict_all_tasks_utilities_preProcessed)
	calculateExpectedUtilities(mine_dict_all_tasks_utilities, deleted_keys,[], "decideNash_mine")

	#clear all global variables
	dict_subtask_utility.clear()
	dict_subtask_percentage.clear()
	dict_task.clear()
	subtask.clear()
	subtask_content.clear()
	percentage.clear()

	#Peer
	parseInput(0,peer_rules[1:len(peer_rules)-1])
	parseSubtasks(list(dict_task.keys()), list(dict_task.values()), False)
	peer_payoff = collections.OrderedDict(sorted(dict_subtask_utility.items()))
	peer_payoff_percentage= collections.OrderedDict(sorted(dict_subtask_percentage.items()))

	peer_dict_all_tasks_utilities_preProcessed = collections.OrderedDict(sorted(getAllTasksUtilities(peer_payoff, peer_payoff_percentage).items()))
	peer_dict_all_tasks_utilities, deleted_keys=deleteOutsidekeys(peer_payoff_percentage, peer_payoff, peer_dict_all_tasks_utilities_preProcessed)
	calculateExpectedUtilities(peer_dict_all_tasks_utilities, deleted_keys,[],"decideNash_peer")

	#order the dictionaries!!!
	peer_expected= collections.OrderedDict(sorted(peer_expected_utilities.items()))
	mine_expected= collections.OrderedDict(sorted(mine_expected_utilities.items()))

	#print("mine: \n")
	#print(mine_payoff)
	#print(mine_payoff_percentage)

	payoff_matrix=[]

	first_element = list(mine_expected.keys())[0]
	first_row = first_element.split("|")[0] # from 'T0|T0' gets T0
	line_length= [element.split("|")[0] for element in mine_expected].count(first_row) # get the line length for matrix dimensions

	#build payoff matrix
	i=1
	line=[]
	for key in mine_expected:
		reverse_key=key.split("|")[1]+"|"+key.split("|")[0]
		l=[mine_expected.get(key),peer_expected.get(reverse_key)]
		line.append(l)
		if(i==line_length):
			payoff_matrix.append(line)
			line=[]
			i=0
		i+=1

	#print payoff matrix
	'''
	print("\n\n")
	for line in payoff_matrix:
		print(line,"\n")
	'''
	return payoff_matrix, mine_expected, peer_expected, line_length


def decideNash(mine_rules, peer_rules):
	
	payoff_matrix, mine_expected, peer_expected, line_length= parseAndBuilMatrix(mine_rules, peer_rules)

	return calculateNashEquilibrium(payoff_matrix, mine_expected, peer_expected, line_length)

def calculateNashEquilibrium(payoff_matrix, peer, mine, line_length):	
	#dominant strategy
	peer_pay = getMatrix(list(peer.keys()), line_length, "peer")
	mine_pay = getMatrix(list(mine.keys()), line_length, "mine")

	#print(peer_pay)
	#print(mine_pay)
	peer_choices_indexes=[]
	for i in range(0, len(payoff_matrix)):
		peer_possible_choices=[int(tuplee[1]) for tuplee in payoff_matrix[i]]
		best_choice =max(peer_possible_choices)	
		aux=[i for i in range(0,len(peer_possible_choices)) if peer_possible_choices[i]==best_choice]
		for indice in aux: 
			peer_choices_indexes.append([i, indice])

	mine_choices_indexes=[]
	for i in range(0, line_length):
		# i is the collumn index
		mine_possible_choices= [int(line[i][0]) for line in payoff_matrix]	
		best_choice =max(mine_possible_choices)
		aux2=[i for i in range(0,len(mine_possible_choices)) if mine_possible_choices[i]==best_choice]	
		for indice in aux2: 
			mine_choices_indexes.append([indice,i])

	#print("peer_choices: ",peer_choices_indexes)
	#print("mine_choices: ",mine_choices_indexes)	
	#calculate how many Nash Equilibriums exist
	number_nash_equilibrium=0
	selected_choices_mine=[]
	selected_choices_peer=[]
	for l in mine_choices_indexes:
		for l2 in peer_choices_indexes:
			if(l==l2):
				number_nash_equilibrium+=1
				selected_choices_mine.append(l)
				selected_choices_peer.append(l2)

	#print("selected :_ ",selected_choices_peer)
	if(number_nash_equilibrium==1):
		my_choice = (mine_pay[selected_choices_mine[0][0]][selected_choices_mine[0][1]]).split("|")[0]
		peer_choice= (peer_pay[selected_choices_peer[0][0]][selected_choices_peer[0][1]]).split("|")[0]
		return "mine="+my_choice+",peer="+peer_choice
	elif(number_nash_equilibrium>1):
		max_sum= 0

		res=[] #contains the indexes of the best choices, it could be just one or more
		for l in selected_choices_mine:
			result=(int((payoff_matrix[l[0]][l[1]])[0]) + int((payoff_matrix[l[0]][l[1]])[1]))
			if(result>=max_sum):
				max_sum=result
				res.append([result,l])

		#print("res: ",res)
		max_sum=0
		for result in res:
			if(result[0]>max_sum):
				max_sum=result[0]

		max_sum= max([result[0] for result in res])		


		results = [result[1] for result in res if result[0] ==max_sum]
		if(len(results)==1): #means that there is one equilibrium better than all the others
			my_choice = (mine_pay[results[0][0]][results[0][1]]).split("|")[0]
			peer_choice= (peer_pay[results[0][0]][results[0][1]]).split("|")[0]
			return "mine="+my_choice+",peer="+peer_choice
		elif(len(results)>1):
			# get the task with lower index for Mine
			results.sort()
			my_choice = (mine_pay[results[0][0]][results[0][1]]).split("|")[0]
			peer_choice= (peer_pay[results[0][0]][results[0][1]]).split("|")[0]
			return "mine="+my_choice+",peer="+peer_choice

	elif(number_nash_equilibrium==0):
		return "blank-decision"

def getMatrix(listt, line_length, tag): #given a list and the line length returns a bi-matrix with size line_length X line_length 
	i=0
	matrix=[]
	l=[]
	for k in range(0, len(listt)):
		l.append(listt[k])	
		if(len(l)==line_length):
			matrix.append(l)
			l=[]
	if(tag=="mine"):
		return matrix
	else:
		transpose = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))] 
		return transpose

def decideMixed(mine_rules, peer_rules):
	payoff_matrix, mine_expected, peer_expected, line_length= parseAndBuilMatrix(mine_rules, peer_rules)

	a,b,c,d= payoff_matrix[0][0][0], payoff_matrix[0][1][0], payoff_matrix[1][0][0], payoff_matrix[1][1][0]
	e,f,g,h= payoff_matrix[0][0][1], payoff_matrix[1][0][1], payoff_matrix[0][1][1], payoff_matrix[1][1][1]

	if((h-f)!=0 and (e-f-g+h)!=0 and (d-b)!=0 and (a-b+d-c)!=0):
		y=(h-f)/(e-f-g+h)
		x=(d-b)/(a-b+d-c)
	
		if(y<1 and x<1):
			y='%.2f' %(y)
			suby= '%.2f' %(1-float(y))
			x='%.2f' %(x)
			subx='%.2f' %(1-float(x)) 

			return "mine=("+y+","+suby+"),peer=("+x+","+subx+")" 
		else:
			return "blank-decision"
	else:
		return "blank-decision"



def getMinUtilityPerTask(dict_all_tasks_utilities, already_visited):
	minimum_utility_task= {}
	new_dict= dict_all_tasks_utilities
	for task in dict_all_tasks_utilities:
		upper=getUpperLevel(task)
		if(upper in dict_task): 
			if(upper in minimum_utility_task):
				value = minimum_utility_task.get(upper)
				new_value = float(dict_all_tasks_utilities.get(task))
				if(new_value < value ): #actualize the variable
					minimum_utility_task[upper] = new_value
			else:
				value= float(dict_all_tasks_utilities.get(task))
				minimum_utility_task[upper]=value
		else:
			if(task not in already_visited):
				upper_level = getUpperLevel(task)
				expected_utility = int(dict_all_tasks_utilities.get(task))
				for k in dict_all_tasks_utilities:
					if (task!=k and getUpperLevel(k) == upper_level):  #join "task" with "k"
						expected_utility+=d.get(k)
						already_visited.append(task)
						already_visited.append(k)

				new_dict[upper_level] = expected_utility
				return getMinUtilityPerTask(new_dict,already_visited)	


	return minimum_utility_task #minimum utility per task


def getUpperLevel(level):
	up_lev = level.split(".")[:-1]
	up_level=""
	# get the uplevel in order to get the correpondent percentage
	if(up_lev==[]):
		up_level = level.split("||")[0]
	else:
		for i in range(0,len(up_lev)):
			if(up_lev[i] != up_lev[-1]):
				up_level+=up_lev[i]+"."
			else:
				up_level+=up_lev[i]
	
	return up_level	

def update_state(task,value,first_call):
	#(-3,T1.B)
	#(2,T1.C.C1) 
	corrected_task=""
	level_to_delete=""
	splitted_task = task.split(".")
	
	all_upper_levels_delete=[]

	if(len(splitted_task)==2):
		corrected_task= splitted_task[0]+"||"+splitted_task[1]  #refactor of the task name
		level_to_delete = getUpperLevel(corrected_task)

	elif(len(splitted_task)>2):
		for i in range(0,len(splitted_task)):
			if(i==0):
				corrected_task+=splitted_task[i]+"||"
			elif(i!=0 and i!= len(splitted_task)-1): # if we are not in the last element
				corrected_task+=splitted_task[i]+"."
			else:
				corrected_task+=splitted_task[i]

		level_to_delete= getUpperLevel(corrected_task)
		all_upper_levels_delete.append(level_to_delete)
		while("||" in level_to_delete):  # get all the upper levels which are to delete	
			level = getUpperLevel(level_to_delete)
			all_upper_levels_delete.append(level)
			level_to_delete=level
	#print("corrected_task = ", corrected_task)
	# save task in updated tasks dictionary
	if(corrected_task in dict_subtask_percentage):
		n_observations= int(dict_subtask_percentage.get(corrected_task))
		updated_tasks[corrected_task] = n_observations+1		
	elif(corrected_task in updated_tasks):
		n_observations= int(updated_tasks.get(corrected_task))
		updated_tasks[corrected_task] = n_observations+1
	else:
		updated_tasks[corrected_task] =1

	# t=T1||C
	# delete all the upper levels that is possible to delete
	to_delete=[]
	number_ocurrences=0
	for task in dict_subtask_percentage:
		if(task not in updated_tasks):
			if(task==corrected_task):
				if("%" not in dict_subtask_percentage.get(task)):
					number_ocurrences=int(dict_subtask_percentage.get(task))

			elif(level_to_delete in task and len(task) == len(corrected_task)):
				if(len(splitted_task) ==2):
					to_delete.append(task)
			
			for up_t in all_upper_levels_delete:
				if(up_t in task and len(task)<len(corrected_task) and ("%" in dict_subtask_percentage.get(task))): # only deletes the upper levels with %
					to_delete.append(task)
	
	if(number_ocurrences==0):
		number_ocurrences+=updated_tasks.get(corrected_task)


	to_delete=list(set(to_delete))
	for task in to_delete:
		del dict_subtask_percentage[task]
		if(task in dict_subtask_utility):
			del dict_subtask_utility[task]


	dict_subtask_utility[corrected_task] = str(value)
	dict_subtask_percentage[corrected_task]= str(number_ocurrences)

	
	if(len(splitted_task)>2): # for special cases like "2>" from AASMA input/output pdf
		up= getUpperLevel(corrected_task)
		if(up in updated_tasks):
			obs = updated_tasks.get(up)	+1

		elif(up in dict_subtask_percentage): # like the case from "3>" from AASMA input/output pdf ..  (3,T1.C.C2)
			obs =  int(dict_subtask_percentage.get(up)) +1

		else:
			obs=1
		dict_subtask_percentage[up] = str(obs)	
		updated_tasks[up]=obs



	append_tasks=[]
	for subtask in dict_subtask_percentage:  # for special cases like the test 8 of mooshak
		up = getUpperLevel(subtask)
		if("||" in up):
			if(up not in dict_subtask_percentage):
				append_tasks.append(up)
	for k in append_tasks:
		dict_subtask_percentage[k] = str(0)

	#print("updated_tasks: ", updated_tasks)
	#print("percentage_dic: ",dict_subtask_percentage)
	#print("utility_dic: ",dict_subtask_utility)
	#print("choice : ",decide_rational())


splited_input = sys.stdin.readline().split(' ')
last_choice=""
size = 1 if len(splited_input) <= 2 else int(splited_input[2])	#[:-1] is to remove '\n'

for i in range(0, size):
	if(i!=0):
		splited_input = sys.stdin.readline().split(' ')

	if(len(splited_input)>1):
		if(splited_input[0]=="decide-rational"):
			rules= splited_input[1]
			parseInput(splited_input[-1],rules[1:len(rules)-1])

			parseSubtasks(list(dict_task.keys()), list(dict_task.values()), False)


			dict_subtask_percentage = collections.OrderedDict(sorted(dict_subtask_percentage.items()))
			dict_subtask_utility = collections.OrderedDict(sorted(dict_subtask_utility.items()))
			#try:
			last_choice = decide_rational()
		
			'''
			except:
				last_choice = list(dict_task.values())[0]
			'''
			sys.stdout.write(last_choice + '\n')

		elif(splited_input[0]=="decide-risk"):
			rules=splited_input[1]
			parseInput(splited_input[-1],rules[1:len(rules)-1])
			parseSubtasks(list(dict_task.keys()), list(dict_task.values()), False)

			dict_subtask_percentage = collections.OrderedDict(sorted(dict_subtask_percentage.items()))
			dict_subtask_utility = collections.OrderedDict(sorted(dict_subtask_utility.items()))
	
			sys.stdout.write(decideRisk()+'\n')

		
		elif(splited_input[0] =="decide-nash"):
			s=splited_input[1].split(",peer=")
			res=decideNash(s[0], s[1])
			sys.stdout.write(str(res) + '\n')

		elif(splited_input[0] =="decide-mixed"):
			s=splited_input[1].split(",peer=")
			res=decideMixed(s[0], s[1])
			sys.stdout.write(str(res) + '\n')

		elif(splited_input[0]=="decide-conditional"):
			s=splited_input[1].split(",peer=")
			res=decideNash(s[0], s[1])
			if(res!="blank-decision"):
				sys.stdout.write(str(res) + '\n')
			else:
				res=decideMixed(s[0], s[1])
				if(res!="blank-decision"):
					sys.stdout.write(str(res) + '\n')	
				else:
					sys.stdout.write("blank-decision" + '\n')	

	else: #updates
		#(1,A)
		#(-3,T1.B)
		obs = splited_input[0][:-1] # [:-1] is to remove '\n'
		splitted= obs[1:len(obs)-1].split(",")
		value= splitted[0]
		task=splitted[1]

		if("." not in task):
			task=last_choice+"."+task
		elif ("." in task and task.split(".")[0] not in dict_task):
			task = last_choice +"."+task
			
		#try:
		update_state(task,value,True)
		#print(dict_subtask_utility,"\n")
		#print(dict_subtask_percentage)
		last_choice = decide_rational()
		'''
		except:
			last_choice = list(dict_task.values())[0]
		'''
		sys.stdout.write(last_choice + '\n')
	'''
	print(dict_task,"\n")
	print(task_expected_utility,"\n")
	print(dict_subtask_utility,"\n")
	print(dict_subtask_percentage)
	'''

