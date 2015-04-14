Before querying, create a PMCQuery object:
from PMCQuery import PMCQuery
qr = PMCQuery('PMC')

Functions in PMCQuery
1.	searchInTitle(keywords, contain_all_kywd)
	Retrieve papers whose titles contain any element in 'keywords'. 'keywords' should be single string containing one or more keywords separated by space. For example, 'Brain Serum'.
	Type of value returned of the function is cursor and you need to use for loop to get each document.
	'contain_all_kywd' is a boolean variable. If 'contain_all_kywd' is True, the title of retrieved paper must contain all given keywords. Otherwise, returning paper whose title contains any of the given keywords
	Example:
			res = searchInTitle(keywords, False)
			for doc in res:
				pprint.pprint(doc)
	
2.	searchInCaption(keywords, contain_all_kywd)
	Retrieve tables whose titles contain any element in 'keywords'. 'keywords' should be single string containing one or more keywords separated by space. For example, 'Brain Serum'.
	Type of value returned of the function is cursor and you need to use for loop to get each document. 
	'contain_all_kywd' is a boolean variable. If 'contain_all_kywd' is True, the caption of retrieved table must contain all given keywords. Otherwise, returning table whose caption contains any of the given keywords
	Example:
			res = searchInCaption(keywords, False)
			for doc in res:
				pprint.pprint(doc)
				
3.	searchByHeader(keywords, contain_all_kywd)
	Retrieve columns whose headers contain any element in 'keywords'. 'keywords' should be single string containing one or more keywords separated by space. For example, 'Brain Serum'.
	Type of value returned of the function is nested list. Each element in the outermost list corresponds to a partial table containing all columns under the queried headers.
	'contain_all_kywd' is a boolean variable. If 'contain_all_kywd' is True, the header of retrieved table must contain all given keywords. Otherwise, returning table whose header contains any of the given keywords

4.	searchBySubheader(keywords, contain_all_kywd)
	Retrieve columns whose sub-headers contain any element in 'keywords'. 'keywords' should be single string containing one or more keywords separated by space. For example, 'Brain Serum'.
	Type of value returned of the function is nested list. Each element in the outermost list corresponds to a partial table containing all columns under the queried sub-headers.
	'contain_all_kywd' is a boolean variable. If 'contain_all_kywd' is True, the sub-header of retrieved table must contain all given keywords. Otherwise, returning table whose sub-header contains any of the given keywords

5.	searchByPubYear(year, publish_type)
	Retrieve papers published in 'year'. 'publish_type' is either 'ppub' (traditional publishing) or 'epub' (electronic publishing)
	
6.	searchByPaperPubBefore(year, publish_type)
	Retrieve papers published before 'year'. 'publish_type' is either 'ppub' (traditional publishing) or 'epub' (electronic publishing)

7.	getTableCol(table_id, index)
	In the table whose id is 'table_id', retrieve columns with indices in 'index'. 'index' could be either a number or a list.

8.	getTableRow(table_id, index)
	In the table whose id is 'table_id', retrieve rows with indices in 'index'. 'index' could be either a number or a list.

9.	setNoteParameter(flag)
	Setting parameter of whether to return the note of the table. The parameter is set to be False by default. You can set it to be 'True' by setting 'flag' in this function to be 'True' 



