class WeatherAPI:
    data = None

    def fetch(self):
        #fetcher data fra apier

        data = None # data fra apier

        self.validate(data)

    def validate(self, data):
        # validerer data

        validatedData = data

        self.data = validatedData

    def getWeekView(self):
        if(self.data == None):
            self.fetch()

    def getMonthView(self):
        if(self.data == None):
            self.fetch()

