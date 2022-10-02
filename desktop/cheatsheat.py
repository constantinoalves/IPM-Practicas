#!/usr/bin/env python3
import view
import cheathelper


class Handler:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.connect_signals(self)

    def run(self):
        self.view.run()

    def quit(self, widget):
        self.view.quit()

    def update_command(self, busqueda):
        # El handler recibe el comando a buscar en el parametro busqueda y lo manda al modelo
        data = self.model.get_cheatsheet(busqueda)
        if busqueda == "":  # Si la barra de búsqueda está vacía, avisa al usuario de que debe introducir algún comando por pantalla
            self.view.info_win()
        elif data == []:
                self.view.error_win()
        else:
            self.view.actualizar_comando(data, busqueda)  # En data está la informacion 'En crudo' del comando buscado#        

if __name__ == "__main__":
    model = cheathelper
    view = view.View()
    controller = Handler(model, view)
    controller.run()
