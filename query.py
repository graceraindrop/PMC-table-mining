#query testing command
#import os
import pprint
#os.chdir('F:\\table mining')
from PMCQuery import PMCQuery
qr = PMCQuery('PMC')
#res = qr.searchInTitle(['brain'])
# res = qr.searchInTitle(['brain', 'mirna'])
# res = qr.searchInTitle(['brain', 'mirna'],True)
#res = qr. searchInCaption(['varicella', 'mirna'])
# res = qr. searchInCaption(['varicella', 'mirna'],True)
# res = qr.searchByPubYear(2014, 'ppub')
# res = qr.searchPaperPubBefore(2013, 'epub')
# res = qr. searchInHeader(['patients'])  
# res = qr. searchInHeader(['healthy', 'controls'])
res = qr. searchInSubheader(['Low-Density'])
#res = qr.getPaperDocument('4014722')
# res = qr.getTableCol('4014722_tb2', [0,1,3])
#res = qr.getTableRow('4014722_tb2',[0,1,3])
pprint.pprint(res)
#for i in res:
	#pprint.pprint(i)


