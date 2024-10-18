import json


class Simbol:
    def __init__(self, simbol:str, name:str, category:str, yearreturn:float, status:str):
        self.simbol = simbol
        self.status = status
        self.name = name
        self.category = category
        self.yearreturn = yearreturn
     

class SimbolsCollection:
    def __init__(self):
        self.simbols = []

    def load_csv(self, filename:str):
        # CSV file structure        
        #  0 - Simbol                  string
        #  1 - Name                    string
        #  2 - Morningstar Category    string
        #  3 - YTD # (Daily)           float
        #  4 - 1 Yr                    float
        #  5 - 3 Yr                    float
        #  6 - 5 Yr                    float
        #  7 - 10 Yr                   float
        #  8 - Life of Fund            float
        #  9 - Net †                   float
        # 10 - Gross ‡                 float
        # 11 - Overall                 float
        
        try:
            with open(filename, 'r') as file:
                for line in file:
                    linedata = line.split(',')
                    if linedata[4] == '--':
                        yr = 0.0
                    else:
                        yr = float(linedata[4].replace("%", ""))
                    smb = Simbol(simbol = linedata[0],
                                name = linedata[1].replace('ï¿½',' '),
                                category = linedata[2],
                                yearreturn =  yr, 
                                status = 'unselected')
                    self.simbols.append(smb)
                   
                   
            
        except FileNotFoundError:
            print(f"The file {filename} does not exist.")   
        except PermissionError:
            print("You do not have permission to access this file.")  
        except IsADirectoryError:
            print("The specified path is a directory, not a file.")
        except IOError:
            print("An I/O error occurred.")
        
    def save(self):
        simbol_dicts = [simbol.__dict__ for simbol in self.simbols]
        with open('simbols.json', 'w') as file:
            json.dump(simbol_dicts, file, indent=4)

    def load(self):
        # Read the JSON file
        with open('simbols.json', 'r') as file:
            simbol_dicts = json.load(file)
        # Convert the list of dictionaries to a list of Person objects
        self.simbols =  [Simbol(**simbol_dict) for simbol_dict in simbol_dicts]
        return self.simbols

        
        # Test required
    def delete(self, simbol:Simbol):
        for i in range(0,len(self.simbols)):
            if self.simbols[i].simbol == simbol.simbol:
                self.simbols.pop(i)
                break
       
          # Test required
   
    def append(self, simbol:Simbol):
        self.simbols.append(simbol)

           # Test required
    def set_status(self, simbol:Simbol, new_status):
        for i in range(0,self.simbols):
            if self.simbols[i].simbol == simbol.simbol:
                self.simbols[i].status = new_status
                break
       


def main():
   
    sl = SimbolsCollection()
    sl.load_csv("docs\\fondslist.csv")
    sl.save()
    simbols = sl.load()
    #sl.delete(s)
    i=1

if __name__ == '__main__':
    main()

    'Fidelityï¿½Select Energy Portfolio (FSENX)'