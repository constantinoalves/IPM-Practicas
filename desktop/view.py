import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

WINDOW_PADDING: int = 10

# Definicion de variables (tmp)
frontmark = "<span foreground=\"#25A18E\" size='50pt'><b>"
endmark = "</b></span>"
#probando main branch


class View():

    # key = Gdk.KEY_

    def __init__(self):
        self.create_ui()

    def run(self):
        self.win.show_all()
        Gtk.main()

    def quit(self):
        Gtk.main_quit()

    def create_ui(self):
        # Creación de la ventana.
        self.win = Gtk.Window(title="CheatSheat")
        self.win.set_default_size(700, 500)
        self.win.set_border_width(10)
        self.win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.command_list = Gtk.ListStore(str)

        # Divisor de pantalla
        paned = Gtk.HPaned()
        self.win.add(paned)
        tamX = self.win.get_default_size()[0]
        paned.set_position(tamX * 0.35)
        # paned.set_size_request(200,-1) # -> Ancho de la ventana entera. 

        # Caja izquierda
        left_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL,
                           homogeneous=False,
                           margin_start=WINDOW_PADDING,
                           margin_end=WINDOW_PADDING)

        paned.add1(left_box)

        self.searchbar = Gtk.SearchBar(valign=Gtk.Align.START, vexpand=False)
        left_box.pack_start(self.searchbar, False, False, 0)

        self.searchentry = Gtk.SearchEntry(valign=Gtk.Align.START, vexpand=False)
        self.searchbar.connect_entry(self.searchentry)
        self.searchbar.add(self.searchentry)
        self.searchentry.set_placeholder_text("Buscar Comando...")
        self.searchbar.set_search_mode(True)

        scroll_izq = Gtk.ScrolledWindow()
        left_box.pack_start(scroll_izq, True, True, 0)

        historial = Gtk.ListBox(valign=Gtk.Align.FILL, vexpand=True, hexpand=True)
        scroll_izq.add(historial)

        # Caja derecha
        caja_der = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL,
                           homogeneous=False,
                           margin_start=WINDOW_PADDING,
                           margin_end=WINDOW_PADDING)
        paned.add2(caja_der)

        self.titulo = Gtk.Label(valign=Gtk.Align.START)
        caja_der.pack_start(self.titulo, False, False, 0)
        scroll_der = Gtk.ScrolledWindow()
        caja_der.pack_start(scroll_der, True, True, 0)

        self.expanderContainer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                         spacing=WINDOW_PADDING)
        scroll_der.add(self.expanderContainer)

        self.resetText()
        self.numElements = 0

    # Definicion de shortcuts
    def on_key_event(self, widget, event, handler):
        shortcut = Gtk.accelerator_get_label(event.keyval, event.state)
        if shortcut in ("Ctrl+F", "Ctrl+Mod2+F"):  # Mostar o esconder la barra de búsqueda
            if self.searchbar.get_search_mode():
                self.searchbar.set_search_mode(False)
            else:
                self.searchbar.set_search_mode(True)

        elif shortcut in ("Return", "Mod2+Return"):  # Pulsar enter para buscar

            busqueda = self.searchentry.get_text()  # Se obtiene el comando que se escribió en la barra de busqueda y se manda al handler
            self.searchentry.set_text('')  # Se vacía la barra de búsqueda
            handler.update_command(busqueda)  # Se pasa el comando a buscar como parametro

        elif shortcut in ("Ctrl+H", "Ctrl+Mod2+H"):  # Shortcut para cerrar todos los expanders
            if self.numElements != 0:  # Si no existe ningun expander no hace nada
                isExpanded = self.commandTitle["expander" + str(0)].get_expanded()  # Coge el estado del primero
                for i in range(self.numElements):
                    if isExpanded:  # Si está expandido.
                        self.commandTitle["expander" + str(i)].set_expanded(False)
                    else:
                        self.commandTitle["expander" + str(i)].set_expanded(True)

        elif shortcut in ("Ctrl+D", "Ctrl+Mod2+D"):  # Shortcut para probar la ventana de carga
            self.loading_win()
        elif shortcut in ("Ctrl+E", "Ctrl+Mod2+E"):
            self.loadingWindow.close()
    def actualizar_comando(self, data, busqueda):

        self.titulo.set_markup(frontmark + busqueda + endmark)
        self.titulo.set_property('halign', Gtk.Align.START)  # Coloca el texto de búsqueda a la izquierda del todo

        descriptions = []
        commands = []
        tags = []
        marks = []

        for i in data:
            if i.commands == '':
                commands.insert(0, "tldr:" + busqueda)
                descriptions.insert(0,i.description.replace("<", "&#60;").replace(">", "&#62;"))
                tags.insert(0,i.tags.replace("<", "&#60;").replace(">", "&#62;"))
                marks.insert(0,i.mark)
            else:
                descriptions.append(i.description.replace("<", "&#60;").replace(">", "&#62;"))
                commands.append(i.commands.replace("<", "&#60;").replace(">", "&#62;"))
                tags.append(i.tags.replace("<", "&#60;").replace(">", "&#62;"))
                marks.append(i.mark)

        if self.numElements != 0:
            for i in range(self.numElements):
                self.commandTitle["expander" + str(i)].hide()

        self.expanderCommands(commands, tags, descriptions)

    # Ventana de error
    def error_win(self):
        dialog = Gtk.MessageDialog(transient_for=self.win,
                                   flags=0,
                                   message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.OK,
                                   text="Comando no encontrado.")
        dialog.format_secondary_text("Inserta un comando valido, por favor.")
        dialog.run()
        dialog.destroy()

    # Si la búsqueda está vacía informa al usuario.
    def info_win(self):
        dialog = Gtk.MessageDialog(transient_for=self.win,
                                   flags=0,
                                   message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK,
                                   text="Introduce un comando")
        dialog.format_secondary_text("Ejemplo: ls, pwd, cd...")
        dialog.run()
        dialog.destroy()

        # Ventana de carga con spinner

    def loading_win(self):
        self.loadingWindow = Gtk.Window(transient_for=self.win)  # Definir el centro de la ventana
        self.loadingWindow.set_decorated(False)  # Para que la ventana no tenga para cerrarse
        self.loadingWindow.set_default_size(150,
                                            50)  # La hacemos rectangular y pequeña para que se ajuste al tamaño que le toca
        self.loadingWindow.set_position(
            Gtk.WindowPosition.CENTER_ON_PARENT)  # Aparece exclusivamente en el centro de la ventana

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        self.loadingWindow.add(grid)

        tituloLoadWin = Gtk.Label(valign=Gtk.Align.CENTER)
        tituloLoadWin.set_markup("<span size='15pt'><b>Loading...</b></span>")

        spinner = Gtk.Spinner()
        spinner.set_vexpand(True)
        spinner.set_hexpand(True)

        grid.attach(spinner, 0, 0, 2, 10)
        grid.attach_next_to(tituloLoadWin, spinner, 1, 5, 10)



        spinner.start()

        self.loadingWindow.show_all()


    # Función que pone el titulo y el textview a 0
    def resetText(self):
        self.titulo.set_markup(frontmark + "<u>" + "Cheat Sheat" + "</u>" + endmark)
        self.titulo.set_property('halign', Gtk.Align.CENTER)  # Coloca el texto en el centro

    """
    Adds the cheatsh into different strings[] to display it on the screen. 

    @param string   expander        comando que has buscado.  
    @param string[] commands        array con las combinaciones posibles de "expander"
    @param string[] tags            opciones de los comandos. 
    @param string[] descripciones   las distintas descripciones de los comandos. 
    
    @return void(). 
    """

    def expanderCommands(self, commands, tags, descripciones):

        expander = "expander"  # [ls] [ls-a]  [ls -b]
        description = "desciption"

        formatoInicioCommmandTitle = "<span size='20pt'><b>"
        formatFinCommandTitle = "</b></span>"

        formatoInicioCommmandDescription = "<span size='15pt'><i>"
        formatFinCommandDescription = "</i></span>"

        self.commandTitle = {}  # > commandTitle
        self.commandDescription = {}  # commandDescription.

        self.numElements = len(commands)

        for i in range(self.numElements):
            # > commandTitle.
            self.commandTitle[expander + str(i)] = Gtk.Expander(label=formatoInicioCommmandTitle
                                                                      + commands[i] + ' ' + tags[i]
                                                                      + formatFinCommandTitle)
            self.commandTitle[expander + str(i)].set_use_markup(True)
            self.commandTitle[expander + str(i)].set_expanded(False)
            self.expanderContainer.add(self.commandTitle[expander + str(i)])

            #       commandDescription. 
            self.commandDescription[description + str(i)] = Gtk.Label()
            self.commandDescription[description + str(i)].set_alignment(0, 1)
            self.commandDescription[description + str(i)].set_markup(
                formatoInicioCommmandDescription + descripciones[i] + formatFinCommandDescription)

            # Asignación de cada descripción a su respectivo comando
            self.commandTitle[expander + str(i)].add(self.commandDescription[description + str(i)])
            self.commandTitle[expander + str(i)].show_all()

    def connect_signals(self, handler):
        self.win.connect("destroy", handler.quit)
        self.win.connect("key-press-event", self.on_key_event, handler)
