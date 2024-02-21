from giris import g_ana
import kayit
import PySimpleGUI as sg

class MainClass:
    def display_main_window(self):
        layout = [
            [sg.Text('Ana Menü', size=(25, 1), justification='center', font=("Helvetica", 25))],
            [sg.Button('Giriş', size=(25, 2)), sg.Button('Kayıt', size=(25, 2))],
            [sg.Button('Kapat', size=(50, 1))]
        ]

        window = sg.Window('Ana Menü', layout, size=(350, 200))

        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == 'Kapat':
                break
            elif event == 'Giriş':
                g_ana()
            elif event == 'Kayıt':
                kayit.main()


        window.close()

if __name__ == '__main__':
    main_app = MainClass()
    main_app.display_main_window()
