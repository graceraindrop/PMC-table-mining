from PMCMongoDB import PMCConnection
import re
import pprint

def termsToPatterns(terms):
	# delimiter is space
	# pattern_temp = terms.split()
	# patterns = [re.compile('.*' + t + '.*') for t in pattern_temp]
	patterns = [re.compile('.*' + t + '.*', re.IGNORECASE) for t in terms]
	return patterns
	# return terms
	
def printExtractedContent(rows):
	for row in rows:
		print(row)

def printQueryResult(res):
	for cursor in res:
		print(cursor)
		
class PMCQuery:
	def __init__(self, database_name):
		#connect to database
		self.connection = PMCConnection(database_name)
		self.paper_collection = self.connection.db.PMCPaperWhole
		self.table_collection = self.connection.db.PMCTableWhole
		#self.paper_collection = self.connection.db.PMCPaper
		#self.table_collection = self.connection.db.PMCTable
		
		self.query = ''
		self.SEARCH_IN_TITLE = 1
		self.SEARCH_IN_CAPTION = 2
		self.SEARCH_IN_BOTH = 3
		self.return_note = False
	
	def setNoteParameter(self, flag):
		self.return_note = flag
			
		
	def getPaperDocument(self, ID):
		p = self.paper_collection.find({'_id':ID})
		return p

	def getTableByID(self, ID):
                t = self.table_collection.find({'_id':ID})
                return t
	
	def getTableCol(self, TableID, col_nums):
		flag = isinstance(col_nums,list)
		papers = self.table_collection.find({'_id':TableID})
		res = []
		if not flag:
			col_nums = [col_nums]
		for p in papers:
			temp = []
			for col in col_nums:
				#header
				h = p['header']
				temp.append(h[col])
			res.append(temp)
			
			#subheader
			sh = p['sub_header']
			for sh_row in sh:
				temp = []
				for col in col_nums:
					temp.append(sh_row[col])
				res.append(temp)
				
			#body
			b = p['body']
			for b_row in b:
				temp = []
				for col in col_nums:
					temp.append(b_row[col])
				res.append(temp)
		return res
	
	def getTableRow(self, TableID, row_nums):
		flag = isinstance(row_nums, list)
		papers = self.table_collection.find({'_id':TableID})
		res = []
		if not flag:
			row_nums = [row_nums]
		for p in papers:
			temp = []
			bd = p['body']
			for row in row_nums:
				temp.append(bd[row])
			res.append(temp)
		return res
	
	def searchInTitle(self, terms, contain_all_kywd = None):  #search terms in paper title(mode=1), table caption(mode=2) or both(mode = 3)
		if contain_all_kywd is None:
			contain_all_kywd = False
		patterns = termsToPatterns(terms) 
		if contain_all_kywd:
			res = self.paper_collection.find({'title':{'$all':patterns}})
		else:
			res = self.paper_collection.find({'title':{'$in':patterns}})
		self.res_p = []
		for r in res:
			self.res_p.append(r)
		return self.res_p
	
	
	def generateAndPattern(self, field_name, patterns):
		new_patterns = []
		for p in patterns:
			new_patterns.append({field_name:{'$in':[p]}})
		return new_patterns
	
	def searchInCaption(self,terms, contain_all_kywd = None):
		if contain_all_kywd is None:
			contain_all_kywd = False
		patterns = termsToPatterns(terms) 
		if contain_all_kywd:
			res = self.table_collection.find({'caption':{'$all':patterns}})
		else:
			res = self.table_collection.find({'caption':{'$in':patterns}})
		if not self.return_note:
			self.res_t=[]
			for r in res:	
				r.pop('table_notes',None)
				self.res_t.append(r)
		else:
			self.res_t= res
		return self.res_t
		
	def searchInKeywords(self,terms, contain_all_kywd = None):
		if contain_all_kywd is None:
			contain_all_kywd = False
		patterns = termsToPatterns(terms) 
		if contain_all_kywd:
			self.res_t = self.paper_collection.find({'keywords':{'$all':patterns}})
		else:
			self.res_t = self.paper_collection.find({'keywords':{'$in':patterns}})
		# print('Paper list:')
		# printQueryResult(self.res_t)
		return self.res_t
			
	def findHeaderName(self, rowh, col_num):
		if rowh[col_num] == '' and col_num == 0:
			return ''
		elif rowh[col_num] == '':
			return self.findHeaderName(rowh,col_num-1)
		else:
			return rowh[col_num]
	
	def searchInHeader(self, terms, contain_all_kywd = None):
		if contain_all_kywd is None:
			contain_all_kywd = False
		patterns = termsToPatterns(terms)
		if contain_all_kywd:
			res = self.table_collection.find({'header':{'$all':patterns}})
		else:
			res = self.table_collection.find({'header':{'$in':patterns}})
		result = []
		#extract columns and print
		for tb in res:
			print(tb['_id'])
			extracted_header_index = [i for i, h in enumerate(tb['header']) for t in terms if t in h]
			extracted_header_index = list(set(extracted_header_index))
			extracted_header_index.sort()
			# extracted_header_index = list(set(extracted_header_index))  #make list elements unique
			# extracted_header_index.sort()
			inds = []
			for ind in extracted_header_index:
				inds.extend(list(range(ind,tb['header_colspan'][ind]+ind)))
			# print('inds: ', inds)
			# for each row in table(including header sub-header)
			extracted_cols = {}
			temp_row = [tb['header'][i] for i in inds]
			extracted_cols['header'] = temp_row

			if len(tb['sub_header']) != 0:
				first_ele = []
				for sh in tb['sub_header']:
					temp_row = [sh[i] for i in inds]
					first_ele.append(temp_row)
				extracted_cols['sub_hearder'] = first_ele
			first_ele = []
			for bd in tb['body']:
				temp_row = [bd[i] for i in inds]
				first_ele.append(temp_row)
				extracted_cols['body'] = first_ele
			# printExtractedContent(extracted_cols)
			result.append(extracted_cols)
			#print tb
		return result
		
	def searchInSubheader(self, terms, contain_all_kywd = None):
		if contain_all_kywd is None:
			contain_all_kywd = False
		patterns = termsToPatterns(terms)
		result = []
		if contain_all_kywd:
			res = self.table_collection.find({'sub_header':{'$elemMatch':{'$elemMatch':{'$all':patterns}}}})
		else:
			res = self.table_collection.find({'sub_header':{'$elemMatch':{'$elemMatch':{'$in':patterns}}}})
		#for ress in res:
			#print(ress['_id'])
		for tb in res:
			extracted_cols = {}
			extracted_header_index = [(i,j) for i,subh_row in enumerate(tb['sub_header']) for j,subh in enumerate(subh_row) for t in terms if t in subh]
			
			# go through header and sub header
			# header
			temp = [self.findHeaderName(tb['header'],j) for i,j in extracted_header_index]
			extracted_cols['header'] = temp
			# sub-header
			if len(tb['sub_header']) != 0:
				temp = []
				for subr in tb['sub_header']:
					temp.append([self.findHeaderName(subr,j) for i,j in extracted_header_index])
					extracted_cols['sub_header'] = temp
			
			# body
			temp = []
			for bd in tb['body']:
				temp.append([bd[j] for i,j in extracted_header_index])
				extracted_cols['body'] = temp
			# pprint.pprint(extracted_cols)
			# printExtractedContent(extracted_cols)
			result.append(extracted_cols)
		return result
	
	def searchByPubYear(self,year, pub_type):
		if pub_type.lower().startswith('p'):
			res = self.paper_collection.find({'ppub_date.year':int(year)})
			# print('Paper list:')
			# printQueryResult(self.res_p)
			# return self.res_p
		elif pub_type.lower().startswith('e'):
			res = self.paper_collection.find({'epub_date.year':int(year)})
			# print('Paper list:')
			# printQueryResult(self.res_p)
			# return self.res_p
		else:
			print('publish type should be either ppub or epub')
			return None
		self.res_p = []
		for r in res:
			self.res_p.append(r)
		return self.res_p
		
	def searchPaperPubBefore(self,year, pub_type):
		if pub_type.lower().startswith('p'):
			res = self.paper_collection.find({'ppub_date.year':{'$lte':int(year)}})
			# print('Paper list:')
			# printQueryResult(self.res_p)
			# return self.res_p
		elif pub_type.lower().startswith('e'):
			res = self.paper_collection.find({'epub_date.year':{'$lte':int(year)}})
			# print('Paper list:')
			# printQueryResult(self.res_p)
			# return self.res_p
		else:
			print('publish type should be either ppub or epub')
			return None
		self.res_p = []
		for r in res:
			self.res_p.append(r)
		return self.res_p
	
	def searchInBody(self,terms,tbs):
		for tb in tbs:
			grids = [(i,j) for i,lst in enumerate(tb.body) for j,ele in enumerate(lst) for t in terms if t in ele]
			
			# print extracted table
	
	
	def searchByColRow(self,**kwarg):
		if 'col' in kwarg:
			col = kwarg['col']
		else:
			col = None
			
		if 'row' in kwarg:
			row = kwarg['row']
		else:
			row = None
		
		if col and row:
			pass
		elif col:
			pass
		elif row:
			pass
		else:
			pass
		
