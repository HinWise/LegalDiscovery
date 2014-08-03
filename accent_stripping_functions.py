
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
    s = re.sub(r'\u2022', "", s) # bullet -> nothing
    s = re.sub(r'\u2019', "'", s) # right single quotation mark -> '
    s = re.sub(r'\u2018', "'", s) # left single quotation mark -> '
    s = re.sub(r'\u25ba', "'", s) # -> black right pointing pointer
    s = re.sub(r'\u201d', "'", s) # -> right double quotation mark
    s = re.sub(r'\u201c', "'", s) # -> left double quotation mark
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if unicodedata.category(c) != 'Mn')
    return s.encode('utf-8')
    

#Note: Test in City in OcrRecord PK = 6
    
all_ocr = OcrRecord.objects.all()

count = 0

with transaction.commit_on_success():
    for item in all_ocr:
    
        print count
        print item.pk
        
        count +=1
        
        item.Document_Type = strip_accents(item.Document_Type)
        item.Amount = strip_accents(item.Amount)
        item.Currency = strip_accents(item.Currency)
        item.Company = strip_accents(item.Company)
        item.Address = strip_accents(item.Address)
        item.Telephone = strip_accents(item.Telephone)
        item.City = strip_accents(item.City)
        item.Country = strip_accents(item.Country)
        item.IssueDate = strip_accents(item.IssueDate)
        item.Day = strip_accents(item.Day)
        item.Month = strip_accents(item.Month)
        item.Year = strip_accents(item.Year)
        item.Document_Number = strip_accents(item.Document_Number)
        item.PurchaseOrder_Number = strip_accents(item.PurchaseOrder_Number)
        item.Piece_Number = strip_accents(item.Piece_Number)
        item.ContainsArabic = strip_accents(item.ContainsArabic)
        item.Page_Number = strip_accents(item.Page_Number)
        item.Notes = strip_accents(item.Notes)
        item.Translation_Notes = strip_accents(item.Translation_Notes)
        item.Source_Bank_Account = strip_accents(item.Source_Bank_Account)
        item.Cheque_Number = strip_accents(item.Cheque_Number)
        item.Sender = strip_accents(item.Sender)
        item.Receiver = strip_accents(item.Receiver)
        item.Blank = strip_accents(item.Blank)
        item.Unreadable = strip_accents(item.Unreadable)
        item.OldCompanyLine = strip_accents(item.OldCompanyLine)
        item.SecondVersionCompanyLine = strip_accents(item.SecondVersionCompanyLine)
        item.save()
        
        
        