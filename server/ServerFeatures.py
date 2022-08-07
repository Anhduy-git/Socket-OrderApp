import socket
from threading import Thread
import time
import pickle
import json
import re
from datetime import datetime
import os.path


class ServerFeatures:
    HEADERSIZE = 10
    FORMAT = 'utf-8'
    SERVER = None
    PORT = 5656
    @classmethod
    def Menu(cls, client):
        try:
            counter = 1
            fileJson = open("Resources/data.json", "rb")

            length = len(json.load(fileJson))

            client.sendall(bytes(str(length), cls.FORMAT))
            while counter != length + 1:
                fname = 'Resources/dish_images/img' + str(counter) + '.png'
                img = open(fname, "rb")
                dataImage = img.read()
                msg = pickle.dumps(dataImage)
                msg = bytes(f"{len(msg):<{cls.HEADERSIZE}}", cls.FORMAT) + msg
                client.sendall(msg)
                counter += 1
                time.sleep(0.1)
                img.close()

            fileJson = open("Resources/data.json", "rb")
            data = fileJson.read()
            msg = pickle.dumps(data)
            msg = bytes(f"{len(msg):<{cls.HEADERSIZE}}", cls.FORMAT) + msg
            client.sendall(msg)
            fileJson.close()
        except Exception as e:
            print("Error: ", e)
    @classmethod
    def getPrice(cls, dishName):
        try:
            jsonFile = open("Resources/data.json", "rb")
            lstDishData = json.load(jsonFile)  # get data from json file as list of dict
            # get price
            for data in lstDishData:
                if data["name"] == dishName:
                    return int(data["price"])
            return 0
        except Exception as e:
            print("Error: ", e)

    @classmethod
    def checkTimeValid(cls, strOrderTime):
        fmt = '%Y-%m-%d %H:%M:%S'
        orderTime = datetime.strptime(strOrderTime, fmt)
        currentTime = datetime.now()
        td = currentTime - orderTime
        dif_hours = int(round(td.total_seconds() / 3600))
        print('Dif hours: ', dif_hours)
        return dif_hours <= 2

    @classmethod
    def checkIfDishExistAndUpdate(cls, lstDictDishInOrder, lstDishChoosed, lstQuantity):
        for i in range(len(lstDishChoosed)):
            exist = False
            for dish in lstDictDishInOrder:
                if (dish["name"] == lstDishChoosed[i]):
                    dish["quantity"] += lstQuantity[i]
                    exist = True
                    break
            if not exist:
                newDish = dict(name=lstDishChoosed[i], price=cls.getPrice(lstDishChoosed[i]), quantity=lstQuantity[i])
                lstDictDishInOrder.append(newDish)



    @classmethod
    def Order(cls, client):
        try:
            # Get table number
            tableNumber = client.recv(1024).decode(cls.FORMAT)
            client.sendall(bytes("data received", cls.FORMAT))

            # Get number of dish in order
            numDishChoosed = client.recv(1024).decode(cls.FORMAT)
            client.sendall(bytes("data received", cls.FORMAT))

            numDishChoosed = int(numDishChoosed)
            lstDishChoosed = []
            lstQuantity = []


            for i in range(numDishChoosed):
                dish = client.recv(1024).decode(cls.FORMAT)
                lstDishChoosed.append(dish)
                client.sendall(bytes("data received", cls.FORMAT))

            for i in range(numDishChoosed):
                num = int(client.recv(1024).decode(cls.FORMAT))
                lstQuantity.append(num)
                client.sendall(bytes("data received", cls.FORMAT))

            # calcul price of current order
            curOrderPrice = 0
            for i in range(numDishChoosed):
                curOrderPrice += cls.getPrice(lstDishChoosed[i]) * lstQuantity[i]

            #check if order file exists
            fileName = "OrderDatabase/" + tableNumber + ".json"
            data = None
            if os.path.exists(fileName):
                jsonFile = open(fileName, "r")
                data = json.load(jsonFile)
            else:
                data = dict(orders=list())


            # number of order of client
            size = len(data["orders"])

            # check if last order is less than 2h ?
            if size > 0 and cls.checkTimeValid(data["orders"][size-1]["time"]):

                client.sendall(bytes("time valid", cls.FORMAT))
                checkdata = client.recv(1024)

                lastOrderSize = len(data["orders"][size - 1]["dishes"])

                #send number of dish of last order to client
                client.sendall(bytes(str(lastOrderSize), cls.FORMAT))
                checkdata = client.recv(1024)

                #send dish name of last order
                for i in range(lastOrderSize):
                    dishName = data["orders"][size - 1]["dishes"][i]["name"]
                    client.sendall(bytes(dishName, cls.FORMAT))
                    checkdata = client.recv(1024)

                # send quantity of last order
                for i in range(lastOrderSize):
                    dishQuantity = data["orders"][size - 1]["dishes"][i]["quantity"]
                    client.sendall(bytes(str(dishQuantity), cls.FORMAT))
                    checkdata = client.recv(1024)


                # send total Price of current order to client
                totalPrice = data["orders"][size - 1]["totalPrice"] + curOrderPrice
                client.sendall(bytes(str(totalPrice), cls.FORMAT))
                checkdata = client.recv(1024)

                # the price client have to pay (may include last order if client not pay yet)
                priceToPay = data["orders"][size - 1]["priceToPay"] + curOrderPrice

                #send price to pay to client
                client.sendall(bytes(str(priceToPay), cls.FORMAT))

                #update database
                cls.checkIfDishExistAndUpdate(data["orders"][size - 1]["dishes"], lstDishChoosed, lstQuantity)
                data["orders"][size - 1]["totalPrice"] = totalPrice
                data["orders"][size - 1]["priceToPay"] = priceToPay
                #if client order more, then they have to pay more, so update status to false again
                data["orders"][size - 1]["status"] = False

                #check if folder order database exist, if not then create folder
                if not os.path.isdir("OrderDatabase"):
                    os.mkdir("OrderDatabase")

                # store data to file json
                with open("OrderDatabase/" + tableNumber + ".json", "w") as f:
                    json.dump(data, f, indent=2)

            else:
                # get time
                dt = datetime.now()
                currentTime = dt.strftime('%Y-%m-%d %H:%M:%S')

                client.sendall(bytes("time invalid", cls.FORMAT))
                checkdata = client.recv(1024)

                # send total price to client
                client.sendall(bytes(str(curOrderPrice), cls.FORMAT))

                # update database
                data["orders"].append(dict(status=False, dishes=list(), time=currentTime, totalPrice=curOrderPrice, priceToPay=curOrderPrice))
                for i in range(numDishChoosed):
                    dish = dict(name=lstDishChoosed[i], price=cls.getPrice(lstDishChoosed[i]), quantity=lstQuantity[i])
                    data["orders"][size]["dishes"].append(dish)

                # check if folder order database exist, if not then create folder
                if not os.path.isdir("OrderDatabase"):
                    os.mkdir("OrderDatabase")

                # store data to file json
                with open("OrderDatabase/" + tableNumber + ".json", "w") as f:
                    json.dump(data, f, indent=2)



        except Exception as e:
            print("Error: ", e)


    @classmethod
    def checkString(cls, str):
        pattern = re.compile("[0-9]+")
        if ((pattern.fullmatch(str) is None) or (len(str) < 10)):
            return False
        return True

    @classmethod
    def Pay(cls, client):
        try:
            # Get table number
            tableNumber = client.recv(1024).decode(cls.FORMAT)
            client.sendall(bytes("data received", cls.FORMAT))

            # get method send from client
            method = client.recv(1024).decode(cls.FORMAT)
            client.sendall(bytes("data received", cls.FORMAT))

            method = str(method)

            if method == "VISA":
                account_number = client.recv(1024).decode(cls.FORMAT)
                print("Account: ", account_number)
                # if found match (entire string matches pattern)
                if cls.checkString(account_number) is True:
                    client.sendall(bytes("Success", cls.FORMAT))

                    with open('OrderDatabase/' + tableNumber + ".json") as f:
                        data = json.load(f)
                    orderSize = len(data['orders'])
                    #update order status to paid
                    data['orders'][orderSize - 1]['status'] = True
                    #update price to pay
                    data['orders'][orderSize - 1]['priceToPay'] = 0
                    with open('OrderDatabase/' + tableNumber + ".json", "w") as f:
                        json.dump(data, f, indent=2)
                else:
                    # if not found match
                    client.sendall(bytes("Failed", cls.FORMAT))
                    # Pay(client)
            elif method == "CASH":
                client.sendall(bytes("Success", cls.FORMAT))
                with open('OrderDatabase/' + tableNumber + ".json") as f:
                    data = json.load(f)
                orderSize = len(data['orders'])
                # update order status to paid
                data['orders'][orderSize - 1]['status'] = True
                # update price to pay
                data['orders'][orderSize - 1]['priceToPay'] = 0
                with open('OrderDatabase/' + tableNumber + ".json", "w") as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            print("Error: ", e)

    # Receive request from client
    @classmethod
    def readRequest(cls, client):
        request = ""
        try:
            request = client.recv(1024).decode(cls.FORMAT)
        finally:
            return request

    # Choose option from request
    @classmethod
    def takeRequest(cls, client):
        while True:
            Request = cls.readRequest(client)
            if Request is None or Request == "":
                client.close()
                break
            print("Request from client: ", Request)
            # take a picture
            if "Menu" == Request:
                cls.Menu(client)
            if "Order" == Request:
                cls.Order(client)
            if "Pay" == Request:
                cls.Pay(client)
    @classmethod
    def Serveur(cls):
        try:
            cls.SERVER.listen()
            ACCEPT_THREAD = Thread(target=cls.waitingConnection)
            ACCEPT_THREAD.start()
            ACCEPT_THREAD.join()
        except:
            print("ERROR!")
        finally:
            cls.SERVER.close()

    # wait to connect for client
    @classmethod
    def waitingConnection(cls):

        print("Waiting for Client")

        while True:
            client, Address = cls.SERVER.accept()
            print("Client ", Address, " connected!")
            Thread(target=cls.takeRequest, args=(client,)).start()
    @classmethod
    def startServer(cls):
        print("Server IP Address Now ", (socket.gethostbyname(socket.gethostname())))
        cls.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.SERVER.bind((socket.gethostbyname(socket.gethostname()), cls.PORT))
        cls.Serveur()


#https://www.analyticssteps.com/blogs/working-python-json-object
#https://helpex.vn/question/cach-kiem-tra-xem-mot-chuoi-chi-chua-cac-ky-tu-az-az-va-0-9-trung-lap-60bea05ed24b80926dc0594d