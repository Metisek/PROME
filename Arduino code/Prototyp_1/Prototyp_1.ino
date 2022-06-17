//Dane do zmiany
char CHARACTER = 59 ;  //Separator w łańcuchu znaków dla liczb (59 ASCII = ;)

#include <ShiftRegister74HC595.h>
ShiftRegister74HC595<8> sr(2, 3, 4);  // Piny arduino, kolejno dla SDO, SCLK i LOAD

uint8_t  nB[] = {B11000000, //0
                      B11111001, //1 
                      B10100100, //2
                      B10110000, //3 
                      B10011001, //4
                      B10010010, //5
                      B10000010, //6
                      B11111000, //7
                      B10000000, //8
                      B10010000 //9
                     };

String serialData;
uint8_t registerNumbers[8] = {nB[0], nB[1], nB[2], nB[3], nB[4], nB[5], nB[6], nB[7]}; // Kolejno od 0 do 7, można pozmieniać indeksy

uint8_t tempNumbers[4] = {0,0,0,0};

String getValue(String data, char separator, int index){ // Zwraca dany kawałek teksty oddzielony znakiem (np.: ";")
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() -1;

  for (int i = 0; i <= maxIndex && found <= index; i++){
    if (data.charAt(i) == separator || i == maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

unsigned int getMaxSeparators(String data, char separator){ // Zwraca ilość wystąpień danego separatora
  int found = 0;
  int maxIndex = data.length() -1;

  for (int i = 0; i <= maxIndex; i++){
    if (data.charAt(i) == separator){
        found++;
    }
  }
  return found;
}

void writeDisplay(uint8_t numbersList[4]) { 
   for (int i = 0; i <= 3; i++){
    int number = numbersList[i];
    registerNumbers[1+(2*i)] = nB[number%10];
    registerNumbers[0+(2*i)] = nB[(number/10)%10];
   } 
   sr.setAll(registerNumbers);
}

void setup() {
  Serial.begin(115200); 
  sr.setAll(registerNumbers);
}

void loop() {
  if (Serial.available() > 0) {
    serialData = Serial.readString();
    int nrOfIndexes = getMaxSeparators(serialData, CHARACTER);
    bool check = 1;

    if (nrOfIndexes != 3){
      Serial.println(String("Error: podano następującą ilość rozdzieleń znaku: " + String(nrOfIndexes) + " dla znaku: '" + String(CHARACTER) +"', ciąg powinien posiadać 3."));
      check = 0;
    } else {
      
      for (int h = 0; h < nrOfIndexes+1; h++){
        String sub_serialData = getValue(serialData, CHARACTER, h);
        int numer = sub_serialData.toInt();
      
        if (numer < 0 || numer > 99){
          Serial.println("Error: liczba " + String(numer) + " w złym zakresie (należeć ma do zakresu od 0 do 99)");
          check = 0;
          break;
        } else {
          tempNumbers[h] = numer;
        }
      }
    }
    if (check == 1){
        writeDisplay(tempNumbers);
    }
  }
}
