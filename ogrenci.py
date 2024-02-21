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

def get_ogretmen_ids():
    conn= create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ogretmen_id FROM ogretmen")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ids

def get_teacher_data(ogretmen_id, table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE ogretmen_id = %s", (ogretmen_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

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
                [sg.Listbox(ogretmen_bilgi, size=(30, 5))],
                [sg.Text("Öğretmen Dersleri")],
                [sg.Listbox(ogretmen_ders, size=(30, 5))],
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

def get_all_teachers():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ogretmen_id, isim FROM ogretmen")
    teachers = cursor.fetchall()
    cursor.close()
    conn.close()
    return teachers

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

def get_incoming_messages(ogrenci_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT ogretmen.isim, ogretmen.soyisim, mesajlar.mesaj_icerik 
                      FROM mesajlar JOIN ogretmen ON mesajlar.ogretmen_id = ogretmen.ogretmen_id
                      WHERE mesajlar.ogrenci_id = %s AND mesajlar.kimden = 'ogretmen'""", (ogrenci_id,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return messages
def mesaj_ekrani(ogrenci_id):
    layout = [
        [sg.Button("Gelen Mesajlar"), sg.Button("Mesaj Gönder"), sg.Button("Geri Dön")]
    ]

    window = sg.Window("Mesaj İşlemleri", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WINDOW_CLOSED, "Geri Dön"):
            break
        elif event == "Gelen Mesajlar":
            gelen_mesajlar(ogrenci_id)
        elif event == "Mesaj Gönder":
            mesaj_gonder_ekrani(ogrenci_id)

    window.close()
def gelen_mesajlar(ogrenci_id):
    messages = get_incoming_messages(ogrenci_id)
    message_list = [f"{msg[0]} {msg[1]}: {msg[2]}" for msg in messages]

    layout = [
        [sg.Listbox(values=message_list, size=(60, 30))],
        [sg.Button("Geri Dön")]
    ]

    window = sg.Window("Gelen Mesajlar", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WINDOW_CLOSED, "Geri Dön"):
            break

    window.close()
def mesaj_gonder_ekrani(ogrenci_id):
    teachers = get_all_teachers()
    layout = [
        [sg.Button(teacher[1], key=f"TEACHER_{teacher[0]}") for teacher in teachers],
        [sg.Multiline(size=(50, 20), key="-MESSAGE_CONTENT-")],
        [sg.Button("Gönder", key="-SEND_MESSAGE-"), sg.Button("Geri Dön")]
    ]

    window = sg.Window("Mesaj Gönder", layout)

    selected_teacher_id = None

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Geri Dön"):
            break
        elif "TEACHER_" in event:
            selected_teacher_id = int(event.split("_")[1])
        elif event == "-SEND_MESSAGE-" and selected_teacher_id:
            mesaj_gonder(ogrenci_id, selected_teacher_id, values["-MESSAGE_CONTENT-"], "ogrenci")
            sg.popup("Mesaj başarıyla gönderildi!")

    window.close()

def get_teacher_courses():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""SELECT ogretmen_ders.ogretmen_id, ogretmen_ders.ders_id, dersler.ders_kodu
                      FROM ogretmen_ders 
                      JOIN dersler ON ogretmen_ders.ders_id = dersler.ders_id""")
    courses = cursor.fetchall()
    connection.close()
    return courses


def create_request(ogrenci_id, ogretmen_id, ders_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO talepler (ogrenci_id, ogretmen_id, ders_id) 
                          VALUES (%s, %s, %s)
                          ON CONFLICT (ogrenci_id, ogretmen_id, ders_id) 
                          DO UPDATE SET ogrenci_id = EXCLUDED.ogrenci_id
                          RETURNING talep_id""",
                       (ogrenci_id, ogretmen_id, ders_id))
        talep_id = cursor.fetchone()[0]
        conn.commit()
    except psycopg2.Error as e:
        print(f"Talep eklenirken bir hata oluştu: {e}")
        talep_id = None

    cursor.close()
    conn.close()

    return talep_id


def student_page(student_id):
    courses = get_teacher_courses()
    layout = [
        [sg.Text(f"Merhaba, {student_id} ID'li öğrenci!")],
        [sg.Listbox(values=[f"Öğretmen ID: {course[0]}, Ders Kodu: {course[2]}" for course in courses], size=(50, 30),
                    key="-COURSE-", enable_events=True)],
        [sg.Button("Talep Oluştur"), sg.Button("Çıkış")]
    ]

    window = sg.Window("Öğrenci Sayfası", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Çıkış":
            break
        elif event == "Talep Oluştur":
            selected_course_info = values["-COURSE-"][0].split(', ')
            ogretmen_id = int(selected_course_info[0].split(': ')[1])
            ders_kodu = selected_course_info[1].split(': ')[1]
            ders_id = [course[1] for course in courses if course[2] == ders_kodu][0]
            create_request(student_id, ogretmen_id, ders_id)
            sg.popup(f"{ders_kodu} kodlu ders için talep oluşturuldu!")

    window.close()

def on_ana(student_id):
    layout = [
        [sg.Text(f"Merhaba, {student_id} ID'li öğrenci!")],
        [sg.Button("Talep Oluştur"), sg.Button("Mesajlar"),sg.Button("Öğretmenler"), sg.Button("Çıkış")]
    ]

    window = sg.Window("Öğrenci Ana Sayfası", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Çıkış":
            break
        elif event == "Talep Oluştur":
            student_page(student_id)
        elif event == "Mesajlar":
            mesaj_ekrani(student_id)
            pass
        elif event == "Öğretmenler":
            display_teacher_buttons()
            pass

    window.close()

