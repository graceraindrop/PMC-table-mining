from xml.dom.minidom import parse
import xml.dom.minidom
import csv
import os
import pymongo

# os.chdir('F:\\table mining')
# os.chdir('/big/bilin/table_mining') #test
os.chdir('/big/TextMining') #whole
# os.chdir('D:\\parsing_temp')  #debug of whole on local
from PMCDocument import PMCDocument
from PMCMongoDB import PMCConnection
# import pymssql

# xmlFolder = os.curdir + '/testDataset' #test
xmlFolder = os.curdir + '/2015PMC' #Whole
# xmlFolder = os.curdir + '/tb'  #debug of whole on local
extractedTableFolder = os.curdir + '/res'
# xmlFolder = os.curdir + '/test2'
# extractedTableFolder = os.curdir + '/res2'


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
			# re.sub(r'\s+', ' ', temp)
			return ''.join([res, temp, suffix])
		else:
			return ''
	elif len(children) == 1 and children[0].firstChild == None:
		temp = children[0].nodeValue
		if not temp or temp.isspace():
			temp = ''
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

def insertToMongoDB(dcObj, collection, conn):
	# conn = PMCCollection(database_name)
	conn.addDocumentToCollection(collection, dcObj)
	
def saveToCSV(table,table_id):
# table_id is paper id + the id number of table in the paper
	with open(''.join([table_id,'.csv']),'w',newline='',encoding='utf-8') as csvfile:
		table_writer = csv.writer(csvfile, delimiter=',')
		table_writer.writerows(table)


def extractTable(table_node, dc):
	row_span_ct = extractTable_2('thead',dc, table_node)
	extractTable_2('tbody',dc, table_node, row_span_ct)

def extractTable_2(tag, dc, table_node, row_span_ct = None):
	if row_span_ct is None:
		row_span_ct = []
		
	component = table.getElementsByTagName(tag)
	trs = []
	if component:
		trs = component[0].getElementsByTagName('tr')
	else:
		if tag == 'thead':
			trs = table.getElementsByTagName('tr')
		else:
			trs == []
	
	row_ct = 0 # if processing the first row of thead, counting the number of columns
	sub_rows = [] # for sub-header
	header_colspan = [] #record the colspan of each unit in the header(first row)
	
	for tr in trs:
		tds = tr.getElementsByTagName('td')
		if not tds:
			tds = tr.getElementsByTagName('th')
		
		row = []
		col_ct = 0
	
		for td in tds:
			span_col = td.getAttribute('colspan') #
			if not span_col or span_col == '':
				span_col = 1
			else:
				span_col = int(span_col)
				
			span_row = td.getAttribute('rowspan')
			if not span_row or span_row == '':
				span_row = 1
			else:
				span_row = int(span_row)
	
			if tag == 'thead' and row_ct == 0:
				header_colspan.append(span_col)
				row_span_ct.extend([span_row - 1]*span_col)
			else:
				if row_span_ct[col_ct] == 0:
					row_span_ct[col_ct] = row_span_ct[col_ct] + span_row - 1
				else: #row_span_ct[col_ct] != 0 and (span_row - 1) == 0
					while(col_ct < len(row_span_ct) and row_span_ct[col_ct]!=0):
						row_span_ct[col_ct] = row_span_ct[col_ct] - 1
						col_ct = col_ct + 1 # point to next
						row.append('')
					# end of while loop, here col_ct are point to current td
					if col_ct < len(row_span_ct):
						row_span_ct[col_ct] = row_span_ct[col_ct] + span_row - 1
			
			print(row_span_ct, col_ct, contentInGrid(td))	
			row.append(contentInGrid(td)) # extract string of current td
			for empty_col in range(span_col - 1): #occupy following units by '' when colspan > 1
				col_ct = col_ct + 1 # pointing to current empty column
				row.append('')
				if tag == 'thead': 
					if row_ct == 0:
						header_colspan.append(0)
					else:
						pass
			col_ct = col_ct + 1 #pointing to next td if exists
			if tag != 'thead' and col_ct >= col_num:
				# no more columns in current row 
				break

	
		# has parsed through the current row
		# if row_span_ct is shorter than col_num, extend it
		#if tag == 'tbody' and len(row_span_ct) < col_num:
		#	row_span_ct.extend([0]*(col_num-len(row_span_ct)))
		
		if col_ct < len(row_span_ct):
			while(col_ct < len(row_span_ct)):
				if row_span_ct[col_ct] > 1:
					row_span_ct[col_ct] = row_span_ct[col_ct] - 1
				col_ct = col_ct + 1
				row.append('')
				
		# rows.append(row)
		if tag == 'thead':
			if row_ct == 0:
				dc['header'] = row
				dc['header_colspan'] = header_colspan
			else:
				sub_rows.append(row)
		else:
			sub_rows.append(row)
		row_ct = row_ct + 1
	if tag == 'thead':
		dc['sub_header'] = sub_rows
	else:
		dc['body'] = sub_rows
		
	return row_span_ct
	
	
	if col_num is None:
		col_num = 0

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
	sub_rows = []
	header_colspan = []
	
	row_span_ct = []
	
	for tr in trs:
		tds = tr.getElementsByTagName('td')
		if not tds:
			tds = tr.getElementsByTagName('th')
		row = []
		col_ct = 0
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
				col_num = col_num + span_col
				header_colspan.append(span_col)
				row_span_ct.extend([span_row - 1]*span_col)	
			elif (tag == 'tbody' and row_ct != 1) and len(row_span_ct) < col_num:
				row_span_ct.extend([0]*(col_num-len(row_span_ct)))
			else:
				if row_span_ct[col_ct] == 0 and (span_row - 1) != 0:
					row_span_ct[col_ct] = row_span_ct[col_ct] + span_row - 1
				elif row_span_ct[col_ct] == 0 and (span_row - 1) == 0:
					pass
				else: #row_span_ct[col_ct] != 0 and (span_row - 1) == 0
					while(row_span_ct[col_ct]!=0):
						row_span_ct[col_ct] = row_span_ct[col_ct] - 1
						col_ct = col_ct + 1
						row.append('')
					row_span_ct[col_ct] = row_span_ct[col_ct] + span_row - 1
								
				
			# print(row_span_ct, col_ct, contentInGrid(td))	
			row.append(contentInGrid(td))
			for empty_col in range(span_col - 1):
				col_ct = col_ct + 1
				if row_span_ct[col_ct] > 0:
					row_span_ct[col_ct] = row_span_ct[col_ct] - 1
				row.append('')
				if tag == 'thead': 
					if row_ct == 1:
						header_colspan.append(0)
					else:
						pass
			col_ct = col_ct + 1
			if tag != 'thead' and col_ct >= col_num:
				break
		
		if col_ct <= (len(row_span_ct)-1):
			while(col_ct < len(row_span_ct)):
				if row_span_ct[col_ct] > 0:
					row_span_ct[col_ct] = row_span_ct[col_ct] - 1
				col_ct = col_ct + 1
				row.append('')
		
		# rows.append(row)
		if tag == 'thead':
			if row_ct == 1:
				dc['header'] = row
				dc['header_colspan'] = header_colspan
			else:
				sub_rows.append(row)
		else:
			sub_rows.append(row)
		row_ct = row_ct + 1
	if tag == 'thead':
		dc['sub_header'] = sub_rows
	else:
		dc['body'] = sub_rows
		
	return col_num
	
# PMCConn = PMCConnection('PMC')
PMCConn = PMCConnection('PMCWhole')	#connect to database 'PMC'
for root, dirs, files in os.walk(xmlFolder):
	dir_name = root
	dir_name.replace(xmlFolder, '', 1)
	
	res_dir = extractedTableFolder + '/' + dir_name + '/'
	#make directory in result folder
	# if dir_name == None or dir_name == '':
		# pass
	# else:
		# if os.path.exists(extractedTableFolder + '/' + dir_name):
			# pass
		# else:
			# os.mkdir(extractedTableFolder + '/' + dir_name)
	
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
			if pid.getAttribute('pub-id-type') == 'pmc-uid' or pid.getAttribute('pub-id-type') == 'pmc':
				paper_id = pid.firstChild.nodeValue
			elif pid.getAttribute('pub-id-type') == 'pmid':
				paper_pmid = pid.firstChild.nodeValue
			else:
				pass
		print(paper_id)

		#extract paper title
		paper_title_temp = paper.getElementsByTagName("article-title")[0]
		paper_title = contentInGrid(paper_title_temp)
		
		temp_dc = {'_id':paper_id,'pmid':paper_pmid,'title':paper_title}
		#extract publish dates
		pub_dates = paper.getElementsByTagName("pub-date")
		for date in pub_dates:
			if date.getAttribute('pub-type') == 'ppub':
				day = date.getElementsByTagName('day')
				if day:
					day = date.getElementsByTagName('day')[0].firstChild.nodeValue
				else:
					day = '0'
				
				month = date.getElementsByTagName('month')
				if month:
					month = date.getElementsByTagName('month')[0].firstChild.nodeValue
				else:
					month = '0'
					
				year = date.getElementsByTagName('year')
				if year:
					year = date.getElementsByTagName('year')[0].firstChild.nodeValue
				else:
					year = '0'
					
				temp_dc.update({'ppub_date' : {'day':int(day),'month':int(month),'year':int(year)}})
			elif date.getAttribute('pub-type') == 'epub':
				day = date.getElementsByTagName('day')
				if day:
					day = date.getElementsByTagName('day')[0].firstChild.nodeValue
				else:
					day = 'Null'
					
				month = date.getElementsByTagName('month')[0].firstChild.nodeValue
				year = date.getElementsByTagName('year')[0].firstChild.nodeValue
				temp_dc.update({'epub_date' : {'day':int(day),'month':int(month),'year':int(year)}})
			else:
				pass
		
		#extract keyword group
		kwd_group = paper.getElementsByTagName("kwd-group")
		if kwd_group:
			kwd_list = []
			kwd_group = kwd_group[0]
			kwds = kwd_group.getElementsByTagName("kwd")
			for kwd in kwds:
				kwd_list.append(kwd.firstChild.nodeValue) 
			temp_dc.update({'keywords':kwd_list})
		# create a paper document
		# paper_dc = PMCDocument(paper_id)
		# paper_dc.addFieldName(title = paper_title) 
		# insertToMongoDB(paper_dc, 'PMCPaper')


		table_wraps = paper.getElementsByTagName("table-wrap")
		ct = 0
		tb_num = 0
		for table_wrap in table_wraps:
			# rows.append([paper_id])
			# rows.append([paper_title])
			# rows.append([])
			
			# caption of current table
			caption = table_wrap.getElementsByTagName('caption')
			if caption:
				title_children = caption[0]
				tb_num = tb_num + 1
			else:
				continue
			
			tables = table_wrap.getElementsByTagName('table')
			if tables:
				table = tables[0]
			else:
				continue
			# No. of current table
			ct = ct + 1
			print(['Table:   ',ct]) #
			
			# create a table document
			temp_dc_tb = {'_id':paper_id + '_tb' + str(ct)}
			temp_dc_tb['paper_id'] = paper_id
			
			#######################
			if PMCConn.db.PMCTableWhole.find({'_id':paper_id+'_tb'+str(ct)}).count() > 0:
				continue
			#######################
			
			
			title_text = contentInGrid(title_children)
			title_text.strip()

			# rows.append([title_text])
			temp_dc_tb['caption'] = title_text
			
			# extractTable(table, rows)
			extractTable(table, temp_dc_tb)
			
			# rows.append([])
			
			#extract table foot
			rows = []
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
							
			temp_dc_tb['table_notes'] = rows
			#save to csv file
			file_name = ''.join([paper_id, '_tb', str(ct)])
			# print(rows)
			# print(rows)
			print(res_dir + file_name)
			# saveToCSV(rows, file_name)
			table_dc = PMCDocument(temp_dc_tb)
			insertToMongoDB(table_dc, 'PMCTableWhole', PMCConn)
			# insertToMongoDB(table_dc, 'PMCTable', PMCConn)
			rows[:] = []

		temp_dc.update({'num_table':tb_num})
		paper_dc = PMCDocument(temp_dc)
		insertToMongoDB(paper_dc, 'PMCPaperWhole', PMCConn)
		# insertToMongoDB(paper_dc, 'PMCPaper', PMCConn)

PMCConn.db.PMCPaperWhole.ensure_index([('title', pymongo.TEXT)])#pymongo.ASCENDING)
PMCConn.db.PMCTableWhole.ensure_index([('caption', pymongo.TEXT)])#pymongo.ASCENDING)
PMCConn.db.PMCTableWhole.ensure_index([('header', pymongo.TEXT)])
PMCConn.db.PMCTableWhole.ensure_index([('sub_header', pymongo.TEXT)])
PMCConn.db.PMCTableWhole.ensure_index([('body', pymongo.TEXT)])

# PMCConn.db.PMCPaper.ensure_index([('title', pymongo.TEXT)])#pymongo.ASCENDING)
# PMCConn.db.PMCTable.ensure_index([('caption', pymongo.TEXT)])#pymongo.ASCENDING)
# PMCConn.db.PMCTable.ensure_index([('header', pymongo.TEXT)])
# PMCConn.db.PMCTable.ensure_index([('sub_header', pymongo.TEXT)])
# PMCConn.db.PMCTable.ensure_index([('body', pymongo.TEXT)])



	
	