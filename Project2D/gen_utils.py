#!/usr/bin/env python
#General helper functions and tools

#Helper function for poorly formatted ps files
def split_and_remove(string, split_char, to_remove):
	toks = string.split(split_char)
	new_toks = []
	for tok in toks:
		if tok != to_remove:
			new_toks = new_toks + [tok]
	return new_toks
	
	
#Remove duplicates from ordered list (checks adjacent items only)
def remove_ordered_duplicates(items_list):
	if len(items_list) <= 1:
		#Cant have duplicates with 1 or less
		return items_list
	
	no_dups = [items_list[0]]
	for i in range(1,len(items_list)):
		if items_list[i] != items_list[i-1]:
			#New, add to list
			no_dups = no_dups + [items_list[i]]
	
	return no_dups
	
