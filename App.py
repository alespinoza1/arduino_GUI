import serial
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as Tk
from tkinter.ttk import Frame
from itertools import count
import random



class serialPlot:
    def __init__(self, puerto, baudios, longitud_grafico):
        self.port = puerto
        self.baud = baudios
        self.plotMaxLength = longitud_grafico

        print('Intentando conectar a: ' + str(puerto) + ' a ' + str(baudios) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(puerto, baudios, timeout=4)
            print('Conectado a: ' + str(puerto) + ' a ' + str(baudios) + ' BAUD.')
        except:
            print("Falla al conectar a: " + str(puerto) + ' a ' + str(baudios) + ' BAUD.')

    def leer_serial(self):
    # lee todos los elementos del serial separados por espacios hasta el salto de linea
        linea = self.serialConnection.readline()
        data = [float(val) for val in linea.split()] # lista con todos los elementos separados
        return data



class Window(Frame):
    def __init__(self, figure, master, obj_serialPlot, maxPlotLength):
        Frame.__init__(self, master)
        self.master = master        # ventana raiz
        self.serial_plot = obj_serialPlot      # objeto de la clase serialPlot
        self.initWindow(figure)     # Se inicializa con la funcion initWindow
        self.contador = count()
        self.maxLen = maxPlotLength
        self.y1_vals = deque([0.0]*self.maxLen, maxlen=self.maxLen)
        self.y2_vals = deque([0.0]*self.maxLen, maxlen=self.maxLen)

    def initWindow(self, figure):
        self.master.title("Grafico en tiempo real")
        canvas = FigureCanvasTkAgg(figure, master=self.master)
        toolbar = NavigationToolbar2Tk(canvas, self.master)
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # Se crean los witget en el la ventana raiz
        lbl1 = Tk.Label(self.master, text="Esto es un label")
        lbl1.pack(padx=5, pady=5)
        self.entry = Tk.Entry(self.master) # Se crea una entrada de texto
        self.entry.insert(0, '1.0')     # (index, string)
        self.entry.pack(padx=5)
        SendButton = Tk.Button(self.master, text='Send', command=self.funcionBoton) # se agrega un boton con la funcion
        SendButton.pack(padx=5)

    def funcionBoton(self):
        print(self.serial_plot.leer_serial())

    def graficar(self, frameNum, linea1,linea2):
        buffer = self.serial_plot.leer_serial() #lista leida


        if len(self.y1_vals) < self.maxLen:
            self.y1_vals.append(buffer[0])
            self.y2_vals.append(buffer[1])
        else:
            self.y1_vals.pop()
            self.y2_vals.pop()
            self.y1_vals.appendleft(buffer[0])
            self.y2_vals.appendleft(buffer[1])

        linea1.set_data(range(self.maxLen), self.y1_vals)
        linea2.set_data(range(self.maxLen), self.y2_vals)
        return linea1,linea2

def main():
    #Parametros del puerto serial
    portName = 'COM13'
    baudRate = 9600
    maxPlotLength = 100     # number of points in x-axis of real time plot
    arduino = serialPlot(portName, baudRate, maxPlotLength)

    #Parametros del gráfico
    xmin = 0
    xmax = maxPlotLength
    ymin = -(1)
    ymax = 100
    fig = plt.figure(figsize=(4, 4))
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title('Arduino data')
    ax.set_xlabel("Time")
    ax.set_ylabel("Humedad relativa")
    linea1, = ax.plot([], [])
    linea2, = ax.plot([], [])


    # Tkinter's GUI
    root = Tk.Tk()
    app = Window(fig, root, arduino, maxPlotLength)

    anim = animation.FuncAnimation(fig, app.graficar, fargs=(linea1, linea2), interval=2, blit=True)

    root.mainloop()



if __name__ == '__main__':
    main()