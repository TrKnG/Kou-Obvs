import PySimpleGUI as sg
import psycopg2

def create_connection():
    return psycopg2.connect(
        dbname="OBS2",
        user="postgres",
        password="1245",
        host="localhost",
        port="5432"
    )

def get_student_data(ogrenci_id, table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE ogrenci_id = %s", (ogrenci_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_ogrenci_ids():
    conn= create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ogrenci_id FROM ogrenci")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ids

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

def get_all_students():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ogrenci_id, isim FROM ogrenci")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return students


def get_incoming_messages_for_teacher(ogretmen_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT ogrenci.isim, ogrenci.soyisim, mesajlar.mesaj_icerik 
                      FROM mesajlar JOIN ogrenci ON mesajlar.ogrenci_id = ogrenci.ogrenci_id
                      WHERE mesajlar.ogretmen_id = %s AND mesajlar.kimden = 'ogrenci'""", (ogretmen_id,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return messages


def ogretmen_mesaj_ekrani(ogretmen_id):
    layout = [
        [sg.Button("Gelen Mesajlar"), sg.Button("Mesaj Gönder"), sg.Button("Geri Dön")]
    ]

    window = sg.Window("Mesaj İşlemleri - Öğretmen", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WINDOW_CLOSED, "Geri Dön"):
            break
        elif event == "Gelen Mesajlar":
            ogretmen_gelen_mesajlar(ogretmen_id)
        elif event == "Mesaj Gönder":
            ogretmen_mesaj_gonder_ekrani(ogretmen_id)

    window.close()


def ogretmen_gelen_mesajlar(ogretmen_id):
    messages = get_incoming_messages_for_teacher(ogretmen_id)
    message_list = [f"{msg[0]} {msg[1]}: {msg[2]}" for msg in messages]

    layout = [
        [sg.Listbox(values=message_list, size=(60, 30))],
        [sg.Button("Geri Dön")]
    ]

    window = sg.Window("Gelen Mesajlar - Öğretmen", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WINDOW_CLOSED, "Geri Dön"):
            break

    window.close()

def mesaj_gonder(ogrenci_id, ogretmen_id, mesaj_icerik, kimden):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO mesajlar (ogrenci_id, ogretmen_id, mesaj_icerik, kimden) VALUES (%s, %s, %s, %s)",
                       (ogrenci_id, ogretmen_id, mesaj_icerik, kimden))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Mesaj gönderilirken bir hata oluştu: {e}")

    cursor.close()
    conn.close()


def ogretmen_mesaj_gonder_ekrani(ogretmen_id):
    students = get_all_students()
    layout = [
        [sg.Button(student[1], key=f"STUDENT_{student[0]}") for student in students],
        [sg.Multiline(size=(50, 20), key="-MESSAGE_CONTENT-")],
        [sg.Button("Gönder", key="-SEND_MESSAGE-"), sg.Button("Geri Dön")]
    ]

    window = sg.Window("Mesaj Gönder - Öğretmen", layout)

    selected_student_id = None

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Geri Dön"):
            break
        elif "STUDENT_" in event:
            selected_student_id = int(event.split("_")[1])
        elif event == "-SEND_MESSAGE-" and selected_student_id:
            mesaj_gonder(selected_student_id, ogretmen_id, values["-MESSAGE_CONTENT-"], "ogretmen")
            sg.popup("Mesaj başarıyla gönderildi!")

    window.close()

def get_incoming_requests(ogretmen_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT ogrenci.isim, ogrenci.soyisim, dersler.ders_kodu, talepler.ogrenci_id, talepler.ders_id 
                      FROM talepler 
                      JOIN ogrenci ON talepler.ogrenci_id = ogrenci.ogrenci_id 
                      JOIN dersler ON talepler.ders_id = dersler.ders_id 
                      WHERE talepler.ogretmen_id = %s""", (ogretmen_id,))
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return requests

def approve_request(ogrenci_id, ders_id, ogretmen_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""UPDATE talepler SET ogretmen_onay = TRUE 
                          WHERE ogrenci_id = %s AND ders_id = %s AND ogretmen_id = %s""",
                       (ogrenci_id, ders_id, ogretmen_id))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Talep onaylanırken bir hata oluştu: {e}")
    cursor.close()
    conn.close()

def ogretmen_talep_ekrani(ogretmen_id):
    requests = get_incoming_requests(ogretmen_id)
    layout = [
        [sg.Listbox(values=[f"Öğrenci: {req[0]} {req[1]}, Ders: {req[2]}" for req in requests], size=(50, 30), key="-REQUEST-", enable_events=True)],
        [sg.Button("Onayla"), sg.Button("Geri Dön")]
    ]

    window = sg.Window("Gelen Talepler", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Geri Dön":
            break
        elif event == "Onayla":
            selected_request_info = values["-REQUEST-"][0].split(', ')
            ogrenci_name = " ".join(selected_request_info[0].split(': ')[1].split(" ")[0:2])
            ders_kodu = selected_request_info[1].split(': ')[1]
            ogrenci_id = [req[3] for req in requests if req[0] + " " + req[1] == ogrenci_name and req[2] == ders_kodu][0]
            ders_id = [req[4] for req in requests if req[0] + " " + req[1] == ogrenci_name and req[2] == ders_kodu][0]
            approve_request(ogrenci_id, ders_id, ogretmen_id)
            sg.popup(f"{ders_kodu} kodlu ders için talep onaylandı!")

    window.close()

def ot_ana(ogretmen_id):
    layout = [
        [sg.Text(f"Merhaba, {ogretmen_id} ID'li öğretmen!")],
        [sg.Button("Gelen Talepler"), sg.Button("Mesajlar"), sg.Button("Öğrenciler"), sg.Button("Çıkış")]
    ]

    window = sg.Window("Öğretmen Ana Sayfası", layout)

    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED or event == "Çıkış":
            break
        elif event == "Gelen Talepler":
            ogretmen_talep_ekrani(ogretmen_id)
        elif event == "Mesajlar":
            ogretmen_mesaj_ekrani(ogretmen_id)
        elif event == "Öğrenciler":
            display_student_buttons()

    window.close()

