
import vk_api, json, os

class VkSearchQuery():
    def __init__(self):
        
        self.fields = "nickname, bdate, sex, city, country"
        self.count  = 100
        
        self.query = {'fields':self.fields,
                      'count':self.count} 

    def setText(self, text):
        self.query['q'] = text

    def setSex(self, sex):
        self.query['sex'] = sex

    def setBirthDay(self, day):
        self.query['birth_day'] = day

    def setBirthMonth(self, month):
        self.query['birth_month'] = month

    def setBirthYear(self, year):
        self.query['birth_year'] = year

    def setAgesLimits(self, ageFrom, ageTo):
        if ageFrom:
            self.query['age_from'] = ageFrom
        if ageTo:
            self.query['age_to'] = ageTo

    def setCountry(self, countryIndex):
        self.query['country'] = countryIndex

    def setCity(self, cityIndex):
        self.query['city'] = cityIndex

    def getQuery(self):
        return self.query

class VkApiInteraction():
    def __init__(self):

        self.VK_ACCESS_DATA_FILE = 'accessData.json'

        self.login = None
        self.password = None
        self.connection = False

        self.setAuthData(login=self._getUserLogin(filename=self.VK_ACCESS_DATA_FILE))
        
        try:
            self.getConnection()
        except vk_api.exceptions.AuthError as connectException:
            print(connectException)
        except vk_api.exceptions.Captcha as connectException:
            print(connectException)

    # Function returns first key from VK_ACCESS_FILE if it exist
    def _getUserLogin(self, filename):

        try:
            with open(filename, 'r') as f:
                jsondata = json.load(f)
        except (IOError, ValueError):
            return None

        keysList = list(jsondata.keys())

        return keysList[0]

    def logOut(self):
        # End session
        self.session = None
        self.connection = False

        # Remove access data file
        try:
            os.remove(self.VK_ACCESS_DATA_FILE)
        except:
            pass

    def getConnection(self):
        self.session.auth()
        self.connection = True

        self.api = self.session.get_api()
        self.profileInfo = self.api.account.getProfileInfo()
    
    def setAuthData(self, login=None, password=None):
        self.login = login
        self.password = password

        self.session = vk_api.VkApi(login=login, password=password, config_filename=self.VK_ACCESS_DATA_FILE)

    def connectionStatus(self):
        return self.connection

    # Returns dictionary with countries {country : id}
    def getCountriesList(self):
        apiAnsver = self.api.database.getCountries()['items']
        return {item['title'] : item['id'] for item in apiAnsver}

    # Returns dictionary with cities by country id {city : id}
    def getCitiesList(self, countryId):
        apiAnsver = self.api.database.getCities(country_id=countryId)['items']
        return {item['title'] : item['id'] for item in apiAnsver}

    def getUsers(self, query):
        if self.connection:
            return self.api.users.search(**query)['items']
        
        # If user is not authorized
        return {}