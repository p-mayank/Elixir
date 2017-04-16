import os.path
import sys
import json
import infermedica_api
import urllib2
import wikipedia
import sys

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'b3ffc5a6079e4660a909efedef6fbfd7'
headers = {'Accept' : 'application/json', 'user_key': 'ada7140b071d43fe7ac36c260b854174', 'User-Agent': 'curl/7.35.0'}


def generateQuestions(kid, choice_id):
    infermedica_api.configure(app_id='182669ec', app_key='65fbdbdf4f285711553f6bc6d94d9e53')
    api = infermedica_api.get_api()
    #UserDetails
    request = infermedica_api.Diagnosis(sex='male', age=35)

    for k in range(len(kid)):
        request.add_symptom(kid[k], choice_id[k])
        #print(kid[k], choice_id[k])

    request = api.diagnosis(request)
    try:
        flag=request.conditions[0]["probability"]
    except:
        flag=1
        print("Elixir: This sounds critical. You may want to consult a doctor instead.")
        return



    while(flag<0.20):
        print("Elixir: "+request.question.text)
        prev_out = request.conditions[0]['name']
        #print(request.conditions)
        entities = request.question.items
        #print(entities)
        # for i in range(len(entities)):
        #     print(entities[i]["id"])
        #     print(entities[i]["name"])
        print("Elixir: "+entities[0]["name"]+"?")
        new_input = raw_input("Elixir: Enter your Choice"+"(Yes/No/Maybe/DontAsk): ")
        new_input = new_input.lower()
        if(new_input=="yes"):
            request.add_symptom(entities[0]["id"], "present")
        elif(new_input=="no"):
            request.add_symptom(entities[0]["id"], "absent")
        elif(new_input=="maybe"):
            request.add_symptom(entities[0]["id"], "unknown")
        else:
            break

        request = api.diagnosis(request)
        try:
            flag=request.conditions[0]["probability"]
        except:
            flag=1
            disease = prev_out
            print("Elixir: You may have "+disease)
            external_page = wikipedia.page(disease)
            print("Elixir: External URL(For more info): "+external_page.url)
            return


    disease = request.conditions[0]['name']
    print("Elixir: You may have "+disease)
    external_page = wikipedia.page(disease)
    print(wikipedia.summary(disease, sentences=1))
    print("Elixir: External URL(For more info): "+external_page.url)



    #req = urllib2.Request('https://api.infermedica.com/v2/triage', headers = {"App-Id": "182669ec","Content-Type": "application/json", "App-Key":"65fbdbdf4f285711553f6bc6d94d9e53"}, data='{"evidence": [{"id":'+pass_id+', "choice_id":'+pass_choice+'}]}')
    #f = urllib2.urlopen(req)
    #f=json.loads(f.read())
    #print f


def generateID(input):
    req = urllib2.Request('https://api.infermedica.com/v2/parse', headers = {"App-Id": "182669ec","Content-Type": "application/json", "App-Key":"65fbdbdf4f285711553f6bc6d94d9e53"}, data='{"text":"'+input+'"}')
    f = urllib2.urlopen(req)
    f=json.loads(f.read())
    #print f
    kid=[]
    choice_id=[]
    for i in range(len(f["mentions"])):
        kid.append(f["mentions"][i]["id"])
        choice_id.append(f["mentions"][i]["choice_id"])
        i+=1

    #Generating Responses
    generateQuestions(kid, choice_id)



def requestquery(input):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'en'
    request.query = input
    response = json.loads(request.getresponse().read().decode())
    #print(response)
    
    symptom=""
    disease=""
    try:
        symptom = response['result']['parameters']['symptom']
    except:
        pass
    try:
        disease = response['result']['parameters']['simplified']
    except:
        pass
    if(disease=="disease name" or disease=="body"):
        generateID(input)
    elif(symptom):
        generateID(input)
    else:
        try:
            if(response["result"]["parameters"]["simplified"]=="goodbye"):
                print("Elixir: Take Care.")
                sys.exit()
        except:
            print("Elixir: "+response['result']['fulfillment']['speech'])


def main():
    inputstring = raw_input("Elixir: Hey, type something: ")
    while(inputstring!='exit'):
        requestquery(inputstring)
        inputstring = raw_input("Elixir: Hey, type something: ")


if __name__ == '__main__':
    main()
