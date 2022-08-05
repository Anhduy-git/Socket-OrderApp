from socket import AF_INET, socket, SOCK_STREAM
import pickle
import json
import Constants
import os.path

class ClientFeatures:
    #client socket
    client = None
    @classmethod
    def revMenu(cls):
        try:
            # check if folder images exist, if not then create folder
            if not os.path.isdir("Resources/dish_images_received"):
                os.mkdir("Resources/dish_images_received")

            cls.client.sendall(bytes("Menu", Constants.FORMAT))
            #Get length of data received from server
            length = cls.client.recv(1024).decode(Constants.FORMAT)
            length = int(length)
            flag = True
            full_msg = b''
            new_msg = True
            counter = 1
            msglen = 0
            # Object contain data received from server
            data = None
            while counter != length + 2:
                fname = 'Resources/dish_images_received/img' + str(counter) + '.png'
                while flag:
                    msg = cls.client.recv(2048)
                    if new_msg:
                        msglen = int(msg[:Constants.HEADERSIZE])
                        new_msg = False
                    full_msg += msg

                    if len(full_msg) - Constants.HEADERSIZE == msglen:
                        if (counter == length + 1):
                            fileJson = open("Resources/menu_received.json", "wb")
                            fileJson.write(pickle.loads(full_msg[Constants.HEADERSIZE:]))
                            fileJson.close()
                            with open("Resources/menu_received.json", 'rb') as f:
                                data = json.load(f)
                            for dish in data:
                                print("{}: {} VND {}".format(dish['name'], dish['price'], dish['description']))
                            break
                        fileImage = open(fname, "wb")
                        fileImage.write(pickle.loads(full_msg[Constants.HEADERSIZE:]))
                        new_msg = True
                        full_msg = b""
                        flag = False
                        fileImage.close()
                counter += 1
                flag = True
            #return list of data
            return data
        except Exception as e:
            print("Error: ", e)
            return None


    @classmethod
    def Order(cls, tableNumber, lstDishChoosed, lstQuantity):
        try:
            numDishChoosed = len(lstDishChoosed)
            cls.client.sendall(bytes("Order", Constants.FORMAT))

            cls.client.sendall(bytes(tableNumber, Constants.FORMAT))
            checkdata = cls.client.recv(1024)

            cls.client.sendall(bytes(str(numDishChoosed), Constants.FORMAT))
            checkdata = cls.client.recv(1024)

            for i in range(numDishChoosed):
                cls.client.sendall(bytes(lstDishChoosed[i], Constants.FORMAT))
                checkdata = cls.client.recv(1024)

            for i in range(numDishChoosed):
                cls.client.sendall(bytes(str(lstQuantity[i]), Constants.FORMAT))
                checkdata = cls.client.recv(1024)

            validateTime = cls.client.recv(1024).decode(Constants.FORMAT)
            cls.client.sendall(bytes("data received", Constants.FORMAT))

            totalPrice = None
            priceToPay = None

            if validateTime =="time valid":

                #get dish list size
                numDishChoosedBefore= cls.client.recv(1024).decode(Constants.FORMAT)
                cls.client.sendall(bytes("data received", Constants.FORMAT))
                numDishChoosedBefore = int(numDishChoosedBefore)

                #Store data received from server
                lstDishChoosedTmp = []
                lstQuantityTmp = []

                #get list of dish in last order
                for i in range(numDishChoosedBefore):
                    dish = cls.client.recv(1024).decode(Constants.FORMAT)
                    lstDishChoosedTmp.append(dish)
                    cls.client.sendall(bytes("data received", Constants.FORMAT))
                # get list of quantity in last order
                for i in range(numDishChoosedBefore):
                    quantity = cls.client.recv(1024).decode(Constants.FORMAT)
                    lstQuantityTmp.append(quantity)
                    cls.client.sendall(bytes("data received", Constants.FORMAT))
                #get total price of cur order
                totalPrice = cls.client.recv(1024).decode(Constants.FORMAT)
                cls.client.sendall(bytes("data received", Constants.FORMAT))

                # get price to pay of cur order
                priceToPay = cls.client.recv(1024).decode(Constants.FORMAT)

                #check if dish exist and update
                for i in range(len(lstDishChoosedTmp)):
                    exist = False
                    for j in range(len(lstDishChoosed)):
                        if (lstDishChoosedTmp[i] == lstDishChoosed[j]):
                            exist = True
                            lstQuantity[j] = str(int(lstQuantity[j]) + int(lstQuantityTmp[i]))
                            break
                    if not exist:
                        lstDishChoosed.append(lstDishChoosedTmp[i])
                        lstQuantity.append(lstQuantityTmp[i])
            else: #invalid time
                totalPrice = cls.client.recv(1024).decode(Constants.FORMAT)
                priceToPay = totalPrice


            return totalPrice, priceToPay

        except Exception as e:
            print("Error: ", e)
            return None

    @classmethod
    def Pay(cls, tableNumber, method, account_number):
        try:
            cls.client.sendall(bytes("Pay", Constants.FORMAT))

            cls.client.sendall(bytes(tableNumber, Constants.FORMAT))
            checkdata = cls.client.recv(1024)

            cls.client.sendall(str(method).encode(Constants.FORMAT))
            checkdata = cls.client.recv(1024)
            msg = ''
            if method == "VISA":
                cls.client.sendall(str(account_number).encode(Constants.FORMAT))
                msg = cls.client.recv(1024).decode(Constants.FORMAT)
            elif method == "CASH":
                msg = cls.client.recv(1024).decode(Constants.FORMAT)
            return msg
        except Exception as e:
            print("Error: ", e)
            return None



    @classmethod
    def connectServer(cls, HOST):
        cls.client = socket(AF_INET, SOCK_STREAM)
        try:
            cls.client.connect((HOST, Constants.PORT))
            cls.client.send(bytes("Success", 'utf-8'))
            return True
        except:
            print("Warning!!!", "Connection error ")
            return False


