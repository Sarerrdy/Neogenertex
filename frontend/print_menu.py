from kivy.app import App
import subprocess
import textwrap
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from pay import PaymentPopup


class PrintMenu(BoxLayout):
    def __init__(self, **kwargs):
        super(PrintMenu, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # Add a back button to navigate back to the menu
        back_button = Button(text='Back', size_hint=(
            None, None), size=(100, 50))
        back_button.bind(on_press=self.back_to_menu)
        self.add_widget(back_button)

        # Add a header label
        self.add_widget(Label(text='Print Menu', font_size=24))

        # Create a grid layout for the printing options
        printing_options_layout = GridLayout(
            cols=2, row_force_default=True, row_default_height=40, size_hint_y=None, height=200)
        self.add_widget(printing_options_layout)

        # Add a label and spinner for the print quality
        printing_options_layout.add_widget(Label(text='Print Quality:'))
        self.quality_spinner = Spinner(text='Draft', values=(
            'Draft', 'Normal', 'High'), size_hint=(None, None), size=(100, 44))
        printing_options_layout.add_widget(self.quality_spinner)

        # Add a label and spinner for the paper size
        printing_options_layout.add_widget(Label(text='Paper Size:'))
        self.size_spinner = Spinner(text='A4', values=(
            'A4', 'Letter', 'Legal'), size_hint=(None, None), size=(100, 44))
        printing_options_layout.add_widget(self.size_spinner)

        # Add a button to browse for file to print
        self.browse_button = Button(text='Browse File', font_size=24)
        self.browse_button.bind(on_press=self.browse_file)
        self.add_widget(self.browse_button)

        # Add a label to display the selected file
        self.file_label = Label(text='No file selected')
        self.add_widget(self.file_label)

        # Add a box layout to hold the print and cancel buttons
        button_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50,
            spacing=20,
        )
        self.add_widget(button_box)

        # Add a button to print the file
        self.print_button = Button(
            text='Print', size_hint=(None, None),  size=(300, 50))
        self.print_button.bind(on_press=self.start_payment_process)
        button_box.add_widget(self.print_button)

        # Add a cancel button
        cancel_button = Button(
            text='Cancel', size_hint=(None, None), size=(300, 50))
        cancel_button.bind(on_press=self.cancel_print)
        button_box.add_widget(cancel_button)

        # Make the buttons center horizontally
        button_box.pos_hint = {'center_x': 0.4}
        button_box.size_hint_x = None
        button_box.width = 200

    def back_to_menu(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'

    def cancel_print(self, instance):
        # Cancel the print operation
        # You can add code here to cancel the print operation
        app = App.get_running_app()
        app.root.current = 'menu'

    def browse_file(self, instance):
        # Create a file chooser to select the file to print
        file_chooser = FileChooserListView(
            path='/home/', filters=['*.docx', '*.pdf', '*.txt', '*.doc', '*.odt', '*.rtf' '*.jpg', '*.png', '*.jpeg'],
            dirselect=False, multiselect=False)
        file_chooser.bind(selection=self.update_file_label)

        # Create a popup to display the file chooser
        popup = Popup(title='Select File to Print', content=file_chooser,
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def update_file_label(self, instance, selection):
        # Update the file label with the selected file
        if selection:
            self.file_label.text = selection[0]

    def start_payment_process(self, instance):
        popup = PaymentPopup(self.payment_callback)
        popup.open()

    def payment_callback(self, success):
        if success:
            self.print_file()
        else:
            error_popup = Popup(title="Payment Failed", content=Label(
                text="Payment failed. Please try again."), size_hint=(0.8, 0.4))
            error_popup.open()

    def print_file(self):
        try:
            # Get the printing options
            file_path = self.file_label.text

            # Check if a physical printer is available
            printers = subprocess.check_output(
                ['lpstat', '-p']).decode('utf-8').splitlines()
            physical_printers = [
                printer.split()[1] for printer in printers if not printer.startswith('*')]

            if physical_printers:
                # Use a physical printer
                print_command = f"lp {file_path}"
                subprocess.run(print_command.split(), check=True)
            else:
                # Use a virtual PDF printer
                print_command = f"lp -d PDF -o /home/sarerrdy/PDF/output.pdf {file_path}"
                subprocess.run(print_command.split(), check=True)

            # Show a success popup
            popup = Popup(title='Print Job Successful', content=Label(
                text='Your file has been printed successfully!'),
                size_hint=(None, None),
                size=(400, 200))
            popup.open()
            Clock.schedule_once(lambda dt: self.dismiss_popup(dt), 2)

        except Exception as e:
            # Show an error popup
            error_message = str(e)
            if len(error_message) > 80:
                error_message = '\n'.join(textwrap.wrap(error_message, 80))
            popup = Popup(title='Error', content=Label(
                text=error_message, text_size=(400, None), valign='middle', halign='center'),
                size_hint=(None, None), size=(400, 200))
            popup.open()
            Clock.schedule_once(lambda dt: self.dismiss_popup(popup), 2)

    def dismiss_popup(self, popup):
        popup.dismiss()  # Dismiss the popup

        app = App.get_running_app()
        app.root.current = 'menu'
