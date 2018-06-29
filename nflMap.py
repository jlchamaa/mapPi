teams = {
'Dallas Cowboys': {'lednum': 11, 'color1': '#041E42','color2': '#FFFFFF'},
'New York Giants': {'lednum': 39, 'color1': '#001E62','color2': '#A6192E'},
'Philadelphia Eagles': {'lednum': 38, 'color1': '#064C53','color2': '#70808F'},
'Washington Redskins': {'lednum': 36, 'color1': '#862633','color2': '#FFCD00'},
'Buffalo Bills': {'lednum': 28, 'color1': '#00338D','color2': '#C8102E'},
'Miami Dolphins': {'lednum': 16, 'color1': '#008E97','color2': '#F58220'},
'New England Patriots': {'lednum': 40, 'color1': '#0C2340','color2': '#C8102E'},
'New York Jets': {'lednum': 39, 'color1': '#0C371D','color2': '#FFFFFF'},
'Arizona Cardinals': {'lednum': 2, 'color1': '#97233F','color2': '#FFC20E'},
'Los Angeles Rams': {'lednum': 3, 'color1': '#002244','color2': '#FFFFFF'},
'San Francisco 49ers': {'lednum': 4, 'color1': '#AA0000','color2': '#B3995E'},
'Seattle Seahawks': {'lednum': 7, 'color1': '#001433','color2': '#4DFF00'},
'Denver Broncos': {'lednum': 9, 'color1': '#FC4C02','color2': '#0C2340'},
'Kansas City Chiefs': {'lednum': 21, 'color1': '#C8102E','color2': '#FFB81C'},
'Los Angeles Chargers': {'lednum': 3, 'color1': '#0072CE','color2': '#FFB81C'},
'Oakland Raiders': {'lednum': 4, 'color1': '#101820','color2': '#A5ACAF'},
'Chicago Bears': {'lednum': 25, 'color1': '#051C2C','color2': '#DC4405'},
'Detroit Lions': {'lednum': 26, 'color1': '#0069B1','color2': '#FFFFFF'},
'Green Bay Packers': {'lednum': 23, 'color1': '#175E33','color2': '#FFB81C'},
'Minnesota Vikings': {'lednum': 22, 'color1': '#4F2683','color2': '#FFC62F'},
'Baltimore Ravens': {'lednum': 37, 'color1': '#241773','color2': '#D0B240'},
'Cincinnati Bengals': {'lednum': 34, 'color1': '#FC4C02','color2': '#FC4C02'},
'Cleveland Browns': {'lednum': 29, 'color1': '#EB3300','color2': '#382F2D'},
'Pittsburgh Steelers': {'lednum': 35, 'color1': '#FFB81C','color2': '#A5ACAF'},
'Atlanta Falcons': {'lednum': 19, 'color1': '#A6192E','color2': '#8C8B89'},
'Carolina Panthers': {'lednum': 33, 'color1': '#0085CA','color2': '#A5ACAF'},
'New Orleans Saints': {'lednum': 14, 'color1': '#D3BC8D','color2': '#FFFFFF'},
'Tampa Bay Buccaneers': {'lednum': 15, 'color1': '#C8102E','color2': '#FF8200'},
'Houston Texans': {'lednum': 13, 'color1': '#091F2C','color2': '#A6192E'},
'Indianapolis Colts': {'lednum': 30, 'color1': '#003A70','color2': '#FFFFFF'},
'Jacksonville Jaguars': {'lednum': 18, 'color1': '#006073','color2': '#D49F12'},
'Tennessee Titans ': {'lednum': 32, 'color1': '#0C2340','color2': '#4B92DB'} };
import subprocess
import serial, time, datetime

gamma = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 ]

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

ser = serial.Serial('/dev/ttyACM0', 38400)

def application(team,points):
    points=int(points)
    cityNum=int(teams[team]['lednum'])
    temp=teams[team]['color1']
    col1r=int(temp[1:3],16)
    col1g=int(temp[3:5],16)
    col1b=int(temp[5:7],16)
    temp=teams[team]['color2']
    col2r=int(temp[1:3],16)
    col2g=int(temp[3:5],16)
    col2b=int(temp[5:7],16)
    ba=bytearray()
    ba[0:8]=[cityNum,points,gamma[col1r],gamma[col1g],gamma[col1b],gamma[col2r],gamma[col2g],gamma[col2b],0]
    for index,value in enumerate(ba):
        ba[index]=min(255,value+1) #ensures zerobyte is the sole zero.  Adjust values back on Arduino Side!
    ba[8]=int(0)
    ser.write(ba)

def cycle():
    for key in teams:
        application(key,9)
        time.sleep(1)
def nfl():
    for path in execute(["node", "nflSockets.js"]):
        plusPos = path.find('+')
        commaPos = path.find(',')
        team=path[0:plusPos]
        points = int(path[plusPos+1:commaPos])
        application(team,points)
        print path

nfl()
