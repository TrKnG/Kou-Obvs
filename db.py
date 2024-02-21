import psycopg2

def create_connection():
    return psycopg2.connect(
        dbname="OBS2",
        user="postgres",
        password="1245",
        host="localhost",
        port="5432"
    )

def create_tables():
    commands = (
        """
        
        CREATE TABLE IF NOT EXISTS ogrenci (
            ogrenci_id SERIAL PRIMARY KEY,
            isim VARCHAR(255) NOT NULL,
            soyisim VARCHAR(255) NOT NULL,
            pdf bytea,
            gno FLOAT DEFAULT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ogretmen (
            ogretmen_id SERIAL PRIMARY KEY,
            isim VARCHAR(255) NOT NULL,
            soyisim VARCHAR(255) NOT NULL,
            kontenjan INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS yonetici (
            yonetici_id SERIAL PRIMARY KEY,
            isim VARCHAR(255) NOT NULL,
            soyisim VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dersler (
            ders_id SERIAL PRIMARY KEY,
            ders_kodu VARCHAR(255) NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ilgi_alanlari (
            ilgi_alani_id SERIAL PRIMARY KEY,
            ilgi_alani VARCHAR(255) NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ogrenci_ilgi (
            ogrenci_id INTEGER REFERENCES ogrenci(ogrenci_id),
            ilgi_alani_id INTEGER REFERENCES ilgi_alanlari(ilgi_alani_id),
            PRIMARY KEY (ogrenci_id, ilgi_alani_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ogretmen_ilgi (
            ogretmen_id INTEGER REFERENCES ogretmen(ogretmen_id),
            ilgi_alani_id INTEGER REFERENCES ilgi_alanlari(ilgi_alani_id),
            PRIMARY KEY (ogretmen_id, ilgi_alani_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ogrenci_puan (
            ogrenci_id INTEGER REFERENCES ogrenci(ogrenci_id),
            ders_id INTEGER REFERENCES dersler(ders_id),
            puan VARCHAR(2),
            PRIMARY KEY (ogrenci_id, ders_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ogrenci_ders (
            ogrenci_id INTEGER REFERENCES ogrenci(ogrenci_id),
            ders_id INTEGER REFERENCES dersler(ders_id),
            ogretmen_id INTEGER REFERENCES ogretmen(ogretmen_id),
            PRIMARY KEY (ogretmen_id,ogrenci_id, ders_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS talepler (
            talep_id SERIAL PRIMARY KEY,
            ogrenci_id INTEGER REFERENCES ogrenci(ogrenci_id),
            ogretmen_id INTEGER REFERENCES ogretmen(ogretmen_id),
            ders_id INTEGER REFERENCES dersler(ders_id),
            ogretmen_onay BOOLEAN DEFAULT FALSE,
            yonetici_onay BOOLEAN DEFAULT FALSE,
            UNIQUE (ogrenci_id, ders_id, ogretmen_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS mesajlar (
            mesaj_id SERIAL PRIMARY KEY,
            ogrenci_id INTEGER REFERENCES ogrenci(ogrenci_id),
            ogretmen_id INTEGER REFERENCES ogretmen(ogretmen_id),
            mesaj_icerik TEXT NOT NULL,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            kimden VARCHAR(10) CHECK (kimden IN ('ogrenci', 'ogretmen'))
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ogretmen_ders (
            ogretmen_id INTEGER REFERENCES ogretmen(ogretmen_id),
            ders_id INTEGER REFERENCES dersler(ders_id),
            PRIMARY KEY (ogretmen_id, ders_id)
        )
        
        """
    )

    conn = create_connection()
    cursor = conn.cursor()

    for command in commands:
        cursor.execute(command)

    conn.commit()
    cursor.close()
    conn.close()

def dersleri_ekle(ders_kodlari):
    conn = create_connection()
    cursor = conn.cursor()
    for ders_kodu in ders_kodlari:
        try:
            cursor.execute("INSERT INTO dersler (ders_kodu) VALUES (%s) ON CONFLICT (ders_kodu) DO NOTHING", (ders_kodu,))
        except psycopg2.Error as e:
            print(f"Error adding course {ders_kodu}: {e}")
    # cursor.execute("INSERT INTO ogrenci (ogrenci_id, isim, soyisim) VALUES (%s, %s, %s)",
    #                (180202042, "ENES", "TOK"))
    # cursor.execute("INSERT INTO ogretmen (ogretmen_id,isim, soyisim) VALUES (%s, %s, %s)", (1,"AHMET", "TOK"))
    # cursor.execute("INSERT INTO yonetici (yonetici_id,isim, soyisim) VALUES (%s, %s, %s)", (1,"SEVDE", "TOK"))
    conn.commit()
    cursor.close()
    conn.close()

def ilgileri_ekle(ilgi_alanlari):
    conn = create_connection()
    cursor = conn.cursor()
    for ilgi_alani in ilgi_alanlari:
        try:
            cursor.execute("INSERT INTO ilgi_alanlari (ilgi_alani) VALUES (%s) ON CONFLICT (ilgi_alani) DO NOTHING", (ilgi_alani,))
        except psycopg2.Error as e:
            print(f"Error adding course {ilgi_alani}: {e}")

    # cursor.execute("INSERT INTO ogrenci (ogrenci_id, isim, soyisim) VALUES (%s, %s, %s)",
    #                (180202042, "ENES", "TOK"))
    # cursor.execute("INSERT INTO ogretmen (ogretmen_id,isim, soyisim) VALUES (%s, %s, %s)", (1,"AHMET", "TOK"))
    # cursor.execute("INSERT INTO yonetici (yonetici_id,isim, soyisim) VALUES (%s, %s, %s)", (1,"SEVDE", "TOK"))
    conn.commit()
    cursor.close()
    conn.close()

def main():
    create_tables()
    ders_kodlari = ["AIT109", "YDB117", "TDB107", "FEF111", "FEF113", "FEF115", "BLM101", "BLM103", "BLM105", "AIT110",
                    "YDB116", "KYP118", "TDB108", "FEF112", "FEF114", "BLM102", "BLM104", "BLM106", "FEF203", "MUH201",
                    "MAT205", "BLM211", "BLM209", "BLM213", "BLM207", "MUH204", "MUH202", "BLM206", "BLM216", "BLM210",
                    "BLM212", "BLM208", "MUH301", "BLM303", "BLM305", "BLM325", "BLM309", "BLM307", "BLM323", "BLM311",
                    "BLM313", "BLM319", "BLM321", "BLM302", "BLM304", "BLM310", "BLM306", "BLM308", "BLM320", "BLM326",
                    "BLM318", "BLM314", "BLM322", "BLM312", "BLM324", "BLM316", "BLM403", "BLM401", "BLM405", "MUH425",
                    "MUH413", "MUH445", "MUH447", "BLM407", "BLM411", "BLM449", "BLM435", "BLM433", "BLM451", "BLM443",
                    "BLM437", "BLM441", "BLM417", "BLM423", "BLM419", "BLM429", "BLM431", "BLM421", "BLM402", "BLM406",
                    "BLM404", "MUH432", "MUH434", "BLM420", "BLM428", "BLM422", "BLM406", "BLM438", "BLM442", "BLM408",
                    "BLM410", "BLM444", "BLM414", "BLM416", "BLM446", "BLM418", "BLM430", "BLM424", "BLM426", "BLM440"
                    ]
    ilgi_alanlari= ["Donanım", "Yazılım", "Makine", "Teknoloji", "Tarih", "Sağlık", "Oyun"]
    dersleri_ekle(ders_kodlari)
    ilgileri_ekle(ilgi_alanlari)

if __name__ == '__main__':
    main()


# ŞİMDİ TALEP TABLOSU YAPMAYA ÇALIŞIYORUM
