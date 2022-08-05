import tkinter as tk

from ClientFeatures import ClientFeatures
import Constants
from PIL import ImageTk, Image


class HomePage:
    def __init__(self, root):
        self.root = root
        self.txtClickBtn = None
        self.menuBtn = None
        self.frame = None
        self.logo = None
        self.inputIPBox = None
        self.txtServerIP = None
        self.inputTableNumberBox = None
        self.txtTableNumber = None
        self.tableNumber = ''

    def onMenuButtonPressed(self):
        for widgets in self.frame.winfo_children():
            widgets.destroy()
        Utils.setTableNumber('Table_' + self.tableNumber)
        self.root.title("Menu Page")
        MenuPage(self.root).onCreate()

    def onConnectButtonPressed(self):
        serverIP = self.inputIPBox.get("1.0", 'end-1c')
        self.tableNumber = self.inputTableNumberBox.get("1.0", 'end-1c')
        if ClientFeatures.connectServer(serverIP) and self.tableNumber.strip() != '':
            # enable button
            self.menuBtn["state"] = "normal"
            # pop up a window succcess
            Utils.successMessage(Constants.txtConnectSuccess, self.root)
        else:
            # pop up a window failed
            errorMessage = Constants.txtConnectFailed
            if self.tableNumber.strip() == '':
                errorMessage = Constants.txtEnterName
            Utils.errorMessage(errorMessage, self.root)

    def onCreate(self):
        # init frame
        self.frame = tk.Frame(self.root, bg=Constants.bgColor)
        self.frame.place(relwidth=1, relheight=1)

        # text table number
        self.txtTableNumber = tk.Label(self.frame, text=Constants.txtTableNumber, font=Constants.mainFont)
        self.txtTableNumber.config(bg=Constants.bgColor)
        self.txtTableNumber.place(relx=0.25, rely=0.4)

        # input table number text box
        self.inputTableNumberBox = tk.Text(self.frame)
        self.inputTableNumberBox.place(relx=0.42, rely=0.4, width=250, height=30)

        # text server IP
        self.txtServerIP = tk.Label(self.frame, text=Constants.txtServerIP, font=Constants.mainFont)
        self.txtServerIP.config(bg=Constants.bgColor)
        self.txtServerIP.place(relx=0.25, rely=0.5)

        # input IP text box
        self.inputIPBox = tk.Text(self.frame)
        self.inputIPBox.place(relx=0.37, rely=0.5, width=250, height=30)

        # button connect server
        txtConnectServerBtn = tk.StringVar()
        self.connectServerBtn = tk.Button(self.frame, textvariable=txtConnectServerBtn, font=Constants.mainFont,
                                          bg="#20bebe", fg="white",
                                          height=1, width=10)
        self.connectServerBtn.place(relx=0.7, rely=0.5)
        self.connectServerBtn.config(command=lambda: self.onConnectButtonPressed())
        txtConnectServerBtn.set(Constants.txtConnect)

        # text click menu
        self.txtClickBtn = tk.Label(self.frame, text=Constants.txtLetSeeMenu, font=Constants.mainFont)
        self.txtClickBtn.config(bg=Constants.bgColor)
        self.txtClickBtn.place(relx=0.4, rely=0.8)

        # button click menu
        txtMenuBtn = tk.StringVar()
        self.menuBtn = tk.Button(self.frame, textvariable=txtMenuBtn, font=Constants.mainFont, bg="#20bebe", fg="white",
                                 height=2, width=15)
        self.menuBtn.place(relx=0.4, rely=0.65)
        self.menuBtn.config(command=lambda: self.onMenuButtonPressed())
        txtMenuBtn.set(Constants.txtMenu)
        self.menuBtn["state"] = "disabled"

        # logo
        img = Image.open(Constants.logo)
        resized_img = img.resize(Constants.imgLogoSize, Image.ANTIALIAS)
        new_img = ImageTk.PhotoImage(resized_img)

        self.logo = tk.Label(self.frame, image=new_img)
        self.logo.photo = new_img
        self.logo.place(relwidth=0.3, relheight=0.3, relx=0.35, rely=0.05)


class MenuPage:
    def __init__(self, root):
        self.root = root
        self.frame = None
        self.lstMenu = None
        self.backBtn = None
        self.backBtnPhoto = None
        self.txtMenu = None
        self.infoFrame = None
        self.txtChoosedList = None
        self.lstChoosed = None
        self.addBtn = None
        self.delBtn = None
        self.inputBox = None
        self.orderBtn = None
        self.menuListData = None
        self.quantityList = []
        self.menuListDataChoosed = []

    def onQuitBtnClick(self):
        for widgets in self.frame.winfo_children():
            widgets.destroy()
        self.root.title("Home Page")
        HomePage(self.root).onCreate()

    def onAddBtnClick(self):
        dish = self.lstMenu.get(tk.ACTIVE)
        quantity = self.inputBox.get(1.0, "end-1c")
        if (quantity == None or quantity == ''):
            quantity = '1'
        dishIsChoosed = False
        for i in range(len(self.menuListDataChoosed)):
            # if dish is choosed, then update quantity
            if self.menuListDataChoosed[i] == dish:
                dishIsChoosed = True
                self.lstChoosed.delete(i)
                self.quantityList[i] = str(int(quantity) + int(self.quantityList[i]))
                self.lstChoosed.insert(i, dish + " X " + self.quantityList[i])
        if not dishIsChoosed:
            self.lstChoosed.insert(tk.END, dish + " X " + quantity)
            self.quantityList.append(quantity)
            self.menuListDataChoosed.append(dish)


    def onDelBtnClick(self):
        dish = self.lstChoosed.get(tk.ACTIVE)
        idx = self.lstChoosed.get(0, tk.END).index(dish)
        self.lstChoosed.delete(idx)
        self.menuListDataChoosed.pop(idx)
        self.quantityList.pop(idx)


    def onOrderBtnClick(self):

        # get total price from server
        if self.menuListDataChoosed is None or len(self.menuListDataChoosed) == 0:
            Utils.errorMessage(Constants.txtAddSomeDishError, self.root)
        else:
            totalPrice, priceToPay = ClientFeatures.Order(Utils.getTableNumber(), self.menuListDataChoosed,
                                                          self.quantityList)
            if totalPrice is None:  # if error occurrs when get total price from server
                Utils.errorMessage(Constants.txtGetPriceError, self.root)
            else:
                self.root.title("Payment")
                for widgets in self.frame.winfo_children():
                    widgets.destroy()
                PaymentPage(self.root, totalPrice, priceToPay, self.menuListDataChoosed, self.quantityList).onCreate()

    def onItemClick(self, evt):
        w = evt.widget
        try:
            pos = int(w.curselection()[0])
        except IndexError:
            return
        # set image info

        if self.menuListData != None:
            img = Image.open("Resources/dish_images_received/img" + str(pos + 1) + ".png")
            resized_img = img.resize(Constants.imgItemMenuSize, Image.ANTIALIAS)
            new_img = ImageTk.PhotoImage(resized_img)
            label = tk.Label(self.frame, image=new_img)
            label.photo = new_img
            label.place(relwidth=0.3, relheight=0.4, relx=0.4, rely=0.2)

            # set detail info
            self.txtName.config(text=Constants.txtName + " " + self.menuListData[pos]["name"])
            self.txtPrice.config(text=Constants.txtPrice + " " + self.menuListData[pos]["price"])
            self.txtDes.config(text=Constants.txtDes + " " + self.menuListData[pos]["description"])

    def onCreate(self):


        # init frame
        self.frame = tk.Frame(self.frame, bg=Constants.bgColor)
        self.frame.place(relwidth=1, relheight=1)

        # List menu
        self.txtMenu = tk.Label(self.frame, text=Constants.txtMenu, font=Constants.mainFont)
        self.txtMenu.config(bg=Constants.bgColor)
        self.txtMenu.place(relx=0.08, rely=0.13)
        self.lstMenu = tk.Listbox(self.frame)

        self.lstMenu.place(relwidth=0.18, relheight=0.3, relx=0.06, rely=0.2)
        self.lstMenu.bind('<<ListboxSelect>>', self.onItemClick)

        #get menu from server
        self.menuListData = ClientFeatures.revMenu()
        if self.menuListData is not None:
            self.lstMenu.delete(0, 'end')
            for item in self.menuListData:
                self.lstMenu.insert("end", item["name"])

        # order button
        txtOrderBtn = tk.StringVar()
        self.orderBtn = tk.Button(self.frame, textvariable=txtOrderBtn, font=Constants.mainFont, bg="#20bebe",
                                  fg="white",
                                  height=2, width=10)
        self.orderBtn.place(relx=0.6, rely=0.7)
        self.orderBtn.config(command=lambda: self.onOrderBtnClick())
        txtOrderBtn.set(Constants.txtOrder)

        # add button
        txtAddBtn = tk.StringVar()
        self.addBtn = tk.Button(self.frame, textvariable=txtAddBtn, font=Constants.mainFont, bg="#20bebe", fg="white",
                                height=1, width=5)
        self.addBtn.place(relx=0.15, rely=0.5)
        self.addBtn.config(command=lambda: self.onAddBtnClick())
        txtAddBtn.set(Constants.txtAdd)


        # input number text box
        self.inputBox = tk.Text(self.frame, height=2, width=8)
        self.inputBox.place(relx=0.06, rely=0.5)
        self.inputBox.insert(tk.END, "1")

        # quit button
        txtQuitBtn = tk.StringVar()
        self.quitBtn = tk.Button(self.frame, textvariable=txtQuitBtn, font=Constants.mainFont, bg="#FF0000",
                                  fg="white",
                                  height=1, width=6)
        self.quitBtn.place(relx=0.02, rely=0.02)
        self.quitBtn.config(command=lambda: self.onQuitBtnClick())
        txtQuitBtn.set(Constants.txtQuit)

        # Infomation
        self.txtInformation = tk.Label(self.frame, text=Constants.txtInfomation, font=Constants.mainFont)
        self.txtInformation.config(bg=Constants.bgColor)
        self.txtInformation.place(relx=0.4, rely=0.1)

        self.infoFrame = tk.Frame(self.frame, bg=Constants.infoBgColor)
        self.infoFrame.place(relwidth=0.3, relheight=0.4, relx=0.7, rely=0.2)

        self.txtName = tk.Label(self.frame, text=Constants.txtName, font=(Constants.mainFont, 12), wraplength=230)
        self.txtName.config(bg=Constants.infoBgColor)
        self.txtName.place(relx=0.7, rely=0.2)

        self.txtPrice = tk.Label(self.frame, text=Constants.txtPrice, font=(Constants.mainFont, 12), wraplength=230)
        self.txtPrice.config(bg=Constants.infoBgColor)
        self.txtPrice.place(relx=0.7, rely=0.3)

        self.txtDes = tk.Label(self.frame, text=Constants.txtDes, font=(Constants.mainFont, 12), wraplength=230)
        self.txtDes.config(bg=Constants.infoBgColor)
        self.txtDes.place(relx=0.7, rely=0.4)

        # choosed list
        self.txtChoosedList = tk.Label(self.frame, text=Constants.txtChoosedList, font=Constants.mainFont)
        self.txtChoosedList.config(bg=Constants.bgColor)
        self.txtChoosedList.place(relx=0.08, rely=0.62)
        self.lstChoosed = tk.Listbox(self.frame)
        self.lstChoosed.place(relwidth=0.18, relheight=0.4, relx=0.06, rely=0.68)

        # remove button
        txtRemoveBtn = tk.StringVar()
        self.removeBtn = tk.Button(self.frame, textvariable=txtRemoveBtn, font=Constants.mainFont, bg="#20bebe",
                                   fg="white",
                                   height=1, width=3)
        self.removeBtn.place(relx=0.25, rely=0.7, relwidth=0.12)
        self.removeBtn.config(command=lambda: self.onDelBtnClick())
        txtRemoveBtn.set(Constants.txtRemove)


class PaymentPage:
    def __init__(self, root, totalPrice, pricetoPay, lstItemChoosed, lstQuantity):
        self.root = root
        self.totalPrice = totalPrice
        self.priceToPay = pricetoPay
        self.lstItemChoosed = lstItemChoosed
        self.lstQuantity = lstQuantity
        self.R1 = None
        self.R2 = None
        self.txtPaymentPage = None
        self.inputBankBox = None
        self.txtPaymentMethod = None
        self.txtTest = None
        self.txtChoosedList = None
        self.lstChoosed = None
        self.methodPayment = None
        self.txtPrice = None
        self.txtPriceToPay = None

    def onRadioBtnClick(self):
        option = self.var.get()

        if option == 1:
            self.methodPayment = "CASH"
            self.inputBankBox.delete("1.0", "end")
            self.inputBankBox.insert("end-1c", "Your Bank Code")
            self.inputBankBox.config(state="disabled")
            #hide price to pay
            self.txtPriceToPay.place_forget()

        elif option == 2:
            self.methodPayment = "VISA"
            self.inputBankBox.config(state="normal")
            self.inputBankBox.delete("1.0", "end")
            #show price to pay
            self.txtPriceToPay.place(relx=0.5, rely=0.63)


    def onPayBtnClick(self):
        bankCode = self.inputBankBox.get("1.0", 'end-1c')
        if self.methodPayment == "VISA" and (bankCode is None or bankCode.strip() == ""):
            Utils.errorMessage(Constants.txtBankCodeError, self.root)
            return
        msg = ClientFeatures.Pay(Utils.getTableNumber(), self.methodPayment, bankCode)
        if msg is None:
            Utils.errorMessage(Constants.txtErrorOccured, self.root)
        elif msg == "Success":
            # return to menu page if pay successfully
            self.onBackPressed()
            Utils.successMessage(Constants.txtPaidSuccess, self.root, 15)
        else:
            Utils.errorMessage(Constants.txtBankCodeInvalid, self.root)

    def onBackPressed(self):
        for widgets in self.frame.winfo_children():
            widgets.destroy()
        self.root.title("Menu Page")
        MenuPage(self.root).onCreate()

    def onCreate(self):
        # init frame
        self.frame = tk.Frame(self.root, bg=Constants.bgColor)
        self.frame.place(relwidth=1, relheight=1)

        # text payment page
        self.txtPaymentPage = tk.Label(self.frame, text=Constants.txtPaymentPage, font=(Constants.mainFont, 20))
        self.txtPaymentPage.config(bg=Constants.bgColor)
        self.txtPaymentPage.place(relx=0.35, rely=0.05)

        # choosed list
        self.txtChoosedList = tk.Label(self.frame, text=Constants.txtChoosedList, font=(Constants.mainFont, 18))
        self.txtChoosedList.config(bg=Constants.bgColor)
        self.txtChoosedList.place(relx=0.1, rely=0.2)
        self.lstChoosed = tk.Listbox(self.frame)
        self.lstChoosed.place(relwidth=0.3, relheight=0.5, relx=0.1, rely=0.2)
        for i in range(0, len(self.lstItemChoosed)):
            self.lstChoosed.insert("end", self.lstItemChoosed[i] + ' X ' + self.lstQuantity[i])

        # text Price
        self.txtPrice = tk.Label(self.frame, text=Constants.txtTotalPrice + self.totalPrice,
                                 font=(Constants.mainFont, 18))
        self.txtPrice.config(bg=Constants.bgColor)
        self.txtPrice.place(relx=0.5, rely=0.2)


        # text Payment Method
        self.txtPaymentMethod = tk.Label(self.frame, text=Constants.txtPaymentMethod, font=(Constants.mainFont, 18))
        self.txtPaymentMethod.config(bg=Constants.bgColor)
        self.txtPaymentMethod.place(relx=0.5, rely=0.3)

        # payment method
        self.var = tk.IntVar()
        self.R1 = tk.Radiobutton(self.root, text="Cash payment", variable=self.var, value=1,
                                 font=(Constants.mainFont, 16),
                                 command=self.onRadioBtnClick)
        self.R1.place(relx=0.5, rely=0.38)
        self.R2 = tk.Radiobutton(self.root, text="Payment via bank card", variable=self.var, value=2,
                                 font=(Constants.mainFont, 16),
                                 command=self.onRadioBtnClick)
        self.R2.place(relx=0.5, rely=0.5)

        # input bank number text box
        self.inputBankBox = tk.Text(self.frame, height=1, width=20, font=(Constants.mainFont, 15))
        self.inputBankBox.place(relx=0.5, rely=0.57)
        self.inputBankBox.insert("end-1c", "Your Bank Code")
        self.inputBankBox.config(state="disabled")

        # text Price to pay
        self.txtPriceToPay = tk.Label(self.frame, text=Constants.txtPriceToPay + self.priceToPay, font=(Constants.mainFont, 15), state="disabled")
        self.txtPriceToPay.config(bg=Constants.bgColor)


        # Pay button
        txtPayBtn = tk.StringVar()
        self.payBtn = tk.Button(self.frame, textvariable=txtPayBtn, font=Constants.mainFont, bg="#20bebe",
                                fg="white",
                                height=2, width=10)
        self.payBtn.place(relx=0.5, rely=0.7)
        self.payBtn.config(command=lambda: self.onPayBtnClick())
        txtPayBtn.set(Constants.txtPay)

        # back button
        photo = tk.PhotoImage(file=Constants.backImagePath)
        self.backBtnPhoto = photo.subsample(10, 10)
        self.backBtn = tk.Button(self.frame, image=self.backBtnPhoto)
        self.backBtn.config(command=lambda: self.onBackPressed())
        self.backBtn.place(relwidth=0.05, relheight=0.05, relx=0.05, rely=0.05)


class Utils:
    tableNumber = None

    @classmethod
    def setTableNumber(cls, tableNumber):
        cls.tableNumber = tableNumber

    @classmethod
    def getTableNumber(cls):
        return cls.tableNumber

    @classmethod
    def errorMessage(cls, msg, root, textSize=20):
        # pop up a window error
        popupRoot = tk.Toplevel(root)
        popupRoot.title("Error")
        canvas = tk.Canvas(popupRoot, width=Constants.POPUP_WIDTH, height=Constants.POPUP_HEIGHT)
        canvas.pack()
        popupFrame = tk.Frame(popupRoot, bg=Constants.bgColor)
        popupFrame.place(relwidth=1, relheight=1)
        txtInformation = tk.Label(popupRoot, text=msg, font=(Constants.mainFont, textSize), wraplength=300)
        txtInformation.config(bg=Constants.bgColor)
        txtInformation.place(x=80, y=80)
        popupRoot.mainloop()

    @classmethod
    def successMessage(cls, msg, root, textSize=20):
        # pop up a window error
        popupRoot = tk.Toplevel(root)
        popupRoot.title("Success")
        canvas = tk.Canvas(popupRoot, width=Constants.POPUP_WIDTH, height=Constants.POPUP_HEIGHT)
        canvas.pack()
        popupFrame = tk.Frame(popupRoot, bg=Constants.bgColor)
        popupFrame.place(relwidth=1, relheight=1)
        txtInformation = tk.Label(popupRoot, text=msg, font=(Constants.mainFont, textSize), wraplength=300)
        txtInformation.config(bg=Constants.bgColor)
        txtInformation.place(x=80, y=80)
        popupRoot.mainloop()
