# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 19:14:45 2024

@author: juanv
"""
import random
from multiprocessing import Queue, Value, Process
import numpy as np

#SE PRESENTAN AQUÍ TODAS LAS FUNCIONES QUE SE HAN UTILIZADO EN EL TRABAJO ORGANIZADAS POR ORDEN DE APARICIÓN.


#PRIMERA CLASE IMPLEMENTADA (CRONOLÓGICAMENTE) DE PROBLEMA GENÉTICO PARA LA CREACIÓN DE MELODÍAS

class ProblemaGeneticoMelodia1(object):
        def __init__(self, genes,fun_dec,fun_muta , fun_cruza, fun_fitness, longitud_individuos): 
            self.genes = genes
            self.fun_dec = fun_dec
            self.fun_cruza = fun_cruza
            self.fun_muta = fun_muta
            self.fun_fitness = fun_fitness
            self.longitud_individuos = longitud_individuos
            
            
            """Constructor de la clase"""
                
        def decodifica(self, genotipo):
            """Devuelve el fenotipo a partir del genotipo"""
            fenotipo = self.fun_dec(genotipo)
            return fenotipo
        
        def muta(self, cromosoma,prob):
            """Devuelve el cromosoma mutado"""   
            mutante = self.fun_muta(cromosoma,prob)
            return mutante
        
        def cruza(self, cromosoma1, cromosoma2):         
            """Devuelve el cruce de un par de cromosomas"""
            cruce = self.fun_cruza(cromosoma1,cromosoma2)
            return cruce 
        
        def fitness(self, cromosoma):    
            """Función de valoración"""
            
            valoracion = self.fun_fitness(cromosoma)
            return valoracion
        
        
#PRIMEROS DICCIONARIOS DE CODIFICACIÓN Y DECODIFICACIÓN

notas_codificar = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F':5, 'F#': 6, 'G': 7, 'G#': 8, 'A':9, 'A#': 10, 'B': 11, 'C2':12}
  
notas_decodificar = {0:'C', 1:'C#', 2:'D', 3:'D#', 4:'E', 5:'F', 6:'F#', 7:'G', 8:'G#', 9:'A', 10:'A#', 11:'B', 12:'C2'}  

#PRIMEROS GENES

genes = []
for i in range(0,len(notas_codificar)):
    genes.append(i)
 

def fun_dec_melodia(genotipo):
    resul = []
    for i in genotipo:
        resul.append(notas_decodificar[i])
    return resul

def poblacion_inicial(problema_genetico, size):
    l=[] # población inicial
    for i in range(size): # añadimos a la población size individuos
        x=[]
        for j in range(problema_genetico.longitud_individuos): # los individuos se generan eligiendo sus genes
                                                               # de manera aleatoria de entre los genes posibles
            x.append(random.choice(problema_genetico.genes))
        l.append(x) 
    
    return l   

    
def seleccion_por_torneo(problema_genetico, poblacion, n, k, opt):
    """Selección por torneo de n individuos de una población. Siendo k el nº de participantes
        y opt la función max o min."""
    seleccionados = []
    for i in range(n): 
        participantes = random.sample(poblacion,k)
        seleccionado = opt(participantes, key=problema_genetico.fitness)
        #opt(poblacion, key=problema_genetico.fitness)
        seleccionados.append(seleccionado)
        # poblacion.remove(seleccionado)
    return seleccionados



def fun_cruzar_dpc(cromosoma1, cromosoma2):  ##HACEMOS DOUBLE POINT CROSSOVER. 
    l1 = len(cromosoma1)
    
    punto_cruce1_1 = random.randint(1,l1-2)
    punto_cruce1_2 = random.randint(1,l1-2)
    c11 = max(punto_cruce1_1, punto_cruce1_2)
    c12 = min(punto_cruce1_1, punto_cruce1_2)
    cruce1 = cromosoma1[0:c12] + cromosoma2[c12:c11] + cromosoma1[c11:l1]
    cruce2 = cromosoma2[0:c12] + cromosoma1[c12: c11] + cromosoma2[c11:l1]
    
    return [cruce1,cruce2]

def cruza_padres(problema_genetico,padres):
    l = []
    for i in range(len(padres)//2):# asumimos que la población de la que partimos tiene tamaño par
        desc = problema_genetico.fun_cruza(padres[2*i],padres[2*i+1]) # El cruce se realiza con la función de cruce  
                                                                     # proporcionada por el propio problema genético
        l.append(desc[0]) # La población resultante se obtiene de cruzar el padre[0] con padre[1], padre[2] con padre[3]...
        l.append(desc[1]) # y añadir cada par de descendientes a la nueva población
    return l 


def muta_individuos(problema_genetico, poblacion, prob):
    # problema_genetico.muta(x,prob) para todos los individuos de la poblacion.
    l = []
    for i in poblacion:
        l.append(problema_genetico.muta(i,prob))
    return l

def fun_mutar_int(cromosoma, prob):  #Se muta cada alelo según una probabilidad de una pequeña cantidad
    l = len(notas_codificar)
    for i in range(len(cromosoma)):
        p = random.randint(1, 4)
        if prob > random.uniform(0,1):
            if cromosoma[i] < 4:
                s = 1
            elif cromosoma[i] > l-5:
                s = -1 
            else:
                s = random.choice([1, -1])
                
            cromosoma[i] = cromosoma[i] + s*p
            
    return cromosoma

def fun_mutar(cromosoma,prob):
    """Elige un elemento al azar del cromosoma y lo modifica con una probabilidad igual a prob"""
    l = len(cromosoma)
    p = random.randint(0,l-1)
    if prob > random.uniform(0,1):
        cromosoma[p] =  random.randint(0, len(notas_decodificar)-1) #Asignamos una nota aleatoria a la secuencia.
        
    return cromosoma


def nueva_generacion(problema_genetico, k,opt, poblacion, n_padres, n_directos, prob_mutar):
    padres2 = seleccion_por_torneo(problema_genetico, poblacion, n_directos, k,opt) # torneo pero no se cruzan
    padres1 = seleccion_por_torneo(problema_genetico, poblacion, n_padres , k, opt) # torneo per sí se cruzan
    cruces =  cruza_padres(problema_genetico,padres1)
    generacion = padres2+cruces
    resultado_mutaciones = muta_individuos(problema_genetico, generacion, prob_mutar)
    return resultado_mutaciones


# La siguiente función implementa una posibilidad para el algoritmo genético completo con los elementos anteriores: 
# inicializa t = 0 
# Generar y evaluar la Población P(t)
# Mientras no hemos llegado al número de generaciones fijado:  t < nGen
#    P1 = Selección por torneo de (1-size)·p individuos de P(t)
#    P2 = Selección por torneo de (size·p) individuos de P(t)
#    Aplicar cruce en la población P2
#    P4 = Union de P1 y P3
#    P(t+1) := Aplicar mutación P4 
#    Evalua la población P(t+1) 
#    t:= t+1
        
# Sus argumentos son:
# problema_genetico: una instancia de la clase ProblemaGenetico con la representación adecuada del problema de optimización 
# que se quiere resolver.
# k: número de participantes en los torneos de selección.
# opt: max ó min, dependiendo si el problema es de maximización o de minimización. 
# nGen: número de generaciones (que se usa como condición de terminación)
# size: número de individuos en cada generación
# prop_cruce: proporción del total de la población que serán padres. 
# prob_mutación: probabilidad de realizar una mutación de un gen.



def algoritmo_genetico(problema_genetico,k,opt,ngen,size,prop_cruces,prob_mutar):
    poblacion= poblacion_inicial(problema_genetico,size)
    
    n_padres=round(size*prop_cruces)
    
    n_padres= int (n_padres if n_padres%2==0 else n_padres-1)
    
    n_directos = size-n_padres
    for _ in range(ngen):
        poblacion= nueva_generacion(problema_genetico,k,opt,poblacion,n_padres, n_directos,prob_mutar)

    mejor_cr= opt(poblacion, key=problema_genetico.fitness)
    mejor=problema_genetico.decodifica(mejor_cr)
    return mejor, problema_genetico.fitness(mejor_cr), mejor_cr



#PRIMER PASO, REFLEXIONAR SOBRE LOS INTERVALOS ENTRE LAS NOTAS




def distancia_relativa1(nota1:int, nota2:int)->int:
    distancia = abs(nota1-nota2) % 12 
    return distancia


##Primer experimento: Para la función de fitness vamos a intentar asignar recompensas en base a como de consonante suena una nota de la siguiente.
##Versión naif: asignamos a mayor grado de consonancia más puntos.

def recompensa(nota:int, siguiente:int)->int:  
    if distancia_relativa1(nota, siguiente) == 0: ##Es la misma nota (no queremos que se repita mucho)
        return 3    
    elif distancia_relativa1(nota, siguiente) == 1:  ##Segunda menor
        return 1
    elif distancia_relativa1(nota, siguiente) == 2: ##Segunda mayor
        return 2
    elif distancia_relativa1(nota, siguiente) == 3: ##Tercera menor
        return 3
    elif distancia_relativa1(nota, siguiente) == 4: ##Tercera mayor
        return 4
    elif distancia_relativa1(nota, siguiente) == 5: ##Cuarta justa
        return 5
    elif distancia_relativa1(nota, siguiente) == 6: ##Cuarta aumentada
        return 1
    elif distancia_relativa1(nota, siguiente) == 7: ##Quinta justa
        return 6
    elif distancia_relativa1(nota, siguiente) == 8: ##Sexta menor
        return 2 
    elif distancia_relativa1(nota, siguiente) == 9: ##Sexta mayor
        return 4
    elif distancia_relativa1(nota, siguiente) == 10: ##Séptima menor
        return 3
    elif distancia_relativa1(nota, siguiente) == 11: ##Séptima mayor
        return 2
    elif distancia_relativa1(nota, siguiente) == 12: ##Octava (muy consonante pero no queremos que aparezca demasiado).
        return 4
    


#PRIMERA FUNCIÓN DE FITNESS QUE IMPLEMENTA TAN SÓLO LA RECOMPENSA DE DE DISTANCIAS RELATIVAS.
def func_fitness1( lista_notas:list)->int:  ##Lista notas es una lista de enteros.
    c = 0 
    fin = len(lista_notas)
    resul = 0
    while c < (fin-1):
       
        rec = recompensa(lista_notas[c], lista_notas[c+1])
        
        resul += rec
        c += 1 
    return resul 


##PRIMER EJEMPLO DE EJECUCIÓN DEL ALGORITMO PARA FIGURAS 3 Y 4
"""
longitud_individuos = 10


opt = max
individuos = 50
generaciones = 800
padres = 0.2
mutacion = 0.1
torneo = 15

problema = ProblemaGeneticoMelodia1(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, func_fitness1, longitud_individuos)

resul = algoritmo_genetico(problema, torneo, opt, generaciones, individuos, padres, mutacion)
print('resultado: ',  resul[0], '\n', 'valor de aptitud: ', resul[1])

"""

nota_escala = random.randint(0,11)##La escala pentatónica sobre la que se hará la melodía será una escogida aleatoriamente.


def escala_pentatonica(nota:int)->list:
    escala = [nota]
    
    lista_distancias = [2,2,3,2]
    for i in lista_distancias:
        nota = (nota + i) % 12
        escala.append(nota)
        
    return escala
        


def func_fitness_pent(lista_notas: list)->int: #Versión más simple: Si es una nota de la escala pentatónica le ponemos 1 y si no, 
     
     escala_p = escala_pentatonica(nota_escala)
    
     
     recompensa = 0
     
     for i in lista_notas:
         
         if i%12 in escala_p:  
             
             recompensa  += 1 
     
     return recompensa



#EJEMPLO DE EJECUCIÓN CON LA FUNCIÓN DE FITNESS DE LA ESCALA PENTATÓNICA (COMO EN LA FIGURA 5).

"""
print(notas_decodificar[nota_escala])
longitud_individuos = 10


opt = max
individuos = 50
generaciones = 800
padres = 0.2
mutacion = 0.1
torneo = 15

problema = ProblemaGeneticoMelodia1(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, func_fitness_pent, longitud_individuos)

resul = algoritmo_genetico(problema, torneo, opt, generaciones, individuos, padres, mutacion)
print('resultado: ',  resul[0], '\n', 'valor de aptitud: ', resul[1])

"""
#AUMENTAMOS EL RANGO DE NOTAS PARA QUE EL PROBLEMA SEA MÁS INTERESANTE

notas_codificar = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F':5, 'F#': 6, 'G': 7, 'G#': 8, 'A':9, 'A#': 10, 'B': 11, 'C2':12, 'C#2': 13, 'D2': 14, 'D#2': 15, 'E2': 16, 'F2':17, 'F#2': 18, 'G2': 19, 'G#2': 20, 'A2':21, 'A#2': 22, 'B2': 23 }
  
notas_decodificar = {0:'C', 1:'C#', 2:'D', 3:'D#', 4:'E', 5:'F', 6:'F#', 7:'G', 8:'G#', 9:'A', 10:'A#', 11:'B', 12:'C2',  13:'C#2', 14:'D2', 15:'D#2', 16:'E2', 17:'F2', 18:'F#2', 19:'G2', 20:'G#2', 21:'A2', 22:'A#2', 23:'B2'}  

#ACTUALIZAMOS LOS GENES

genes = []
for i in range(0,len(notas_codificar)):
    genes.append(i)
 

#SE INTENTA AHORA HACER LAS MELODÍAS MÁS CANTABILES

def recompensa_por_distancias1(lista_notas: list)-> int: ##Esta función mira la sucesión de las notas y da una evaluación positiva si no distan mucho (tiene más sentido si consideramos más octavas). 
      c = 0 
      fin = len(lista_notas)
      recompensa = 0
      while c < (fin-1):
          distancia = abs(lista_notas[c] - lista_notas[c+1])
          if distancia <= 4:   
              recompensa += 2 
              
          elif distancia > 4 and distancia  <= 9:
              recompensa += 1
          
          c += 1 
      return recompensa
  

def func_fitness_pentV2(lista_notas: list)->int:  
     
     escala_p = escala_pentatonica(nota_escala)
     recompensa = 0
     
     for i in lista_notas:
         
         if i%12 in escala_p:  
             
             recompensa  += 1 
             
     recompensa += recompensa_por_distancias1(lista_notas)
     
     return recompensa
    
    
    
#EJEMPLO DE EJECUCIÓN DE LA FUNCIÓN DE FITNESS CON ESCALA PENTATÓNICA Y RECOMPENSA POR DISTANCIAS (COMO EN LA FIGURA 6)

"""
print(notas_decodificar[nota_escala])
longitud_individuos = 11 #Se ha cambiaado la estructura rítmica.


opt = max
individuos = 50
generaciones = 800
padres = 0.2
mutacion = 0.1
torneo = 15

problema = ProblemaGeneticoMelodia1(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, func_fitness_pentV2, longitud_individuos)

resul = algoritmo_genetico(problema, torneo, opt, generaciones, individuos, padres, mutacion)
print('resultado: ',  resul[0], '\n', 'valor de aptitud: ', resul[1])

"""




modos_de_la_escala = {'jonico': [2,2,1,2,2,2,1], 'dorico' : [2,1,2,2,2,1,2], 'frigio' : [1,2,2,2,1,2,2], 'lidio' : [2,2,2,1,2,2,1],  'mixolidio' : [2,2,1,2,2,1,2], 'eolico' : [2,1,2,2,1,2,2], 'locrio' : [1,2,2,1,2,2,2] }

def escala_modal(nota:int, modo:str)->list:
    mod = modos_de_la_escala[modo]
    
    escala = [nota]
    for i in range(len(mod)-1):
        escala.append((escala[-1] + mod[i]) % 12)
    return escala
   
##MODO
modo = random.choice(list(modos_de_la_escala.keys()))



def recompensa_escala_modo(lista_notas, modo, nota_escala):
    recompensa = 0
    escala_m = escala_modal(nota_escala, modo)
    for i in lista_notas:
        if notas_decodificar[i%12] in escala_m:
            recompensa += 1 
    return recompensa


def recompensa_creciente(lista_notas:list)->int:
    recompensa = 0
    #Para que no sea sólo una sucesión creciente de notas, vamos a dividir la melodía en dos bloques (para empezar).
    bloque = len(lista_notas)//2 
    parte1 = lista_notas[0: bloque]
    parte2 = lista_notas[bloque:]
    #En principio no vamos a poner un requisito especial sobre cómo de mucho queremos que crezca
    if parte1[-1] - parte1[0] > 0:
        recompensa += 1
    if parte2[-1] - parte2[0] > 0:
        recompensa += 1
    if lista_notas[-1] - lista_notas[0] > 0:
        recompensa += 1
        
    return recompensa

def recompensa_tonica(lista_notas: list)->int:
    recompensa = 0
    tonica = nota_escala
    if lista_notas[0] == tonica:
        recompensa += 1 
    if lista_notas[-1] == tonica%12:
        
        recompensa += 1 
    if lista_notas[-1] == (tonica + 12): #FORZAMOS QUE TERMINE UNA OCTAVA POR ENCIMA.
        
        recompensa += 5
    return recompensa


def func_fitness_modal(lista_notas:list):
    modo_esc = escala_modal(nota_escala, modo)
    recompensa = 0
    for i in lista_notas:
        if i in modo_esc:
            recompensa += 1 
            
    if recompensa == len(lista_notas): #PREMIAMOS SÓLO CON PUNTOS ADICIONALES A LOS RESULTADOS QUE TIENEN TODAS LAS NOTAS EN LA ESCALA MAYOR.
       rec = recompensa_por_distancias1(lista_notas)
       recompensa += rec
       #PASO 1: AÑADIMOS NUEVAS RECOMPENSAS. EMPEZAR Y TERMINAR EN LA TÓNICA.
       rec2 = recompensa_tonica(lista_notas)
       recompensa += rec2
       #PASO 2: RECOMPENSAMOS QUE SEA UNA MELODÍA CRECIENTE
       rec3 = recompensa_creciente(lista_notas)
       recompensa += rec3
    return recompensa

#EJEMPLO DE EJECUCIÓN CON LA FUNCIÓN DE FITNESS func_fitness_modal DE LA QUE SE HA OBTENIDO LA FIGURA 7
"""
print(notas_decodificar[nota_escala])
print(modo)
longitud_individuos = 11 


opt = max
individuos = 100
generaciones = 1500
padres = 0.2
mutacion = 0.1
torneo = 15

problema = ProblemaGeneticoMelodia1(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, func_fitness_modal, longitud_individuos)

resul = algoritmo_genetico(problema, torneo, opt, generaciones, individuos, padres, mutacion)
print('resultado: ',  resul[0], '\n', 'valor de aptitud: ', resul[1])
"""


# =============================================================================
# MELODÍA SOBRE ACORDES
# =============================================================================


#SE MODIFICA LA CLASE DE PROBLEMA GENÉTICO  Y SE AUMENTA EL ESPECTRO DE NOTAS PARA PODER TRABAJR CON LOS ACORDES

notas_codificar = {'C0': 0, 'C#0': 1, 'D0': 2, 'D#0': 3, 'E0': 4, 'F0':5, 'F#0': 6, 'G0': 7, 'G#0': 8, 'A0':9, 'A#0': 10, 'B0': 11, 'C1':12, 'C#1': 13, 'D1': 14, 'D#1': 15, 'E1': 16, 'F1':17, 'F#1': 18, 'G1': 19, 'G#1': 20, 'A1':21, 'A#1': 22, 'B1': 23, 'C2':24, 'C#2': 25, 'D2': 26, 'D#2': 27, 'E2': 28, 'F2':29, 'F#2': 30, 'G2': 31, 'G#2': 32, 'A2':33, 'A#2': 34, 'B2': 35}
  
notas_decodificar = {0:'C0', 1:'C#0', 2:'D0', 3:'D#0', 4:'E0', 5:'F0', 6:'F#0', 7:'G0', 8:'G#0', 9:'A0', 10:'A#0', 11:'B0', 12:'C1',  13:'C#1', 14:'D1', 15:'D#1', 16:'E1', 17:'F1', 18:'F#1', 19:'G1', 20:'G#1', 21:'A1', 22:'A#1', 23:'B1' , 24:'C2', 25:'C#2', 26:'D2', 27:'D#2', 28:'E2', 29:'F2', 30:'F#2', 31:'G2', 32:'G#2', 33:'A2', 34:'A#2', 35:'B2'}


#SE VUELVEN A ACTUALIZAR LOS GENES

genes = []
for i in range(0,len(notas_codificar)):
    genes.append(i)
 

class ProblemaGeneticoMelodia(object):
        def __init__(self, genes,fun_dec,fun_muta , fun_cruza, fun_fitness, longitud_individuos, notas_por_acorde, escala, acordes): 
            self.genes = genes
            self.fun_dec = fun_dec
            self.fun_cruza = fun_cruza
            self.fun_muta = fun_muta
            self.fun_fitness = fun_fitness
            self.longitud_individuos = longitud_individuos
            self.notas_por_acorde = notas_por_acorde
            self.escala = escala
            self.acordes = acordes
            
            """Constructor de la clase"""
                
        def decodifica(self, genotipo):
            """Devuelve el fenotipo a partir del genotipo"""
            fenotipo = self.fun_dec(genotipo)
            return fenotipo
        
        def muta(self, cromosoma,prob):
            """Devuelve el cromosoma mutado"""   
            mutante = self.fun_muta(cromosoma,prob)
            return mutante
        
        def cruza(self, cromosoma1, cromosoma2):         
            """Devuelve el cruce de un par de cromosomas"""
            cruce = self.fun_cruza(cromosoma1,cromosoma2)
            return cruce 
        
        def fitness(self, cromosoma):    
            """Función de valoración"""
            
            escala = self.escala
            acordes = self.acordes
            notas_por_acorde = self.notas_por_acorde
            valoracion = self.fun_fitness(cromosoma, escala, acordes, notas_por_acorde)
            
            return valoracion


#PARA ESTA SECCIÓN SE PRESENTAN LAS FUNCIONES QUE HAN SIDO RETOCADAS CON LAS PONDERACIONES DE LAS RECOMPENSAS DE LOS ÚLTIMOS RESULATDOS.


#SE PUEDE JUGAR A MODIFICAR LAS RECOMPENSAS PARA VER CÓMO AFECTA ESTO A LAS SOLUCIONES. 

def recompensa_melodia_acordes(lista_notas:list, acordes, notas_por_acorde)->int: #PREMIAMOS TANTO QUE ESTÉ EN LA ESCALA MAYOR COMO QUE ALGUNAS NOTAS ESTÉN EN LOS ACORDES, EN PARTICULAR QUEREMOS QUE EL PULSO FUERTE CAIGA SOBRE UNA NOTA DEL ACORDE.
    posicion_actual = 0
    rec = 0
    
  
    for i in range( len(acordes)):
        acorde = acordes[i]
        
        num_notas = notas_por_acorde[i]
        
        cont = 0
        for i in range(posicion_actual, posicion_actual + num_notas):
            nota = lista_notas[i]%12
            if nota in acorde:
                cont += 1
            if nota in acorde and i == posicion_actual: #DE ESTE MODO PREMIAMOS A LAS NOTAS DEL ACORDE QUE CAEN EN EL PULSO.
                rec += 5
        posicion_actual += num_notas
        if cont >= 1:   ##HEMOS MODIFICADO EL 2 POR EL 1 PARA VER SI ASÍ CONSEGUIMOS UNA MELODÍA MÁS CONTINUA
            rec +=5
            
    return rec 

def recompensa_escala(lista_notas:list, escala:list):
    recompensa = 0 
    for i in lista_notas:
        if (i%12) in escala:
            recompensa += 1 
    return recompensa

def recompensa_por_distancias(lista_notas: list)-> int: ##Esta función mira la sucesión de las notas y da una evaluación positiva si no distan mucho (tiene más sentido si consideramos más octavas). 
      c = 0 
      fin = len(lista_notas)
      recompensa = 0
      while c < (fin-1):
          distancia = abs(lista_notas[c] - lista_notas[c+1])
          if distancia <= 4:   ##HEMOS CAMBIADO EL 5 POR EL 4 PARA VER SI ACORTANDO LAS DISTANCIAS OBTENEMOS UNA MELODÍA MÁS CONTINUA.
              recompensa += 10 ##AUMENTAMOS ESTAS RECOMPENSAS
              
          elif distancia > 4 and distancia  <= 9:
              recompensa += 4
          
          c += 1 
      return recompensa
    




def fun_fitness_melodia1(lista_notas:list, escala, acordes, notas_por_acorde):
    
    rec1 = recompensa_melodia_acordes(lista_notas, acordes, notas_por_acorde)
    rec2 = recompensa_escala(lista_notas, escala)
    rec3 = recompensa_por_distancias(lista_notas)
    
    aptitud = rec1 + rec2 + rec3
    
    return aptitud


#PRIMER EJEMPLO DE EJECUCIÓN DE MELODÍA SOBRE ACORDES (FIGURA 8)


#PROBAR A EJECUTAR VARIAS VECES PARA COMPARAR RESULTADOS DE APTITUD
"""
longitud_individuos = 16
notas_por_acorde = [4,4,4,4]
escala = escala_modal(0, 'jonico') #EL MODO JONICO COINCIDE CON LA ESCALA MAYOR
acordes = [[0,4,7], [0, 5, 9], [2, 5, 7, 11], [4, 7, 12]]
    
torneo = 10
opt = max
individuos_por_gen = 50
generaciones = 1000
padres = 0.7
   
mutacion = 0.1
    

problema = ProblemaGeneticoMelodia(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, fun_fitness_melodia1, longitud_individuos, notas_por_acorde, escala, acordes)
resul, valor, _ = algoritmo_genetico(problema, torneo, opt, generaciones, individuos_por_gen, padres, mutacion)
     
print(resul, valor)

"""


def distancia_minima(acorde, nota): #En este primer caso, no vamos a tener en cuenta que las disonancias se atenúan cuanto más amplio es el intervalo.
    l = []
    nota = nota%12
    
    for i in range(len(acorde)):
        nota_ac = acorde[i]%12
        dist = min(abs(nota_ac - nota), abs(nota_ac - (nota+12)), abs(nota_ac+12 - nota))
        
        l.append(dist)
    dist_min = min(l)
    return dist_min


def penalizacion_dist_min(lista_notas, acordes, notas_por_acorde):
    
    posicion_actual = 0
    penalizacion = 0
  
    for i in range( len(acordes)):
        acorde = acordes[i]
        
        num_notas = notas_por_acorde[i]
        
        
        for i in range(posicion_actual, posicion_actual + num_notas):
            nota = lista_notas[i]
            if nota%12 not in acorde and distancia_minima(acorde, nota) == 1 :
                
                
                penalizacion -= 20  #PENALIZAMOS BASTANTE PORQUE ES UN SONIDO BASTANTE DESAGRADABLE 
        posicion_actual += num_notas
        
            
    return penalizacion


def fun_fitness_melodia2(lista_notas:list, escala, acordes, notas_por_acorde):
    
    rec1 = recompensa_melodia_acordes(lista_notas, acordes, notas_por_acorde)
    rec2 = recompensa_escala(lista_notas, escala)
    rec3 = recompensa_por_distancias(lista_notas)
    pen = penalizacion_dist_min(lista_notas, acordes, notas_por_acorde)
    
    aptitud = rec1 + rec2 + rec3 + pen
    
    return aptitud


#SEGUNDO EJEMPLO DE EJECUCIÓN DE MELODÍA SOBRE ACORDES (FIGURA 9)


#PROBAR A EJECUTAR VARIAS VECES PARA COMPARAR RESULTADOS DE APTITUD
"""
longitud_individuos = 16
notas_por_acorde = [4,4,4,4]
escala = escala_modal(0, 'jonico') #EL MODO JONICO COINCIDE CON LA ESCALA MAYOR
acordes = [[0,4,7], [0, 5, 9], [2, 5, 7, 11], [4, 7, 12]]
    
torneo = 10
opt = max
individuos_por_gen = 50
generaciones = 1000
padres = 0.7
   
mutacion = 0.1
    

problema = ProblemaGeneticoMelodia(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, fun_fitness_melodia2, longitud_individuos, notas_por_acorde, escala, acordes)
resul, valor, _ = algoritmo_genetico(problema, torneo, opt, generaciones, individuos_por_gen, padres, mutacion)
     
print(resul, valor)
"""


def penalizacion_solapamiento(lista_notas, acordes, notas_por_acorde): #PENALIZAMOS ESAS SITUACIONES EN LAS QUE SE SOLAPAN NOTAS DEL ACORDE CON NOTAS DE LA MELODÍA (CONSTITUYE TAMBIÉN UN INTENTO DE QUE LA MELODÍA SE AMOLDE A LA FORMA DE LOS ACORDES).
    posicion_actual = 0
    penalizacion = 0
  
    for i in range( len(acordes)):
        acorde = acordes[i]
        
        num_notas = notas_por_acorde[i]
        
        
        for i in range(posicion_actual, posicion_actual + num_notas):
            nota = lista_notas[i]
            if nota in acorde:
                
                penalizacion -= 20
            for i in acorde:
                
                if abs(i-nota) == 2:
                    penalizacion -= 15
                
        posicion_actual += num_notas
        
            
    return penalizacion    




def fun_fitness_melodia3(lista_notas:list, escala, acordes, notas_por_acorde):   #ES TODO EL TRABAJO HECHO EL DÍA 09/06
      
      rec1 = recompensa_melodia_acordes(lista_notas, acordes, notas_por_acorde)
      
      rec2 = recompensa_por_distancias(lista_notas)
      pen = penalizacion_dist_min(lista_notas, acordes, notas_por_acorde) #LA PENALIZACIÓN SE HA HECHO MÁS ACUSADA.
      pen2 = penalizacion_solapamiento(lista_notas, acordes, notas_por_acorde)
      
      aptitud = rec1 + rec2 + pen + pen2
      
      return aptitud 

# EJEMPLO DE EJECUCIÓN DE MELODÍA SOBRE ACORDES (FIGURA 10)

"""
#PROBAR A EJECUTAR VARIAS VECES PARA COMPARAR RESULTADOS DE APTITUD

longitud_individuos = 16
notas_por_acorde = [4,4,4,4]
escala = escala_modal(0, 'jonico') #EL MODO JONICO COINCIDE CON LA ESCALA MAYOR
acordes = [[0,4,7], [0, 5, 9], [2, 5, 7, 11], [4, 7, 12]]
    
torneo = 10
opt = max
individuos_por_gen = 50
generaciones = 1000
padres = 0.7
   
mutacion = 0.1
    

problema = ProblemaGeneticoMelodia(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, fun_fitness_melodia3, longitud_individuos, notas_por_acorde, escala, acordes)
resul, valor, _ = algoritmo_genetico(problema, torneo, opt, generaciones, individuos_por_gen, padres, mutacion)
     
print(resul, valor)
"""


#SE MODIFICA LA FUNCIÓN DE RECOMPENSA DE ESCALA


#CREAMOS UN DICCIONARIO CON TODOS LOS ACORDES MAYORES.

escalas_mayores = {}
for i in range(12):
    escalas_mayores[i] = escala_modal(i, 'jonico')

##  LA NUEVA RECOMPENSA A LA MELODÍA CONSISTIRÁ EN QUE SE LE ESTÁ PERMITIDO MOVERSE POR LA ESCALA MAYOR DEL ACORDE, SI ES MAYOR

def es_acorde_mayor(acorde):
    
    if len(acorde) == 3:    #NO CONSIDERAMOS OTROS CASOS POR EL MOMENTO
    #REORDENAMOS PRIMERO EL ACORDE
        acorde_reordenado =sorted([i%12 for i in acorde])
    #REORDENÁNDOLO DE ESTA FORMA EL ACORDE PUEDE APARECER TAMBIÉN EN PRIMERA O SEGUNDA INVERSIÓN
        dist1 = acorde_reordenado[1] - acorde_reordenado[0]
        dist2 = acorde_reordenado[2] - acorde_reordenado[1]
    
        if (dist1 == 4 and dist2 == 3) or (dist1 == 3 and dist2 == 5) or (dist1 == 5 and dist2 == 4):
            return True
        else:
            return False
        
##NECESITAMOS TAMBIÉN UNA FORMA DE ENCONTRAR LA TÓNICA DEL ACORDE MAYOR
def encontrar_tonica(acorde):
    acorde_reordenado =sorted([i%12 for i in acorde])
    
    dist1 = acorde_reordenado[1] - acorde_reordenado[0]
    dist2 = acorde_reordenado[2] - acorde_reordenado[1]
    
    if (dist1 == 4 and dist2 == 3):
        return acorde_reordenado[0]
    
    elif(dist1 == 3 and dist2 == 5):
        return acorde_reordenado[2]
    
    elif (dist1 == 5 and dist2 == 4):
        return acorde_reordenado[1]

def recompensa_escalaV2(lista_notas:list, acordes, notas_por_acorde, escala):
    
    
    posicion_actual = 0
    rec = 0
    
  
    for i in range( len(acordes)):
        acorde = acordes[i]
        
        num_notas = notas_por_acorde[i]
        
        if es_acorde_mayor(acorde):
            
            tonica = encontrar_tonica(acorde)
            if tonica == escala[4]: #ES DECIR ES EL QUINTO GRADO (LE PEDIMOS QUE TOQUE LA ESCALA MAYOR DE I)
                for i in range(posicion_actual, posicion_actual + num_notas):
                    nota = lista_notas[i]%12
                    if nota in escala:
                        rec += 10
                posicion_actual += num_notas
            else:
                for i in range(posicion_actual, posicion_actual + num_notas):
                    nota = lista_notas[i]%12
                    if nota in escalas_mayores[tonica]:
                    
                        rec += 10
                posicion_actual += num_notas
        
        else:
            for i in range(posicion_actual, posicion_actual + num_notas):
                nota = lista_notas[i]%12
                if nota in escala:
                    
                    rec += 10  ##AUMENTAMOS LAS RECOMPENSAS A 5 PARA QUE TENGA MÁS CLARO EL OBJETIVO PRINCIPAL.
                else:
                    rec -= 50  ##EN EL CASO DE QUE NO SEA UNA NOTA DE LA ESCALA VAMOS A PENALIZAR 
            posicion_actual += num_notas
            
            
    return rec 

#IMPLEMENTAMOS AHORA UNA RECOMPENSA A QUE SE SUCEDAN CIERTAS REPETICIONES EN LA MELODÍA. EL ESTRIBILLO ES UNA COSA ESENCIAL.

def recompensa_repeticion(lista_notas, escala, acordes, notas_por_acorde):
    
    

    rec = 0
    estribillo = lista_notas[0: (notas_por_acorde[0]+ notas_por_acorde[1])]
    #REESCRIBIMOS LOS ACORDES SIMPLIFICADOS PARA BUSCARLOS EN EL RESTO DE LA LISTA DE ACORDES.
    ac0 = set(sorted([nota%12 for nota in acordes[0]]))
    ac1 = set(sorted([nota%12 for nota in acordes[1]]))
    for i in range(2, len(acordes)-1):
        if set(sorted([nota%12 for nota in acordes[i]])) == ac0 and set(sorted([nota%12 for nota in acordes[i+1]])) == ac1:
            #NOS CALCULAMOS LA POSICIÓN DE LA QUE TENEMOS QUE PARTIR DE LISTA_NOTAS
            pos = sum(notas_por_acorde[:i])
            final =pos + notas_por_acorde[i] + notas_por_acorde[i+1]
            segundo_estribillo = lista_notas[pos:final]
            for i in range(len(estribillo)):
                if estribillo[i] == segundo_estribillo[i]:  
                    rec += 1 
    return rec





def fun_fitness_melodia4(lista_notas:list, escala, acordes, notas_por_acorde):   
      
      rec1 = recompensa_melodia_acordes(lista_notas, acordes, notas_por_acorde)
      rec2 = recompensa_escalaV2(lista_notas,acordes, notas_por_acorde, escala)
      rec3 = recompensa_por_distancias(lista_notas)
      rec4 = recompensa_repeticion(lista_notas, escala, acordes, notas_por_acorde)
      pen = penalizacion_dist_min(lista_notas, acordes, notas_por_acorde) #LA PENALIZACIÓN SE HA HECHO MÁS ACUSADA.
      pen2 = penalizacion_solapamiento(lista_notas, acordes, notas_por_acorde)
      
      aptitud = rec1 + rec2 + rec3 + rec4 + pen + pen2
      
      return aptitud


# EJEMPLO DE EJECUCIÓN DE MELODÍA SOBRE ACORDES (FIGURA 11)

"""
#PROBAR A EJECUTAR VARIAS VECES PARA COMPARAR RESULTADOS DE APTITUD



escala = escala_modal(0, 'jonico') #EL MODO JONICO COINCIDE CON LA ESCALA MAYOR
acordes_pop = [[0,4,7],[2,7,11], [0,4,7], [2,7,11], [4,7,12], [5,9,12], [2,7,11], [4,7,12]]
notas_por_acorde_pop = [4,4,4,4,4,4,4,4]
longitud_individuos_pop = 32
torneo = 10
opt = max
individuos_por_gen = 100
generaciones = 500
padres = 0.7

mutacion = 0.1
    

problema = ProblemaGeneticoMelodia(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, fun_fitness_melodia4, longitud_individuos_pop, notas_por_acorde_pop, escala, acordes_pop)
resul, valor, _ = algoritmo_genetico(problema, torneo, opt, generaciones, individuos_por_gen, padres, mutacion)
     
print(resul, valor)
"""

# =============================================================================
# MELODÍA EN UNA PIEZA
# =============================================================================

"""
#PRIMER EJEMPLO DE EJECUCIÓN


longitud_individuos = 42
acordes = [[9, 12, 16], [9, 14, 16],[9, 12, 16], [9, 14, 16], [9, 12, 16], [9, 11, 14], [9, 12, 16], [9, 12, 16], [14, 17, 21], [12, 16, 21], [14, 17, 21] , [12, 16, 21], [14, 17, 21] , [12, 16, 21], [8, 14,16], [4], [11, 14, 16], [9,12], [4, 12], [4, 8, 14], [9,12],] #ESTÁN BIEN LOS ACORDES (REVISADOS)
notas_por_acorde = [2 for i in range(21)]          #EMPEZAMOS PONIENDO SÓLO CORCHEAS.
escala = [9, 11, 0, 2, 4, 5, 7]        #ES LA MENOR

torneo_mel = 15
opt = max
individuos_por_gen_mel = 150
generaciones_mel = 200
padres_mel = 0.8
num_busquedas_mel = 30
mutacion_mel = 0.1


problema = ProblemaGeneticoMelodia(genes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, fun_fitness_melodia4, longitud_individuos, notas_por_acorde, escala, acordes)
resul, valor, _ = algoritmo_genetico(problema, torneo_mel, opt, generaciones_mel, individuos_por_gen_mel, padres_mel, mutacion_mel)
     
print(resul, valor)

"""


# =============================================================================
# PARALELIZACIÓN DEL ALGORITMO
# =============================================================================


def buscador(q_resul, problema, torneo, opt, individuos_por_gen, generaciones, padres, mutacion, num_busquedas):
    
    
    while num_busquedas.value > 0:
        
        num_busquedas.value -= 1
        
        
        resul, valor, resul_cod= algoritmo_genetico(problema, torneo, opt, generaciones, individuos_por_gen, padres, mutacion)
        
        q_resul.put((resul,valor,resul_cod))
        print('valor: ',valor , 'resultado: ', resul)
      
        if num_busquedas.value == 0:
            q_resul.put(None)
        
        
        
def main_mel( num_busquedas_mel, genes, fun_dec_mel, fun_mutar, fun_cruzar_mel, fun_fitness_mel, longitud_individuos, notas_por_acorde, acordes, escala, torneo_mel, opt,  individuos_por_gen_mel,  generaciones_mel,  prob_padres_mel,  prob_mutacion_mel):
    
  
    q_resul = Queue()

    
    num_busquedas = Value('i', num_busquedas_mel)
    
            
            

    problema_mel = ProblemaGeneticoMelodia(genes, fun_dec_mel, fun_mutar, fun_cruzar_mel, fun_fitness_mel, longitud_individuos, notas_por_acorde, escala, acordes)
    
    buscadores_mel = [Process(target=buscador, args = (q_resul, problema_mel, torneo_mel, opt, individuos_por_gen_mel, generaciones_mel, prob_padres_mel, prob_mutacion_mel, num_busquedas)) for _ in range(12)]

    for bus in buscadores_mel:
        bus.start()
    
    l_mel = []
    
    melodia = q_resul.get()
    
    while melodia != None:
        
        
        
        l_mel.append(melodia)
        
        melodia = q_resul.get()
        
    for bus in buscadores_mel:
        bus.join()
        
    mejor_melodia = max(l_mel, key = lambda x: x[1])
    media_res = np.mean([x[1] for x in l_mel])
    
    print('media de los resultados: ', media_res)
    
    print(mejor_melodia[0], mejor_melodia[1])
    while not q_resul.empty(): #VOLVEMOS A VACIAR LA COLA
        q_resul.get()
    
    
# =============================================================================
# MEJORA DE LAS FUNCIONES DE APTITUD
# =============================================================================


##VAMOS A PENALIZAR SALTOS MUY GRANDES ENTRE NOTAS:
def penalizacion_saltos_grandes(lista_notas):
    pen = 0
    for i in range(len(lista_notas)- 1):
        if abs(lista_notas[i] - lista_notas[i+1]) > 9:
            pen -= 10
            
    return pen

#PENALIZAMOS QUE LA MELODÍA SE VAYA HACIA ABAJO
def penalizacion_melodia_grave(lista_notas):
    pen = 0
    for i in lista_notas:
        if i < 12:
            pen -= 20
    return pen

#ESTÁ ENFOCADA EN LA PIEZA QUE HEMOS USADO (TRAUER).
def encontrar_V_I(escala, acordes):
    lista_v_i = [False for i in range(len(acordes))]
    tercera_v = (escala[4] + 4)%12   
    septima_v = (escala[4] + 10)%12
   
    tonica_i = escala[0]
    tercera_i = escala[2]
    
    to_y_s = set([escala[4], septima_v])
    
    to_y_te = set([tonica_i, tercera_i])
    
    #EMPEZAMOS BUSCANDO EL QUINTO GRADO QUE LO VAMOS A ENCONTRAR BUSCANDO LA TERCERA Y LA SÉPTIMA:
    for i in range(len(acordes)- 1):
        acorde = set([nota %12 for nota in acordes[i]])
        #VAMOS A BUSCAR TANTO EL QUINTO GRADO MAYOR COMO MENOR
        if  (to_y_s.issubset( acorde)) or set([escala[4], tercera_v]).issubset(acorde) or set([escala[4], escala[4] + 3]).issubset(acorde): #SIGNIFICA QUE HEMOS ENCONTRADO UN QUINTO GRADO Y QUEREMOS VER SI RESUELVE AL I
            
            acorde_sig = set([nota %12 for nota in acordes[i+1]])
            lista_v_i[i] = 'V'
            if to_y_te.issubset(acorde_sig):
                
                lista_v_i[i+1] = 'I'
    
    return lista_v_i



def recompensa_respiracion(lista_notas, escala, acordes, notas_por_acorde):
    rec = 0
    grados = encontrar_V_I(escala, acordes)
    for i in range(len(grados)):
        if grados[i] == 'V':
            
            #PEDIMOS QUE LAS NOTAS DEL SIGUIENTE ACORDE SE REPITAN (RESPIRACIÓN)
            inic = sum(notas_por_acorde[:i+1])
            fin = inic + notas_por_acorde[i+1]
            acorde_sig = lista_notas[inic:fin]
            
            for i in range(len(acorde_sig)-1):
                if acorde_sig[i] == acorde_sig[i+1]:
                    rec += 5
                    
                    if i%2 == 0:#ES DECIR SI NOS ENCONTRAMOS EN UNA POSICIÓN PAR.
                        rec += 2     #ES DECIR, SI LA CANTIDAD DE NOTAS REPETIDAS ES PAR.
    return rec   





def fun_fitness_melodia5(lista_notas:list, escala, acordes, notas_por_acorde):   
      
      rec1 = recompensa_melodia_acordes(lista_notas, acordes, notas_por_acorde)
      rec2 = recompensa_escalaV2(lista_notas,acordes, notas_por_acorde, escala)
      rec3 = recompensa_por_distancias(lista_notas)
      rec4 = recompensa_repeticion(lista_notas, escala, acordes, notas_por_acorde)
      pen = penalizacion_dist_min(lista_notas, acordes, notas_por_acorde) #LA PENALIZACIÓN SE HA HECHO MÁS ACUSADA.
      pen2 = penalizacion_solapamiento(lista_notas, acordes, notas_por_acorde)
      
      
      pen3 = penalizacion_saltos_grandes(lista_notas)
      pen4 = penalizacion_melodia_grave(lista_notas)
      
      
      rec5 = recompensa_respiracion(lista_notas, escala, acordes, notas_por_acorde)
      
      aptitud = rec1 + rec2 + rec3 + pen + pen2 + rec4 + pen3 + pen4 + rec5
      
      return aptitud                   


#EJEMPLO DE EJECUCIÓN CON NUEVAS IMPLEMENTACIONES Y PARALELIZANDO  (FIGURA 14)

#SE HA DECIDIDO NO MODIFICAR LOS VALORES DE LAS FUNCIONES DE RECOMPENSA Y PENALIZACIÓN (QUE IMPLICARÍA EMPEORARLOS) PARA INTENTAR MANTENER EL CÓDIGO LO MÁS SIMPLE POSIBLE. ES POR ESO QUE NO SE HA RECREADO LA FIGURA 13.

#A PARTIR DE AQUÍ LOS TIEMPOS DE EJECUCIÓN SON MÁS LARGOS, PUES SE ESTÁ HACIENDO UNA BÚSQUEDDA MÁS EXHAUSTIVA.
"""
if __name__ == '__main__':
    
    longitud_individuos = 24
    acordes = [[9, 12, 16], [9, 14, 16],[9, 12, 16], [9, 14, 16], [9, 12, 16], [9, 11, 14], [9, 12, 16], [9, 12, 16], [14, 17, 21], [12, 16, 21], [14, 17, 21] , [12, 16, 21]] #ESTÁN BIEN LOS ACORDES (REVISADOS)
    notas_por_acorde = [2 for i in range(12)]          #EMPEZAMOS PONIENDO SÓLO CORCHEAS.
    escala = [9, 11, 0, 2, 4, 5, 7]        #ES LA MENOR
     
    torneo_mel = 10
    opt = max
    individuos_por_gen_mel = 100
    generaciones_mel = 200
    padres_mel = 0.7
    num_busquedas_mel = 60
    mutacion_mel = 0.1

     
    main_mel(num_busquedas_mel, genes,  fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, 
            fun_fitness_melodia5, longitud_individuos, notas_por_acorde, acordes, escala, torneo_mel,  
          opt, individuos_por_gen_mel,  generaciones_mel,  padres_mel, mutacion_mel)
    
"""

#MELODÍA COMPLETA

def recompensa_final(lista_notas, escala):
    rec = 0
    if lista_notas[-1] == lista_notas[-2] and lista_notas[-1] in escala:
        rec += 10
    return rec


def fun_fitness_melodia6(lista_notas:list, escala, acordes, notas_por_acorde):   
      
      rec1 = recompensa_melodia_acordes(lista_notas, acordes, notas_por_acorde)
      rec2 = recompensa_escala(lista_notas, escala)
      rec3 = recompensa_por_distancias(lista_notas)
      rec4 = recompensa_repeticion(lista_notas, escala, acordes, notas_por_acorde)
      pen = penalizacion_dist_min(lista_notas, acordes, notas_por_acorde) #LA PENALIZACIÓN SE HA HECHO MÁS ACUSADA.
      pen2 = penalizacion_solapamiento(lista_notas, acordes, notas_por_acorde)
      
      
      pen3 = penalizacion_saltos_grandes(lista_notas)
      pen4 = penalizacion_melodia_grave(lista_notas)
      
      
      rec5 = recompensa_respiracion(lista_notas, escala, acordes, notas_por_acorde)
      
      rec6 = recompensa_final(lista_notas, escala)
      aptitud = rec1 + rec2 + rec3 + pen + pen2 + rec4 + pen3 + pen4 + rec5 + rec6
      
      return aptitud                         
        
"""
if __name__ == '__main__':   
     
     longitud_individuos = 42
     acordes = [[9, 12, 16], [9, 14, 16],[9, 12, 16], [9, 14, 16], [9, 12, 16], [9, 11, 14], [9, 12, 16], [9, 12, 16], [14, 17, 21], [12, 16, 21], [14, 17, 21] , [12, 16, 21], [14, 17, 21] , [12, 16, 21], [8, 14,16], [4], [11, 14, 16], [9,12], [4, 12], [4, 8, 14], [9,12],] #ESTÁN BIEN LOS ACORDES (REVISADOS)
     notas_por_acorde = [2 for i in range(21)]          #EMPEZAMOS PONIENDO SÓLO CORCHEAS.
     escala = [9, 11, 0, 2, 4, 5, 7]        #ES LA MENOR
     
     torneo_mel = 15
     opt = max
     individuos_por_gen_mel = 150
     generaciones_mel = 200
     prob_padres_mel = 0.8
     num_busquedas_mel = 30
     prob_mutacion_mel = 0.1
     
     
     main_mel(num_busquedas_mel, genes,  fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, 
            fun_fitness_melodia6, longitud_individuos, notas_por_acorde, acordes, escala, torneo_mel,  
          opt, individuos_por_gen_mel,  generaciones_mel,  prob_padres_mel, prob_mutacion_mel)
     
"""

# =============================================================================
# TRABAJO CON ACORDES     
# =============================================================================

class ProblemaGeneticoAcordes(object):
        def __init__(self, genes,fun_dec,fun_muta , fun_cruza, fun_fitness, longitud_individuos, longitud_acorde, grados_de_la_tonalidad): 
            self.genes = genes
            self.fun_dec = fun_dec
            self.fun_cruza = fun_cruza
            self.fun_muta = fun_muta
            self.fun_fitness = fun_fitness
            self.longitud_individuos = longitud_individuos
            self.grados_de_la_tonalidad = grados_de_la_tonalidad
            self.longitud_acorde = longitud_acorde
            
            """Constructor de la clase"""
                
        def decodifica(self, genotipo):
            """Devuelve el fenotipo a partir del genotipo"""
            fenotipo = self.fun_dec(genotipo , self.longitud_acorde)
            return fenotipo
        
        def muta(self, cromosoma,prob):
            """Devuelve el cromosoma mutado"""   
            mutante = self.fun_muta(cromosoma,prob)
            return mutante
        
        def cruza(self, cromosoma1, cromosoma2):         
            """Devuelve el cruce de un par de cromosomas"""
            cruce = self.fun_cruza(cromosoma1,cromosoma2)
            return cruce 
        
        def fitness(self, cromosoma):    
            """Función de valoración"""
            grados = self.grados_de_la_tonalidad
            
            valoracion = self.fun_fitness(cromosoma, grados)
            return valoracion

#TODO EL TRABAJO AQUÍ PRESENTE SE VA A HACER SÓLO PARA TRIADAS.
def fun_dec_acordes(genotipo, long_ac):
     
     resul = []
     pos = 0
     acorde = []
     for cantidad in long_ac:
         for i in range(cantidad):  
             acorde.append(genotipo[pos+i])
         pos += cantidad
         acorde = sorted(acorde)
         for i in range(len(acorde)):
             acorde[i] = notas_decodificar[acorde[i]]
         resul.append(acorde)
         acorde = []   
             
     return resul
 
    
#NUEVA FUNCIÓN DE DISTANCIA RELATIVA ÚTIL PARA TRABAJAR CON ACORDES.


def distancia_relativa(nota1:int, nota2:int)->int:
    distancia = (nota2-nota1)
    if distancia > 0:
        distancia %= 12
    return distancia


def recompensa_acordeMm(lista_notas:list): #PARA TRIADAS
    recompensa = 0
    i = 0
    while i < len(lista_notas)-2:
        
        if distancia_relativa(lista_notas[i], lista_notas[i+2]) == 7 or distancia_relativa(lista_notas[i+1], lista_notas[i+2]) == 8 or distancia_relativa(lista_notas[i+1], lista_notas[i+2]) in [3,4]:
            recompensa += 1 
            
        if distancia_relativa(lista_notas[i], lista_notas[i+1]) in [3,4] or distancia_relativa(lista_notas[i], lista_notas[i+1]) == 5:
            recompensa+= 1
          
        if distancia_relativa(lista_notas[i], lista_notas[i+1]) in [3,4] and distancia_relativa(lista_notas[i], lista_notas[i+2]) == 7: 
            recompensa+=2
            
        elif distancia_relativa(lista_notas[i], lista_notas[i+1]) in [3,4] and distancia_relativa(lista_notas[i+1], lista_notas[i+2]) == 8: #PRIMERA INVERSIÓN
            recompensa += 2
            
        elif distancia_relativa(lista_notas[i], lista_notas[i+1]) == 5 and distancia_relativa(lista_notas[i+1], lista_notas[i+2]) in [3,4]: #SEGUNDA INVERSIÓN 
            recompensa += 2
        
        i += 3
        
    return recompensa
    

#IMPLEMENTAMOS LA PRIMERA DIRECCIÓN PROPUESTA POR SCHOENBERG (PÁG 39)

def recompensa_desplazamientos_cercanos(lista_notas:list):
    recompensa = 0
    i = 0
    while i < len(lista_notas) - 5:
        
        dist1 = abs(lista_notas[i] - lista_notas[i+3])
        dist2 = abs(lista_notas[i+1] - lista_notas[i+4])
        dist3 = abs(lista_notas[i+2] - lista_notas[i+5])
        suma_dist = dist1+dist2+dist3
        
        if suma_dist <= 6:
            recompensa += 1 
        i += 3
            
    return recompensa

        
            
def func_fitness_acordes1(lista_acordes:list, grados):
    
    rec1 = recompensa_acordeMm(lista_acordes)
    rec2 = recompensa_desplazamientos_cercanos(lista_acordes)
    
    
    aptitud = rec1 + rec2 
   
    
    return aptitud    

#PROBAR VARIAS VECES PARA VER LOS DISTINTOS VALORES DE APTITUD OBTENIDOS
#FIGURA 16
"""
longitud_individuos = 12
longitud_acorde = [3,3,3,3]
grados = []
problema = ProblemaGeneticoAcordes(genes, fun_dec_acordes, fun_mutar_int, fun_cruzar_dpc, func_fitness_acordes1, longitud_individuos, longitud_acorde, grados)
res, valor, _ = algoritmo_genetico(problema, 10, max, 50, 1000, 0.2, 0.2)
   
print('resultado: ', res, 'valor de aptitud: ', valor)
"""



def recompensa_notas_en_comun(lista_notas:list): #PREMIAMOS SI COMPARTEN UNA O DOS NOTAS, PENALIZAMOS, EN PRINCIPIO, SI EL ACORDE SE REPITE
    recompensa = 0 
    fin = len(lista_notas) // 3 
    for i in range(fin - 1):
        acorde1 = set(lista_notas[i*3: i*3 + 3])
        acorde2 = set(lista_notas[(i+1)*3: (i+1)*3 + 3])
        
        inter = acorde1.intersection(acorde2)
        if len(inter) == 1 or len(inter) == 2:
            recompensa += 1 
        
            
    return recompensa
        
  
def func_fitness_acordes2(lista_acordes:list, grados):
    
    rec1 = recompensa_acordeMm(lista_acordes)
    rec2 = recompensa_desplazamientos_cercanos(lista_acordes)
    rec3 = recompensa_notas_en_comun(lista_acordes)
    
    aptitud = rec1 + rec2 + rec3
   
    
    return aptitud

#FIGURAS 17 y 18
"""
longitud_individuos = 12
longitud_acorde = [3,3,3,3]
grados = []
problema = ProblemaGeneticoAcordes(genes, fun_dec_acordes, fun_mutar_int, fun_cruzar_dpc, func_fitness_acordes2, longitud_individuos, longitud_acorde, grados)
res, valor, _ = algoritmo_genetico(problema, 10, max, 50, 1000, 0.2, 0.2)
   
print('resultado: ', res, 'valor de aptitud: ', valor)

"""

# =============================================================================
# BUSCAMOS AHORA UNA FUNCIÓN FITNESS QUE IMPLEMENTE EL ESQUEMA DE ACORDES DE SCHOEMBERG
# =============================================================================
def calcular_grados(tonica:int):
    t = tonica % 12 
    i = {t,(t+4)%12, (t+7)%12}
    ii = {(t+2)%12, (t+5)%12, (t+9)%12}
    iii = {(t+4)%12, (t+7)%12, (t+11)%12}
    iv = {(t+5)%12, (t+9)%12, t}
    v = {(t+7)%12, (t+11)%12, (t+2)%12}
    vi = {(t+9)%12,  t , (t+4)%12}
    vii = {(t+11)%12, (t+2)%12, (t+5)%12}
    
    return [i,ii,iii,iv,v,vi,vii]


def recompensa_grados(lista_notas:list, grados):
    recompensa = 0
    for i in range(len(lista_notas)//3):
        acorde = lista_notas[i*3:i*3+3]
        for i in range(len(acorde)):
            acorde[i] %= 12 
        acorde = set(acorde)
        if acorde in grados:
            recompensa += 3
            
    return recompensa
        
def recompensa_acorde_compacto(lista_notas:list ):
    recompensa = 0 
    for i in range(len(lista_notas)//3):
        acorde = lista_notas[i*3:i*3+3] 
        
        acorde = sorted(acorde)
        
        
        condicion = abs(acorde[0] -acorde[1]) + abs(acorde[1] - acorde[2])
        if condicion <= 12:
            recompensa += 1 
        if condicion <= 9:
            recompensa += 1
    return recompensa

def recompensa_terminar_empezar(lista_notas:list, grados):
    recompensa = 0
    primer_acorde = set(lista_notas[:3])
    l1 = len(primer_acorde & grados[0])
    l2 = len(primer_acorde & grados[4])
    
    
    
    if primer_acorde in [grados[0], grados[4]]:
        recompensa += 3
    elif 2 in [l1,l2]:
        recompensa += 2 
    elif 1 in [l1,l2]:
        recompensa += 1
    ultimo_acorde = set(lista_notas[-3:])
    
    lf1= len(ultimo_acorde & grados[0])
    lf2 = len(primer_acorde & grados[4])
    
    if ultimo_acorde == grados[0]  or ultimo_acorde == grados[4]: #termina en la tónica o en cadecia rota.
        recompensa += 3
    elif 2 in [lf1,lf2]:
        recompensa += 2 
    elif 1 in [lf1,lf2]:
        recompensa += 1
        
    return recompensa


def func_fitness_acordes3(lista_notas:list, grados): 
    
    rec1 = recompensa_grados(lista_notas, grados)
    
    rec2 = recompensa_terminar_empezar(lista_notas, grados)
    
    rec3 = recompensa_acorde_compacto(lista_notas)
       
       
    rec4 = recompensa_notas_en_comun(lista_notas)
           
    rec5 = recompensa_desplazamientos_cercanos(lista_notas)
    
    aptitud =  + rec3  + rec1 + rec2 + rec4 + rec5
        
        
            
           
    
    
    return aptitud
        
#VEMOS AHORA UN EJEMPLO CON ESTA FUNCIÓN DE FITNESS (FIGURA 19)
"""
if __name__ == "__main__":

    longitud_individuos = 24
    longitud_acorde = [3]*8
    torneo_ac = 10
    opt = max
    individuos_por_gen_ac = 100
    generaciones_ac = 1000
    padres_ac = 0.9
    mutacion_ac = 0.1



    tonica = random.randint(0,11)
    grados = calcular_grados(tonica)
    print('tonica = ', notas_decodificar[tonica])

    problema_ac = ProblemaGeneticoAcordes(genes, fun_dec_acordes, fun_mutar_int, fun_cruzar_dpc, func_fitness_acordes3, 24, longitud_acorde, grados)
    q_resul = Queue()

    num_busquedas = Value('i',60)    
    buscadores_ac = [Process(target=buscador, args = (q_resul, problema_ac, torneo_ac, opt, individuos_por_gen_ac, generaciones_ac, padres_ac, mutacion_ac, num_busquedas)) for _ in range(12)]
    for bus in buscadores_ac:
        bus.start()

    l_ac = []
    acordes = q_resul.get()
    while acordes != None:
    
    
    
        l_ac.append(acordes)
    
        acordes = q_resul.get()
    
    for bus in buscadores_ac:
        bus.join()
    
    
    mejores_acordes = max(l_ac, key = lambda x: x[1])
    print(mejores_acordes[0], mejores_acordes[1])

"""



def recompensa_empezar_y_451(lista_notas:list, grados):
    recompensa = 0
    primer_acorde = lista_notas[:3]
    if set(primer_acorde) == grados[0]:
        recompensa += 5    #HEMOS MODIFICADO LAS RECOMPENSAS DE 1 A 5.
    ultimo_acorde = lista_notas[-3:]
    penul_acorde = lista_notas[-6:-3]
    antep_acorde = lista_notas[-9:-6]
    
    if set(ultimo_acorde) == grados[0] and set(penul_acorde) == grados[4] and set(antep_acorde) == grados[3]:
        recompensa += 15
    
    elif set(ultimo_acorde) == grados[0] and set(penul_acorde) == grados[4]:
        recompensa += 10
    
    elif set(ultimo_acorde) == grados[0]:
        recompensa += 5
    
    return recompensa


def recompensa_registro_grave(lista_notas):
    rec = 0
    for i in lista_notas:
        if i < 20:
            rec += 1
    return rec

def func_fitness_acordes4(lista_notas:list, grados): 
    aptitud = 0
    rec1 = recompensa_grados(lista_notas, grados)
    
    rec2 = recompensa_empezar_y_451(lista_notas, grados)
    
    rec3 = recompensa_acorde_compacto(lista_notas)
       
       
    rec4 = recompensa_notas_en_comun(lista_notas)
    
    rec5 = recompensa_registro_grave(lista_notas)
           
    aptitud +=  + rec3  + rec1 + rec2 + rec4 + rec5
    
    return aptitud


#GENERACIÓN DE ACORDES CON LOS PARÁMETROS YA MEJORADOS (FIGURA 21)

"""
if __name__ == "__main__":

    longitud_individuos = 24
    longitud_acorde = [3]*8
    torneo_ac = 10
    opt = max
    individuos_por_gen_ac = 100
    generaciones_ac = 800
    padres_ac = 0.9
    mutacion_ac = 0.1



    tonica = random.randint(0,11)
    grados = calcular_grados(tonica)
    print('tonica = ', notas_decodificar[tonica])

    problema_ac = ProblemaGeneticoAcordes(genes, fun_dec_acordes, fun_mutar_int, fun_cruzar_dpc, func_fitness_acordes4, 24, longitud_acorde, grados)
    q_resul = Queue()

    num_busquedas = Value('i',60)    
    buscadores_ac = [Process(target=buscador, args = (q_resul, problema_ac, torneo_ac, opt, individuos_por_gen_ac, generaciones_ac, padres_ac, mutacion_ac, num_busquedas)) for _ in range(12)]
    for bus in buscadores_ac:
        bus.start()

    l_ac = []
    acordes = q_resul.get()
    while acordes != None:
    
    
    
        l_ac.append(acordes)
    
        acordes = q_resul.get()
    
    for bus in buscadores_ac:
        bus.join()
    
    
    mejores_acordes = max(l_ac, key = lambda x: x[1])
    print(mejores_acordes[0], mejores_acordes[1])

"""

# =============================================================================
# ACORDES Y MELODÍA
# =============================================================================


def main(num_busquedas_ac, num_busquedas_mel, genes, fun_dec_ac, fun_dec_mel, fun_mutar, fun_cruzar_ac, fun_cruzar_mel, fun_fitness_ac, fun_fitness_mel, longitud_individuos_ac, longitud_individuos_mel, longitud_acorde, notas_por_acorde_mel, grados_de_la_tonalidad, torneo_ac, torneo_mel, opt, individuos_por_gen_ac, individuos_por_gen_mel, generaciones_ac, generaciones_mel, prob_padres_ac, prob_padres_mel, prob_mutacion_ac, prob_mutacion_mel):
    
  
    
    problema_ac = ProblemaGeneticoAcordes(genes, fun_dec_ac, fun_mutar, fun_cruzar_ac, fun_fitness_ac, longitud_individuos_ac, longitud_acorde, grados_de_la_tonalidad)
    q_resul = Queue()
    
    num_busquedas = Value('i',num_busquedas_ac)    
    buscadores_ac = [Process(target=buscador, args = (q_resul, problema_ac, torneo_ac, opt, individuos_por_gen_ac, generaciones_ac, prob_padres_ac, prob_mutacion_ac, num_busquedas)) for _ in range(8)]
    for bus in buscadores_ac:
        bus.start()
    
    l_ac = []
    acordes = q_resul.get()
    while acordes != None:
        
        
        
        l_ac.append(acordes)
        
        acordes = q_resul.get()
        
    for bus in buscadores_ac:
        bus.join()
        
        
    mejores_acordes = max(l_ac, key = lambda x: x[1])
    print('mejores acordes: ', mejores_acordes[0], mejores_acordes[1], '\n', '\n')
    
    #NECESITAMOS TRANSFORMAR LOS ACORDES EN EL FORMATO QUE NOS INTERESA PARA LA MELODÍA
    
    acordes = mejores_acordes[0]
    for i in range(len(mejores_acordes[0])):
        for j in range(len(mejores_acordes[0][i])):
            acordes[i][j] = notas_codificar[mejores_acordes[0][i][j]]
    #print(acordes)
    
    
    

    #VAMOS A CALCULAR TODO EL INPUT QUE NECESITAMOS PARA CREAR LA MELODÍA A PARTIR DE LOS ACORDES
    escala = escala_modal(list(grados_de_la_tonalidad[0])[0], 'jonico')
    
   
    
    num_busquedas = Value('i', num_busquedas_mel)
    

    problema_mel = ProblemaGeneticoMelodia(genes, fun_dec_mel, fun_mutar, fun_cruzar_mel, fun_fitness_mel, longitud_individuos_mel, notas_por_acorde_mel, escala, acordes)
    
    buscadores_mel = [Process(target=buscador, args = (q_resul, problema_mel, torneo_mel, opt, individuos_por_gen_mel, generaciones_mel, prob_padres_mel, prob_mutacion_mel, num_busquedas)) for _ in range(8)]
    
    ##VACIAMOS PRIMERO LA COLA ANTES DE EMPEZAR A USARLA DE NUEVO
    while not q_resul.empty():
        q_resul.get()

    for bus in buscadores_mel:
        bus.start()
    
    l_mel = []
    
    melodia = q_resul.get()
    
    while melodia != None:
        
        
        
        l_mel.append(melodia)
        
        melodia = q_resul.get()
        
        
    for bus in buscadores_mel:
        bus.join()
        
    mejor_melodia = max(l_mel, key = lambda x: x[1])
    print('mejor melodia: ', mejor_melodia[0], mejor_melodia[1])
    
    while not q_resul.empty(): #VOLVEMOS A VACIAR LA COLA
        q_resul.get()
        

#RESULTADO FINAL DE COMBINAR LAS FUNCIONES DE APTITUD DE LOS ACORDES Y DE LA MELODÍA.

"""

if __name__ == "__main__":
    
     longitud_individuos_ac = 24
     longitud_acorde = [3]*8
     torneo_ac = 10
     opt = max
     individuos_por_gen_ac = 100
     generaciones_ac = 800
     prob_padres_ac = 0.9
     prob_mutacion_ac = 0.1
     num_busquedas_ac = 60
     
     
     #PARA EXPLORAR MEJOR LOS PARÁMETROS LOS DISTINGUIMOS PARA LOS ACORDES Y PARA LA MELODÍA
     longitud_individuos_mel = 32
     
     notas_por_acorde_mel = [4 for i in range(8)]          #EMPEZAMOS PONIENDO SÓLO CORCHEAS.
     escala = [0, 2, 4, 5, 7, 9, 11]  #DO MAYOR POR SIMPLICIDAD
     grados_de_la_tonalidad = calcular_grados(0)
     
     
     torneo_mel = 10
     opt = max
     individuos_por_gen_mel = 100
     generaciones_mel = 200
     prob_padres_mel = 0.7
     num_busquedas_mel = 60
     prob_mutacion_mel = 0.1
     
    
     main(num_busquedas_ac, num_busquedas_mel, genes, fun_dec_acordes, fun_dec_melodia, fun_mutar_int, fun_cruzar_dpc, fun_cruzar_dpc, func_fitness_acordes3, 
             fun_fitness_melodia5, longitud_individuos_ac, longitud_individuos_mel, longitud_acorde, notas_por_acorde_mel, grados_de_la_tonalidad,
             torneo_ac, torneo_mel, opt, individuos_por_gen_ac, individuos_por_gen_mel, generaciones_ac, generaciones_mel, prob_padres_ac,
             prob_padres_mel, prob_mutacion_ac, prob_mutacion_mel)
     

"""