import random
import tkinter as tk
from tkinter import ttk, messagebox

# Dati di base
TAPPI={
    "Tappi in Alluminio":{
        "tempo_preparazione": 0.4,
        "tempo_modellazione": 0.6, 
        "tempo_raffreddamento": 1.5,
        "tempo_controllo_qualità": 0.3,
        "tempo_marcatura": 0.0, 
        "tempo_confezionamento": 0.3
    },
    "Tappi in Plastica":{
        "tempo_preparazione": 0.8,
        "tempo_modellazione": 0.4, 
        "tempo_raffreddamento": 0.5, 
        "tempo_controllo_qualità": 0.3, 
        "tempo_marcatura": 0.0, 
        "tempo_confezionamento": 0.2
    },
    "Tappi in Sughero":{
        "tempo_preparazione": 1.0,
        "tempo_modellazione": 0.4, 
        "tempo_raffreddamento": 0.6, 
        "tempo_controllo_qualità": 0.8,
        "tempo_marcatura": 0.3,
        "tempo_confezionamento": 0.2
    }
}


def genera_quantita_casuale(prodotti):  # Genera una quantità casuale di produzione per ogni tipo di prodotto usando una distribuzione normale
    quantita_produzione = {}
    for tipo_prodotto in prodotti.keys():   # Genera quantità intere non negative usando una normale (media 700, dev.std 100)
        q = int(round(random.gauss(700, 100)))
        quantita_produzione[tipo_prodotto] = max(0, q)
    return quantita_produzione


def genera_parametri_configurabili(prodotti):   # Aggiunge un tempo variabile (simula usura/malfunzionamenti) e calcola la capacità massima teorica per tipologia
    tempi_variabili = {}
    for tipo, tempi_base in prodotti.items():
        tempi_variabili[tipo] = {}
        moltiplicatore = random.uniform(0.9, 1.1)  # Variazione di +/- 10%
        
        for fase, tempo_base in tempi_base.items(): # Mantiene in float per accuratezza nel calcolo del tempo totale
            tempi_variabili[tipo][fase] = tempo_base * moltiplicatore
            
    # Parametro casuale per la capacità massima complessiva
    capacita_max = random.randint(1000, 1440)  # Minuti/giorno

    # Calcola la capacità teorica per tipologia (numero massimo di pezzi in 1440 minuti)
    capacita_per_tipo = {}
    tempo_max_giornaliero = 1440    # 24 ore * 60 minuti
    for tipo, tempi in tempi_variabili.items():     # Calcola il tempo unitario totale (somma di tutte le fasi)
        tempo_unitario_tot = sum(tempi.values())
        if tempo_unitario_tot > 0:      # Capacità teorica massima di pezzi producibili in un giorno per quel tipo
            capacita_per_tipo[tipo] = int(tempo_max_giornaliero // tempo_unitario_tot)
        else:
            capacita_per_tipo[tipo] = 0

    return tempi_variabili, capacita_max, capacita_per_tipo


def calcola_tempo_produzione(quantita_prodotta: dict[str, int], tempi_unitari: dict) -> dict:   #Calcola il tempo totale di produzione e il tempo per ogni fase
    tempo_totale_fasi_frazionario = {}      # Accumula in float per accuratezza
    tempo_totale_min_frazionario = 0.0
    
    for tipo_prodotto, quantita in quantita_prodotta.items():
        tempi_prodotto = tempi_unitari.get(tipo_prodotto, {})
        
        for fase, tempo_unitario in tempi_prodotto.items():     # Calcolo del tempo totale richiesto per ogni fase per quel prodotto (in minuti frazionari)
            tempo_fase_frazionario = quantita * tempo_unitario
            
            tempo_totale_fasi_frazionario[fase] = tempo_totale_fasi_frazionario.get(fase, 0.0) + tempo_fase_frazionario
            tempo_totale_min_frazionario += tempo_fase_frazionario

    minuti_totali_arrotondati = int(round(tempo_totale_min_frazionario))    # Arrotondamento del tempo totale (al minuto intero più vicino)

    # Arrotondamento del tempo per ogni fase (al minuto intero più vicino)
    tempo_totale_fasi_arrotondato = {}
    for fase, tempo_frazionario in tempo_totale_fasi_frazionario.items():   # Arrotonda il totale di ogni fase (in minuti interi)
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
        self.title("⚙️ Simulazione Produzione Tappi (ATTAPPA S.R.L.)")
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Accent.TButton', foreground='white', background="#ac2b36", font=('Futura', 12, 'bold'))
        
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)

        # Output Capacità Massima Casuale
        ttk.Label(main_frame, text="Capacità Massima Giornaliera:", font=('Futura', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.cap_max_var = tk.StringVar(value="Generata Casualmente")
        ttk.Label(main_frame, textvariable=self.cap_max_var).grid(row=0, column=1, sticky='w', pady=5)
        
        # Pulsante di Azione
        ttk.Button(main_frame, text="Avvia Simulazione Produzione Mista Tappi", 
        command=self.esegui_simulazione, style='Accent.TButton').grid(row=1, column=0, columnspan=2, pady=20)
        
        # Area Risultati Totali
        ttk.Label(main_frame, text="--- Risultato Complessivo Produzione ---", font=('Futura', 12, 'bold')).grid(row=2, column=0, columnspan=2, pady=10)

        # AGGIUNTA: Giorni Necessari
        self.giorni_necessari_var = tk.StringVar(value="Giorni Necessari: N/D")
        ttk.Label(main_frame, textvariable=self.giorni_necessari_var, font=('Futura', 12, 'bold'), foreground='darkred').grid(row=3, column=0, columnspan=2, pady=5)
        
        # Quantità totale prodotta
        self.quantita_totale_var = tk.StringVar(value="Quantità Prodotta Complessiva: N/D")
        ttk.Label(main_frame, textvariable=self.quantita_totale_var, font=('Futura', 12, 'bold')).grid(row=4, column=0, columnspan=2, pady=5)
        
        # Tempo Complessivo
        self.risultato_tempo = tk.StringVar(value="Tempo Complessivo: N/D")
        ttk.Label(main_frame, textvariable=self.risultato_tempo, font=('Futura', 14, 'bold')).grid(row=5, column=0, columnspan=2, pady=5)

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
        self.tree.grid(row=6, column=0, columnspan=2, pady=10)

        # Dettaglio Output Seconda Tabella (Dettaglio Tempi per ogni Fase)
        ttk.Label(main_frame, text="--- Dettaglio Tempi per ogni Fase ---", font=('Futura', 12, 'bold')).grid(row=8, column=0, columnspan=2, pady=(15, 5))
        
        # Estraggo l'ordine delle fasi
        fasi_set = set()
        for tempi in self.prodotti_base.values():
            fasi_set.update(tempi.keys())
            
        primo_prodotto = next(iter(self.prodotti_base.values()))    # Ordina il primo prodotto
        self.fasi_ordinate = [fase for fase in primo_prodotto.keys()]
        # Aggiungo fasi uniche non presenti nel primo elemento, ordinate alfabeticamente
        for fase in sorted(fasi_set - set(self.fasi_ordinate)):
             self.fasi_ordinate.append(fase)

        self.fase_tree = ttk.Treeview(main_frame, columns=('Fase', 'TempoTotale'), show='headings', height=len(self.fasi_ordinate))
        self.fase_tree.heading('Fase', text='Fase Produttiva')
        self.fase_tree.heading('TempoTotale', text='Tempo Totale (min)')
        self.fase_tree.column('Fase', width=200)
        self.fase_tree.column('TempoTotale', width=150, anchor='center')
        
        # Prepopola la tabella delle fasi e SALVA I RIFERIMENTI
        for fase in self.fasi_ordinate:
            # Formatta il nome della fase per la visualizzazione
            display = fase.replace('tempo_', '').replace('_', ' ').capitalize()
            # Inserisce l'elemento e salva il suo 'item' ID associato al nome della fase
            item_id = self.fase_tree.insert('', 'end', values=(display, 'N/D'))
            self.fase_tree_items[fase] = item_id 
            
        self.fase_tree.grid(row=10, column=0, columnspan=2, pady=5)


    def esegui_simulazione(self):
        # 1.Generazione Casuale di Tutti i Parametri
        quantita_produzione = genera_quantita_casuale(self.prodotti_base)
        tempi_unitari_config, capacita_max, capacita_per_tipo = genera_parametri_configurabili(self.prodotti_base)
        
        # 2.Limitazione: usa la capacità teorica per tipologia
        for nome, quantita in list(quantita_produzione.items()):
            cap = capacita_per_tipo.get(nome)
            if cap is not None and quantita > cap:
                quantita_produzione[nome] = cap
                
        # 3.Calcolo del Risultato (dopo eventuale riduzione)
        risultato_calcolo = calcola_tempo_produzione(quantita_produzione, tempi_unitari_config)

        # 4.Aggiornamento GUI
        self.cap_max_var.set(f"**{capacita_max} minuti/giorno**")
        
        # Calcola i giorni necessari
        tempo_min_totale = risultato_calcolo['tempo_produzione_complessivo_min']
        # Calcola i giorni di produzione richiesti
        giorni_richiesti = round(tempo_min_totale / capacita_max, 2) if capacita_max > 0 else "Illimitato" 
        
        self.giorni_necessari_var.set(f"Giorni di Produzione Richiesti: **{giorni_richiesti} giorni**")

        # Calcola e mostra la quantità totale prodotta
        quantita_totale = sum(quantita_produzione.values())
        self.quantita_totale_var.set(f"Quantità Prodotta Complessivamente: **{quantita_totale}**")

        self.risultato_tempo.set(
            f"Tempo di Produzione Complessivo: **{tempo_min_totale} Minuti** "
            f"(ovvero {risultato_calcolo['tempo_produzione_complessivo_formato']} ore)"
        )

        # Aggiorna Dettaglio per Prodotto (Treeview principale) - CANCELLA E INSERISCI
        for item in self.tree.get_children():
            self.tree.delete(item)

        for nome, quantita in quantita_produzione.items():
            tempi = tempi_unitari_config.get(nome, {})
            tempo_unitario_totale = sum(tempi.values())
            self.tree.insert('', 'end', values=(
                nome,
                quantita,
                round(tempo_unitario_totale, 2) 
            ))
        
        # Aggiorna Dettaglio per Fase (fase_tree) - AGGIORNA GLI ELEMENTI ESISTENTI
        for fase, item_id in self.fase_tree_items.items():
            tempo_totale = risultato_calcolo['tempo_fasi_dettaglio'].get(fase, 0)
            # Recupera il nome display corretto (colonna 0) e aggiorna solo il tempo (colonna 1)
            current_values = self.fase_tree.item(item_id, 'values')
            display_name = current_values[0] if current_values else fase.replace('tempo_', '').replace('_', ' ').capitalize()
            self.fase_tree.item(item_id, values=(display_name, tempo_totale))

        # 5. Notifica di successo
        messagebox.showinfo("Simulazione Completata", f"L'ordine di {quantita_totale} tappi richiede {giorni_richiesti} giorni di produzione.")


if __name__ == "__main__":
    app = SimulaProduzione(TAPPI)
    app.mainloop()