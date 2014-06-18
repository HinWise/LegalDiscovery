
import re, unicodedata, string

def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters)

    
def strip_accents(s): ## for alphanumeric input
    s = s.strip()
    s = re.sub(ur'\xa0', ' ', s) # non-breaking space -> space
    s = re.sub(ur'\u00b0', 'o', s,re.UNICODE) # degree -> o
    s = re.sub(ur'\u00a3', '(GBPOUNDS)', s,re.UNICODE) # £ -> (GBPOUNDS)   
    s = re.sub(ur'\x87', 'c', s,re.UNICODE) # ç -> c   
    s = re.sub(r'\x80', '(EUR)', s) # eurosymbol -> (EUR)

    s = ''.join(c for c in unicodedata.normalize('NFKD', s.decode(encoding='Windows-1252')) if unicodedata.category(c) != 'Mn')
    return s.encode('utf-8')
    

#Note: Test in City in OcrRecord PK = 6
    
all_ocr = OcrRecord.objects.all()

count = 0

with transaction.commit_on_success():
    for item in all_ocr:
    
        print count
        print item.pk
        
        count +=1
        
        item.Address = strip_accents(str(item.Address))
        item.City = strip_accents(str(item.City))
        item.Country = strip_accents(str(item.Country))
        item.Company = strip_accents(str(item.Company))
        item.Currency = strip_accents(str(item.Currency))
        
        item.save()
        
        
        