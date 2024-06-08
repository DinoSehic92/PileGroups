npiles = 8
mindirpiles = 4
alpha_save = []

for i in range(1 << npiles):                            # Räkna fram till npiles
    vek_bin     = format(i, '0' + str(npiles) + 'b')    # Skapa en binär sträng av värdet 1-8, exempelvis 001, 010, 011...
    vek_try     = [int(x) for x in [*vek_bin]]          # Konvertera till en lista, exempelcis [0,0,1], [0,1,0]...

    # Summera elementen i listan och jämför mot avgränsningen. Sorterar alltså bort konfigurationer med färre än mindirpiles i en enskild riktning
    if sum(vek_try) >= mindirpiles and sum(vek_try) <= npiles - mindirpiles:                     
        alpha_save.append(vek_try)                      # Spara ner konfigurationen i en lista

print(alpha_save)



alpha = 90                                              # Multiplikator
for i in range(len(alpha_save)):                        # Gå igenom alla sparade konfigurationer
    alpha_res = [x*alpha for x in alpha_save[i]]        # Multiplicera varje element i listan med mulriplikatorn alpha
    print(alpha_res)                            