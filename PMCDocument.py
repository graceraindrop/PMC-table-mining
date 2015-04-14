class PMCDocument:
	def __init__(self, fields):
		self.id = fields['_id']
		self.dc = {}
		for key, val in fields.items():
			self.dc[key] = val
		self.collection = None
		
	def addFieldName(self,**kwarg):
		if self.collection:
			new_field = {}
			for field_name in kwarg:
				new_field[field_name] = kwarg[field_name]
			self.collection.update({'_id':self.id},{'$set':new_field})
			
		
	