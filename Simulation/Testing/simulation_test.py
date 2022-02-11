import pytest
from pathlib import Path
from sys import path, set_coroutine_origin_tracking_depth
import logging
logging.basicConfig(filename='simulation_test.log', filemode='w', format='%(levelname)s ~ %(asctime)s -> %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

path.append(str(Path(__file__).parent.parent.absolute()))

from simulation import Simulation


@pytest.mark.parametrize('col, row, res1, res2, res3, res4',
                        [
                           (3,3,3,3,{},[]),  
                           (2,3,2,3,{},[]),  
                           (4,3,4,3,{},[])  
                        ]
                        )

def test_simulation_creation(col, row, res1, res2, res3, res4) -> None:
    # Crear Simuladior y checkear atributos
    sim = Simulation(row, col)
    assert sim.columns == res1
    assert sim.rows == res2
    assert sim.actual_species == res3
    assert sim.inter_dependences == res4
    
#@pytest.mark.skip()
def test_simulation_redimention_map_values() -> None:
    # Crear Simuladior, redimencionar y checkear atributos
    sim = Simulation(2,3)
    sim.Re_Dimention_Map(4,5)
    assert sim.columns == 5
    assert sim.rows == 4    
    sim.Re_Dimention_Map(1,2)
    assert sim.columns == 2
    assert sim.rows == 1
    sim.Re_Dimention_Map(3,1)
    assert sim.columns == 1
    assert sim.rows == 3
    sim.Re_Dimention_Map(2,4)
    assert sim.columns == 4
    assert sim.rows == 2

#@pytest.mark.skip()
def test_simulation() -> None:
    sim = Simulation(2,3)

    #Testeando añadir
    res1 = False
    res2 = False
    sim.Add_Species('Humano')
    sim.Add_Species('Marciano')
    sim.actual_species["Humano"].Set_Default_Characteristics()
    sim.actual_species["Marciano"].Set_Default_Characteristics()
    for actual in sim.actual_species.values():
        if actual.name == 'Humano':
            res1 = True
        elif actual.name == 'Marciano':
            res2 = True
    assert  res1
    assert  res2
    res1 = False
    res2 = False
    res3 = False
    sim.Add_Species('Humano')
    sim.Add_Species('Yedi')
    sim.actual_species["Yedi"].Set_Default_Characteristics()
    for actual in sim.actual_species.values():
        if actual.name == 'Humano':
            res1 = True
        elif actual.name == 'Marciano':
            res2 = True
        elif actual.name == 'Yedi':
            res3 = True
    assert  res1
    assert  res2
    assert  res3
    assert  len(sim.actual_species)==3

    #Testeando eliminar
    assert sim.Delete_Species(20) is None
    assert  len(sim.actual_species)==3
    assert sim.Delete_Species("juan") is None
    assert  len(sim.actual_species)==3

    sim.Delete_Species('Marciano')
    res1 = False
    res2 = False
    res3 = True
    for actual in sim.actual_species.values():
        if actual.name == 'Humano':
            res1 = True
        elif actual.name == 'Marciano':
            res3 = False
        elif actual.name == 'Yedi':
            res2 = True
    assert  res1
    assert  res2
    assert  res3
    assert  len(sim.actual_species)==2

    for specie in sim.actual_species:
        for i in range(sim.rows):
            for j in range(sim.columns):
                sim.Add_Society(i,j,specie, specie)                                
        sim.Set_Default_Species_Characteristic(specie)
        assert  len(sim.actual_species[specie].characteristic) == 13

    for i in range(2):
        for j in range(3):
            sim.Set_Default_Land_Characteristic(i,j)
            assert  len(sim.map[i][j].characteristic) == 6

    # Actualmente tenemos tenemos dos especies con las ccaracteristicas por defecto, y un terreno de 2 filas y 3 columnas 
    # A continuación agregaremos 3 interpedendencias especie especie, terreno terreno, terreno especie 
    # Luego comprobaremos que efectivamente la simulación se mueve un día y se cambia de valor las características

    sim.Add_Inter_Dependence([1,1], "Humano","Poblacion", [1,1],"Yedi", "Economía",5)
    sim.Move_One_Day_Inter_Dependences()
    assert  (sim.map[1][1]).Get_Entities_Characteristic_value('Yedi', "Economía") > 1

    sim.Add_Inter_Dependence([1,2], "","Altitud", [1,1],"", "Temperatura",-1)
    sim.Move_One_Day_Inter_Dependences()
    assert (sim.map[1][1]).Get_Entities_Characteristic_value(
        '', "Temperatura"
    ) != [0, 1]

        

    sim.Add_Inter_Dependence([0,0], "","Capacidad de Recursos", [0,0],"Humano", "Esperanza de Vida",2)
    sim.Move_One_Day_Inter_Dependences()
    assert  (sim.map[0][0]).Get_Entities_Characteristic_value('Humano', "Esperanza de Vida") > 1

    #Por último agregaremos dependencias entre especies y correremos todo un día verificando los avances
    sim.Add_Land_Dependences(0,1,"Humano","Poblacion","Humano","Poblacion",2)
    sim.Change_Land_Characteristic(0,1,"Fertilidad",[1,2])
    sim.Add_Land_Dependences(0,1,"","Fertilidad","","Capacidad de Recursos",10)

    sim.Move_One_Day_All()
    assert  (sim.map[1][1]).Get_Entities_Characteristic_value("Yedi","Economía") == 201
    assert  (sim.map[1][1]).Get_Entities_Characteristic_value("","Temperatura") == [-3,-2]
    assert  (sim.map[0][0]).Get_Entities_Characteristic_value("Humano","Esperanza de Vida") == 5
    assert  (sim.map[0][1]).Get_Entities_Characteristic_value("Humano", "Poblacion") == 30

    assert sim.actual_species["Humano"].societies == 6
    assert sim.actual_species["Humano"].characteristic['Natalidad']["summation"] == 6
    sim.Change_Society_Characteristic(0,0,"Humano", "Poblacion", -1)
    sim.Move_One_Day_All()
    assert sim.actual_species["Humano"].characteristic['Natalidad']["summation"] == 5
    assert sim.actual_species["Humano"].societies == 5
