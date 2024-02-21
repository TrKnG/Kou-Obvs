import re
gno = None
def c_ana():
    with open('C:/Users/etok6/Downloads/ilovepdf_pages-to-jpg/yuksekogretim-kurulu-transkript-belgesi-sorgulama.txt', 'r', encoding='utf-8') as file_1:
        content = file_1.read()
        float_values = re.findall(r"(\d+\.\d+)", content)
        if len(float_values) >= 2:
            global gno
            gno = float(float_values[2])
        else:
            gno = 0.00
            print("Doğru gno değeri bulunamadı gno 0.00 olarak tanımlandı")
    with open('C:/Users/etok6/Downloads/ilovepdf_pages-to-jpg/yuksekogretim-kurulu-transkript-belgesi-sorgulama.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    #kişi_bilgileri = lines[21:26]

    ders_kodları = ["AIT109", "YDB117", "TDB107", "FEF111", "FEF113", "FEF115", "BLM101", "BLM103", "BLM105", "AIT110", "YDB116", "KYP118", "TDB108", "FEF112", "FEF114", "BLM102", "BLM104", "BLM106", "FEF203", "MUH201", "MAT205", "BLM211", "BLM209", "BLM213", "BLM207", "MUH204", "MUH202", "BLM206", "BLM216", "BLM210", "BLM212", "BLM208", "MUH301", "BLM303", "BLM305", "BLM325", "BLM309", "BLM307", "BLM323", "BLM311", "BLM313", "BLM319", "BLM321", "BLM302", "BLM304", "BLM310", "BLM306", "BLM308", "BLM320", "BLM326", "BLM318", "BLM314", "BLM322", "BLM312", "BLM324", "BLM316", "BLM403", "BLM401", "BLM405", "MUH425", "MUH413", "MUH445", "MUH447", "BLM407", "BLM411", "BLM449", "BLM435", "BLM433", "BLM451", "BLM443", "BLM437", "BLM441", "BLM417", "BLM423", "BLM419", "BLM429", "BLM431", "BLM421", "BLM402", "BLM406", "BLM404", "MUH432", "MUH434", "BLM420", "BLM428", "BLM422", "BLM406", "BLM438", "BLM442", "BLM408", "BLM410", "BLM444", "BLM414", "BLM416", "BLM446", "BLM418", "BLM430", "BLM424", "BLM426", "BLM440"
    ]
    ders_puanlari = ["AA","BA", "BB","CB", "CC","DC", "DD","FD", "FF"]



    dersler = []
    notlar = []
    ders_listesi=0
    i = 0
    ders_sayisi=0
    ders_sayisi_temp=0
    liste_devam = 0
    while i < len(lines):
        line = lines[i].strip()
        while any(kod in line for kod in ders_kodları):
            dersler.append(line)
            i += 2
            line = lines[i].strip()
            if not any(kod in line for kod in ders_kodları):
                ders_listesi += 1
                ders_sayisi_temp= ders_sayisi
                ders_sayisi = len(dersler)
                liste_devam = 1
                while liste_devam:
                    if any(kod in line for kod in ders_puanlari):
                        t = 0
                        while t < ders_sayisi-ders_sayisi_temp:
                            notlar.append(line)
                            i += 2
                            t += 1
                            line = lines[i].strip()
                        liste_devam = 0
                    i += 1
                    line = lines[i].strip()

        i += 1
    with open('dersler_notlar.txt', 'w') as dosya:
        for satır in range(len(dersler)):
            dosya.write(dersler[satır] + '  ' +  notlar[satır] +  '\n')
