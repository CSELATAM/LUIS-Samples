########### Python 3.6 #############
# -*- coding: utf-8 -*-

import http.client, sys, os.path, json, time

# Update the host if your LUIS subscription is not in the West US region
LUIS_HOST       = "westus.api.cognitive.microsoft.com"

# uploadFile is the file containing JSON for utterance(s) to add to the LUIS app.
# The contents of the file must be in this format described at: https://aka.ms/add-utterance-json-format
UTTERANCE_FILE   = "./utterances.json"
RESULTS_FILE     = "./utterances.results.json"

# LUIS client class for adding and training utterances
class LUISApp:
    
    # endpoint method names
    TRAIN    = "train"
    EXAMPLES = "examples"
    INTENTS  = "intents?"
    DELETE_INTENT = "intents"
    DELETE_APP = "DELETE_APP"
    PUBLISH = "pulbish?"

    # HTTP verbs
    GET  = "GET"
    POST = "POST"
    DELETE = "DELETE"
    
    # Encoding
    UTF8 = "UTF8"

    # path template for LUIS endpoint URIs
    PATH = "/luis/api/v2.0/apps/{app_id}/versions/{app_version}/"
    

    # default HTTP status information for when we haven't yet done a request
    http_status = 200
    reason = ""
    result = ""

    #intent dict in order to store the id of each intent
    intent_dict = {}

    #This is the constructor in case you want to create a application
    def __init__(self, subscription_key, name='myApp', culture='en-us'):
        data = str({'name': name, 'culture': culture})
        creation_path = '/luis/api/v2.0/apps/'
        self.key = subscription_key
        self.host = LUIS_HOST
        headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': self.key}
        conn = http.client.HTTPSConnection(self.host)
        conn.request('POST', creation_path, data.encode('UTF8'), headers)
        response = conn.getresponse()
        string_id = response.read().decode('utf-8')
        self.path = self.PATH.format(app_id=string_id, app_version='0.1').replace('"',"")
    

    # def __init__(self, host, app_id, app_version, key):
    #     if len(key) != 32:
    #         raise ValueError("LUIS subscription key not specified in " +
    #                          os.path.basename(__file__))
    #     if len(app_id) != 36:
    #         raise ValueError("LUIS application ID not specified in " +
    #                          os.path.basename(__file__))
    #     self.key = key
    #     self.host = host
    #     self.path = self.PATH.format(app_id=app_id, app_version=app_version)

    def call(self, luis_endpoint, method, data='',intent_name=''):
        if luis_endpoint == self.DELETE_APP:
            path = self.path[0:self.path.find('versions')]
        elif luis_endpoint == self.DELETE_INTENT and method == self.DELETE:
            path = self.path + luis_endpoint + '/' + self.intent_dict[data]
            data = ''
        else:
            path = self.path + luis_endpoint

        headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': self.key}
        conn = http.client.HTTPSConnection(self.host)
        conn.request(method, path, data.encode(self.UTF8) or None, headers)
        response = conn.getresponse()
        decoded = response.read().decode(self.UTF8)
        
        if intent_name and method == self.POST:
            self.intent_dict[intent_name] = decoded.replace('"',"")

        self.result = json.dumps(json.loads(decoded),
                                 indent=2)
        self.http_status = response.status
        self.reason = response.reason

        return self

    def add_utterances(self, filename=UTTERANCE_FILE):
        with open(filename, encoding=self.UTF8) as utterance:
            data = utterance.read()
        return self.call(self.EXAMPLES, self.POST, data)
        
    def train(self):
        return self.call(self.TRAIN, self.POST)

    def status(self):
        return self.call(self.TRAIN, self.GET)

    def write(self, filename=RESULTS_FILE):
        if self.result:
            with open(filename, "w", encoding=self.UTF8) as outfile:
                outfile.write(self.result)
        return self

    def print(self):
        if self.result:
            print(self.result)
        return self

    def raise_for_status(self):
        if 200 <= self.http_status < 300:
            return self
        raise http.client.HTTPException("{} {}".format(
            self.http_status, self.reason))

    def add_intent(self, intent_name):
        data = str({'name': intent_name})
        return self.call(self.INTENTS, self.POST, data, intent_name=intent_name)

    def delete_app(self):
        return self.call(self.DELETE_APP, self.DELETE)


    ############################ THIS TWO ARE TOGETHER ########################################################################
    def delete_intent(self, intent_name):
        return self.call(self.DELETE_INTENT, self.DELETE, intent_name)

    def publish_app(self):
        return self.call(self.PUBLISH, self.POST)


if __name__ == "__main__":

    luis = LUISApp('')
    luis.add_intent('BookFlight')
    luis.add_utterances().print()
    time.sleep(60)
    luis.train().print()
    time.sleep(60)
    exit()
    luis.train().print()
    luis.status().print()
    exit()

    try:
        if len(sys.argv) > 1:
            option = sys.argv[1].lower().lstrip("-")
            if option == "train":
                print("Adding utterance(s).")
                luis.add_utterances()   .write().raise_for_status()
                print("Added utterance(s). Requesting training.")
                luis.train()            .write().raise_for_status()
                print("Requested training. Requesting training status.")
                luis.status()           .write().raise_for_status()
            elif option == "status":
                print("Requesting training status.")
                luis.status().write().raise_for_status()
        else:
            print("Adding utterance(s).")
            luis.add_utterances().write().raise_for_status()
    except Exception as ex:
        luis.print()    # JSON response may have more details
        print("{0.__name__}: {1}".format(type(ex), ex))
    else:
        print("Success: results in", RESULTS_FILE)
        
