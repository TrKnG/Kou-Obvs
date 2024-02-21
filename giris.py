import psycopg2
import PySimpleGUI as sg
from ogrenci import on_ana
from ogretmen import ot_ana
from atama import rastgele_ders_ata
def create_connection():
    return psycopg2.connect(
        dbname="OBS2",
        user="postgres",
        password="1245",
        host="localhost",
        port="5432"
    )
def get_incoming_requests():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM talepler """)
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return requests
def display_demands_buttons():
    requests = get_incoming_requests()

    layout = [
        [sg.Listbox(values=requests, size=(60, 20), key="-REQUESTS-", enable_events=True)],
        [sg.Button("Onayla", key="-APPROVE-"), sg.Button("Geri Dön")]
    ]

    window = sg.Window("Yönetici Talepleri", layout)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Geri Dön"):
            break
        elif event == "-APPROVE-":
            selected_request = values["-REQUESTS-"]
            if selected_request:

                request_id = selected_request[0][0]
                approve_request(request_id,selected_request[0][2])

    window.close()


def approve_request(request_id,teacher_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE talepler SET yonetici_onay = TRUE WHERE talep_id = %s", (request_id,))
        conn.commit()
        cursor.execute(f"SELECT kontenjan FROM ogretmen WHERE ogretmen_id = %s", (teacher_id,))
        row = cursor.fetchall()
        kontenjan = row[0][0]
        kontenjan = kontenjan -1
        cursor.execute("UPDATE ogretmen SET kontenjan = %s WHERE ogretmen_id = %s",
                       (kontenjan,teacher_id))
        conn.commit()
        cursor.execute(f"SELECT * FROM talepler WHERE talep_id = %s", (request_id,))
        row = cursor.fetchall()
        ogrenci_id=row[0][1]
        ders_id = row[0][3]
        cursor.execute("INSERT INTO ogrenci_ders (ogrenci_id,ders_id,ogretmen_id) VALUES (%s,%s,%s)",
                       (ogrenci_id,ders_id,teacher_id))
        conn.commit()
        sg.popup("Onaylanma tamamlandı")
    except psycopg2.Error as e:
        print(f"Talep onaylanırken bir hata oluştu: {e}")
    cursor.close()
    conn.close()
def get_student_data(ogrenci_id, table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE ogrenci_id = %s", (ogrenci_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
def get_teacher_data(ogretmen_id, table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE ogretmen_id = %s", (ogretmen_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_ogretmen_ids():
    conn= create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ogretmen_id FROM ogretmen")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ids
def get_ogrenci_ids():
    conn= create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ogrenci_id FROM ogrenci")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ids
def get_ogrenci_id(isim,soyisim):
    conn= create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT ogrenci_id FROM ogrenci WHERE isim = %s AND soyisim = %s", (isim, soyisim))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
def get_ogretmen_id(isim,soyisim):
    conn= create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT ogretmen_id FROM ogretmen WHERE isim = %s AND soyisim = %s", (isim, soyisim))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

# def get_yonetici_id(isim,soyisim):
#     conn= create_connection()
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT yonetici_id FROM yonetici WHERE isim = %s AND soyisim = %s", (isim, soyisim))
#     result = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return result

def display_student_buttons():
    ids = [str(id) for id in get_ogrenci_ids()]
    layout = [[sg.Button(str(id))] for id in ids] + [[sg.Button('Geri Dön')]]
    window = sg.Window('Öğrenci IDleri', layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Geri Dön':
            break
        elif str(event) in ids:
            ogrenci_bilgi = get_student_data(event,"ogrenci")
            ogrenci_puan = get_student_data(event, "ogrenci_puan")
            ogrenci_ilgi = get_student_data(event, "ogrenci_ilgi")
            layout = [
                [sg.Text("Öğrenci Bilgisi")],
                [sg.Listbox(ogrenci_bilgi, size=(80, 5))],
                [sg.Text("Öğrenci Puanları")],
                [sg.Listbox(ogrenci_puan, size=(80, 5))],
                [sg.Text("Öğrenci İlgileri")],
                [sg.Listbox(ogrenci_ilgi, size=(80, 5))],
                [sg.Button("Kapat")]
            ]
            window = sg.Window(f"{event} ID'li Öğrenci Bilgisi", layout)
            while True:
                event, values = window.read()
                if event == sg.WINDOW_CLOSED or event == "Kapat":
                    break

        else:
            print(f"'{event}' ID'li öğrenciye tıklandı")
    window.close()
def display_teacher_buttons():
    ids = [str(id) for id in get_ogretmen_ids()]
    layout = [[sg.Button(str(id))] for id in ids] + [[sg.Button('Geri Dön')]]
    window = sg.Window('Öğretmen IDleri', layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Geri Dön':
            break
        elif str(event) in ids:
            ogretmen_bilgi = get_teacher_data(event,"ogretmen")
            ogretmen_ders = get_teacher_data(event, "ogretmen_ders")
            ogretmen_ilgi = get_teacher_data(event, "ogretmen_ilgi")
            layout = [
                [sg.Text("Öğretmen Bilgisi")],
                [sg.Listbox(ogretmen_bilgi, size=(80, 5))],
                [sg.Text("Öğretmen Dersleri")],
                [sg.Listbox(ogretmen_ders, size=(80, 5))],
                [sg.Text("Öğretmen İlgileri")],
                [sg.Listbox(ogretmen_ilgi, size=(80, 5))],
                [sg.Button("Kapat")]
            ]
            window = sg.Window(f"{event} ID'li Öğretmen Bilgisi", layout)
            while True:
                event, values = window.read()
                if event == sg.WINDOW_CLOSED or event == "Kapat":
                    break

        else:
            print(f"'{event}' ID'li öğrenciye tıklandı")
    window.close()
def user_login(user_type, isim, soyisim):
    with create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {user_type} WHERE isim = %s AND soyisim = %s", (isim, soyisim))
            result = cursor.fetchone()
            return bool(result)

def g_ana():
    layout = [
        [sg.Text('Kullanıcı Giriş', size=(25, 1), justification='center', font=("Helvetica", 25))],
        [sg.Text('Kullanıcı Tipi', size=(15, 1)), sg.Combo(values=['yonetici', 'ogretmen', 'ogrenci'], default_value='yonetici', size=(20, 1), key='-USERTYPE-')],
        [sg.Text('İsim', size=(15, 1)), sg.InputText(size=(20, 1), key='-ISIM-')],
        [sg.Text('Soyisim', size=(15, 1)), sg.InputText(size=(20, 1), key='-SOYISIM-')],
        [sg.Button('Giriş'), sg.Button('Vazgeç')]
    ]

    window = sg.Window('Kullanıcı Giriş', layout, size=(500, 300))

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Vazgeç':
            break
        elif event == 'Giriş':
            if user_login(values['-USERTYPE-'], values['-ISIM-'], values['-SOYISIM-']):
                sg.popup('Başarıyla giriş yaptınız!')
                kullanici_tipi = values['-USERTYPE-']
                kullanici_isim = values['-ISIM-']
                kullanici_soyisim = values['-SOYISIM-']
                if kullanici_tipi == 'yonetici':
                    layout = [
                        [sg.Button('Öğrenciler', size=(15, 2)),sg.Button('Öğretmenler', size=(15, 2))],
                        [sg.Button('Talepler', size=(32, 2))],
                        [sg.Button('Rastgele Atama', size=(32, 2))],
                        [sg.Button('Çıkış', size=(32, 2))]
                    ]
                    # yonetici_id= get_yonetici_id(kullanici_isim,kullanici_soyisim)
                    window = sg.Window('Ana Menü', layout)
                    while True:
                        event, values = window.read()
                        if event == sg.WINDOW_CLOSED or event == 'Çıkış':
                            break
                        elif event == 'Öğrenciler':
                            window.hide()
                            display_student_buttons()
                            window.un_hide()
                        elif event == 'Öğretmenler':
                            window.hide()
                            display_teacher_buttons()
                            window.un_hide()
                        elif event == 'Talepler':
                            window.hide()
                            display_demands_buttons()
                            window.un_hide()
                        elif event == 'Rastgele Atama':
                            window.hide()
                            rastgele_ders_ata()
                            sg.popup('Her öğrenciye birer ders atandı')
                            window.un_hide()

                    window.close()
                elif kullanici_tipi == 'ogrenci':
                    window.hide()
                    ogrenci_id = get_ogrenci_id(kullanici_isim,kullanici_soyisim)
                    on_ana(ogrenci_id)
                    window.un_hide()
                elif kullanici_tipi == 'ogretmen':
                    window.hide()
                    ogretmen_id = get_ogretmen_id(kullanici_isim,kullanici_soyisim)
                    ot_ana(ogretmen_id)
                    window.un_hide()



            else:
                sg.popup_error('Giriş başarısız. Lütfen bilgilerinizi kontrol edin.')


    window.close()
if __name__ == '__main__':
    g_ana()