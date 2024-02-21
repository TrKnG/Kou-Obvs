import PySimpleGUI as sg
import psycopg2
import pdfm
import configure
from pdfm import p_ana
from configure import c_ana

def create_connection():
    return psycopg2.connect(
        dbname="OBS2",
        user="postgres",
        password="1245",
        host="localhost",
        port="5432"
    )


def get_all_courses():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ders_kodu FROM dersler")
    courses = cursor.fetchall()
    conn.close()
    return [course[0] for course in courses]
def get_all_ilgiler():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ilgi_alani FROM ilgi_alanlari")
    ilgiler = cursor.fetchall()
    conn.close()
    return [ilgi[0] for ilgi in ilgiler]
def admin_register():
    layout = [
        [sg.Text('Yönetici ID'), sg.InputText(key='admin_id')],
        [sg.Text('İsim'), sg.InputText(key='name')],
        [sg.Text('Soyisim'), sg.InputText(key='surname')],
        [sg.Button('Kaydet'), sg.Button('Geri')]
    ]
    window = sg.Window('Öğrenci Kayıt', layout)
    while True:
        event, values = window.read()
        admin_id = values['admin_id']
        name = values['name']
        surname = values['surname']
        if event == sg.WINDOW_CLOSED or event == 'Geri':
            window.close()
            return
        elif event == 'Kaydet':
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO yonetici (yonetici_id, isim, soyisim) VALUES (%s, %s, %s)",
                           (admin_id, name, surname))
            conn.commit()
            cursor.close()
            conn.close()
            sg.popup('Başarıyla kayıt yaptınız!')
    window.close()
def student_register():
    ilgiler = get_all_ilgiler()
    ilgi_checkboxes = [[sg.Checkbox(ilgi, key=ilgi)] for ilgi in ilgiler]
    layout = [
        [sg.Text('Öğrenci ID'), sg.InputText(key='student_id')],
        [sg.Text('İsim'), sg.InputText(key='name')],
        [sg.Text('Soyisim'), sg.InputText(key='surname')],
        [sg.Column(ilgi_checkboxes, scrollable=True, vertical_scroll_only=True, size=(200, 200))],
        [sg.Button('Kaydet'), sg.Button('Geri')]
    ]
    window = sg.Window('Öğrenci Kayıt', layout)
    while True:
        event, values = window.read()
        student_id = values['student_id']
        name = values['name']
        surname = values['surname']
        selected_ilgiler = [ilgi for ilgi in ilgiler if values[ilgi]]
        if event == sg.WINDOW_CLOSED or event == 'Geri':
            window.close()
            return
        elif event == 'Kaydet':
            p_ana()
            c_ana()
            dosya_yolu= pdfm.dosya_yolu
            with open(dosya_yolu, 'rb') as file:
                pdf_data = file.read()

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ogrenci (ogrenci_id, isim, soyisim,pdf,GNO) VALUES (%s, %s, %s,%s,%s)",
                           (student_id, name, surname,pdf_data,configure.gno))
            for ilgi in selected_ilgiler:
                cursor.execute("SELECT * FROM ilgi_alanlari WHERE ilgi_alani = %s", (ilgi,))
                result = cursor.fetchone()
                ilgi_alani_id=result[0]
                cursor.execute("INSERT INTO ogrenci_ilgi (ogrenci_id, ilgi_alani_id) VALUES (%s, %s)",
                               (student_id,ilgi_alani_id ))
            conn.commit()
            def get_ders_id(ders_kodu):
                with create_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT ders_id FROM dersler WHERE ders_kodu = %s", (ders_kodu,))
                        result = cursor.fetchone()
                        return result[0] if result else None

            def insert_ogrenci_puan(ogrenci_id, ders_id, puan):
                with create_connection() as conn:
                    with conn.cursor() as cursor:
                        try:
                            cursor.execute(
                                    """
                                    INSERT INTO ogrenci_puan (ogrenci_id, ders_id, puan) 
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT (ogrenci_id, ders_id) 
                                    DO UPDATE SET puan = %s
                                    """, (ogrenci_id, ders_id, puan, puan)
                                )
                            conn.commit()
                        except psycopg2.Error as e:
                            print("Bir hata oluştu:", e)

            def add_student_courses_from_file(ogrenci_id, filename):
                with open(filename, 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        line = line.replace('*', '').strip()
                        ders_kodu, puan = line.strip().split()
                        ders_id = get_ders_id(ders_kodu)
                        if ders_id:
                            insert_ogrenci_puan(ogrenci_id, ders_id, puan)
                        else:
                            print(f"Ders kodu {ders_kodu} için ders id bulunamadı!")

            ogrenci_id = student_id
            add_student_courses_from_file(ogrenci_id, 'dersler_notlar.txt')

            conn.commit()
            cursor.close()
            conn.close()
            sg.popup('Başarıyla kayıt yaptınız!')
    window.close()

def teacher_register():
    courses = get_all_courses()
    ilgiler = get_all_ilgiler()
    course_checkboxes = [[sg.Checkbox(course, key=course)] for course in courses]
    ilgi_checkboxes = [[sg.Checkbox(ilgi, key=ilgi)] for ilgi in ilgiler]
    layout = [
        [sg.Text('Öğretmen ID'), sg.InputText(key='teacher_id')],
        [sg.Text('İsim'), sg.InputText(key='name')],
        [sg.Text('Soyisim'), sg.InputText(key='surname')],
        [sg.Text('Kontenjan'), sg.InputText(key='kontenjan')],
        [
            sg.Column(course_checkboxes, scrollable=True, vertical_scroll_only=True, size=(200, 200)),
            sg.Column(ilgi_checkboxes, scrollable=True, vertical_scroll_only=True, size=(200, 200))
        ],
        [sg.Button('Kaydet'), sg.Button('Geri')]
    ]
    window = sg.Window('Öğretmen Kayıt', layout)
    while True:
        event, values = window.read()
        teacher_id = values['teacher_id']
        name = values['name']
        surname = values['surname']
        kontenjan = values['kontenjan']
        selected_courses = [course for course in courses if values[course]]
        selected_ilgiler = [ilgi for ilgi in ilgiler if values[ilgi]]
        if event == sg.WINDOW_CLOSED or event == 'Geri':
            window.close()
            return
        elif event == 'Kaydet':
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ogretmen (ogretmen_id, isim, soyisim,kontenjan) VALUES (%s, %s, %s,%s)", (teacher_id, name, surname,kontenjan))
            for course in selected_courses:
                cursor.execute("SELECT * FROM dersler WHERE ders_kodu = %s", (course,))
                result = cursor.fetchone()
                ders_id=result[0]
                cursor.execute("INSERT INTO ogretmen_ders (ogretmen_id, ders_id) VALUES (%s, %s)",
                               (teacher_id,ders_id ))
            for ilgi in selected_ilgiler:
                cursor.execute("SELECT * FROM ilgi_alanlari WHERE ilgi_alani = %s", (ilgi,))
                result = cursor.fetchone()
                ilgi_alani_id=result[0]
                cursor.execute("INSERT INTO ogretmen_ilgi (ogretmen_id, ilgi_alani_id) VALUES (%s, %s)",
                               (teacher_id,ilgi_alani_id ))
            conn.commit()
            cursor.close()
            conn.close()
            sg.popup('Başarıyla kayıt yaptınız!')

    window.close()


def main():
    layout = [
        [sg.Text('Kayıt türünü seçin:')],
        [sg.Button('Öğrenci'), sg.Button('Öğretmen'), sg.Button('Yönetici')],
        [sg.Button('Çıkış')]
    ]

    window = sg.Window('Kayıt Türü Seçimi', layout)

    while True:
        event, _ = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Çıkış':
            break
        elif event == 'Öğretmen':
            window.hide()
            teacher_register()
            window.un_hide()
        elif event == 'Öğrenci':
            window.hide()
            student_register()
            window.un_hide()
        elif event == 'Yönetici':
            window.hide()
            admin_register()
            window.un_hide()

    window.close()


if __name__ == "__main__":
    main()
