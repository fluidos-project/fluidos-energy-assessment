# REPORT SUI PRIMI RISULTATI
L'obiettivo di questi test è quello di investigare per cercare di capire se tutti i vantaggi in termini di risparmio di risorse computazionali e energetiche derivanti dall'approccio coudificato possa applicarsi anche in scenari edge-like, caratterzzati da dispositivi general purpose e con capacità computazionali limitate.

A questo proposito è stato sviluppato un simulatore che, a partire da un'infrastruttura eterogenea di dispositivi e da un set di workload da schedulare, è in grado di identificare la soluzione di scheduling ottimale dal punto di vista del consumo energetico.

## DESCRIZIONE DEI TEST
I test sono stati fatti su un'infrastruttura di dimensioni fisse, andando a differenziare il carico da schedulare. In particolare tale infrastruttura è caratterizzata da:

 - 20 postazioni desktop (modellate prendendo come riferimento una macchina desktop di laboratorio)
 - 10 server (modellati prendendo a riferimento una macchina presente nella sala server del laboratorio)

Su questa infrastruttura fissa sono stati definiti due tipi di test in modo tale da identificare i possibili vantaggi di un approccio cloudificato al variare del carico applicato al sistema. In particolare si è voluto investigare in che modo 1) la dimensione e 2) il numero delle applicazioni da schedulare possa influenzare la soluzione ottimale di scheduling. In particolare nello scenario analizzato le 20 macchine desktop sono quelle che hanno la possibilità di spostare il proprio carico all'interno dell'infrastruttura, mentre le postazioni server hanno l'unico scopo di fornire all'occorrenza capacità computazionali.

NOTA: quando si parla generalmente di risorse computazionali (quindi senza menzionare espressamente il termine CPU) si fa riferimento ai "punteggi passmark" che identificano sia lo score delle applicazioni da spostare, sia le risorse disponibili sulle macchine. Si tenga comunque in considerazione che si può sempre passare da CPU a "punteggi passmark" e viceversa.

## UNA APPLICAZIONE
Questa tipologia di test permette di capire come impatta la dimensione delle applicazioni da schedulare sul consumo complessivo della soluzione di scheduling. In particolare nei due grafici successivi sull'asse delle ascisse andiamo a rappresentare la dimensione in percentuale delle applicazioni da schedulare; tale percentuale viene calcolata a partire dal quantitativo di risorse disponibili nelle macchine desktop. Per esempio un valore di 20% che possiamo riscontare nei grafici corrisponde ad uno scenario in cui tutte le macchine desktop hanno un workload da spostare, corrispondente al 20% delle loro risorse disponibili.

Il primo risultato che andiamo ad analizzare è il consumo di risorse CPU nei due tipi di dispositivi; in particolare andiamo ad evidenziare il consumo percentuale di CPU rispettivamente per le postazioni desktop e per i server.

Come si può notare dal grafico successivo, per applicazioni di piccole dimensioni (fino al 20%) si ottiene che la soluzione migliore di scheduling preveda l'utilizzo esclusivo di risorse desktop; all'aumentare della dimensione delle applicazioni si evidenzia come la soluzione migliore di scheduling preveda l'uso (quasi sempre esclusivo) di risorse server, fino alla soglia critica di 80%, oltre la quale le risorse messe a disposizione dal server non garantiscono l'ottimalità della soluzione. Tale comportamento è dovuto alla funzionalità di hyperthreading del server: se si considera la solgia critica dell'80% si può vedere come l'occupazione delle risorse del server sia del 51,4%. Ciò significa che in tale configurazione sono stati riservati tutti i core fisici messi a disposizione del server, lasciando "liberi" quelli virtuali. Aumentando ulteriormente la dimensione delle applicazioni da schedulare al 90%, la scelta di scheduling sul server prevederebbe l'uso dei core virtuali, i quali garantiscono un aumento delle prestazioni del sistema rispetto ai soli core fisici, ma tuttavia comportano un consumo energetico aggiuntivo non in linea con l'aumento delle prestazioni.

![One_application_cpu_usage](../report/plot/one_application_cpu_usage.png)

Una volta analizzata la distribuzione dei diversi workload sull'infrastruttura si può analizzare il consumo energetico di tali soluzioni, soprattutto rapportandoci ad una soluzione che non possa beneficiare dell'approccio cloudificato (ogni applicazione viene eseguita sul desktop di riferimento, con label ORIGINAL nei grafici). Dal grafico successivo si può quindi notare come lo scheduling ottimizzato possa portare dei benefici dal punto di vista del consumo energetico dell'infrastruttura; tali benefici risultano maggiormente evidenti in corrispondenza di scelte di scheduling che prevedano l'uso dei server (per applicazioni di dimensioni comprese tra 20% e 80%), raggiungendo un valore massimo di risparmio teorico di poco superiore all'8% rispetto alla soluzione non cloudificata.

![One_application_consumption](../report/plot/one_application_consumption.png)


## DUE APPLICAZIONI
Questo set di test ha lo scopo di capire se il numero delle appplicazioni da schedulare possa avere un impatto sul consumo energetico complessivo dell'infrastruttura. A tale scopo i workload da schedulare sono stati modificati rispetto al caso precedente: mentre nel caso precedente un workload al 10% corrispondeva ad una applicazione con una richiesta di risorse equivalente a 1/10 delle risorse a disposizione di una macchina desktop, in questo caso la stessa configurazione al 10% corrisponde a due applicazioni, ognuna delle quali richiede 1/20 delle risorse della macchina. Questa scelta garantisce di avere la stessa situazione di carico complessivo dei test precedenti ma con il vantaggio di avere maggiore variabilità delle soluzioni di scheduling (grazie ad applicazioni di dimensioni minori).

Nell'immagine successiva viene mostrato il consumo percentuale delle risorse CPU sia nel caso delle macchine server, sia di quelle desktop. Come si può vedere in questo scenario si ha una maggiore distribuzione delle risorse sulle due tipologie di macchine, rispetto al test precedente, grazie appunto alla maggiore flessibilità derivante dalle applicazioni di dimensione contenuta.

![Two_application_cpu_usage](../report/plot/two_application_cpu_usage.png)

Nel grafico viene infine riportato il consumo della soluzione di scheduling ottimizzata sul consumo energetico e quella originale (che prevede l'esecuzione dei workload sulle maccine desktop). Come per il caso precedente ri riscontrano dei miglioramenti per un carico compessivo compreso tra i 20% e 80%, raggiungendo in questo caso valori di risparmio energetico superiori al 9%.

![Two_application_consumption](../report/plot/two_application_consumption.png)

## COMPARATIVA
In questa comparativa finale vengono messi a confronto i valori di risparmio energetico percepiti nel caso di una singola applicazione e nel caso di due applicazioni (ossia i due test precedenti). Come si può notare dal grafico successivo entrambe le configurazioni presentano lo stesso andamento in termini di risparmio energetico al variare della dimensione dei workload da schedulare; inoltre si può notare che nel caso di 2 applicazioni si riesce ad ottenere sempre un valore maggiore di risparmio grazie alla minore dimensione delle applicazioni, che garantisce maggiore libertà nelle scelte di scheduling.

![Percentual_power_consumption](../report/plot/percentual_power_consumption.png)

# NOTE:
Nella definizione dell'infrastruttura non mettere il "-" nel nome dei device
