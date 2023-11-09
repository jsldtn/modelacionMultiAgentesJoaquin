''' Por: Joaquín Saldarriaga (A01783093); 11/08/23 '''
'''' Elaboración de ejercicio M1; multiagentes en un ambiente (room)... '''
''' Referencias principales: *https://mesa.readthedocs.io/en/stable/* 
*https://mesa.readthedocs.io/en/stable/tutorials/intro_tutorial.html*; *https://stackoverflow.com/questions/74963945/how-can-i-make-it-so-agents-only-perform-action-during-a-certain-time-step-in-me*;
*https://inst.eecs.berkeley.edu/~cs188/sp21/project2/*; *https://medium.com/agents-and-robots/a-multi-agent-system-in-python-74701f256c3a*;
'''

## Se importan las librerías 'mesa' y 'random'; ésta se usa para generar valores aleatorios: 'posiciones iniciales'
import mesa
import random

# Definir la clase agentePedestrian (orginal del Enunciado):
class agentePedestrian(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        ''' Ahora, se definen las 'posiciones iniciales' de los agentes... 
        las cuales se generan aleatoriamente partiendo de la Altura/height del Ambiente '''
                
        self.posicion = (0, random.choice(range(model.grid.height)))
        self.pasosFallidos = 0

    def step(self):
        if self.pasosFallidos > 3:
            # EN caso que un Agente ha tenido bastantes movimientos fallidos... se detiene.
            return

        # Se definen las 'posibles transiciones (i.e. 'movidas')' de cada Estado (celda)
        movidasPosibles = [(1, 0), (1, 1), (1, -1)]  # i.e. -> derecha, arriba-derecha, arriba-izquierda

        siguientePosicion = (
            
            self.posicion[0] + 1,
            self.posicion[1] + random.choice([-1, 0, 1]),
            
        )

        if self.model.is_cell_empty(siguientePosicion):
            
            # Si después de un movimiento, la 'celda final' está vacía...
            self.model.move_agent(self, siguientePosicion) # el Agente se mueve hacia esa Celda
            
        else:
            self.pasosFallidos += 1

# Se define la clase 'ObstacleAgent'
class ObstacleAgent(mesa.Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

# Se define la "nueva conducta" adicional: 'agenteRebelde':
class AgenteRebelde(mesa.Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.posicion = (0, random.choice(range(model.grid.height)))

    def step(self):
        siguientePosicion = (self.posicion[0] + 1, self.posicion[1])
        if self.model.is_cell_empty(siguientePosicion):
            self.model.move_agent(self, siguientePosicion)

# Se define el modelo 'modeloAgentePedestrian':
class modeloAgentePedestrian(mesa.Model):
    def __init__(self, width, height, numeroDeAgentes, densidadDeObstaculo, maximoNumDePasos):
        self.numeroDeAgentes = numeroDeAgentes
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.densidadDeObstaculo = densidadDeObstaculo
        self.maximoNumDePasos = maximoNumDePasos
        self.pasosRealizados = 0
        self.numDeAccidentes = 0
        self.numeroTotalDelAgente = 0

        # Mediante este 'for' se crean instancias de 'agentes peatones':
        for i in range(self.numeroDeAgentes):
            a = agentePedestrian(i, self)
            self.schedule.add(a)

            # Se agrega el agente a la fila inferior:
            x = 0
            y = random.randint(0, height - 1)
            self.grid.place_agent(a, (x, y))

        # Teniendo en cuenta la 'densidad' de obstáculos definida...
        # se crean instancias de 'agentes obstáculo':
        for x in range(width):
            
            for y in range(height):
                
                if random.random() < densidadDeObstaculo:
                    
                    obstacle = ObstacleAgent(self.numeroDeAgentes + x * height + y, self)
                    self.grid.place_agent(obstacle, (x, y))

    def is_cell_empty(self, posicion):
        # Se obtienen las 'x' e 'y' desde la Posición
        x, y = posicion

        # Se verifica que las coordenadas estén 'dentro' de los límites de la matriz Ambiente>
        if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
            
            # En tal caso, se verifica si (una) celda está vacía
            cellmates = self.grid.get_cell_list_contents([posicion])
            return not any(isinstance(agent, (agentePedestrian, ObstacleAgent)) for agent in cellmates)
        
        else:
            # De lo contrario,i.e. 'coordenadas  fuera de los límites'...
            # Se asume que la celda 'no' está vacía
            return False


    def move_agent(self, agent, posicion):
        
        # Se mueve un agente a una nueva Posición en el Ambiente:
        self.grid.move_agent(agent, posicion)
        if isinstance(agent, agentePedestrian):
            
            if self.grid.get_cell_list_contents([posicion]).count(agent) > 1:
                
                # Si dos agentes terminan en la Misma celda...
                # 'esto' se considera como un 'accidente':
                self.numDeAccidentes += 1
            
            self.numeroTotalDelAgente += 1

    def step(self):
        self.pasosRealizados += 1
        self.schedule.step()

# Se definen las Dimensiones y los parámetros para la simulación:
width = 30  # Ancho de la habitación    
height = 60  # Altura de la habitación
num_pedestrian_agents = 10  # Número de isntancias de 'agentePedestrian'
num_agentes_rebelde = 20  # Número de instancias de 'AgenteRebelde'
densidadDeObstaculo = 0.3  # Se define un 'porcentaje' de Obstáculos en el ambiente
maximoNumDePasos = 120  # Se define el máximo num. de 'pasos' para la simulación

'''
(en lo anterior) Se intentó definir '10' como base y height... sin embargo este fue el error:
raceback (most recent call last):
[...]
IndexError: list index out of range

Entonces se quito aumentar AMBAS dimensiones; siguiendo el requisito de "Habitación de MxN espacios."
'''

print("Ancho del ambiente - ", width)
print("Altura del ambiente - ", height)
print("Numero de instancias 'pedestrian agents' - ", num_pedestrian_agents)
print("Numero de instancias 'rebel agents' - ", num_agentes_rebelde)
print("Porcentaje de obstaculos (en decimal) - ", densidadDeObstaculo)
print("Maximo numero de pasos - ", maximoNumDePasos)

# Se crea y ejecuta el modelo para los agentes 'agentePedestrian'
pedestrian_model = modeloAgentePedestrian(width, height, num_pedestrian_agents, densidadDeObstaculo, maximoNumDePasos)
for _ in range(maximoNumDePasos):
    
    pedestrian_model.step()

# ... a partir del cual se recopila info. de los Agentes:
num_accidents_pedestrian = pedestrian_model.numDeAccidentes   # Num. de accidentes para los 'agentePedestrian'-s
agentePedestrianPasosTotales = pedestrian_model.numeroTotalDelAgente  # Num. total de 'movimientos' realizados

# Se calcula la 'velocidad promedio' de los agentes agentePedestrian:
average_speed_pedestrian = (num_pedestrian_agents * (maximoNumDePasos - num_accidents_pedestrian)) / agentePedestrianPasosTotales

# Se imprime la info. recopilada para los agentes 'agentePedestrian'
print("\nNúmero de accidentes para agentePedestrian - ", num_accidents_pedestrian)
print("Velocidad promedio de los agentes para agentePedestrian - ", average_speed_pedestrian)
print("Número de movimientos realizados por todos los agentes para agentePedestrian - ", agentePedestrianPasosTotales)

# Ahora se crea y ejecuta OTRO modelo para los agentes 'AgenteRebelde'-s:
modeloDelAgenteRebelde = modeloAgentePedestrian(width, height, num_agentes_rebelde, densidadDeObstaculo, maximoNumDePasos)
for _ in range(maximoNumDePasos):
    
    modeloDelAgenteRebelde.step()

# Se recopila su respectiva info.:
numeroAgentesRebelde = modeloDelAgenteRebelde.numDeAccidentes  # Num. de 'accidentes'
agenteRebeldePasosTotales = modeloDelAgenteRebelde.numeroTotalDelAgente  # Num. de 'movimientos' realizados (por este tipo de Agente)

# Se recopilar la 'velocidad promedio':
velocidadPromedioAgenteRebelde = (num_agentes_rebelde * (maximoNumDePasos - numeroAgentesRebelde)) / agenteRebeldePasosTotales

# Se imprime la info. anterior:
print("\nNúmero de accidentes para AgenteRebelde - ", numeroAgentesRebelde)
print("Velocidad promedio de los agentes para AgenteRebelde - ", velocidadPromedioAgenteRebelde)
print("Número de movimientos realizados por todos los agentes para AgenteRebelde -", agenteRebeldePasosTotales)
print("\n")

