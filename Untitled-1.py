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