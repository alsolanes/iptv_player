import IPTV
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QListWidget, QListWidgetItem

class IPTVApp(QWidget):
    def __init__(self):
        super().__init__()

        # Crear widgets
        self.llista_lbl = QLabel('Llista M3U:')
        self.llista_le = QLineEdit()
        self.llista_bt = QPushButton('Obrir')
        self.play_bt = QPushButton('Reproduir')
        self.stop_bt = QPushButton('Aturar')
        self.canals_lbl = QLabel('Canals:')
        self.canals_lw = QListWidget()

        # Connexió de senyals i slots
        self.llista_bt.clicked.connect(self.obrir_llista)
        self.play_bt.clicked.connect(self.reproduir)
        self.stop_bt.clicked.connect(self.aturar)
        self.canals_lw.itemClicked.connect(self.canal_seleccionat)

        # Configuració de la disposició
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.llista_lbl)
        hbox1.addWidget(self.llista_le)
        hbox1.addWidget(self.llista_bt)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.play_bt)
        hbox2.addWidget(self.stop_bt)
        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.canals_lbl)
        vbox2.addWidget(self.canals_lw)
        hbox3 = QHBoxLayout()
        hbox3.addLayout(vbox1)
        hbox3.addLayout(vbox2)
        self.setLayout(hbox3)

        # Inicialitzar l'objecte IPTV
        self.iptv = IPTV.IPTV()

    def obrir_llista(self):
        # Obrir finestra per seleccionar el fitxer M3U
        filename, _ = QFileDialog.getOpenFileName(self, 'Obrir fitxer', '', 'M3U files (*.m3u)')
        if filename:
            self.llista_le.setText(filename)
            self.iptv.load(filename)
            # Afegir els canals a la llista
            for canal in self.iptv.channels:
                item = QListWidgetItem(canal['name'])
                self.canals_lw.addItem(item)

    def reproduir(self):
        # Començar la reproducció
        self.iptv.play()

    def aturar(self):
        # Aturar la reproducció
        self.iptv.stop()

    def canal_seleccionat(self, item):
        # Seleccionar el canal escollit per l'usuari
        index = self.canals_lw.indexFromItem(item).row()
        self.iptv.select_channel(index)

if __name__ == '__main__':
    # Crear l'aplicació i mostrar la finestra
    app = QApplication([])
    iptv_app = IPTVApp()
    iptv_app.show()
    app.exec_()
