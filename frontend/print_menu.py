from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView

import subprocess
import textwrap

from pay import PaymentPopup


class PrintMenu(BoxLayout):
    def __init__(self, **kwargs):
        super(PrintMenu, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = (50, 50, 50, 50)
        self.spacing = 20

        self.file_label = Label(text='Select a file to print', font_size=24)
        self.add_widget(self.file_label)

        self.file_chooser = FileChooserListView(
            path='/home/', filters=['*.pdf', '*.txt'])  # Filters for file types
        self.file_chooser.bind(selection=self.on_file_select)
        self.add_widget(self.file_chooser)

        # Create a horizontal BoxLayout for the buttons
        button_layout = BoxLayout(
            orientation='horizontal', spacing=10, size_hint=(1, None), height=50)

        self.cancel_select_button = Button(
            text='Cancel', font_size=24, size_hint=(0.5, 1))
        self.cancel_select_button.bind(on_press=self.dismiss_select_file)
        button_layout.add_widget(self.cancel_select_button)

        self.preview_button = Button(
            text='Preview', font_size=24, size_hint=(0.5, 1))
        self.preview_button.bind(on_press=self.preview_text)
        button_layout.add_widget(self.preview_button)

        self.add_widget(button_layout)

    def on_file_select(self, instance, value):
        if value:
            self.file_label.text = value[0]

    def dismiss_select_file(self, instance):
        # Remove or hide the file chooser and buttons
        # self.remove_widget(self.file_chooser)
        # self.remove_widget(self.file_label)
        # Return to the main menu
        app = App.get_running_app()
        app.root.current = 'menu'

    #     # Update file_label with the selected file path
    # def on_file_select(self, instance, value):
    #     if value:
    #         self.file_label.text = value[0]

    #     self.preview_button = Button(
    #         text='Preview', font_size=24, size_hint=(1, None), size=(100, 50))
    #     self.preview_button.bind(on_press=self.preview_text)
    #     self.add_widget(self.preview_button)

    def preview_text(self, instance):
        file_path = self.file_chooser.selection[0]
        self.pages = self.read_file(file_path)
        layout = self._create_layout()

        # Ensure scroll view supports mouse and touch scrolling
        scrollview = ScrollView(
            scroll_type=['bars', 'content'], bar_width=10, size_hint=(1, .1))
        grid_layout = self._create_grid_layout()
        self.text_input = self._create_text_input()
        self.text_input.text = self.pages[0]
        page_layout = self._create_page_layout()
        page_layout.add_widget(self.text_input)
        grid_layout.add_widget(page_layout)
        scrollview.add_widget(grid_layout)
        layout.add_widget(scrollview)
        navigation_layout = self._create_navigation_layout()
        layout.add_widget(navigation_layout)
        button_layout = BoxLayout(orientation='horizontal')
        button_layout = self._create_button_layout()
        layout.add_widget(button_layout)
        self.preview_popup = Popup(
            title='Text Preview', content=layout, size_hint=(0.8, 0.8))
        self.preview_popup.open()
        self.current_page = 1
        scrollview.scroll_y = 0
        grid_layout.height = self.text_input.height

    def read_file(self, file_path):
        with open(file_path, 'r') as file:
            text = file.read()
            pages = []
            while text:
                page, text = text[:2500], text[2500:]
                pages.append(page)
            return pages

    def _create_layout(self):
        layout = BoxLayout(orientation='vertical')
        return layout

    def _create_grid_layout(self):
        grid_layout = GridLayout(cols=1, size_hint=(1, 1))
        return grid_layout

    def _create_text_input(self):
        text_input = TextInput(multiline=True, font_size=24)
        return text_input

    def _create_page_layout(self):
        page_layout = BoxLayout(orientation='vertical')
        return page_layout

    def _create_navigation_layout(self):
        navigation_layout = BoxLayout(
            orientation='horizontal', size_hint=(None, None), size=(400, 50))
        navigation_layout.pos_hint = {'center_x': 0.5}  # Center horizontally
        navigation_layout.spacing = 10  # Add some space between widgets
        # Add some padding to center the widgets
        navigation_layout.padding = (20, 0)

        previous_button = Button(text='Previous', font_size=18,
                                 font_name='Roboto', size_hint=(None, None), size=(100, 50))
        previous_button.bind(on_press=self.previous_page)
        navigation_layout.add_widget(previous_button)

        self.current_page_label = Label(
            text=f'Page 1 of {len(self.pages)}', font_size=18, font_name='Roboto')
        self.current_page_label.size_hint = (
            None, None)  # Set size hint to None
        self.current_page_label.width = 200  # Set a fixed width
        self.current_page_label.valign = 'middle'  # Center vertically
        self.current_page_label.halign = 'center'  # Center horizontally
        self.current_page_label.padding = (
            0, 20, 0, 0)  # Add padding to the top
        navigation_layout.add_widget(self.current_page_label)

        next_button = Button(text='Next', font_size=18, font_name='Roboto', size_hint=(
            None, None), size=(100, 50))
        next_button.bind(on_press=self.next_page)
        navigation_layout.add_widget(next_button)
        return navigation_layout

    def _create_button_layout(self):
        button_layout = BoxLayout(
            orientation='horizontal', size_hint=(1, None), height=50)
        left_layout = BoxLayout(orientation='horizontal', size_hint=(0.5, 1))
        cancel_button = Button(text='Cancel', font_size=18, font_name='Roboto', size_hint=(
            None, None), size=(100, 50))
        cancel_button.bind(on_press=self.dismiss_preview)
        left_layout.add_widget(cancel_button)
        print_button = Button(text='Print', font_size=18, font_name='Roboto', size_hint=(
            None, None), size=(100, 50))
        print_button.bind(on_press=self.calculate_print_cost)
        left_layout.add_widget(print_button)
        button_layout.add_widget(left_layout)
        right_layout = BoxLayout(
            orientation='horizontal', size_hint=(None, None), size=(600, 50),
            pos_hint={'right': 0, 'bottom': 1})
        self.set_page_numbers_label = Label(
            text='Pages:', size_hint=(None, None), size=(60, 44), font_size=18, font_name='Roboto')
        right_layout.add_widget(self.set_page_numbers_label)
        self.preview_page_numbers_input = TextInput(
            hint_text='e.g. 1-3, 5, All', size_hint=(None, None), size=(120, 44), font_size=18)
        right_layout.add_widget(self.preview_page_numbers_input)

        self.set_copies_label = Label(
            text='copies:', size_hint=(None, None), size=(60, 44), font_size=18, font_name='Roboto')
        right_layout.add_widget(self.set_copies_label)
        self.preview_copies_input = TextInput(hint_text='1', size_hint=(
            None, None), size=(50, 44), font_size=18, input_filter='int')
        right_layout.add_widget(self.preview_copies_input)

        self.set_color_label = Label(
            text='Color:', size_hint=(None, None), size=(60, 44), font_size=18, font_name='Roboto')
        right_layout.add_widget(self.set_color_label)
        self.preview_color_spinner = Spinner(text='Color', values=(
            'Color', 'Gray'), size_hint=(None, None), size=(70, 44), font_size=18)
        right_layout.add_widget(self.preview_color_spinner)
        button_layout.add_widget(right_layout)
        return button_layout

    def next_page(self, instance):
        if self.current_page < len(self.pages):
            self.current_page += 1
            self.text_input.text = self.pages[self.current_page-1]
            self.current_page_label.text = f'Page {self.current_page} of {len(self.pages)}'

    def previous_page(self, instance):
        if self.current_page > 1:
            self.current_page -= 1
            self.text_input.text = self.pages[self.current_page-1]
            self.current_page_label.text = f'Page {self.current_page} of {len(self.pages)}'

    def dismiss_preview(self, instance=None):
        self.preview_popup.dismiss()

    def start_payment_process(self, total_cost):
        popup = PaymentPopup(self.payment_callback, total_cost)
        popup.open()
        # self.payment_process(total_cost)

    # def payment_process(self, total_cost):
    #     popup = PaymentPopup(self.payment_callback, total_cost)
    #     popup.open()

    def payment_callback(self, success):
        if success:
            print("About to print file from callback.")
            self.print_file()
        else:
            error_popup = Popup(title="Payment Failed", content=Label(
                text="Payment failed. Please try again."), size_hint=(0.8, 0.4))
            error_popup.open()

    def dismiss_popup(self, popup):
        popup.dismiss()
        app = App.get_running_app()
        app.root.current = 'menu'

    def calculate_print_cost(self, instance):

        if not self.preview_page_numbers_input.text or not self.preview_copies_input.text:
            popup = Popup(title='Error', content=Label(
                text='Please enter both page numbers and copies'),
                size_hint=(None, None), size=(400, 200))
            popup.open()
            Clock.schedule_once(lambda dt: self.dismiss_popup(popup), 2)
            return

        page_numbers = self.preview_page_numbers_input.text

        if page_numbers.lower() == 'all':
            num_pages = len(self.pages)
        else:
            page_ranges = page_numbers.replace('_', ',').split(',')
            page_numbers = []
            for page_range in page_ranges:
                if '-' in page_range:
                    start_page, end_page = map(int, page_range.split('-'))
                    page_numbers.extend(range(start_page, end_page + 1))
                else:
                    page_numbers.append(int(page_range))

            # Validate and adjust page numbers if necessary
            max_page_number = len(self.pages)
            adjusted_page_numbers = [
                min(page_number, max_page_number) for page_number in page_numbers]

            num_pages = len(set(adjusted_page_numbers))

        num_copies = int(self.preview_copies_input.text)
        print_color = self.preview_color_spinner.text

        total_cost = num_pages * num_copies * 5
        if print_color == 'Color':
            total_cost *= 2

        # Create a popup window to display the summary
        summary_popup = Popup(title='Print Summary',
                              size_hint=(None, None), size=(600, 400))
        summary_layout = BoxLayout(orientation='vertical')
        summary_label = Label(text=f'Page Numbers: {page_numbers}\n'
                              f'Number of Copies: {num_copies}\n'
                              f'Total Cost: R{total_cost}',
                              font_size=16, text_size=(500, None), valign='middle', halign='left', size_hint=(1, None), height=400)

        summary_label.height = len(summary_label.text.split(
            '\n')) * 20  # assuming 20 pixels per line
        summary_scroll = ScrollView(size_hint=(1, 1))
        summary_scroll.add_widget(summary_label)
        summary_layout.add_widget(summary_scroll)

        # Add a button to confirm and start the payment process
        button_layout = BoxLayout(
            orientation='horizontal', size_hint=(1, 0.2))
        cancel_button = Button(text='Cancel and Close Summary',
                               background_color=(1, 0, 0, 1),  # Red color
                               color=(1, 1, 1, 1))  # White text color)
        confirm_button = Button(text='Confirm and Pay',
                                background_color=(
                                    0, 1, 0, 1),  # Green color
                                color=(1, 1, 1, 1))  # White text color)
        cancel_button.bind(on_press=lambda x: summary_popup.dismiss())
        confirm_button.bind(on_press=lambda x: summary_popup.dismiss())
        confirm_button.bind(
            on_press=lambda x: self.start_payment_process(total_cost))
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        summary_layout.add_widget(button_layout)

        summary_popup.add_widget(summary_layout)  # Add the summary_layout

        summary_popup.open()

    def print_file(self):
        if not self.validate_input():
            return
        try:
            # Generate the initial print command
            print_command = self.generate_print_command()
            print("print_command generated")

            # Check available printers
            printer_list = subprocess.check_output(
                ['lpstat', '-p']).decode('utf-8').splitlines()
            print("printers checked")

            # Extract physical printer names
            physical_printers = [
                printer.split()[1] for printer in printer_list if not printer.startswith('*')]
            print("physical_printers generated")

            if 'PDF' in physical_printers:
                # Remove PDF virtual printer from physical printers list
                physical_printers.remove('PDF')

            if physical_printers:
                # Print to physical printer
                print("physical_printers detected")
                # Remove redundant "lp" from the start of the command
                print_command = ["lp"] + print_command[1:]
                subprocess.run(print_command, check=True)
                print("file printed on physical printer")
            else:
                # Print to PDF virtual printer
                print("physical_printers not detected")
                # Add '-d PDF' for virtual printer command
                print_command = ["lp", "-d", "PDF"] + print_command[1:]
                subprocess.run(print_command, check=True)
                print("file printed as PDF")

            # Show success popup
            print_success_popup = Popup(title='Print Job Successful', content=Label(
                text=f'Your file has been printed successfully!\nNumber of Copies: {self.preview_copies_input.text}\nPage Numbers: {self.preview_page_numbers_input.text}'),
                size_hint=(None, None), size=(400, 200))
            print_success_popup.open()
            Clock.schedule_once(
                lambda dt: self.dismiss_popup(print_success_popup), 3)
            Clock.schedule_once(
                lambda dt: self.dismiss_preview(), 4)

        except Exception as e:
            error_message = str(e)
            if len(error_message) > 80:
                error_message = '\n'.join(textwrap.wrap(error_message, 80))
            popup = Popup(title='Error', content=Label(
                text=error_message, text_size=(400, None), valign='middle', halign='center'),
                size_hint=(None, None), size=(400, 200))
            popup.open()
            Clock.schedule_once(lambda dt: self.dismiss_popup(popup), 4)

    def generate_print_command(self):
        # Generate the print command based on the selected printer, number of copies, page numbers, and print color
        file_path = self.file_label.text
        page_numbers = self.preview_page_numbers_input.text

        if page_numbers.lower() == 'all':
            print_command = ["lp", "-n",
                             str(self.preview_copies_input.text), file_path]
        elif '-' in page_numbers:
            start_page, end_page = page_numbers.split('-')
            print_command = [
                "lp", "-n", str(self.preview_copies_input.text), "-P", f"{start_page}-{end_page}", file_path]
        else:
            print_command = [
                "lp", "-n", str(self.preview_copies_input.text), "-P", page_numbers, file_path]

        return print_command

    def validate_input(self):
        if not self.preview_page_numbers_input.text or not self.preview_copies_input.text:
            popup = Popup(title='Error', content=Label(
                text='Please enter both page numbers and copies'),
                size_hint=(None, None), size=(400, 200))
            popup.open()
            Clock.schedule_once(lambda dt: self.dismiss_popup(popup), 4)
            return False
        return True


class MyApp(App):
    def build(self):
        return PrintMenu()


if __name__ == "__main__":
    MyApp().run()
