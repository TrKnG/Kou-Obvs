import PySimpleGUI as sg
from pdfminer.high_level import extract_text

dosya_yolu = None
def p_ana():
    layout = [
        [sg.Text("Dosyayı buraya sürükleyip bırakın veya seçmek için tıklayın:", key="-TXT-")],
        [sg.InputText(enable_events=True, key="-IN-"), sg.FileBrowse()],
        [sg.Button("Tamam"), sg.Button("Çıkış")]
    ]

    window = sg.Window("Dosya Sürükle-Bırak", layout, finalize=True)
    window["-IN-"].Widget.config(insertwidth=0)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Çıkış":
            break
        if event == "-IN-":
            global dosya_yolu
            dosya_yolu = values["-IN-"]
            if dosya_yolu:
                #print(f"Seçilen dosya: {dosya_yolu}")
                window["-TXT-"].update(f"Seçilen dosya: {dosya_yolu}")
                def pdf_to_text(pdf_path):
                    return extract_text(pdf_path)
                def write_to_txt(text, output_path):
                    with open(output_path, 'w', encoding='utf-8') as file:
                        file.write(text)
                pdf_path = dosya_yolu
                output_txt_path = 'C:/Users/etok6/Downloads/ilovepdf_pages-to-jpg/yuksekogretim-kurulu-transkript-belgesi-sorgulama.txt'

                extracted_text = pdf_to_text(pdf_path)

                write_to_txt(extracted_text, output_txt_path)

                #print(f"Metin {output_txt_path} dosyasına yazdırıldı!")

    window.close()
