
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.clock import Clock
import requests
from smartcard.System import readers
from smartcard.util import toHexString
import datetime
import random


class PaymentPopup(Popup):
    def __init__(self, callback, total_cost, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.total_cost = total_cost
        self.title = "Payment"
        self.size_hint = (0.4, 0.3)

        layout = BoxLayout(orientation='vertical')

        total_cost_label = Label(
            text=f"Total Cost: R{self.total_cost}", font_size=16)
        layout.add_widget(total_cost_label)

        self.label = Label(
            text="Please insert your card into the reader.", font_size=16, bold=True)
        layout.add_widget(self.label)

        pay_button = Button(text="Pay Now",
                            size=(100, 50),
                            background_color=(0, 1, 0, 1),  # Green color
                            color=(1, 1, 1, 1),
                            on_press=self.read_card)
        layout.add_widget(pay_button)
        self.add_widget(layout)

    def read_card(self, instance):
        r = readers()
        if len(r) > 0:
            reader = r[0]
            connection = reader.createConnection()
            connection.connect()
            apdu = [0x00, 0xA4, 0x04, 0x00, 0x0A, 0xA0, 0x00,
                    0x00, 0x00, 0x03, 0x80, 0x02, 0x00, 0x00, 0x00]
            response, sw1, sw2 = connection.transmit(apdu)
            card_data = toHexString(response)
            self.process_payment(card_data, self.total_cost)
        else:
            # self.label.text = "No card reader found. Using dummy card data for testing."
            dummy_card_data = "4111111111111111"  # Dummy card number
            self.process_payment(dummy_card_data, self.total_cost)

    def process_payment(self, card_data, amount):

        reference = self.generate_payment_reference()

        # Assuming we're using the PayFast sandbox environment for testing
        response = requests.post('https://sandbox.payfast.co.za/eng/process', data={
            'merchant_id': '10036103',
            'merchant_key': 'gnbf1i7nmna5d',
            'amount': amount * 100,  # Amount in cents
            'item_name': 'Test Payment',
            'item_description': 'Testing payment gateway integration',
            'm_payment_id': reference,
            'card_number': card_data,
            'passphrase': 'Test my Neogenertex'
        })
        if response.status_code == 200:
            self.dismiss()
            success_popup = Popup(title="Payment Successful", content=Label(
                text="Payment was successful!"), size_hint=(0.4, 0.3))
            success_popup.open()
            # Pass success status to callback
            Clock.schedule_once(lambda dt: self.callback(True), 1)
            Clock.schedule_once(
                lambda dt: self.close_payment_popup(success_popup), 4)
        else:
            error_popup = Popup(title="Payment Failed", content=Label(
                text="Payment failed. Please try again."), size_hint=(0.4, 0.3))
            error_popup.open()
            # Pass failure status to callback
            Clock.schedule_once(lambda dt: self.callback(False), 1)
            Clock.schedule_once(
                lambda dt: self.close_payment_popup(error_popup), 4)

    def generate_payment_reference(self):
        prefix = "PAY"
        date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = random.randint(10000000, 99999999)
        reference = f"{prefix}-{date_str}-{unique_id}"
        return reference

    def close_payment_popup(self, pop):
        print("Dismissing popup...")
        pop.dismiss()
        print("Popup dismissed.")
