from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import requests
from smartcard.System import readers
from smartcard.util import toHexString
import datetime
import random


class PaymentPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Payment"
        self.size_hint = (0.8, 0.6)

        layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Please insert your card into the reader.")
        layout.add_widget(self.label)

        self.amount_input = TextInput(
            hint_text="Enter amount in Rand", multiline=False, input_filter='int')
        layout.add_widget(self.amount_input)

        pay_button = Button(text="Read Card", on_press=self.read_card)
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
            self.process_payment(card_data)
        else:
            self.label.text = "No card reader found. Using dummy card data for testing."
            dummy_card_data = "4111111111111111"  # Dummy card number
            self.process_payment(dummy_card_data)

    def process_payment(self, card_data):
        try:
            amount = int(self.amount_input.text)  # User-defined amount in Rand
        except ValueError:
            error_popup = Popup(title="Invalid Amount", content=Label(
                text="Please enter a valid amount."), size_hint=(0.8, 0.4))
            error_popup.open()
            return

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
                text="Payment was successful!"), size_hint=(0.8, 0.4))
            success_popup.open()
            # Pass success status to callback
            Clock.schedule_once(lambda dt: self.callback(True), 1)
        else:
            error_popup = Popup(title="Payment Failed", content=Label(
                text="Payment failed. Please try again."), size_hint=(0.8, 0.4))
            error_popup.open()
            # Pass failure status to callback
            Clock.schedule_once(lambda dt: self.callback(False), 1)

    def generate_payment_reference(self):
        prefix = "PAY"
        date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = random.randint(10000000, 99999999)
        reference = f"{prefix}-{date_str}-{unique_id}"
        return reference


class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        hello_label = Label(text="Hello World", font_size='20sp')
        layout.add_widget(hello_label)

        pay_button = Button(text="Test Pay", font_size='20sp')
        pay_button.bind(on_press=self.show_payment_popup)
        layout.add_widget(pay_button)

        return layout

    def show_payment_popup(self, instance):
        popup = PaymentPopup(self.payment_callback)
        popup.open()

    def payment_callback(self, success):
        if success:
            print("Payment was successful!")
        else:
            print("Payment failed.")


if __name__ == "__main__":
    MyApp().run()
