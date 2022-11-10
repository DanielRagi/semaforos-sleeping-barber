# Sleepy-Barber.
# https://cs.uns.edu.ar/~gd/soyd/clasesgus/07-Ejemplosdesincronización2x.pdf
# https://lsi2.ugr.es/jagomez/sisopi_archivos/Sincronizacion.htm
# https://es.wikipedia.org/wiki/Problema_del_barbero_durmiente
# https://xdoc.mx/preview/72-procesos-cap-2-al-hacer-automatica-la-exclusion-5c020b09cd0d9 

# Una barbería consta de una sala de espera con n sillas y la silla de barbero. Si no hay clientes que
# atender, el barbero se va a dormir. Si un cliente ingresa a la barbería y todas las sillas están
# ocupadas, abandona la tienda. Si el barbero está ocupado, pero hay sillas disponibles, entonces el
# cliente se sienta en una de las sillas libres. Si el barbero está dormido, el cliente lo despierta.

from __future__ import with_statement
from threading import Thread, Semaphore
import time, random

def delay():
    time.sleep(1)

class Barberia:
    def __init__(self, numSillas):
        self.sillasDisponibles = numSillas
        self.mutexSillas = Semaphore(1)
        self.clientes = Semaphore(0)
        self.barberos = Semaphore(0)
        
    # Barbero queda listo. Si hay clientes en espera, pasa a uno.
    # Si no hay clientes en espera, queda dormido.
    def barbero_listo(self):
        self.clientes.acquire()            # Down
        self.mutexSillas.acquire()         # Down: queda dormido si no hay clientes.
        self.sillasDisponibles += 1        # Var
        self.barberos.release()            # Up
        self.mutexSillas.release()         # Up

    # Un cliente entra al lugar si hay sillas disponibles.
    def cliente_entra(self):
        self.mutexSillas.acquire()
        if self.sillasDisponibles > 0:
            self.sillasDisponibles -= 1
            return True
        else:
            self.mutexSillas.release()
            return False

    # El cliente toma asiento y espera a ser atendido.
    def cliente_espera(self):
        self.clientes.release()
        self.mutexSillas.release()
        self.barberos.acquire()

class Barbero(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        global barberia

        while True:
            print ("Barbero #%d: listo para cortar." % self.id)
            barberia.barbero_listo()
            delay()
            print ("Barbero #%d: atendiendo un cliente." % self.id)
            delay()
            print ("Barbero #%d: finalizó atención de cliente." % self.id)
            delay()

class Cliente(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        global barberia

        while True:
            print ("Cliente #%d: llegó a la barbería." % self.id)
            delay()
            if barberia.cliente_entra():
                print ("Cliente #%d: entró y tomó asiento en espera." % self.id)
                delay()
                barberia.cliente_espera()
                print ("Cliente #%d: atendido correctamente." % self.id)
                delay()
            else:
                print ("Cliente #%d: se retiró, no hay lugar." % self.id)
                delay()
            delay()

numBarberos=1
numClientes=4
barberia = Barberia(1)
for i in range(0, numBarberos):
    Barbero(i).start()
for i in range(0, numClientes):
    Cliente(i).start()