from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image as KivyImage
from pytesseract import image_to_string
from PIL import Image
from fpdf import FPDF
import subprocess
import os
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class ScanMenu(BoxLayout):
    def __init__(self, **kwargs):
        super(ScanMenu, self).__init__(**kwargs)
        # self.layout = BoxLayout()
        # # Add your widgets to the layout here
        # self.add_widget(self.layout)
        self.orientation = 'vertical'

        # Add a header label
        self.add_widget(Label(text='Scan Menu', font_size=24))

        # Create a grid layout for the scanning options
        scanning_options_layout = GridLayout(
            cols=2, row_force_default=True, row_default_height=40, size_hint_y=None, height=200)
        self.add_widget(scanning_options_layout)

        # Add a label and spinner for the file format
        scanning_options_layout.add_widget(Label(text='Save As:'))
        self.format_spinner = Spinner(text='PNG', values=(
            'PNG', 'TIFF', 'JPEG', 'PDF'), size_hint=(None, None), size=(100, 44))
        scanning_options_layout.add_widget(self.format_spinner)

        # Add a label and spinner for the color mode
        scanning_options_layout.add_widget(Label(text='Color Mode:'))
        self.mode_spinner = Spinner(text='Color', values=(
            'Color', 'Gray', 'Lineart'), size_hint=(None, None), size=(100, 44))
        scanning_options_layout.add_widget(self.mode_spinner)

        # Add a label and text input for the filename
        scanning_options_layout.add_widget(Label(text='Filename:'))
        self.filename_input = TextInput(
            hint_text='Enter filename', size_hint=(None, None), size=(200, 44))
        scanning_options_layout.add_widget(self.filename_input)

        # Add a button to select the save location
        self.save_location_button = Button(
            text='Select Save Location', font_size=24)
        self.save_location_button.bind(on_press=self.select_save_location)
        self.add_widget(self.save_location_button)

        # Add a label to display the selected save location
        self.save_location_label = Label(text='Save Location: ')
        self.add_widget(self.save_location_label)

        # Add a scan button
        self.scan_button = Button(text='Scan Document', font_size=24)
        self.scan_button.bind(on_press=self.scan_document)
        self.add_widget(self.scan_button)

        # Initialize the save location
        self.save_location = os.getcwd()

    def select_save_location(self, instance):
        # Create a file chooser to select the save location
        file_chooser = FileChooserListView(
            path=self.save_location, filters=['*'], dirselect=True)
        file_chooser.bind(selection=self.update_save_location)

        # Create a button to close the file chooser
        ok_button = Button(text='OK', size_hint=(None, None), size=(100, 40))

        # Create a layout to combine the file chooser and the button
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(file_chooser)
        layout.add_widget(ok_button)

        # Create a popup to display the layout
        popup = Popup(title='Select Save Location', content=layout,
                      size_hint=(None, None), size=(400, 400))

        # Bind the button to dismiss the popup
        ok_button.bind(on_press=popup.dismiss)

        popup.open()

    def update_save_location(self, instance, selection):
        # Update the save location
        self.save_location = selection[0]
        self.save_location_label.text = f'Save Location: {self.save_location}'

    def scan_document(self, instance):
        try:
            # Get the scanning options
            file_format = self.format_spinner.text
            color_mode = self.mode_spinner.text
            filename = self.filename_input.text or 'scanned_document'

            # Use Tesseract OCR to recognize text in the image
            if file_format == 'PDF':
                # Create a PDF file
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=15)
                pdf.cell(200, 10, txt="Scanned Document", ln=True, align='C')

                # Add the scanned image to the PDF file
                image_path = f"{filename}.jpg"
                pdf.image(image_path, x=50, y=50, w=100)

                # Save the PDF file
                pdf.output(os.path.join(self.save_location, f"{filename}.pdf"))

            else:
                # Use the scanimage command to scan the document
                scan_command = f"scanimage --format={file_format} --mode={color_mode} --output={os.path.join(self.save_location, f'{filename}.{file_format}')}"

                # Run the scan command and check for errors
                try:
                    subprocess.run(scan_command.split(), check=True)
                except subprocess.CalledProcessError as e:
                    self.show_error_popup(f"Error scanning document: {e}")
                    return

                # Use Tesseract OCR to recognize text in the image
                image_path = os.path.join(
                    self.save_location, f"{filename}.{file_format}")
                try:
                    text = image_to_string(Image.open(image_path))
                except Exception as e:
                    self.show_error_popup(
                        f"Error recognizing text in image: {e}")
                    return

                # Display the recognized text in a popup window
                popup = Popup(title='Scanned Document', content=Label(
                    text=text), size_hint=(None, None), size=(400, 200))
                popup.open()
                Clock.schedule_once(lambda dt: self.dismiss_popup(popup), 5)

        except Exception as e:
            self.show_error_popup(f"An error occurred: {e}")

    def show_error_popup(self, error_message):
        scroll_view = ScrollView(size_hint=(None, None), size=(400, 200))
        text_input = TextInput(text=error_message, size_hint=(
            None, None), size=(400, 200), multiline=True, readonly=True)
        scroll_view.add_widget(text_input)
        popup = Popup(title='Error', content=scroll_view,
                      size_hint=(None, None), size=(400, 200))
        # popup.bind(on_touch_down=self.dismiss_popup)
        popup.open()
        Clock.schedule_once(lambda dt: self.dismiss_popup(popup), 2)

    def dismiss_popup(self, instance):
        # if instance.collide_point(*touch.pos):
        instance.dismiss()
        app = App.get_running_app()
        app.root.current = 'menu'


class ScanApp(App):
    def build(self):
        return ScanMenu()


if __name__ == '__main__':
    ScanApp().run()
