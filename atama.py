import psycopg2
import random

def create_connection():
    return psycopg2.connect(
        dbname="OBS2",
        user="postgres",
        password="1245",
        host="localhost",
        port="5432"
    )

def rastgele_ders_ata():
    conn = create_connection()
    cursor = conn.cursor()

    # Öğrencileri ve öğretmenleri seçme sorguları
    select_ogrenciler_query = "SELECT ogrenci_id FROM ogrenci"
    select_ogretmenler_query = "SELECT ogretmen_id FROM ogretmen"

    cursor.execute(select_ogrenciler_query)
    ogrenciler = cursor.fetchall()

    cursor.execute(select_ogretmenler_query)
    ogretmenler = cursor.fetchall()

    for ogrenci in ogrenciler:
        # Öğrencinin almadığı rastgele bir ders seçme
        cursor.execute("SELECT ders_id FROM ogretmen_ders WHERE ders_id NOT IN (SELECT ders_id FROM ogrenci_ders WHERE ogrenci_id = %s)", (ogrenci,))
        dersler = cursor.fetchall()

        if dersler:
            rastgele_ders = random.choice(dersler)[0]
            rastgele_ogretmen = random.choice(ogretmenler)[0]

            # Seçilen dersi ve öğretmeni ekleyin
            cursor.execute("INSERT INTO ogrenci_ders (ogrenci_id, ders_id, ogretmen_id) VALUES (%s, %s, %s)",
                           (ogrenci, rastgele_ders, rastgele_ogretmen))
            conn.commit()
            cursor.execute("UPDATE ogretmen SET kontenjan = kontenjan - 1 WHERE ogretmen_id = %s", (rastgele_ogretmen,))
            conn.commit()

    conn.commit()
    cursor.close()
    conn.close()


