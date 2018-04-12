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
    PUBLISH = "publish?"

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
    utterance_dict = {}

    def __init__(self, subscription_key, name='myApp', culture='en-us'):
        """
        Constructor method. Creates a luis app on your subscription page.

        Parameters:
        -----------
        subscription_key : string
            Mandatory parameter with the subscription key you will create the app
        name : string
            Optional parameter that tells the name of the app you want to create
        culture : string
            Optional parameter that defines which culture is your app targeting.

        Returns:
        --------
        None
        """
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
    

    def call(self, luis_endpoint, method, data='',intent_name=''):
        """
        Method responsible for calling all the API Requests on this code. The other methods calls this one.
        After this method is called, the result, http_status and reason fields of the object are changed in
        order to show how was the last call.

        Parameters:
        -----------
        luis_endpoint : string
            Mandatory parameter that will help in the decision on how to create the path to the request
        method : string
            Mandatory parameter that tells which HTTP method will be used with the call
        data : dict
            Optional parameter used to add the data, in cases of POST requests
        intent_name : string
            Optional parameter used to find which intent you're trying to make the changes
        
        Returns:
        --------
        self : object
        """
        if luis_endpoint == self.DELETE_APP:
            path = self.path[0:self.path.find('versions')]
        elif luis_endpoint == self.DELETE_INTENT and method == self.DELETE:
            path = self.path + luis_endpoint + '/' + self.intent_dict[data]
            data = ''
        elif luis_endpoint == self.PUBLISH:
            path = self.path[0:self.path.find('versions')] + '/' + luis_endpoint
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

        if luis_endpoint == self.EXAMPLES and method == self.POST:
            for json_phrase in json.loads(luis.result):
                self.utterance_dict[json_phrase['value']['UtteranceText']] = json_phrase['value']['ExampleId']

        if luis_endpoint == luis.TRAIN and method == self.POST:
            luis.status()
            while json.loads(luis.result)[0]['details']['status'] == 'InProgress':
                luis.status()
                time.sleep(2)

        return self

    def add_utterances(self, filename=UTTERANCE_FILE, utterance='', intent_name=''):
        """
        Method used to add utterances to a intent at the model. You can add the utterances by passing
        them as list or with a file. You must pass filename or utterance parameters

        Parameters:
        -----------
        filename : string
            Optional parameter that tells which is the path of the file you want to get the utterances from
        utterance : list
            Optional parameter coitaining the list of phrases you want to add to a model
        intent_name : string
            Optional parameter with the intent name you want to add the phrases

        Returns:
        --------
        self.call : object
            Use the call method in order to really do the request to API
        """
        if utterance and intent_name:
            data = []
            for phrase in utterance:
                data.append({'text': phrase, 'intentName': intent_name, 'entityLabels': []})
            data = str(data)
        else:
            with open(filename, encoding=self.UTF8) as utterance:
                data = utterance.read()
        
        return self.call(self.EXAMPLES, self.POST, data)
        
    def train(self):
        """
        Method used to train the model. You must add at least 5 utterances to each intent.

        Parameters:
        -----------
        None

        Returns:
        --------
        self.call : object
            Use the call method in order to really do the request to API
        """
        return self.call(self.TRAIN, self.POST)

    def status(self):
        """
        Method used to discover which is the status of the model training process

        Parameters:
        -----------
        None

        Returns:
        --------
        self.call : object
            Use the call method in order to really do the request to API
        """
        return self.call(self.TRAIN, self.GET)

    def write(self, filename=RESULTS_FILE):
        """
        Method used to write on a file the renponse from the last API call

        Parameters:
        -----------
        filename : string
            Used to identify the path of the file which will be written

        Returns:
        --------
        self.call : object
            Use the call method in order to really do the request to API
        """
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

    def delete_intent(self, intent_name):
        if (intent_name not in self.intent_dict):
            print('The intent ' + intent_name + ' is not registered yet')
        else:
            return self.call(self.DELETE_INTENT, self.DELETE, intent_name)

    def publish(self, versionId='0.1',region='westus'):
        data = str({'versionId':versionId, 'region': region})
        return self.call(self.PUBLISH, self.POST, data=data)
    
    def delete_utterance(self, uterrance):
        if (uterrance not in self.utterance_dict):
            print('The phrase ' + uterrance + ' is not registered yet')
        else:
            return self.call(self.EXAMPLES + '/' + str(self.utterance_dict[uterrance]), self.DELETE)


if __name__ == "__main__":

    luis = LUISApp('')
    luis.add_intent('BookFlight')
    luis.delete_intent('sdasdasdasdsad')
    exit()
    luis.add_utterances(utterance=['sdasdasdasdasd','dasdasdasdasd','dasdasdasdasdsa','dsadasdasdasd','dasdasdsadsads'], intent_name='BookFlight')
    print(luis.utterance_dict)
    luis.delete_utterance('sassaasasasassas53425')
    exit()
    luis.train()
    luis.publish()
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
        
