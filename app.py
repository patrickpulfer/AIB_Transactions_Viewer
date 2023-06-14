from pathlib import Path
import sys
import csv
import os
import random
import gi

gi.require_version(namespace='Gtk', version='4.0')
gi.require_version(namespace='Adw', version='1')

from gi.repository import Adw, Gio, Gtk
from gi.repository.GdkPixbuf import Pixbuf
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models.transactions
import services.csv
import services.database


#temp_file = 'Transaction_Export.csv'
#temp_dict = csv.get_dictionary_from_csv(temp_file)


#print(temp_database_results)


Adw.init()


class Dialog(Adw.MessageDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_heading(heading='Are you sure?')
        self.set_body(body='All stored records will be lost.')
        self.add_response(Gtk.ResponseType.CANCEL.value_nick, 'Cancel')
        self.set_response_appearance(
            response=Gtk.ResponseType.CANCEL.value_nick,
            appearance=Adw.ResponseAppearance.DESTRUCTIVE
        )
        self.add_response(Gtk.ResponseType.OK.value_nick, 'OK')
        self.set_response_appearance(
            response=Gtk.ResponseType.OK.value_nick,
            appearance=Adw.ResponseAppearance.SUGGESTED
        )
        self.connect('response', self.dialog_response)

    def dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK.value_nick:
            print('Botão OK pressionado')
            results = database_service.delete_all_records()
            print(results)
        elif response == Gtk.ResponseType.CANCEL.value_nick:
            print('Botão CANCELAR pressionado')


class SettingsWindow(Gtk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_modal(modal=True)
        self.set_title(title='Settings')
        self.set_default_size(width=int(1366 / 3), height=int(768 / 3))
        self.set_size_request(width=int(1366 / 3), height=int(768 / 3))

        vbox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_margin_top(margin=12)
        vbox.set_margin_end(margin=12)
        vbox.set_margin_bottom(margin=12)
        vbox.set_margin_start(margin=12)
        vbox.set_valign(Gtk.Align.CENTER)
        self.set_child(child=vbox)

        # Button
        button_delete_records = Gtk.Button.new_with_label('Delete All Records')
        button_delete_records.add_css_class(css_class='suggested-action')
        button_delete_records.connect('clicked', self.on_window_button_close_clicked)
        vbox.append(child=button_delete_records)

        self.show()

    def on_window_button_close_clicked(self, widget):
        dialog = Dialog(transient_for=self)
        dialog.present()
    
    def dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK.value_nick:
            print('Botão OK pressionado')
        elif response == Gtk.ResponseType.CANCEL.value_nick:
            print('Botão CANCELAR pressionado')


class DialogSelecFolder(Gtk.FileChooserDialog):
    
    home = Path.home()

    parent = ''

    def __init__(self, parent):
        super().__init__(transient_for=parent, use_header_bar=True)
        #self.select_multiple = select_multiple

        self.parent = parent

        self.set_action(action=Gtk.FileChooserAction.OPEN)
        title = 'Select a File'
        self.set_title(title=title)
        self.set_modal(modal=True)
        self.connect('response', self.dialog_response)
        self.set_current_folder(
            Gio.File.new_for_path(path=str(self.home)),
        )

        self.add_buttons(
            '_Cancel', Gtk.ResponseType.CANCEL,
            '_Select', Gtk.ResponseType.OK
        )
        btn_select = self.get_widget_for_response(
            response_id=Gtk.ResponseType.OK,
        )

        btn_select.add_css_class(css_class='suggested-action')
        btn_cancel = self.get_widget_for_response(
            response_id=Gtk.ResponseType.CANCEL,
        )
        btn_cancel.add_css_class(css_class='destructive-action')

        csv_filter = Gtk.FileFilter()
        csv_filter.set_name(name='CSV Files')
        csv_filter.add_pattern(pattern='.csv')
        csv_filter.add_mime_type(mime_type='text/csv')
        self.add_filter(filter=csv_filter)

        
        text_filter = Gtk.FileFilter()
        text_filter.set_name(name='Text Files')
        text_filter.add_pattern(pattern='.txt')
        text_filter.add_mime_type(mime_type='text/plain')
        self.add_filter(filter=text_filter)

        self.show()

    def dialog_response(self, widget, response):
        parent = self.parent
        if response == Gtk.ResponseType.OK:
            glocalfile = self.get_file()
            print(f'Nome da pasta selecionada: {glocalfile.get_basename()}')
            print(f'Caminho da pasta selecionada: {glocalfile.get_path()}')
            AppWindow.response_From_FileDialog(glocalfile.get_basename(), glocalfile.get_path(), parent)
        widget.close()


class AppWindow(Gtk.ApplicationWindow):

    selected_file = ''
    selected_file_path = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(title='AIB Viewer')
        #self.set_icon('./resources/logo.png')
        self.set_default_size(width=int(1366 / 2), height=int(768 / 2))
        #self.set_size_request(width=int(1366 / 2), height=int(768 / 2))
        #self.set_default_icon(GdkPixbuf.Pixbuf.new_from_file("./resources/logo.png"))
        #self.set_icon_from_file("./resources/logo.png")

        """
        header_bar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=header_bar)
        """

        # Creating a box vertically
        vbox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_child(child=vbox)

        header_bar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=header_bar)

        # Menu
        menu_button_model = Gio.Menu()
        menu_button_model.append('Settings', 'app.preferences')
        menu_button_model.append('About', 'app.about')
        menu_button = Gtk.MenuButton.new()
        menu_button.set_icon_name(icon_name='open-menu-symbolic')
        menu_button.set_menu_model(menu_model=menu_button_model)
        header_bar.pack_end(child=menu_button)


        # File Button
        button_Home = Gtk.Button.new_with_label(label='Home')
        button_Home.set_icon_name(icon_name='go-home-symbolic')
        button_Home.connect('clicked', self.button_Home_Clicked)
        header_bar.pack_start(child=button_Home)

        # New Stack
        self.stack = Gtk.Stack.new()
        self.stack.set_transition_type(
            transition=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )
        self.stack.set_transition_duration(duration=1000)

        """
        Defining Stack Pages
        """
        page1 = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.stack.add_titled(child=page1, name='pagina1', title='Page 1')

        page2 = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.stack.add_titled(child=page2, name='pagina2', title='Page 2')

        page3 = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.stack.add_titled(child=page3, name='pagina3', title='Page 3')

        vbox.append(child=self.stack)


        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        Stack Page 1
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        # Box within Page 1
        vbox_stackpage_1 = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox_stackpage_1.set_margin_top(margin=20)
        vbox_stackpage_1.set_margin_end(margin=20)
        vbox_stackpage_1.set_margin_bottom(margin=20)
        vbox_stackpage_1.set_margin_start(margin=20)
        vbox_stackpage_1.set_vexpand(True)
        page1.append(child=vbox_stackpage_1)

        # Image within vbox_stackpage_1
        image = Gtk.Image.new_from_file(filename='./resources/logo.png')
        image.add_css_class(css_class='size: 20')
        #image = Gtk.Image.new_from_icon_name("user-home-symbolic")
        default_size = Gtk.IconSize.NORMAL
        vbox_stackpage_1.append(child=image)
        image.set_pixel_size(100 * default_size)

        # First Set of Labels
        label1 = Gtk.Label.new(str='AIB Transactions Viewer')
        vbox_stackpage_1.append(child=label1)

        label2 = Gtk.Label.new(str='Add a new report or view previous ones.')
        vbox_stackpage_1.append(child=label2)

        css_provider = Gtk.CssProvider()
        css_data = """
        label {
            font-size: 24px;
        }
        """
        css_provider.load_from_data(css_data, -1)

        context = label1.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        """
        Box: First Choice Area
        """
        hbox_Choice_Area = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        hbox_Choice_Area.set_margin_top(margin=20)
        hbox_Choice_Area.set_margin_end(margin=20)
        hbox_Choice_Area.set_margin_bottom(margin=20)
        hbox_Choice_Area.set_margin_start(margin=20)
        hbox_Choice_Area.set_hexpand(True)
        hbox_Choice_Area.set_halign(align=Gtk.Align.CENTER)
        vbox_stackpage_1.append(child=hbox_Choice_Area)

        # Button in hbox_FileSelectArea
        button_AddNew = Gtk.Button.new()
        button_AddNew.set_margin_start(margin=0)
        button_AddNew.set_margin_end(margin=0)
        button_AddNew.connect('clicked', self.button_AddNew_Clicked)

        button_AddNew.set_halign(Gtk.Align.CENTER)
        hbox_Choice_Area.append(child=button_AddNew)

        button_AddNew_Content = Adw.ButtonContent.new()
        button_AddNew_Content.set_icon_name(icon_name='document-new-symbolic')
        button_AddNew_Content.set_label(label='Add new report')
        button_AddNew_Content.set_use_underline(use_underline=True)
        button_AddNew.set_child(button_AddNew_Content)

        button_Go = Gtk.Button.new()
        button_Go.set_margin_start(margin=0)
        button_Go.set_margin_end(margin=0)
        button_Go.connect('clicked', self.create_and_show_report)

        button_Go.set_halign(Gtk.Align.CENTER)
        hbox_Choice_Area.append(child=button_Go)

        button_Go_Content = Adw.ButtonContent.new()
        button_Go_Content.set_icon_name(icon_name='emblem-documents-symbolic')
        button_Go_Content.set_label(label='Open previous report')
        button_Go_Content.set_use_underline(use_underline=True)
        button_Go.set_child(button_Go_Content)

        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        Stack Page 2
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

        # Box within Page 1
        vbox_stackpage_1 = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox_stackpage_1.set_margin_top(margin=20)
        vbox_stackpage_1.set_margin_end(margin=20)
        vbox_stackpage_1.set_margin_bottom(margin=20)
        vbox_stackpage_1.set_margin_start(margin=20)
        vbox_stackpage_1.set_vexpand(True)
        page2.append(child=vbox_stackpage_1)

        # Image within vbox_stackpage_1
        image = Gtk.Image.new_from_file(filename='./resources/logo.png')
        image.add_css_class(css_class='size: 20')
        #image = Gtk.Image.new_from_icon_name("user-home-symbolic")
        default_size = Gtk.IconSize.NORMAL
        vbox_stackpage_1.append(child=image)
        image.set_pixel_size(100 * default_size)

        # First Set of Labels
        label1 = Gtk.Label.new(str='AIB Transactions Viewer')
        vbox_stackpage_1.append(child=label1)

        label2 = Gtk.Label.new(str='Click the button below to select an exported AIB transactions file.')
        vbox_stackpage_1.append(child=label2)

        css_provider = Gtk.CssProvider()
        css_data = """
        label {
            font-size: 24px;
        }
        """
        
        css_provider.load_from_data(css_data, -1)

        context = label1.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        """
        Box: File Select Area
        """
        hbox_FileSelectArea = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        hbox_FileSelectArea.set_margin_top(margin=20)
        hbox_FileSelectArea.set_margin_end(margin=20)
        hbox_FileSelectArea.set_margin_bottom(margin=20)
        hbox_FileSelectArea.set_margin_start(margin=20)
        hbox_FileSelectArea.set_hexpand(True)
        hbox_FileSelectArea.set_halign(align=Gtk.Align.CENTER)
        vbox_stackpage_1.append(child=hbox_FileSelectArea)

        # Button in hbox_FileSelectArea
        button_FileSelect = Gtk.Button.new()
        button_FileSelect.set_margin_start(margin=0)
        button_FileSelect.set_margin_end(margin=0)
        button_FileSelect.connect('clicked', self.button_FileSelect_Clicked)

        button_FileSelect.set_halign(Gtk.Align.CENTER)
        hbox_FileSelectArea.append(child=button_FileSelect)

        button_FileSelect_Content = Adw.ButtonContent.new()
        button_FileSelect_Content.set_icon_name(icon_name='document-open-symbolic')
        button_FileSelect_Content.set_label(label='Select a new AIB transaction export')
        button_FileSelect_Content.set_use_underline(use_underline=True)
        button_FileSelect.set_child(button_FileSelect_Content)

        # File Select Label
        self.labelFileSelectArea = Gtk.Label.new(str='No file selected')
        hbox_FileSelectArea.append(child=self.labelFileSelectArea)
        """
        End of File Select Area
        """

        # Go button outside of FileSelect Area
        button_Go = Gtk.Button.new()
        button_Go.set_margin_start(margin=0)
        button_Go.set_margin_end(margin=0)
        button_Go.connect('clicked', self.button_Go_Clicked)
        button_Go.add_css_class(css_class='suggested-action')

        button_Go.set_halign(Gtk.Align.CENTER)
        vbox_stackpage_1.append(child=button_Go)

        button_Go_Content = Adw.ButtonContent.new()
        button_Go_Content.set_icon_name(icon_name='emblem-ok-symbolic')
        button_Go_Content.set_label(label='Start!')
        button_Go_Content.set_use_underline(use_underline=True)
        button_Go.set_child(button_Go_Content)


        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        Stack Page 3
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

        # Box within Page 3
        vbox_stackpage_3 = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox_stackpage_3.set_margin_top(margin=20)
        vbox_stackpage_3.set_margin_end(margin=20)
        vbox_stackpage_3.set_margin_bottom(margin=20)
        vbox_stackpage_3.set_margin_start(margin=20)
        vbox_stackpage_3.set_vexpand(True)
        page3.append(child=vbox_stackpage_3)

        # Image within vbox_stackpage_1
        image = Gtk.Image.new_from_file(filename='./resources/logo.png')
        image.add_css_class(css_class='size: 20')
        #image = Gtk.Image.new_from_icon_name("user-home-symbolic")
        default_size = Gtk.IconSize.NORMAL
        vbox_stackpage_3.append(child=image)
        image.set_pixel_size(100 * default_size)

        hbox_BankDetailsArea = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_BankDetailsArea.set_margin_top(margin=20)
        hbox_BankDetailsArea.set_margin_end(margin=20)
        hbox_BankDetailsArea.set_margin_bottom(margin=20)
        hbox_BankDetailsArea.set_margin_start(margin=20)
        hbox_BankDetailsArea.set_hexpand(True)
        hbox_BankDetailsArea.set_halign(align=Gtk.Align.CENTER)
        vbox_stackpage_3.append(child=hbox_BankDetailsArea)

        # Top labels
        label_bank_account = Gtk.Label.new(str='Bank Account:')
        hbox_BankDetailsArea.append(child=label_bank_account)
        self.label_bank_account_value = Gtk.Label.new(str='XXXX,')
        hbox_BankDetailsArea.append(child=self.label_bank_account_value)
        label_bank_sortcode = Gtk.Label.new(str='Sort Code:')
        hbox_BankDetailsArea.append(child=label_bank_sortcode)
        self.label_bank_sortcode_value = Gtk.Label.new(str='XXXX,')
        hbox_BankDetailsArea.append(child=self.label_bank_sortcode_value)
        label_bank_balance = Gtk.Label.new(str='Balance:')
        hbox_BankDetailsArea.append(child=label_bank_balance)
        self.label_bank_balance_value = Gtk.Label.new(str='XXXX')
        hbox_BankDetailsArea.append(child=self.label_bank_balance_value)


        scrolled_window = Gtk.ScrolledWindow.new()
        vbox_stackpage_3.append(child=scrolled_window)
        scrolled_window.set_vexpand(True)

        self.listbox = Gtk.ListBox.new()
        self.listbox.set_selection_mode(mode=Gtk.SelectionMode.NONE)
        self.listbox.add_css_class(css_class='boxed-list')
        scrolled_window.set_child(child=self.listbox)

        

    """
    Functions
    """

    def button_Home_Clicked(self, button):
        self.stack.set_visible_child_name('pagina1')

    def button_AddNew_Clicked(self, button):
        self.stack.set_visible_child_name('pagina2')

    def button_FileSelect_Clicked(self, button):
        DialogSelecFolder(parent=self)

    def response_From_FileDialog(file, path, self):
        self.selected_file_path = path
        self.selected_file = file
        self.labelFileSelectArea.set_text(file)
    
    def button_Go_Clicked(self, button):
        temp_dict = csv.get_dictionary_from_csv(self.selected_file_path)
        database_service.add_from_transaction_file(temp_dict)
        self.create_and_show_report(button)

    def create_and_show_report(self, button):

        # Clear current List
        children = []
        first_row = ''

        for child in children:
            self.listbox.remove(child)

        data_base_results = database_service.get_all_transactions()
        if not data_base_results:
            print('yes')
        else:
            print('no')

        try:
            first_row = data_base_results[0]._mapping
            self.label_bank_account_value.set_text(str(first_row['account_number']) + ',')
            self.label_bank_sortcode_value.set_text(str(first_row['sort_code']) + ',')
            self.label_bank_balance_value.set_text(str(first_row['balance']) + '€')
        except:
            pass


        # Generate new list
        for row in data_base_results:
            row_as_dict = row._mapping

            row_subtitle = str(row_as_dict['transaction_date']) + ', ' + row_as_dict['receiver_name']

            if row_as_dict['type'] == 'Debit':
                row_title = '- ' + str(row_as_dict['amount']) + '€'
            else:
                row_title = '+ ' + str(row_as_dict['amount']) + '€'

            row_expanded = row_as_dict['card_function'] + '\nBalance: ' + str(row_as_dict['balance']) + '€'
            

            if row_as_dict['card_function'] == 'Direct Debit':
                row_icon = 'emblem-synchronizing-symbolic'
            elif row_as_dict['card_function'] == 'Deposit':
                row_subtitle = str(row_as_dict['transaction_date']) + ', ' + row_as_dict['transaction_reference']
                row_icon = 'list-add-symbolic'
            elif row_as_dict['card_function'] == 'ATM':
                row_icon = 'preferences-system-privacy-symbolic'
                row_subtitle = str(row_as_dict['transaction_date']) + ', ATM withdrawal at ' + row_as_dict['location']
            elif row_as_dict['card_function'] == 'Contactless Visa Debit':
                row_icon = 'network-wireless-signal-excellent-symbolic'
            elif row_as_dict['card_function'] == 'Transfer via Mobile App':
                row_icon = 'phone-symbolic'
            elif row_as_dict['card_function'] == 'Bank Transfer':
                row_icon = 'view-fullscreen-symbolic'
            elif row_as_dict['card_function'] == 'Mortgage Payment':
                row_icon = 'go-home-symbolic'
                row_subtitle = str(row_as_dict['transaction_date']) + ', Mortgage Payment'
            elif row_as_dict['card_function'] == 'Card Stamp Duty Fee':
                row_icon = 'view-fullscreen-symbolic'
                row_subtitle = str(row_as_dict['transaction_date']) + ', Card Stamp Duty Fee for ' + row_as_dict['receiver_name']
            else:
                row_icon = 'accessories-text-editor-symbolic'

            #text = '<big>Lorem ipsum</big>\n\nLorem ipsum dolor sit amet, consectetur...'
            #
            #

            icon = Gtk.Image.new_from_icon_name(icon_name=row_icon)

            label = Gtk.Label.new()
            label.set_markup(str=row_expanded)
            label.set_wrap(wrap=True)

            adw_expander_row = Adw.ExpanderRow.new()
            adw_expander_row.add_prefix(widget=icon)
            adw_expander_row.set_title(title=row_title)
            adw_expander_row.set_subtitle(subtitle=row_subtitle)
            adw_expander_row.add_row(child=label)
            self.listbox.append(child=adw_expander_row)
        self.stack.set_visible_child_name('pagina3')


class App(Adw.Application):

    def __init__(self):
        super().__init__(application_id='cloud.pulfer', flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('quit', self.exit_app, ['<primary>q'])
        self.create_action('preferences', self.on_preferences_action)
        self.create_action('about', self.on_about_action)

        csv = services.csv.CSV_Service()
        database_service = services.database.Database_Service(engine, session)

    def on_about_action(self, action, param):
        dialog = Adw.AboutWindow.new()
        dialog.set_transient_for(parent=self.get_active_window())
        dialog.set_application_name('AIB Transactions Viewer')
        dialog.set_version('0.0.1')
        dialog.set_developer_name('Patrick Pulfer')
        dialog.set_license_type(Gtk.License(Gtk.License.MIT_X11))
        dialog.set_comments('Application to view transactions export from AIB Ireland.')
        dialog.set_website('https://pweb.solutions')
        dialog.set_issue_url("https://github.com/issues")
        #dialog.add_credit_section('Contributors', ['Name 01', 'Name 02'])
        #dialog.set_translator_credits('Translator')
        dialog.set_copyright('© 2023 Patrick Pulfer')
        dialog.set_developers(['Patrick Pulfer https://github.com/patrickpulfer/'])
        dialog.set_application_icon('help-about-symbolic')
        dialog.present()
    
    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = AppWindow(application=self)
        win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)

    def on_preferences_action(self, action, param):
        print('Ação app.preferences foi ativa.')
        SettingsWindow()#transient_for=self

    def exit_app(self, action, param):
        self.quit()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)


if __name__ == '__main__':
    import sys

    Base = declarative_base()
    engine = create_engine("sqlite:///database.db", echo=True, connect_args={'check_same_thread':False}, poolclass=StaticPool)
    base_trables = getattr(models.transactions, 'Transactions')
    base_trables.__table__.create(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    csv = services.csv.CSV_Service()
    database_service = services.database.Database_Service(engine, session)

    app = App()
    app.run(sys.argv)
