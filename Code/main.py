import os
import PySimpleGUI as sg
import random
import string
from tkinter import messagebox
from ast import literal_eval
import shutil

from configparser import ConfigParser 

import database_functions as dbfunc
import functions as func

CFILE = "config.ini"

config = ConfigParser()

def read_config():
    global config
    config.read(CFILE)
    
def write_config():
    global config
    with open(CFILE, 'w') as f:
        config.write(f)

was_cfile_replaced = False

if os.path.isfile(CFILE):
    read_config()
else:
    was_cfile_replaced = True
    shutil.copyfile('data/default_config.ini', 'config.ini')
    read_config()
    
# Funkcje sprawdzające bazę danych i inicjacja takowej jak jest zapisana.

is_db_selected = False

def check_db():
    try:
        dbfunc.validate(config.get('database', 'path'))
    except:
        return 1
    try:
        dbfunc.validate_table(dbfunc.create_connection(config.get('database', 'path')), config.get('database', 'table'))
    except:
        return 2
    return 0

init_check = check_db() 
if init_check == 0:
    is_db_selected = True
    database = dbfunc.create_connection(config.get('database', 'path'))
    table_headers = dbfunc.print_all_col_names(database)
elif init_check == 2: 
    table_headers = ''
    config.set('database', 'table', '')
    database = dbfunc.create_connection(config.get('database', 'path'))
    write_config()
elif init_check == 1:
    database = ''
    table_headers = ''
    config.set('database', 'table', '')
    config.set('database', 'path', '')
    write_config()
    
# Nadpisywnie headerów, gdyż coś tutaj nie działa poprawnie z nimi.

db_headers = ['CNAME{}'.format(i) for i in range(0,99)]
draw_headers = ['CNAME{}'.format(i) for i in range(0,99)]

def update_title(table, new_headings, main_headings):
    pop_headings = 0
    if len(new_headings)<8:
        pop_headings = 8 - len(new_headings)
        for _ in range(pop_headings):
            new_headings.append('')
    for cid, text in zip(main_headings, new_headings):
        table.heading(cid, text=text)
        table.configure(displaycolumns=[main_headings[i] for i in range(len(new_headings))])
    for _ in range(pop_headings):
            new_headings.pop(-1)

# Inicjacja listy indeksów PROME

prome_list = func.init_prome()

prome_count = []

LARGE_FONT= ('Verdana', 12)
NORM_FONT = ('Helvetica', 10)
SMALL_FONT = ('Helvetica', 8)

buffervar = ""

# Funkcie wypełniajace tabele tymczasowe by poprawnie było widoczne okno.

def word():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(5))

def number(max_val=1000):
    return random.randint(0, max_val)

def make_table(num_rows, num_cols):
    data = [[j for j in range(num_cols)] for i in range(num_rows)]
    data[0] = [word() for __ in range(num_cols)]
    for i in range(1, num_rows):
        data[i] = [word(), *[number() for i in range(num_cols - 1)]]
    return data

data = make_table(num_rows=50, num_cols=10)

# Funkcje ukrywające okna

def hide_window(win):
    win["-MAIN GROUP-"].update(visible=False)
    win["-SEND GROUP-"].update(visible=False)

def show_window(win):
    win["-MAIN GROUP-"].update(visible=True)
    win["-SEND GROUP-"].update(visible=True)
    
def draw_tab_visibility(win):
    global is_db_selected
    if is_db_selected == False:
        win["-DRAW ENABLED-"].hide_row()
        win["-DRAW ENABLED-"].update(visible=is_db_selected)
        win["-DRAW DISABLED-"].unhide_row()
        win["-DRAW DISABLED-"].update(visible=not(is_db_selected))
    else:
        win["-DRAW ENABLED-"].unhide_row()
        win["-DRAW ENABLED-"].update(visible=is_db_selected)
        win["-DRAW ENABLED-"].expand(expand_x = True,
            expand_y = True,
            expand_row = True)
        win["-DRAW DISABLED-"].hide_row()
        win["-DRAW DISABLED-"].update(visible=not(is_db_selected))
        
def db_tab_visibility(win):
    global is_db_selected
    if is_db_selected == False:
        win["-DB ENABLE-"].hide_row()
        win["-DB ENABLE-"].update(visible=is_db_selected)
        win["-DB DISABLE-"].unhide_row()
        win["-DB DISABLE-"].update(visible=not(is_db_selected))
    else:
        win["-DB ENABLE-"].unhide_row()
        win["-DB ENABLE-"].update(visible=is_db_selected)
        win["-DB ENABLE-"].expand(expand_x = True,
            expand_y = True,
            expand_row = True)
        win["-DB DISABLE-"].hide_row()
        win["-DB DISABLE-"].update(visible=not(is_db_selected))

# Funkcje okna paska postępu do wysyłania danych.

progressbar_window = ''

def init_progressbar_window(val, max_val, text):
    global progressbar_window
    layout = [[sg.Text('{}'.format(text), pad = (3,0))],
              [sg.Text('{} z {}'.format(str(val), str(max_val)), key ='-VALS-', pad=(3,0))],
              [sg.ProgressBar(max_value=int(max_val), orientation='h', size=(22, 20), key='progress', )]]
    
    progressbar_window = sg.Window('Custom Progress Meter', layout, finalize=True, no_titlebar = True,keep_on_top=True, grab_anywhere = True)
    
def update_progressbar_window(val, max_val):
    global progressbar_window
    progressbar_window['-VALS-'].update('{} z {}'.format(val, max_val))
    progressbar_window['progress'].update_bar(val)

def close_progressbar_window():
    global progressbar_window
    progressbar_window.close()


# GŁÓWNE OKNO

def make_window(theme=None):
    
    sg.theme(theme)
    
    # Tab losujący "-DRAW *-"
    
    draw_layout =  [
        [ 
            sg.Frame('',[ # GRUPA GŁÓWNA -DRAW ENABLED- wyświetlona wtedy gdy jest wczytana baza danych              
                [
                    sg.Frame('',[ # Grupa -DRAW GROUP *-: Wybranie kolumn filtrujących dane
                        [sg.Text('Wybór danych do filtrowania:', font=LARGE_FONT, pad=(0,4))],
                        [
                            sg.Text('Kolumna:',pad=(1,5)), 
                            sg.Combo(values=[], 
                                default_value='', 
                                readonly=True, 
                                key='-DRAW GROUP COL-',
                                enable_events = True,
                                size = (13,1),
                                pad=(0,5)),
                            sg.Text('Wartość:',pad=(2,5)), 
                            sg.Combo(values=[], 
                                default_value='', 
                                readonly=True, 
                                key='-DRAW GROUP VAL-',
                                size = (10,1),
                                pad=(2,5)),
                            sg.Push(),
                            sg.Button("Wpisz", key="-DRAW GROUP SEL-")
                        ]
                    ],  border_width=0, size = (390,60)),
                
                    sg.VSeparator(pad=(2,0)),
                    
                    sg.Frame('',[ # Grupa -DRAW SELNUMBERS *-: Wybranie kolumny z liczbami do losowania
                        [sg.Text('Wybór liczb do losowania:', font=LARGE_FONT, pad=(0,4))],
                        [
                            sg.Text('Kolumna:', pad=(2,0)),
                            sg.Combo(values=[], 
                                default_value='', 
                                readonly=True, 
                                key='-DRAW SELNUMBERS VAL-',
                                size = (13,1)
                                ),
                            sg.Button("Wpisz", key="-DRAW SELNUMBERS SEL-")
                        ]
                    ], border_width=0, expand_x=True, element_justification="rr", size = (200,60)),
                ],
                [sg.HSeparator()],
                [
                    sg.Frame('',[ # Grupa -DRAW QUERY *-: Widok kwerendy uwzględniający wybrane dane
                        [sg.Text('Widok kwerendy:', font=LARGE_FONT,pad=(0,5))],
                        [
                            sg.Table(values=[], headings=draw_headers,max_col_width=25,
                                auto_size_columns=True,
                                justification='right',
                                key='-DRAW QUERY DISP-',
                                row_height=18,
                                num_rows=300,
                                alternating_row_color = "#516c87",
                                def_col_width=10,
                                vertical_scroll_only = False,)
                        ]
                    ],  size=(400,120), border_width=0, expand_x=True, expand_y=True),
                
                    sg.Frame('',[ # Grupa -DRAW DISPEDITGROUP *-: Wyświetlenie filtrów i ich edycja
                        [sg.Text('Aktywne filtry:', font=LARGE_FONT,pad=(0,5))],
                        [
                            sg.Table(values=[], headings=["Nazwa", "Wartość"], max_col_width=25,
                                auto_size_columns=True,
                                justification='right',
                                key='-DRAW DISPEDITGROUP VIEW-',
                                row_height=18,
                                enable_events=True,
                                num_rows=4,
                                def_col_width=10,
                                vertical_scroll_only = False,
                                )
                        ],
                        [sg.Button("Wyczyść zaznaczone", key="-DRAW DISPEDITGROUP CLEAR-", size=(20,1))],
                        [sg.Button("Wyczyść wszystkie filtry", key="-DRAW DISPEDITGROUP CLEARALL-", size=(20,1))],
                        [sg.HSeparator(pad = (0,8))],
                        [sg.Button("LOSUJ", key="-DRAW DISPEDITGROUP RANDOMIZE-", size = (12,2), font=LARGE_FONT, pad = (3,3))], 
                    ],  size=(200,280), border_width=0, expand_x=False, expand_y=False, element_justification="r")
                ]
            ], border_width=0, expand_x=True, expand_y=True, key = '-DRAW ENABLED-') 
        ],
        
        
        [
            sg.Frame('',[ # GRUPA -DRAW DISABLED-: Wyświetla się gdy nie wczytano bazy danych
                [sg.Text('NIE WYBRANO BAZY DANYCH.', font=LARGE_FONT,pad=(0,15))],
                [sg.Text('Przejdź do zakładki "Ustawienia baz danych" by wybrać\n i aktywować bazę danych do losowania.', font=NORM_FONT,pad=(0,5), justification="center")],
                [sg.Button("DEBUG", key="-DRAW DEBUG-")]
            ], visible=False, border_width=0, expand_x=True, expand_y=False, key = '-DRAW DISABLED-', element_justification="c")
        ]
    ]
    
    # Tab edytujący "-EDIT *-"
    
    edit_layout =  [
        [
            sg.Frame('',[ # Grupa -EDIT NUMBERS *-: Edycja numerów ręczna
                         
                [sg.Text('Wybór liczby:', font=LARGE_FONT,pad=(5,7))],
                [
                    sg.Text('Indeks PROME:'), 
                    sg.Push(),
                    sg.Combo(values = [i for i in range(1, int(config.get("main", "prome_count"))+1)], 
                        default_value='', 
                        readonly=True, 
                        size = (8,1),
                        enable_events=True,
                        key='-EDIT NUMBERS PROMEINDEX-'),
                ],
                [
                    sg.Text('Indeks liczby:'), 
                    sg.Push(),
                    sg.Combo(values=[], 
                        default_value='', 
                        readonly=True, 
                        key='-EDIT NUMBERS INDEX-',
                        size = (8,1),
                        enable_events=True,),

                ],
                [
                    sg.Text('Liczba:'), 
                    sg.Push(),
                    sg.Input(size = 5,
                        key='-EDIT NUMBERS NUMBER-'),
                ],
            ],  size=(250,120), border_width=0,),
            
            sg.VSeparator(),
            
            sg.Frame('',[ # Grupa -EDIT SEND *-: Wysyłanie numerów do listy wysyłającej
                [sg.Button("Nadpisz liczbę", key="-EDIT SEND VALUE-", size=(12,2))],
                [sg.Button("Wyczyść liczbę", key="-EDIT SEND CLEAR-", size=(12,1))],
            ], border_width=0,),
            
            sg.VSeparator(),
            
            sg.Frame('',[ # Grupa -EDIT VIEW *-: Wyświetlenie indeksów liczb dla danego PROME ID
                [
                    sg.Table(values=[], headings=["Indeks liczby", "Wartość"], max_col_width=25,
                        auto_size_columns=True,
                        justification='right',
                        key='-EDIT VIEW TABLE-',
                        row_height=18,
                        font=LARGE_FONT,
                        enable_events=True,
                        num_rows=300,
                        def_col_width=10,
                        vertical_scroll_only = False,
                        )
                ]
            ],size=(50, 120),border_width=0, expand_x=True, expand_y=False, element_justification="r")
        ], 
        [sg.HSeparator()],
        [ 
            sg.Frame('',[ # Grupa -EDIT IMPLEMENTATION *-: DO PRZYSZŁEJ IMPLEMENTACJI ALGORYTMÓW
                [sg.Text("Miejsce do implementacji algorytmów edycji", font=LARGE_FONT,pad = (0,20))]
            ], expand_x= True, expand_y=True, element_justification="c"),
        ]
    ]
    
    # Tab edycji i wyboru bazy danych "-DB *-"
    
    database_layout = [
        [
            sg.Frame('',[ # Grupa -DB SELECT *-: Wybór bazy danych
                         
                [sg.Text('Wybór bazy danych:', font=LARGE_FONT,pad=(5,7))],
                [
                    sg.Input(key = '-DB SELECT NAME-',size = (36,1)),
                    sg.Push(),
                    sg.FileBrowse("Przeglądaj", target="-DB SELECT NAME-", size = (10,1), file_types = (('Pliki bazy danych SQLite', '*.db'),))
                ],
                [
                    sg.Button("Wybierz", key="-DB SELECT APPLY-", size = (10,1)),
                    sg.Button("Wyczyść", key="-DB SELECT CLEAR-", size = (10,1)),
                ],

            ],  size=(360,100), border_width=0,),
            
            sg.VSeparator(),
            
            sg.Frame('',[ # Grupa -DB SELTABLE *-: Wybór 
                    [sg.Text('Wybór tabeli:', font=LARGE_FONT,pad=(5,7))],
                    [
                        sg.Text('Nazwa tabeli:',pad=(5,7)),
                        sg.Combo(values='', 
                                default_value='', 
                                readonly=True, 
                                key='-DB SELTABLE SELECT-',
                                size = (25,1),
                                pad=(0,5)),
                    ],
                    [
                        sg.Button("Wybierz", key="-DB SELTABLE SEND-", size = (10,1)),
                    ],
                    
            ], border_width=0,size=(295,100), element_justification="r"),
        
        ],
        [sg.HSeparator()],
        [sg.Text('Widok tabeli:', font=LARGE_FONT,pad=(10,5))],
        [
            sg.Frame('',[ # Grupa -DB TABLE *-: Wgląd na wybraną tabelę (DB ENABLE DAJE WIDOCZNOŚĆ GDY BAZA JEST AKTYWNA)
                [
                    sg.Table(values=[], headings=db_headers,max_col_width=25,
                        auto_size_columns=True,
                        justification='right',
                        key='-DB TABLE VIEW-',
                        row_height=18,
                        num_rows=300,
                        def_col_width=50,
                        alternating_row_color = "#516c87",
                        vertical_scroll_only = False,)
                ]
            ], size = (600,200), border_width=0, expand_x=True, expand_y=True, visible=True, key="-DB ENABLE-"),
        ],
        [
            sg.Frame('',[ # Grupa -DB DISABLED-: Wgląd na wybraną tabelę (ENABLE DAJE WIDOCZNOŚĆ GDY BAZA JEST AKTYWNA)
                [sg.Text('NIE WYBRANO TABELI.', font=LARGE_FONT,pad=(0,15))],
                [sg.Text('Wybierz bazę danych oraz jedną tabelę\nby wyświetlic jej zawartość.', font=NORM_FONT,pad=(0,5), justification="center")],
            ], border_width=0, expand_x=True, expand_y=True, visible=False, element_justification="c", key="-DB DISABLE-"),
        ],
    ]
    
    # Tab edycji i wyboru bazy danych "-HARDWARE *-"
    
    hardware_layout =  [
        [
            sg.Frame('',[ # Grupa -HARDWARE SELECT *-: Wybór ilości oraz wybranego urządzenia PROME do edycji
                         
                [sg.Text('Wybór urządzeń:', font=LARGE_FONT,pad=(5,7))],
                [
                    sg.Text('Wybór ilości podłączonych urządzeń:'), 
                    sg.Push(),
                    sg.Input(size = 5, key='-HARDWARE SELECT COUNT-'),
                    sg.Button("Nadpisz", key = "-HARDWARE SELECT COUNT SEND-", size=(7,1))
                ],
                [
                    sg.Text('Wybór PROME ID do edycji:'), 
                    sg.Push(),
                    sg.Combo(values=[i for i in range(1, int(config.get('main', 'prome_count'))+1)],
                        default_value='', 
                        readonly=False, 
                        key='-HARDWARE SELECT PROMEID-',
                        size = (13,1),
                        enable_events=True,
                    ),
                ],
                
            ],  size=(370,100), border_width=0,),
            
            sg.VSeparator(),
            
            
        ], 
        [sg.HSeparator()],
        [
            sg.Frame('',[ # Grupa -HARDWARE EDITDEV *-: Edycja własności wybranego urządzenia
                [sg.Text('Edycja ustawień dla wybranego PROME ID:', font=LARGE_FONT,pad=(5,5))],
                [
                    sg.Text('Port COM:', pad = (4,10)), 
                    sg.Combo(values=func.com_ports(), 
                        default_value="", 
                        readonly=True, 
                        key='-HARDWARE EDITDEV COMPORT-',
                        size = (8,1),
                        pad = (8,10)
                        ),
                    sg.Push(),
                    sg.Text('Ilość wyświetlaczy:',pad = (0,10)), 
                    sg.Combo(values=[i for i in range(1,100)], 
                        default_value='', 
                        readonly=True, 
                        key='-HARDWARE EDITDEV DISPLAYS-',
                        size = (5,1),
                        pad = (0,10)
                        ),
                ],
                [
                    sg.Text('Baudrate:    '), 
                    sg.Combo(values=func.serial_speeds(), 
                        default_value='', 
                        readonly=True, 
                        key='-HARDWARE EDITDEV COMSPEED-',
                        size = (8,1),
                        pad = (8,0)),
                ],
                [
                    sg.Text('Bity danych:'), 
                    sg.Combo(values=[6,7,8], 
                        default_value='', 
                        readonly=True, 
                        key='-HARDWARE EDITDEV COMDATABITS-',
                        size = (3,1),
                        pad = (7,0)),
                ],
                [
                    sg.Text('Bity stopu:   '), 
                    sg.Combo(values=[1,2], 
                        default_value='', 
                        readonly=True, 
                        key='-HARDWARE EDITDEV COMSTOPBITS-',
                        size = (3,1)),
                ],
                [
                    sg.Text('Parzystość:'), 
                    sg.Combo(values=["None", "Odd", "Even", "Mark", "Space"], 
                        default_value='', 
                        readonly=True, 
                        key='-HARDWARE EDITDEV COMPARITY-',
                        size = (6,1),
                        pad = (10,0)),
                ],
                [sg.VPush()],
                [
                    sg.Button("Nadpisz dla danego\nPROME ID", key="-HARDWARE EDITDEV SENDID-", size=(20,2)),
                    sg.Push(),
                    sg.Button("Nadpisz dla KAŻDEGO PROME ID*", key="-HARDWARE EDITDEV SENDALL-", size=(20,2))
                ],
            ], pad=(5,5), expand_y=True, border_width=0, size = (370,240)), 
            
            sg.Frame('',[ # Bez grupy, zostaje na razie jako info dla użytkownika
                [sg.VPush()],
                [sg.Text("*Wysyłanie ustawień dla każdego PROME ID nadpisuje\n wszystko poza numerem portu COM", font=SMALL_FONT, justification="left")] 
            ], pad=(5,5), border_width=0, expand_y=True, element_justification="l"),
        ],
    ]

    # Tab główny "-MAIN *-"
    
    layout = [
        [
            sg.Frame("",[ #GRUPA "-MAIN GROUP-" do ukrywania
                [
                    sg.TabGroup([ #Grupa zakładek do ukrycia
                        [   
                            sg.Tab('Losowanie', draw_layout),
                            sg.Tab('Edytowanie', edit_layout),
                            sg.Tab('Ustawienia baz danych', database_layout),
                            sg.Tab('Ustawienia sprzętu', hardware_layout),
                        ]
                    ], key='-TAB GROUP-', expand_x=True, expand_y=True, pad=(5,5), visible= True)
                ], 
            ], key='-SEND GROUP-', expand_x=True, expand_y=True, pad=(0,0), visible= True, border_width=0),
        ],
        
        [
            sg.Frame("",[ #GRUPA "-SEND GROUP-" do ukrywania
                [  
                    sg.Frame('',[ #GRUPA "-MAIN *-": Funkcje okna głównego
                        [
                            sg.Table(values = [[1,[1,2,3,4,5]]], 
                                headings=["PROME ID", "LICZBY"],
                                max_col_width=25,
                                auto_size_columns=True,
                                justification='right',
                                key='-MAIN LIST-',
                                row_height=20,
                                num_rows=5,
                                def_col_width=100,
                                vertical_scroll_only = False,
                                font=NORM_FONT,
                            ),
                        ],
                    ], border_width=0, expand_x=False, element_justification="l", size=(280,130)),
                    
                    sg.Frame('',[  
                        [sg.Button("Sprawdź stan\npołączeń", key="-MAIN CONNCHECK-", size=(13,2)),],
                        [sg.Button("Wyślij do\nurządzeń", key="-MAIN SEND-", size=(13,2))],
                    ], border_width=0, expand_x=False, element_justification="c"),
                    
                    sg.Frame('',[
                        [sg.HSeparator(pad = (0,5))],
                        [sg.Text("Losowanie według kolumny:", font = LARGE_FONT,),],
                        [sg.Multiline(config.get('database', 'draw'), key = "-MAIN DB COL-", size = (32,1),  justification="right", font=SMALL_FONT, pad = (3,1)),  ],
                        [sg.HSeparator(pad=(0,7))],
                        [sg.Text("Aktywna baza danych:", font = LARGE_FONT), ],
                        [sg.Multiline(func.db_validate(config.get('database', 'path')), key = "-MAIN DB SELECTED-", font=SMALL_FONT, pad = (3,1),  size = (45,2), justification="right"), ],
                    ], size = (280,160), border_width=0, expand_x=True, element_justification="r"),
                
                ],
            ], key = '-MAIN GROUP-', visible = True, border_width=0, pad=(0,0), element_justification="c"),
        ],
        [sg.HSeparator()]
    ]   
        
    layout[-1].append(sg.Sizegrip())
    window = sg.Window('PROME wersja alfa', layout, 
        resizable=False, 
        right_click_menu_tearoff=True, 
        grab_anywhere=False, 
        margins=(0,0), 
        use_custom_titlebar=False, 
        finalize=True, 
        keep_on_top=False)
    window.set_min_size(window.size)
    
    # FUCKJE POZOSTAŁE DO ZMIANY FORMATOWANIA TABEL I WYŚWIETLENIA PRZY STARTUPIE
    
    window['-MAIN LIST-'].update(values = func.prome_list_table(prome_list))
    update_title(window['-DB TABLE VIEW-'].Widget, ['' for _ in range(len(db_headers))], db_headers)
    update_title(window['-DRAW QUERY DISP-'].Widget, ['' for _ in range(len(db_headers))], draw_headers)
    
    if is_db_selected == True:
        table_headers = dbfunc.print_all_col_names(database)      
        update_title(window['-DB TABLE VIEW-'].Widget, table_headers, db_headers)
        update_title(window['-DRAW QUERY DISP-'].Widget, table_headers, draw_headers)     
        window['-DB TABLE VIEW-'].update(values=dbfunc.db_values(database, table_headers))
        window['-DRAW QUERY DISP-'].update(values=dbfunc.query_table(database))
        window['-DB SELTABLE SELECT-'].update(values=dbfunc.list_tables(database))
        window['-DRAW GROUP COL-'].update(values=table_headers)
        window['-DRAW SELNUMBERS VAL-'].update(values=dbfunc.exclude_filters(table_headers))
        window['-DRAW DISPEDITGROUP VIEW-'].update(values=literal_eval(config.get('database', 'filters')))
    elif init_check == 2:
        window['-DB SELTABLE SELECT-'].update(values=dbfunc.list_tables(database))
        
    draw_tab_visibility(window)
    db_tab_visibility(window)
    
    return window


def mainloop():
    global is_db_selected; global prome_count; global prome_list; global database; global table_headers; global was_cfile_replaced
    
    window = make_window(sg.theme())
    
    if was_cfile_replaced == True:
        hide_window(window)
        messagebox.showinfo("Błąd konfiguracji","Nie znaleziono pliku konfiguracyjnego\nZostanie wczytana konfiguracja domyślna.",) 
        show_window(window)
        
    was_cfile_replaced = False
    
    # Event loop
    while True:
        event, values = window.read()
        
        # Zamykanie okna
        
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        # Funkcje ustawień "DRAW"

        if event == '-DRAW GROUP COL-':
            window["-DRAW GROUP VAL-"].update(values = dbfunc.query_group(database, values['-DRAW GROUP COL-']))
        elif event == '-DRAW GROUP SEL-':
            read_config()
            val = [values['-DRAW GROUP COL-'], values['-DRAW GROUP VAL-']]
            try:
                if val[0] == '':
                    raise ValueError
                elif val[1] == '':
                    raise ValueError
                else:
                    filters = literal_eval(config.get('database', 'filters'))
                    for i in range(0, len(filters)):
                        if filters[i][0] == val[0]:
                            filters[i][1] = val[1]
                            break
                    else:
                        filters.append(val)
                    config.set('database', 'filters', str(filters))
                    if config.get('database', 'draw') == val[0]:
                        config.set('database', 'draw', '')
                        window['-MAIN DB COL-'].update('')
                    write_config()
                    window['-DRAW QUERY DISP-'].update(values=dbfunc.query_table(database))
                    window['-DRAW DISPEDITGROUP VIEW-'].update(values=literal_eval(config.get('database', 'filters')))
                    window['-DRAW SELNUMBERS VAL-'].update(values=dbfunc.exclude_filters(table_headers))
            except ValueError:        
                hide_window(window)
                messagebox.showinfo("Błąd wartości","Nie podano filtru bądź wartości.", )
                show_window(window)
        elif event == '-DRAW SELNUMBERS VAL-':
            pass
        elif event == '-DRAW SELNUMBERS SEL-':
            read_config()
            try:
                vals = dbfunc.query_col(database, values['-DRAW SELNUMBERS VAL-'])
                for i in range(len(vals)):
                    vals[i] = vals[i][0]
                    error_vals = []
                for i in range(0, len(vals)):
                    vals[i] = int(vals[i])
                    if vals[i] not in range(0,100):
                        error_vals.append(vals[i])
                if len(error_vals) > 0:
                    err_str = ''
                    for i in error_vals:
                        err_str += str(i)
                        err_str += ', '
                    err_str = err_str[:-2]
                    hide_window(window)
                    messagebox.showinfo("Informacja","Podane wartości są poza przedziałem liczbowym od 0 do 99:\n{}\nZostaną one zingnorowane przy losowaniu.".format(err_str))
                    show_window(window)
                window['-MAIN DB COL-'].update(values['-DRAW SELNUMBERS VAL-'])
                config.set('database','draw', values['-DRAW SELNUMBERS VAL-'])
                write_config()
            except:
                hide_window(window)
                messagebox.showinfo("Błąd bazy danych","W podanej kolumnie znajdują się wartości które nie mogą\n zostać przekonwertowane na liczbę całkowitą.", )
                show_window(window)
            
        elif event == '-DRAW DISPEDITGROUP CLEAR-':
            indexes = values['-DRAW DISPEDITGROUP VIEW-']
            if len(indexes) == 0:
                pass
            else:
                read_config()
                indexes = values['-DRAW DISPEDITGROUP VIEW-']
                indexes.sort(reverse=True)
                filters = literal_eval(config.get('database', 'filters'))
                for i in indexes:
                    filters.pop(i)
                config.set('database', 'filters', str(filters))
                write_config()
                window['-DRAW QUERY DISP-'].update(values=dbfunc.query_table(database))
                window['-DRAW DISPEDITGROUP VIEW-'].update(values=literal_eval(config.get('database', 'filters')))
                window['-DRAW SELNUMBERS VAL-'].update(values=dbfunc.exclude_filters(table_headers))
                
        elif event == '-DRAW DISPEDITGROUP CLEARALL-':
                filters = []
                config.set('database', 'filters', str(filters))
                write_config()
                window['-DRAW QUERY DISP-'].update(values=dbfunc.query_table(database))
                window['-DRAW DISPEDITGROUP VIEW-'].update(values=literal_eval(config.get('database', 'filters')))
                window['-DRAW SELNUMBERS VAL-'].update(values=dbfunc.exclude_filters(table_headers))
                
        elif event == '-DRAW DISPEDITGROUP RANDOMIZE-':
            read_config()
            try:
                if config.get('database', 'draw') == '':
                    raise ReferenceError
                vals = dbfunc.query_table(database, config.get('database', 'draw'))
                for i in range(len(vals)):
                    vals[i] = vals[i][0]
                prome_draw_dict = func.update_prome_draw(prome_list, vals)
                prome_list = prome_draw_dict['output_list']
                
                if len(prome_draw_dict['left_vals']) > 20:
                    hide_window(window)
                    messagebox.showinfo("Informacja","Ilość wybranych wartości znacznie prekracza ilość\ndostępnych wyświetlaczy na urządzeniach PROME.")
                    show_window(window)
                elif len(prome_draw_dict['left_vals']) > 0:
                    left_str = ''
                    for i in prome_draw_dict['left_vals']:
                        left_str += str(i)
                        left_str += ', '
                    left_str = left_str[:-2]
                    hide_window(window)
                    messagebox.showinfo("Informacja","Podane wartości zostały pominięte przy losowaniu:\n{}.".format(left_str))
                    show_window(window)
                if values['-EDIT NUMBERS PROMEINDEX-'] != '':
                    window['-EDIT VIEW TABLE-'].update(values = func.prome_list_index_values(prome_list, values['-EDIT NUMBERS PROMEINDEX-']))
                window['-MAIN LIST-'].update(values=func.prome_list_table(prome_list))
            except ReferenceError:
                hide_window(window)
                messagebox.showinfo("Błąd bazy danych","Nie wybrano kolumny do losowania.", )
                show_window(window)

            

        # Funkcje ustawień "EDIT"
        
        if event == '-EDIT NUMBERS PROMEINDEX-':
            read_config()
            dev = "P{}".format(values['-EDIT NUMBERS PROMEINDEX-'])
            window['-EDIT NUMBERS INDEX-'].update(values=[i for i in range(1, int(config.get(dev, 'displays'))+1)])
            window['-EDIT VIEW TABLE-'].update(values = func.prome_list_index_values(prome_list, values['-EDIT NUMBERS PROMEINDEX-']))

        elif event == '-EDIT SEND VALUE-':
            try:
                val = int(values['-EDIT NUMBERS NUMBER-'])
                if val not in range(0,100):
                    raise ValueError
                else:
                    prome_list = func.update_prome_val(prome_list, val, values['-EDIT NUMBERS INDEX-'], values['-EDIT NUMBERS PROMEINDEX-'])
                    window['-EDIT VIEW TABLE-'].update(values = func.prome_list_index_values(prome_list, values['-EDIT NUMBERS PROMEINDEX-']))
                    window['-MAIN LIST-'].update(values=func.prome_list_table(prome_list))
            except:
                hide_window(window)
                messagebox.showinfo("Błąd wartości","Wpisano niepoprawną wartość bądź nie podano indeksów.\nMusi zostać wpisana liczba z przedziało od 0 do 99.", )
                show_window(window)
        
        elif event == '-EDIT SEND CLEAR-':
            try:
                val = int(values['-EDIT NUMBERS NUMBER-'])
                prome_list = func.update_prome_val(prome_list, 0, values['-EDIT NUMBERS INDEX-'], values['-EDIT NUMBERS PROMEINDEX-'])
                window['-EDIT VIEW TABLE-'].update(values = func.prome_list_index_values(prome_list, values['-EDIT NUMBERS PROMEINDEX-']))
                window['-MAIN LIST-'].update(values=func.prome_list_table(prome_list))
            except:
                hide_window(window)
                messagebox.showinfo("Błąd wartości","Nie podano indeksów.", )
                show_window(window)
            
            
        # Funkcje ustawień "DB"
        
        if event == "-DB SELECT APPLY-":
            read_config()
            path = values['-DB SELECT NAME-']

            try:
                if path.find('/') == -1:
                    raise ValueError
                dbfunc.validate(path)
                database = dbfunc.create_connection(path)
                is_db_selected = False
                config.set('database', 'path', path)
                config.set('database', 'table', '')
                write_config()
                
                window['-DRAW GROUP COL-'].update(values=table_headers)
                window['-DB SELTABLE SELECT-'].update(values=dbfunc.list_tables(database))
                window['-MAIN DB SELECTED-'].update(func.db_validate(config.get('database', 'path')))
                                
                draw_tab_visibility(window)
                db_tab_visibility(window)

            except:
                hide_window(window)
                messagebox.showinfo("Błąd bazy danych","Podano niepoprawny plik bazy danych SQLite", )
                show_window(window)



        elif event == "-DB SELECT CLEAR-":
            window["-DB SELECT NAME-"].update(value="")
        
        elif event == "-DB SELTABLE SEND-":
            read_config()
            try:
                table = values['-DB SELTABLE SELECT-'][0]
                dbfunc.validate_table(database, table)
                if len(dbfunc.print_all_col_names(database)) > 99:
                    raise MemoryError
                is_db_selected = True
                config.set('database', 'table', table)
                config.set('database', 'filters', '[]')
                write_config()
                
                table_headers = dbfunc.print_all_col_names(database)
                
                update_title(window['-DB TABLE VIEW-'].Widget, table_headers, db_headers)
                update_title(window['-DRAW QUERY DISP-'].Widget, table_headers, draw_headers)
                
                window['-DRAW DISPEDITGROUP VIEW-'].update(values=[])
                window['-DB TABLE VIEW-'].update(values=dbfunc.db_values(database, table_headers))
                window['-DRAW QUERY DISP-'].update(values=dbfunc.db_values(database, table_headers))
                window['-DRAW GROUP COL-'].update(values=table_headers)
                window['-DRAW SELNUMBERS VAL-'].update(values=dbfunc.exclude_filters(table_headers))
                
                draw_tab_visibility(window)
                db_tab_visibility(window)
                
            except MemoryError:
                hide_window(window)
                messagebox.showinfo("Błąd bazy danych","Podana tabela zawiera ponad 99 kolumn.\nZe względu na ograniczenie pamięci należy wybrać mniejszą tabelę.", )
                show_window(window)
            except:
                hide_window(window)
                messagebox.showinfo("Błąd bazy danych","Nie można wyświetlic wybranej tabeli.", )
                show_window(window)
            


            
        # Funkcje ustawień "HARDWARE"
        
        if event == '-HARDWARE SELECT COUNT SEND-':
            try:
                temp = int(window["-HARDWARE SELECT COUNT-"].get()) 
                if temp <= 0:
                    raise ValueError
                elif temp > 99:
                    raise MemoryError
                window['-HARDWARE SELECT PROMEID-'].update(values=func.get_prome_index(values["-HARDWARE SELECT COUNT-"]))
                window['-EDIT NUMBERS PROMEINDEX-'].update(values=func.get_prome_index(values["-HARDWARE SELECT COUNT-"]))
                config.set("main", "prome_count", values["-HARDWARE SELECT COUNT-"])
                write_config()
                prome_list = func.update_prome_list(prome_list)
                window['-MAIN LIST-'].update(values=func.update_promelist_length(values["-MAIN LIST-"]))
            except ValueError:
                hide_window(window)
                messagebox.showinfo("Błąd wartości","Wpisano niepoprawną wartość.\nZmienna musi być liczbą całkowitą dodatnią.", )
                show_window(window)
            except MemoryError:
                hide_window(window)
                messagebox.showinfo("Błąd wartości","W celu kontroli pamięci nie zezwala się w aplikacji\ndodania więcej niż 99 urządzeń PROME.", )
                show_window(window)
                
        elif event == '-HARDWARE SELECT PROMEID-':
            read_config()
            dev = "P{}".format( values['-HARDWARE SELECT PROMEID-'])
                # W tej sekcji składnia "Aktualizuj jeżeli wartość jest standardowa, inaczej aktualizuj pustą wartość."
            window["-HARDWARE EDITDEV COMPORT-"].update(set_to_index = func.com_ports().index(config.get(dev, "port"))) if config.get(dev, "port") in func.com_ports() else window["-HARDWARE EDITDEV COMPORT-"].update(value = "")
            window["-HARDWARE EDITDEV COMPARITY-"].update(set_to_index = func.parity().index(config.get(dev, "parity"))) if config.get(dev, "parity") in func.parity() else window["-HARDWARE EDITDEV COMPARITY-"].update(value = "")  
            try:
                window["-HARDWARE EDITDEV COMDATABITS-"].update(set_to_index = func.data_bits().index(int(config.get(dev, "bytesize")))) 
            except: window["-HARDWARE EDITDEV COMDATABITS-"].update(value = "")
            
            try:
                window["-HARDWARE EDITDEV DISPLAYS-"].update(set_to_index = func.displays().index(int(config.get(dev, "displays"))))
            except: window["-HARDWARE EDITDEV DISPLAYS-"].update(value = "")  
            try: 
                window["-HARDWARE EDITDEV COMSPEED-"].update(set_to_index = func.serial_speeds().index(int(config.get(dev, "baudrate")))) 
            except: window["-HARDWARE EDITDEV COMSPEED-"].update(value = "")
            try:
                window["-HARDWARE EDITDEV COMSTOPBITS-"].update(set_to_index = func.stop_bits().index(int(config.get(dev, "stopbits")))) 
            except: window["-HARDWARE EDITDEV COMSTOPBITS-"].update(value = "")
   
        elif event == '-HARDWARE EDITDEV SENDID-':
            read_config()
            dev = "P{}".format(values['-HARDWARE SELECT PROMEID-'])
            try:
                config.set(dev, 'port', str(values['-HARDWARE EDITDEV COMPORT-']))
                config.set(dev, 'baudrate', str(values['-HARDWARE EDITDEV COMSPEED-']))
                config.set(dev, 'bytesize', str(values['-HARDWARE EDITDEV COMDATABITS-']))
                config.set(dev, 'displays', str(values['-HARDWARE EDITDEV DISPLAYS-']))
                config.set(dev, 'stopbits', str(values['-HARDWARE EDITDEV COMSTOPBITS-']))
                config.set(dev, 'parity', str(values["-HARDWARE EDITDEV COMPARITY-"]))
                write_config()
                prome_list = func.update_prome_conf(prome_list, values['-HARDWARE SELECT PROMEID-'])
                window['-MAIN LIST-'].update(values=func.prome_list_table(prome_list))
                
                if values['-EDIT NUMBERS PROMEINDEX-'] in range(1,100):
                    dev = "P{}".format(values['-HARDWARE SELECT PROMEID-'])
                    window['-EDIT NUMBERS INDEX-'].update(values=[i for i in range(1, int(config.get(dev, 'displays'))+1)])
                    window['-EDIT VIEW TABLE-'].update(values = func.prome_list_index_values(prome_list, values['-EDIT NUMBERS PROMEINDEX-']))

            except:
                hide_window(window)
                messagebox.showinfo("Błąd wartości","Nie wybrano indeksu PROME", )
                show_window(window)
            
        elif event == '-HARDWARE EDITDEV SENDALL-':
            error_list = []       
            read_config()
            for i in range(0, int(config.get('main','prome_count'))):
                dev = "P{}".format(i+1)
                try:
                    config.set(dev, 'baudrate', str(values['-HARDWARE EDITDEV COMSPEED-']))
                    config.set(dev, 'bytesize', str(values['-HARDWARE EDITDEV COMDATABITS-']))
                    config.set(dev, 'displays', str(values['-HARDWARE EDITDEV DISPLAYS-']))
                    config.set(dev, 'stopbits', str(values['-HARDWARE EDITDEV COMSTOPBITS-']))
                    config.set(dev, 'parity', str(values["-HARDWARE EDITDEV COMPARITY-"]))
                except:
                    error_list.append(i+1)
            write_config()
            prome_list = func.update_prome_conf(prome_list, -1)
            window['-MAIN LIST-'].update(values=func.prome_list_table(prome_list))
            
            pid = values['-EDIT NUMBERS PROMEINDEX-'] 
            
            if (pid in range(1, 100)) and (pid not in error_list):
                dev = "P{}".format(pid)
                window['-EDIT NUMBERS INDEX-'].update(values=[i for i in range(1, int(config.get(dev, 'displays'))+1)])
                window['-EDIT VIEW TABLE-'].update(values = func.prome_list_index_values(prome_list, values['-EDIT NUMBERS PROMEINDEX-']))
                
            if len(error_list) > 0:
                hide_window(window)
                messagebox.showerror("Błąd","Wystąpił bład przy nadpisywaniu indeksów:\n{}".format(error_list), )
                show_window(window)
                
        # Funkcje główne "MAIN"
        
        elif event == '-MAIN CONNCHECK-':
            hide_window(window)
            err_con = []
            init_progressbar_window(0, int(config.get('main', 'prome_count')), "Sprawdzanie połączeń z urządzeniami:")
            update_progressbar_window(0, int(config.get('main', 'prome_count')))
            for i in range(0, int(config.get('main', 'prome_count'))):
                dev = 'P{}'.format(str(i+1))
                if func.serial_check(dev) == 1:
                    err_con.append([dev, config.get(dev,'port')])
                update_progressbar_window(i+1, int(config.get('main', 'prome_count')))
            close_progressbar_window()
            if len(err_con) > 0:
                str_err = ''
                for i in err_con:
                    str_err += i[0]
                    str_err += ': '
                    str_err += i[1]
                    str_err += ', '
                str_err = str_err[:-2]
                messagebox.showwarning("Błąd połączeń","Nie udało się połączyć z urządzeniami:\n{}.".format(str_err),)
            else:
                messagebox.showinfo("Informacja","Wszytkie urządzenia znaleziono pomyslnie.")
            show_window(window)
                
        elif event == '-MAIN SEND-':
            hide_window(window)
            err_con = []
            init_progressbar_window(0, int(config.get('main', 'prome_count')), "Wysyłanie danych:")
            update_progressbar_window(0, int(config.get('main', 'prome_count')))
            for i in range(0, int(config.get('main', 'prome_count'))):
                dev = 'P{}'.format(str(i+1))
                if func.serial_send(dev, prome_list[i]) == 1:
                    err_con.append([dev, config.get(dev,'port')])
                update_progressbar_window(i+1, int(config.get('main', 'prome_count')))
            close_progressbar_window()
            if len(err_con) > 0:
                str_err = ''
                for i in err_con:
                    str_err += i[0]
                    str_err += ': '
                    str_err += i[1]
                    str_err += ', '
                str_err = str_err[:-2]
                messagebox.showwarning("Błąd połączeń","Nie udało się wysłać danych do urządzeń:\n{}.".format(str_err),)
            else:
                messagebox.showinfo("Informacja","Wysłano wszystkie dane.")
            show_window(window)
    
    window.close()  
    
mainloop()



