from xml.dom.minidom import parse
# from PMCdocument import PMCdocument
import xml.dom.minidom
import csv
import os
import re

# import pymssql

xmlFolder = os.curdir + '/test2'
extractedTableFolder = os.curdir + '/res2'


def leafNodeValue(nd):
	children = nd.childNodes
	# print(nd.nodeName) #
	if nd.nodeName == 'xref':
		res = '(note: '
		suffix = ')'
	elif nd.nodeName == 'sup':
		res = '^{'
		suffix = '}'
	elif nd.nodeName == 'sub':
		res = '_{'
		suffix = '}'
	else:
		res = ''
		suffix = ''
	
	if len(children) == 0:
		if nd.nodeValue:
			temp = nd.nodeValue
			if temp.isspace():
				temp = ''
			# temp = temp.strip('\t\n\r') #
			# re.sub(r'\s+', ' ', temp)
			return ''.join([res, temp, suffix])
		else:
			return ''
	elif len(children) == 1 and children[0].firstChild == None:
		temp = children[0].nodeValue
		if temp.isspace():
			temp = ''
		# temp = temp.strip('\t\n\r') #
		# re.sub(r'\s+', ' ', temp)
		return ''.join([res, temp, suffix])
	else:
		for child in children:
			res = ''.join([res, leafNodeValue(child)])
		return ''.join([res, suffix])
			
			

def contentInGrid(ele):
	if ele.firstChild == None:
		# return (ele, 'None Type')
		# return ele
		# return None
		return ''
	else:
		leaf_value = leafNodeValue(ele)
		return leaf_value
		
def dataType(d):
	try: 
		float(d)
		return 'Numeric'
	except ValueError:
		return 'To be determined'

	
def saveToCSV(table,table_id):
# table_id is paper id + the id number of table in the paper
	with open(''.join([table_id,'.csv']),'w',newline='',encoding='utf-8') as csvfile:
	# with open(''.join([table_id,'.csv']),'w',newline='') as csvfile:
		table_writer = csv.writer(csvfile, delimiter=',')
		# table_writer.writerows(table)
		# encoded_table = [[s.encode('utf-8') for s in t] for t in table]
		table_writer.writerows(table)


def extractTable(table_node, rows):
	extractTable_2('thead',rows, table_node)
	extractTable_2('tbody',rows, table_node)

def extractTable_2(tag, rows, table):
	print('tag:  ', tag)
	component = table.getElementsByTagName(tag)
	trs = []
	if component:	
		trs = component[0].getElementsByTagName('tr')
	else:
		if tag == 'thead':
			trs = table.getElementsByTagName('tr')
		else:
			trs == []
	row_ct = 1 		
	row_span_ct = []
	for tr in trs:
		tds = tr.getElementsByTagName('td')
		if not tds:
			tds = tr.getElementsByTagName('th')
		row = []
		col_ct = 0
		# print('row_len:  ', len(tds))
		for td in tds:
			span_col = td.getAttribute('colspan')
			if not span_col or span_col == '':
				span_col = 1
			else:
				span_col = int(span_col)
				
			span_row = td.getAttribute('rowspan')
			if not span_row or span_row == '':
				span_row = 1
			else:
				span_row = int(span_row)	
				
			if (tag == 'thead' and row_ct == 1) or (tag == 'tbody' and row_ct == 1):
				row_span_ct.extend([span_row - 1]*span_col)			
			else:
				# print(row)			
				# print(row_span_ct, col_ct, row_ct)
				if row_span_ct[col_ct] == 0 and (span_row - 1) != 0:
					row_span_ct[col_ct] = row_span_ct[col_ct] + span_row - 1
				elif row_span_ct[col_ct] == 0 and (span_row - 1) == 0:
					pass
				else: #row_span_ct[col_ct] != 0 and (span_row - 1) == 0
					while(row_span_ct[col_ct]!=0):
						row_span_ct[col_ct] = row_span_ct[col_ct] - 1
						col_ct = col_ct + 1
						row.append('')
			
			row.append(contentInGrid(td))
			for empty_col in range(span_col - 1):
				col_ct = col_ct + 1
				row.append('')
			col_ct = col_ct + 1
		# print(row)
		rows.append(row)
		row_ct = row_ct + 1
	
	
	
	
for root, dirs, files in os.walk(xmlFolder):
	dir_name = root
	dir_name.replace(xmlFolder, '', 1)
	
	res_dir = extractedTableFolder + '/' + dir_name + '/'
	#make directory in result folder
	if dir_name == None or dir_name == '':
		pass
	else:
		if os.path.exists(extractedTableFolder + '/' + dir_name):
			pass
		else:
			os.mkdir(extractedTableFolder + '/' + dir_name)
	
	for filespath in files:
		print(root + '/' + filespath)
		curXMLfile = os.path.join(root,filespath)
	
		# DOMTree = xml.dom.minidom.parse('journal.pone.0106771.XML')
		DOMTree = xml.dom.minidom.parse(curXMLfile)
		paper = DOMTree.documentElement

		rows = []  #for saving as csv file


		# extract paper id
		paper_ids = paper.getElementsByTagName("article-id")
		paper_id = ''
		for pid in paper_ids:
			if pid.getAttribute('pub-id-type') == 'pmc-uid':
				paper_id = pid.firstChild.nodeValue
				break
		# print(paper_id)

		#extract paper title
		paper_title_temp = paper.getElementsByTagName("article-title")[0]
		paper_title = contentInGrid(paper_title_temp)





		table_wraps = paper.getElementsByTagName("table-wrap")
		ct = 0
		for table_wrap in table_wraps:
			rows.append([paper_id])
			rows.append([paper_title])
			rows.append([])
			
			# caption of current table
			caption = table_wrap.getElementsByTagName('caption')
			if caption:
				title_children = caption[0]
			else:
				continue
			
			tables = table_wrap.getElementsByTagName('table')
			table = tables[0]
			# No. of current table
			ct = ct + 1
			print(['Table:   ',ct]) #
			
			
			title_text = contentInGrid(title_children)
			title_text.strip()

			rows.append([title_text])
			extractTable(table, rows)
			
			rows.append([])
			
			#extract table foot
			fn_flag = True
			table_wrap_foots = table_wrap.getElementsByTagName('table-wrap-foot')
			if table_wrap_foots:
				table_wrap_foot = table_wrap_foots[0]
				table_foot_texts = table_wrap_foot.getElementsByTagName('fn')
				if not table_foot_texts:
					table_foot_texts = table_wrap_foot.getElementsByTagName('p')
					fn_flag = False
				label_ct = 1
				for line in table_foot_texts:
					line_labels = line.getElementsByTagName('label')
					if fn_flag:
						line_text = leafNodeValue(line.getElementsByTagName('p')[0])
					else:
						line_text = leafNodeValue(line)
					if line_labels:
						line_label = leafNodeValue(line_labels[0])
						if line_label == '' or line_label == None:
							rows.append([line_text])
						else:
							rows.append([line_label, line_text])
					else:
						rows.append([line_text])
							
			
			#save to csv file
			file_name = ''.join([paper_id, '_tb', str(ct)])
			# print(rows)
			# print(rows)
			print(res_dir + file_name)
			saveToCSV(rows, res_dir + file_name)
			rows[:] = []

		


	
	
	
