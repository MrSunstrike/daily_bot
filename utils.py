import dateparser

def standardize_birthdate(date):
    '''Функция стандартизации даты рождения'''
    # Приводим строку к формату даты
    birthdate = dateparser.parse(date, languages=['ru', 'en'])
    if birthdate != None:
    # Приводим полученную дату к нужному формату "ДД.ММ.ГГГГ"
        return birthdate
    else:
        raise ValueError