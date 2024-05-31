# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# *** Design by Barbosa, D. ***

# Importando as classes
import glob
import os
import multiprocessing
import math

## Importante read PL4
from lib_readPL4 import readPL4
from lib_writePL4 import writePL4


def execCutPL4(filePL4, pathPL4):

    ## Pasta com os resultados parciais

        dirResults = os.path.join(pathPL4, 'PL4Proc')

        try:
            if not os.path.isdir(dirResults):
                os.mkdir(dirResults)
        except OSError as error:
            print(error)

        # Tempo inicial do corte
        startCutTIME = 3
        # Tempo final do corte
        # Se o tempo for maior que o máximo, todo o arquivo será considerado
        finishCutTIME = 10
    
    #try:
        # DataFrame para Salvar os resultados

        # Lendo o arquivo PL4
        filePL4Processado = dirResults + "/" + filePL4[filePL4.rfind('/') + 1:filePL4.rfind('.pl4')] + 'proc.pl4'

        if not os.path.exists(filePL4Processado):

            dfHEADPL4, dataPL4, miscDataPL4 = readPL4(filePL4)
    
            # Calculando o tamanho do bloco

            if (startCutTIME < 0) or (startCutTIME > miscDataPL4['tmax']) or (startCutTIME > finishCutTIME):
                startTimeSteps = 0
            else:
                startTimeSteps = round(startCutTIME / miscDataPL4['deltat'])

            if (finishCutTIME < miscDataPL4['tmax']) and (finishCutTIME > startCutTIME):
                finishTimeSteps = round(finishCutTIME / miscDataPL4['deltat'])
            else:
                finishTimeSteps = len(dataPL4)

            # Fazendo o corte nos dados

            dataFile = dataPL4[startTimeSteps:finishTimeSteps, :]

            # Corrigindo o tempo para começar do zero
            dataFile = dataFile - dataFile[0, 0, None]

            # Corrigindo o cabeçalho

            miscDataPL4['steps'] = len(dataFile)

            miscDataPL4['tmax'] = dataFile[len(dataFile)-1][0] #(miscDataPL4['steps'] - 1) * miscDataPL4['deltat']

            miscDataPL4['lfirst'] = int(80 + 16 * (miscDataPL4['nvar'] / (miscDataPL4['numhfs'] + 1)) + 1)

            expsize = (5 + miscDataPL4['nvar']) * 16 + miscDataPL4['steps'] * (miscDataPL4['nvar'] + 1) * 4
            miscDataPL4['pl4size'] = expsize

            writePL4(filePL4Processado, dfHEADPL4, dataFile, miscDataPL4)

        else:
            print("[Error] Arquivo já existe: " + filePL4Processado)

    #except:
    #    print("[Error] Arquivo não processado: " + filePL4[filePL4.rfind('/') + 1:len(filePL4)] + "\n")


def execPL4Files(pathFiles):
    print('===========================================\n');
    print('<<<<<<<<<<<<<< Execute Cut PL4 >>>>>>>>>>>>\n');
    print('===========================================\n');

    extPL4 = '.pl4'

    # Pegando todos os arquivos .pl4 da pasta para processamento

    # to store files in a list
    listFilesPL4Path = glob.glob(pathFiles + '/*' + extPL4)

    #Verificando o tamanho dos PL4 antes de processar
    listFilesPL4 = []
    with open(pathFiles + "/" + "tamArquivosPL4.txt", "w") as checkPL4:
        checkPL4.write("Arquivos vazios! Verificar a simulação!\n")
        for filePL4 in listFilesPL4Path:
            get_size = os.path.getsize(filePL4)
            if get_size < 1000:
                checkPL4.write(filePL4 + "\n")
            else:
                listFilesPL4.append(filePL4)



    numberCores = os.cpu_count()

    numberFilesCore = math.ceil(len(listFilesPL4) / numberCores)

    filesPorCore = [listFilesPL4[i:i + numberFilesCore] for i in range(0, len(listFilesPL4), numberFilesCore)]

    threads = []

    # variando o arquivo PL4 da lista de path...
    index = 0

    while index < len(listFilesPL4):

        if (len(listFilesPL4) - index) > numberCores:
            numberCoresActive = numberCores
        else:
            numberCoresActive = (len(listFilesPL4) - index)

        for nCore in range(0, numberCoresActive):
            arquivoPL4= listFilesPL4[index + nCore]

            thr = multiprocessing.Process(target=execCutPL4, args=(arquivoPL4,pathFiles,))

            threads.append(thr)

            thr.start()

            print("Iniciando processamento PL4 [", nCore, "]: ", arquivoPL4[arquivoPL4.rfind('/') + 1:len(arquivoPL4)])

        for idxThr, thread in enumerate(threads):
            thread.join()

            print("PL4 Finalizado: [", idxThr, "]")

        index += numberCoresActive


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Definir a pasta com os arquivos .pl4 para processamento e pegar as variáveis que deseja
    # pathPL4 = ''
    #pathArquivos = '/hdarquivos/CNPq_2021/tBar/ExpP'
    pathArquivos = '/home/dbarbosa/ATPdata/work'
    pathArquivos = '/home/dbarbosa/ATPdata/work/PL4Proc/PL4Proc/PL4Proc'

    execPL4Files(pathArquivos)
