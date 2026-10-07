# LISTA VARIANTI

#### Metodi originali (bottom-up)
- **metodo che ritorna optimal_war e tabella s**: costruisce m e s (da usare con ricostruzione soluzione ottima da s)
- **metodo che ritorna solo optimal_war**: costruisce solo m (da usare con ricostruzione soluzione ottima da m)
- **metodo meno efficiente con return tables**: credo da scartare

#### Metodo di costruzione con un solo vettore 
ritorna solo optimal_war, non costruisce ne s ne m. Da utilizzare come variante piu efficiente del bottom-up che restituisce solo optimal war

#### Metodo di costruzione ricorsivo
ritorna solo optimal_war, costruisce m parziale. Da utilizzare come variante piu efficiente del bottom-up che restituisce solo optimal war

#### Metodo di costruzione soluzione ottima da m
ricostruisce soluzione ottima senza s. Da utilizzare come aggiunta al bottom-up originale che calcola solo m.

#### Metodo di costruzione soluzione ottima da s
ricostruisce soluzione ottima con s. Da utilizzare come aggiunta al bottom-up originale che calcola sia m sia s.

#### Filtro di pareto
da usare come variante che abbassa i tempi di esecuzione dei metodi (originale e varianti) che non calcolano s


1) calcolo di m e s, costruzione soluzione ottima da s
2) costruzione di m, calcolo soluzione ottima da m

Varianti per calcolo soluzione ottima: 2
Varianti per calcolo optimal_war con calcolo di s: 2
Varianti per calcolo optimal_war con calcolo solo di m: 4