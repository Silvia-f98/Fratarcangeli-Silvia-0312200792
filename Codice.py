import random
import tkinter as tk
from tkinter import ttk, messagebox


# Costanti
CAPACITA_MAX_GIORNALIERA = 86400 # Secondi in un giorno
CAPACITA_MIN_GIORNALIERA = 70000 # Variazione massima (in negativo) possibile dalla Capacità Max
VARIAZIONE_TEMPI_MAX = 1.1 # Aumenta del 10% max il Tempo di Produzione


# Dati di base dei prodotti
TAPPI={
    "Tappi in Alluminio":{
        "tempo_preparazione": 0.06,
        "tempo_modellazione": 0.12, # Fase più lunga per questo tipo di prodotto
        "tempo_raffreddamento": 0.08,
        "tempo_controllo_qualità": 0.03,
        "tempo_marcatura": 0.0, # Fase non necessaria per questo tipo di prodotto
        "tempo_confezionamento": 0.03
    },
    "Tappi in Plastica":{
        "tempo_preparazione": 0.04,
        "tempo_modellazione": 0.08, 
        "tempo_raffreddamento": 0.15, # Fase più lunga per questo tipo di prodotto
        "tempo_controllo_qualità": 0.03, 
        "tempo_marcatura": 0.0, # Fase non necessaria per questo tipo di prodotto
        "tempo_confezionamento": 0.03
    },
    "Tappi in Sughero":{
        "tempo_preparazione": 0.10, 
        "tempo_modellazione": 0.08, 
        "tempo_raffreddamento": 0.00,   # Fase non necessaria per questo tipo di prodotto
        "tempo_controllo_qualità": 0.13,    # Fase più lunga per questo tipo di prodotto
        "tempo_marcatura": 0.03,
        "tempo_confezionamento": 0.05
    }
}


def genera_quantita_casuale(prodotti):  # Genera una quantità casuale prodotta per ogni tipo di prodotto usando una distribuzione normale
    quantita_produzione = {}   
    for tipo_prodotto in prodotti.keys():
        if tipo_prodotto == "Tappi in Alluminio": # Set media e dev.std. per il primo prodotto
            media = 8400000
            dev_std = 1000000
        elif tipo_prodotto == "Tappi in Plastica": # Set media e dev.std. per il secondo prodotto
            media = 3990000
            dev_std = 50000
        elif tipo_prodotto == "Tappi in Sughero": # Set media e dev.std. per il terzo prodotto
            media = 1095000
            dev_std = 5000
            
        q = int(round(random.gauss(media, dev_std))) # Genera quantità casuali intere usando una normale
        quantita_produzione[tipo_prodotto] = max(0, q) # Controlla che la quantità generata non sia negativa
        
    return quantita_produzione


def genera_parametri_configurabili(prodotti):   # Aggiunge un tempo variabile (simula usura/malfunzionamenti/ritardi) e calcola la capacità teorica per tipologia
    tempi_variabili = {}
    for tipo, tempi_base in prodotti.items():
        tempi_variabili[tipo] = {}
        moltiplicatore = random.uniform(1.0, VARIAZIONE_TEMPI_MAX)  # Servirà ad aumentare al max del 10% il tempo base della produzione
        for fase, tempo_base in tempi_base.items(): # Mantiene in float per accuratezza nel calcolo del tempo totale
            tempi_variabili[tipo][fase] = tempo_base * moltiplicatore

    # Calcola la capacità teorica per tipologia (numero massimo di pezzi in 86400 secondi, ovvero 1440 minuti, ovvero 1 giorno)
    tempo_effettivo_giornaliero = random.randint(CAPACITA_MIN_GIORNALIERA, CAPACITA_MAX_GIORNALIERA)  # Tempo di attività di produzione giornaliera del macchinario
    capacita_per_tipo = {}
    for tipo, tempi in tempi_variabili.items():     # Calcola il tempo unitario totale (somma di tutte le fasi)
        tempo_unitario_tot = sum(tempi.values())
        if tempo_unitario_tot > 0:      # Capacità teorica massima di pezzi producibili in un giorno per quel tipo
            capacita_per_tipo[tipo] = int(tempo_effettivo_giornaliero // tempo_unitario_tot)
        else:
            capacita_per_tipo[tipo] = 0

    return tempi_variabili, tempo_effettivo_giornaliero, capacita_per_tipo


def calcola_tempo_produzione(quantita_prodotta: dict[str, int], tempi_unitari: dict) -> dict:   # Calcola il tempo totale di produzione e il tempo per ogni fase
    tempo_totale_fasi_frazionario = {}  # Accumula in float per accuratezza
    tempo_totale_min_frazionario = 0.0
    
    for tipo_prodotto, quantita in quantita_prodotta.items():
        tempi_prodotto = tempi_unitari.get(tipo_prodotto, {})
        
        for fase, tempo_unitario in tempi_prodotto.items(): # Calcolo del tempo totale richiesto per ogni fase per quel prodotto (in secondi frazionari)
            tempo_fase_frazionario = (quantita * tempo_unitario) / 60   # Dividendo per 60 si converte l'unità di misura passando da secondi a minuti   
            
            tempo_totale_fasi_frazionario[fase] = tempo_totale_fasi_frazionario.get(fase, 0.0) + tempo_fase_frazionario
            tempo_totale_min_frazionario += tempo_fase_frazionario

    minuti_totali_arrotondati = int(round(tempo_totale_min_frazionario))   # Arrotondamento del tempo totale (al minuto intero più vicino)

    # Arrotondamento del tempo per ogni fase (al minuto intero più vicino)
    tempo_totale_fasi_arrotondato = {}
    for fase, tempo_frazionario in tempo_totale_fasi_frazionario.items():   # Arrotonda il totale di ogni fase (in secondi interi)
        tempo_totale_fasi_arrotondato[fase] = int(round(tempo_frazionario))
    
    # Calcola ore e minuti per la visualizzazione
    ore = minuti_totali_arrotondati // 60
    minuti = minuti_totali_arrotondati % 60

    risultato = {
        "tempo_produzione_complessivo_min": minuti_totali_arrotondati,
        "tempo_produzione_complessivo_ore": ore,
        "tempo_produzione_complessivo_formato": f"{ore:02d}:{minuti:02d}",
        "tempo_fasi_dettaglio": tempo_totale_fasi_arrotondato,
    }
    
    return risultato


class SimulaProduzione(tk.Tk):

    def __init__(self, prodotti_base):
        super().__init__()
        self.prodotti_base = prodotti_base
        self.fasi_ordinate = []     # Nuove variabili per salvare i riferimenti agli elementi della fase_tree
        self.fase_tree_items = {} 
        self.crea_interfaccia()

    def crea_interfaccia(self):
        self.title("Simulazione Processo di Produzione (ATTAPPA S.R.L.)") 
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Accent.TButton', foreground='white', background="#ac2b36", font=('Futura', 12, 'bold'))
        
        main_frame = ttk.Frame(self, padding="40")  # Inizializza il frame dell'interfaccia
        main_frame.pack(fill='both', expand=True)   # Rende espandibile l'interfaccia in base al contenuto sia in orizzontale sia in verticale

        # Area Risultati Totali
        ttk.Label(main_frame, text="--- Risultato Complessivo Produzione ---", font=('Futura', 16, 'bold'), foreground='darkred').grid(row=0, column=0, columnspan=2, pady=10)
        
        # Quantità Totale Prodotta
        self.quantita_totale_var = tk.StringVar(value="Quantità Prodotta Complessiva: N/D")
        ttk.Label(main_frame, textvariable=self.quantita_totale_var, font=('Futura', 12, 'bold')).grid(row=1, column=0, columnspan=2, pady=5)

        # Tempo Complessivo
        self.risultato_tempo = tk.StringVar(value="Tempo di Produzione Complessivo: N/D")
        ttk.Label(main_frame, textvariable=self.risultato_tempo, font=('Futura', 12, 'bold')).grid(row=2, column=0, columnspan=2, pady=5)

        # Giorni Necessari
        self.giorni_necessari_var = tk.StringVar(value="Giorni di Produzione Richiesti: N/D")
        ttk.Label(main_frame, textvariable=self.giorni_necessari_var, font=('Futura', 12, 'bold')).grid(row=3, column=0, columnspan=2, pady=5)

        # Tempo Lavoro Macchinario
        self.cap_max_var = tk.StringVar(value="Tempo Operativo Macchinari: N/D")
        ttk.Label(main_frame, textvariable=self.cap_max_var, font=('Futura', 12, 'bold')).grid(row=4, column=0, columnspan=2, pady=5)

        # Dettaglio Output Prima Tabella (Treeview Prodotto / Quantità / Tempo Unitario)
        colonne = ('Prodotto', 'Quantita', 'Tempo Unitario Totale (min)')
        self.tree = ttk.Treeview(main_frame, columns=colonne, show='headings', height=len(self.prodotti_base))
        self.tree.heading('Prodotto', text='Prodotto')
        self.tree.heading('Quantita', text='Q.tà Prodotta')
        self.tree.heading('Tempo Unitario Totale (min)', text='Tempo Unitario Totale (min)')
        self.tree.column('Prodotto', width=130, anchor='w')
        self.tree.column('Quantita', width=100, anchor='center')
        self.tree.column('Tempo Unitario Totale (min)', width=180, anchor='center')
        for nome in self.prodotti_base.keys():      # Imposta di default N/D ai nomi dei prodotti prima di eseguire il programma
            self.tree.insert('', 'end', values=(nome, "N/D", "N/D"))
        self.tree.grid(row=5, column=0, columnspan=2, pady=10)

        # Dettaglio Output Seconda Tabella (Dettaglio Tempi per ogni Fase)
        ttk.Label(main_frame, text="--- Dettaglio Tempi per ogni Fase ---", font=('Futura', 12, 'bold')).grid(row=7, column=0, columnspan=2, pady=(15, 5))

        # Pulsante di Azione
        ttk.Button(main_frame, text="Avvia Simulazione", command=self.esegui_simulazione, style='Accent.TButton').grid(row=11, column=0, columnspan=2, pady=20)
        
        # Estrazione dell'ordine delle fasi
        fasi_set = set()
        for tempi in self.prodotti_base.values():
            fasi_set.update(tempi.keys())
            
        primo_prodotto = next(iter(self.prodotti_base.values()))    # Ordina il primo prodotto
        self.fasi_ordinate = [fase for fase in primo_prodotto.keys()]
        # Aggiunta di fasi uniche non presenti nel primo elemento, ordinate alfabeticamente
        for fase in sorted(fasi_set - set(self.fasi_ordinate)):
             self.fasi_ordinate.append(fase)

        self.fase_tree = ttk.Treeview(main_frame, columns=('Fase', 'TempoTotale'), show='headings', height=len(self.fasi_ordinate))
        self.fase_tree.heading('Fase', text='Fase Produttiva')
        self.fase_tree.heading('TempoTotale', text='Tempo Totale (min)')
        self.fase_tree.column('Fase', width=200)
        self.fase_tree.column('TempoTotale', width=150, anchor='center')
        
        # Prepopola la tabella delle fasi e Salva i riferimenti
        for fase in self.fasi_ordinate:
            # Formatta il nome della fase per la visualizzazione
            display = fase.replace('tempo_', '').replace('_', '').capitalize()
            # Inserisce l'elemento e salva il suo 'item' ID associato al nome della fase
            item_id = self.fase_tree.insert('', 'end', values=(display, 'N/D'))
            self.fase_tree_items[fase] = item_id 
            
        self.fase_tree.grid(row=10, column=0, columnspan=2, pady=5)


    def esegui_simulazione(self):

        # Generazione Casuale di Tutti i Parametri
        quantita_produzione = genera_quantita_casuale(self.prodotti_base)
        tempi_unitari_config, tempo_effettivo_giornaliero, capacita_per_tipo = genera_parametri_configurabili(self.prodotti_base)
        
        # Calcolo del Risultato (dopo eventuale riduzione)
        risultato_calcolo = calcola_tempo_produzione(quantita_produzione, tempi_unitari_config)

        # Inizia l'aggiornamento della GUI
        # Calcola e mostra la quantità totale prodotta
        quantita_totale = sum(quantita_produzione.values())
        self.quantita_totale_var.set(f"Quantità Prodotta Complessivamente: {quantita_totale} unità")
        
        # Calcola i giorni necessari
        tempo_min_totale = risultato_calcolo['tempo_produzione_complessivo_min']
        # Calcola i giorni di produzione richiesti
        giorni_richiesti = round(tempo_min_totale / round (tempo_effettivo_giornaliero / 60), 2) if tempo_effettivo_giornaliero > 0 else "Illimitato" 
        self.risultato_tempo.set(f"Tempo di Produzione Complessivo: {tempo_min_totale} minuti " f"(ovvero {risultato_calcolo['tempo_produzione_complessivo_formato']} ore)")
        
        self.giorni_necessari_var.set(f"Giorni di Produzione Richiesti: {giorni_richiesti} giorni")

        # Aggiornamento GUI
        self.cap_max_var.set(f"Tempo Operativo Macchinari: {round(tempo_effettivo_giornaliero/60)} minuti/giorno") # Converte e arrotonda il tempo effettivo giornaliero da secondi in minuti


        # Aggiorna Dettaglio per Prodotto (Treeview principale) - Cancella e inserisci
        for item in self.tree.get_children():
            self.tree.delete(item)

        for nome, quantita in quantita_produzione.items():
            tempi = tempi_unitari_config.get(nome, {})
            tempo_unitario_totale = sum(tempi.values())
            self.tree.insert('', 'end', values=(nome, quantita, round(tempo_unitario_totale, 2)))
        
        # Aggiorna Dettaglio per Fase (fase_tree) - Aggiorna gli elementi esistenti
        for fase, item_id in self.fase_tree_items.items():
            tempo_totale = risultato_calcolo['tempo_fasi_dettaglio'].get(fase, 0)
            # Recupera il nome display corretto (colonna 0) e aggiorna solo il tempo (colonna 1)
            current_values = self.fase_tree.item(item_id, 'values')
            display_name = current_values[0] if current_values else fase.replace('tempo_', '').replace('_', ' ').capitalize()
            self.fase_tree.item(item_id, values=(display_name, tempo_totale))

        # Notifica di successo
        messagebox.showinfo("Simulazione Completata", f"L'ordine di {quantita_totale} tappi richiede {giorni_richiesti} giorni di produzione.")


if __name__ == "__main__":
    app = SimulaProduzione(TAPPI)
    app.mainloop()