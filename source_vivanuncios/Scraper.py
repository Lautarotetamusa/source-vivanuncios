from . import functions
import requests
import json

site = "https://www.vivanuncios.com.mx"


#Recibe a raw html page source and return the list of ads data
#Return a json in the dom page with the util information
def get_data(html):

    #Html page source matching for the json
    init = "</noscript><script>(function(){var w=window;w.$components=(w.$components||[]).concat("
    end  = ")||w.$components})()</script></body></html>"

    #Get the json from the html source
    try:

        #with open("rawjson.json", "w") as f:
        #    json.dump(json.loads(html.split(init)[1].split(end)[0]), f, indent=4)
        #exit()

        return json.loads(html.split(init)[1].split(end)[0])["o"]["w"][0][3]["s"]
    except Exception as e:
        print("Error loading the json, the matching is wrong")
        return []

#example with s-renta-inmuebles/distrito-federal/v1c1098l1008p1?pr=,30000&ba=20
#get v1c1098l1008p1 and replace p1 por p{}, de esta manera podemos pasar entre paginass
def format_url(url):

    params = url.split('/')[-1]
    if "?" in url:
        pagename = params.split('?')[0]
    else:
        pagename = params

    pageformat = pagename.replace("p1", "p{}")

    return url.replace(pagename, pageformat)

#Get the data of all properties in a search
#Send messages to all properties
def get_properties(url):

    #firsturl = url
    url = format_url(url)

    page = 1
    products = []
    ads = []
    firstpage = True

    while len(ads) > 0 or firstpage:

        #Get the html page source
        while True:
            res = requests.get(url.format(page))
            print(res.status_code)
            if res.status_code == 200:
                break

        #Scrape the util information for de ads in this same zone
        #The other zone ads is not necesary
        data = get_data(res.text)

        #La url que devuelve la pagina
        currenturl = site + data["searchParams"]["url"]

        #print(currenturl)
        #print(firsturl)

        #Si volvimos a empezar por la primer pagina
        if not "/page-" in currenturl and not firstpage:
            break

        ads = data["adsToPlot"]
        for ad in ads:

            #This keys are equal to new and common properties
            product = {
                "title": ad["title"],
                "price": ad["price"]["formattedAmount"] + " " + ad["price"]["currency"],
                "url":   ad["viewSeoUrl"],
            }

            #If is not a new or presales properties
            if not "badge" in ad:
                product["zone"] = ad["geo"]["name"]
                product["adid"] = ad["adId"]

                #bathrooms, parkings, area, Phone, etc
                for attr in ad["adAttributes"]:
                    product[attr["name"]] = attr["value"]["attributeValue"]
            else:
                #This are the first properties appers in the page
                #Are the new and presale properties
                #The json keys are different

                print("presale property")

                areas = [str(i) for i in ad["unitAreaAvailable"]] if "unitAreaAvailable" in ad else []

                product.update({
                    "adid":  ad["referenceAdId"],
                    "zone":  ad["geo"]["geoName"],
                    "agency":ad["agency"],
                    "area":  " - ".join(areas),
                    "bedrooms":  ad["bedroomAvailable"][0]  if ad["bedroomAvailable"]  != [] else "",
                    "bathrooms": ad["bathroomAvailable"][0] if ad["bathroomAvailable"] != [] else "",
                    "parkings":  ad["parkingAvailable"][0]  if ad["parkingAvailable"]  != [] else ""
                })

            products.append(product)

        print("Page nro: ", page, "properties:", len(ads))
        firstpage = False
        page += 1

    #return products
    print("Total of ", len(products), "ads in the search")
    return list({v['adid']:v for v in products}.values()) #Remove the duplicated items

#payload con la data del que envia
#cookies que las sacamos de res.cookies.get_dict
#un header con {csrf-token: token}; que lo saccamos de la etiqueta <meta name="csrf-token" content="TOKEN">
def send_messages(properties, senders, variables, msg):

    #Set the payload
    send_url = "https://www.vivanuncios.com.mx/api/items/reply?noredirect="
    set_payload_url = "https://www.vivanuncios.com.mx/s-venta-terrenos/"

    res = requests.get(set_payload_url)

    cookies = res.cookies.get_dict()
    csfr = res.text.split('<meta name="csrf-token" content="')[1].split('"')[0]

    headers = {"csrf-token": csfr}
    #
    #send the messages

    senders_i = 0
    for property in properties:
        sender = senders[senders_i % len(senders)] #Rotate sender for each property

        format_msg = functions.format_message(msg, property, variables)

        data = {
        	"adId": property["adid"],
        	"buyerName": sender["name"],
        	"email": sender["email"],
        	"phoneNumber": sender["phone"],
        	"replyMessage": format_msg
        }

        res = requests.post(send_url, data=data, cookies=cookies, headers=headers)

        print("Send message to: ", property["adid"])
        print(format_msg)
        print()

        senders_i += 1


if __name__ == '__main__':
    import time

    #test_url = "https://www.vivanuncios.com.mx/s-renta-inmuebles/alvaro-obregon/v1c1098l10265p1?pr=,30000&ba=20&be=3"
    #841
    #258 anuncios en la zona

    #test_url = "https://www.vivanuncios.com.mx/s-renta-inmuebles/distrito-federal/v1c1098l1008p1?pr=,30000&ba=20&be=3"
    #2063 totales
    #anuncios en la zona: 307
    #no proxy

    test_url = "https://www.vivanuncios.com.mx/s-renta-inmuebles/distrito-federal/v1c1098l1008p1?pr=,30000&ba=20"
    #4941 totales
    #anuncios en la zona: 314
    #no proxy

    #test_url = "https://www.vivanuncios.com.mx/s-renta-inmuebles/distrito-federal/v1c1098l1008p1?pr=,30000"
    #8135 totales
    #anuncios en la zona: 320
    #no proxy


    #test_url = "https://www.vivanuncios.com.mx/s-renta-inmuebles/distrito-federal/privada/v1c1098l1008a1dgp1?pr=,30000"
    #test_url = "https://www.vivanuncios.com.mx/s-renta-inmuebles/distrito-federal/page-50/v1c1098l1008p55?pr=,30000"

    msg = "Hola {que tal como estás?|como te va?}, {vi tu publicación|estaba viendo una publicación tuya} [titulo] con precio de [precio], {vi que está en la zona|y me di cuenta que estaba en la zona} [zona], {quiero hacerte una propuesta y quiero más información| tengo unas dudas y quiero preguntarte unas cosas| tengo unas dudas y me gustaría pregunta unos puntos importantes} te dejo mi sitio web [sitio] y la referencia [referencia] para seguir en contacto, este mes en temas legales de escrituración te propongo hacerlo con un descuento para agilizar la operación. Gracias, te paso mi whatsapp por si tienes dudas: [telefono]"

    #Scrape the data
    start_time = time.time()
    props = get_properties(test_url)

    print(len(props), "Properties extracted in ", time.time()-start_time, " seconds")
    #print("Total api calls: ",  api_requests.api_calls)
    #print("Succes api calls: ", api_requests.succes_api_calls)
    #print("Succes percent: ",   api_requests.succes_api_calls / api_requests.api_calls * 100)

    with open("properties.json", "w") as f:
        json.dump(props, f, indent=4)

    #Send the messages
    variables = {
        "phone": "+54934159592",
        "site": "holaoficial.ml",
        "reference": "lautaro@gmail.com"
    }

    print("Start to send messages")
    senders = functions.read_senders()
    send_messages(props, senders, variables, msg)
    print("All messages has been sended")
