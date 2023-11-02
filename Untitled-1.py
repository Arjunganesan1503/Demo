#sample trial for git practice
a=30
b=20
print(a+b)
#add method in set
practice_set={1,2,3,4}
practice_set.add(5)
print(practice_set)
#remove method in set
practice_set.remove(1)
print(practice_set) 
#union method in set 
practice_set1={10,20,30}
practice_set2={20,30,40}
union_set=practice_set2.union(practice_set1)
print(union_set)
#output
#{20, 40, 10, 30} - set remove duplicate implicitly 
difference_set=practice_set1.difference(practice_set2)
print(difference_set) 
#output
#{10} - because it takes the variable inside the method bracket that is practice_set2 and remove it from the practice_set 1, it wont keep the remaining element in practice_set
#symmetric difference method in set
symmetric_diff_set = practice_set1.symmetric_difference(practice_set2)
print(symmetric_diff_set) 
#{40,10} - It retrieves the remaining value from both practice_set1 and practice_set2 
#clear method in set
clear_set={100,105,110,120}
clear_set.clear()
print(clear_set)  
#output
#set() -clears the value inside the set variable 
#check clear
print(clear_set) # working fine
# again adding elements to the clear_set
clear_set = {100,105,110,120}
print(clear_set) 
#output {120, 105, 100, 110}
#dictionary 
sample_dict ={"name":"lion", "family":"cat", "type":"carnivorous"}
print(sample_dict) 
#output
#{'name': 'lion', 'family': 'cat', 'type': 'carnivorous'}
#fetching values using key in dictionary
sample_dict["family"] 
#output
#'cat'
#fetching keys seperately from the dictionary
sample_dict.keys() 
#output
#dict_keys(['name', 'family', 'type'])
#converting it to list by typecasting
list(sample_dict.keys()) 
#output
#['name', 'family', 'type']
#fetching values seperately from the dictionary
sample_dict.values()
#output
#dict_values(['lion', 'cat', 'carnivorous'])
#converting values from dictionary to list by typecasting
list(sample_dict.values())
#output 
#['lion', 'cat', 'carnivorous'] 
#Replacing/mutable actions in dictionaries
sample_dict ={"name":"lion", "family":"cat", "type":"carnivorous"}
sample_dict["type"] = "nocturnal"
print(sample_dict)
#adding elements in dictionary
sample_dict["color"] = "yellow"
print(sample_dict)
#removing elements from dictionary
del sample_dict["color"]
print(sample_dict)
#another method for removing elements
sample_dict["color"] = "yellow"
print(sample_dict)
del sample_dict["color"]
print(sample_dict) 
#condtional statements
a = 25
b = 124
if (a+b)<200:
 print("lesser than 200")
if (a+b)>=200:
 print("greater than 200")





